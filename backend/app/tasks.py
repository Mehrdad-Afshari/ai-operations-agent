from sqlalchemy.orm import Session

from app.db import SessionLocal
from app.models import OperationRequest, RequestStatus
from app.schemas import AgentDecision
from app.services.audit import record_event
from app.services.workflow import run_workflow

TERMINAL_OR_WAITING_STATUSES = {
    RequestStatus.PENDING_APPROVAL,
    RequestStatus.APPROVED,
    RequestStatus.REJECTED,
    RequestStatus.COMPLETED,
}


def process_request(request_id: str) -> None:
    db: Session = SessionLocal()
    request: OperationRequest | None = None
    try:
        request = db.get(OperationRequest, request_id)
        if request is None:
            return

        # Celery delivery is at-least-once. A retried/redelivered task must not
        # repeat an already completed tool call or overwrite an approval state.
        if request.status in TERMINAL_OR_WAITING_STATUSES:
            return

        request.status = RequestStatus.PROCESSING
        record_event(
            db,
            request_id=request.id,
            event_type="processing_started",
            actor="system",
        )

        state = run_workflow(request.title, request.description)
        decision = AgentDecision.model_validate(state["decision"])
        request.risk_level = decision.risk_level
        request.proposed_tool = decision.proposed_tool
        request.proposed_arguments = decision.tool_arguments

        record_event(
            db,
            request_id=request.id,
            event_type="agent_decision_created",
            actor="agent",
            details=decision.model_dump(mode="json"),
        )

        if state["requires_approval"]:
            request.status = RequestStatus.PENDING_APPROVAL
            record_event(
                db,
                request_id=request.id,
                event_type="approval_required",
                actor="policy_engine",
                details={"reason": state["policy_reason"]},
            )
        else:
            request.status = RequestStatus.COMPLETED
            record_event(
                db,
                request_id=request.id,
                event_type="tool_executed",
                actor="system",
                details={
                    "tool": decision.proposed_tool,
                    "result": state["tool_result"],
                },
            )

        db.commit()
    except Exception as exc:
        db.rollback()
        if request is not None:
            request.status = RequestStatus.FAILED
            record_event(
                db,
                request_id=request.id,
                event_type="processing_failed",
                actor="system",
                details={"error_type": type(exc).__name__},
            )
            db.commit()
        raise
    finally:
        db.close()
