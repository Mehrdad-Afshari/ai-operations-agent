from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.models import ApprovalDecision, ApprovalOutcome, OperationRequest, RequestStatus
from app.services.audit import record_event
from app.services.tools import execute_tool


class ApprovalConflictError(RuntimeError):
    pass


class ApprovalStateError(RuntimeError):
    pass


def decide_request(
    db: Session,
    *,
    request: OperationRequest,
    outcome: ApprovalOutcome,
    actor: str,
    reason: str,
) -> OperationRequest:
    if request.status is not RequestStatus.PENDING_APPROVAL:
        raise ApprovalStateError("Request is not pending approval")
    if request.approval is not None:
        raise ApprovalConflictError("Request already has an approval decision")

    decision = ApprovalDecision(
        request_id=request.id,
        outcome=outcome,
        actor=actor,
        reason=reason,
    )
    db.add(decision)

    try:
        if outcome is ApprovalOutcome.REJECTED:
            request.status = RequestStatus.REJECTED
            record_event(
                db,
                request_id=request.id,
                event_type="request_rejected",
                actor=actor,
                details={"reason": reason},
            )
            db.commit()
            db.refresh(request)
            return request

        if request.proposed_tool is None or request.proposed_arguments is None:
            raise ApprovalStateError("Approved request has no executable tool proposal")

        request.status = RequestStatus.APPROVED
        record_event(
            db,
            request_id=request.id,
            event_type="request_approved",
            actor=actor,
            details={"reason": reason},
        )

        result = execute_tool(request.proposed_tool, request.proposed_arguments)
        request.status = RequestStatus.COMPLETED
        record_event(
            db,
            request_id=request.id,
            event_type="tool_executed_after_approval",
            actor="system",
            details={"tool": request.proposed_tool, "result": result},
        )
        db.commit()
        db.refresh(request)
        return request
    except IntegrityError as exc:
        db.rollback()
        raise ApprovalConflictError("Approval decision already exists") from exc
    except Exception:
        db.rollback()
        raise
