from sqlalchemy.orm import Session

from app.db import SessionLocal
from app.models import OperationRequest, RequestStatus
from app.services.agent import make_deterministic_decision
from app.services.audit import record_event
from app.services.policy import evaluate_policy
from app.services.tools import execute_tool


def process_request(request_id: str) -> None:
    db: Session = SessionLocal()
    try:
        request = db.get(OperationRequest, request_id)
        if request is None:
            return

        request.status = RequestStatus.PROCESSING
        record_event(
            db,
            request_id=request.id,
            event_type="processing_started",
            actor="system",
        )

        decision = make_deterministic_decision(request.title, request.description)
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

        policy = evaluate_policy(decision)
        if policy.requires_approval:
            request.status = RequestStatus.PENDING_APPROVAL
            record_event(
                db,
                request_id=request.id,
                event_type="approval_required",
                actor="policy_engine",
                details={"reason": policy.reason},
            )
        else:
            result = execute_tool(decision.proposed_tool, decision.tool_arguments)
            request.status = RequestStatus.COMPLETED
            record_event(
                db,
                request_id=request.id,
                event_type="tool_executed",
                actor="system",
                details={"tool": decision.proposed_tool, "result": result},
            )

        db.commit()
    except Exception:
        db.rollback()
        raise
    finally:
        db.close()
