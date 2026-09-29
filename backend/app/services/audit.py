from sqlalchemy.orm import Session

from app.models import AuditEvent


def record_event(
    db: Session,
    *,
    request_id: str,
    event_type: str,
    actor: str,
    details: dict | None = None,
) -> AuditEvent:
    event = AuditEvent(
        request_id=request_id,
        event_type=event_type,
        actor=actor,
        details=details or {},
    )
    db.add(event)
    db.flush()
    return event
