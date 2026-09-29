from sqlalchemy import create_engine
from sqlalchemy.orm import Session

from app.db import Base
from app.models import ApprovalOutcome, OperationRequest, RequestStatus, RiskLevel
from app.services.approvals import ApprovalStateError, decide_request


def make_db() -> Session:
    engine = create_engine("sqlite+pysqlite:///:memory:")
    Base.metadata.create_all(engine)
    return Session(engine)


def make_pending_request(db: Session) -> OperationRequest:
    request = OperationRequest(
        title="Disable former employee access",
        description="Disable access for the departed employee account.",
        requester="ops@example.com",
        status=RequestStatus.PENDING_APPROVAL,
        risk_level=RiskLevel.HIGH,
        proposed_tool="disable_user_access",
        proposed_arguments={"reason": "employee departed"},
    )
    db.add(request)
    db.commit()
    db.refresh(request)
    return request


def test_approve_executes_once_and_completes_request() -> None:
    db = make_db()
    request = make_pending_request(db)

    result = decide_request(
        db,
        request=request,
        outcome=ApprovalOutcome.APPROVED,
        actor="reviewer@example.com",
        reason="Offboarding ticket verified.",
    )

    assert result.status is RequestStatus.COMPLETED
    assert result.approval is not None
    assert result.approval.outcome is ApprovalOutcome.APPROVED
    event_types = [event.event_type for event in result.events]
    assert event_types.count("tool_executed_after_approval") == 1

    try:
        decide_request(
            db,
            request=result,
            outcome=ApprovalOutcome.APPROVED,
            actor="reviewer@example.com",
            reason="Duplicate click.",
        )
    except ApprovalStateError:
        pass
    else:
        raise AssertionError("A completed request must not execute twice")


def test_reject_records_actor_reason_and_never_executes_tool() -> None:
    db = make_db()
    request = make_pending_request(db)

    result = decide_request(
        db,
        request=request,
        outcome=ApprovalOutcome.REJECTED,
        actor="security@example.com",
        reason="Identity could not be verified.",
    )

    assert result.status is RequestStatus.REJECTED
    assert result.approval is not None
    assert result.approval.actor == "security@example.com"
    assert result.approval.reason == "Identity could not be verified."
    event_types = [event.event_type for event in result.events]
    assert "request_rejected" in event_types
    assert "tool_executed_after_approval" not in event_types
