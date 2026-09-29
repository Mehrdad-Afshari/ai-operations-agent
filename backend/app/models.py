import enum, uuid
from datetime import datetime, timezone
from sqlalchemy import JSON, DateTime, Enum, ForeignKey, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship
from app.db import Base

def utcnow() -> datetime: return datetime.now(timezone.utc)
class RequestStatus(str, enum.Enum):
    RECEIVED="received"; PROCESSING="processing"; PENDING_APPROVAL="pending_approval"; APPROVED="approved"; REJECTED="rejected"; COMPLETED="completed"; FAILED="failed"
class RiskLevel(str, enum.Enum): LOW="low"; MEDIUM="medium"; HIGH="high"
class OperationRequest(Base):
    __tablename__="operation_requests"
    id: Mapped[str]=mapped_column(String(36),primary_key=True,default=lambda:str(uuid.uuid4()))
    title: Mapped[str]=mapped_column(String(200)); description: Mapped[str]=mapped_column(Text); requester: Mapped[str]=mapped_column(String(200))
    status: Mapped[RequestStatus]=mapped_column(Enum(RequestStatus),default=RequestStatus.RECEIVED,index=True)
    risk_level: Mapped[RiskLevel|None]=mapped_column(Enum(RiskLevel),nullable=True); proposed_tool: Mapped[str|None]=mapped_column(String(100),nullable=True); proposed_arguments: Mapped[dict|None]=mapped_column(JSON,nullable=True)
    created_at: Mapped[datetime]=mapped_column(DateTime(timezone=True),default=utcnow); updated_at: Mapped[datetime]=mapped_column(DateTime(timezone=True),default=utcnow,onupdate=utcnow)
    events: Mapped[list["AuditEvent"]]=relationship(back_populates="request",cascade="all, delete-orphan")
class AuditEvent(Base):
    __tablename__="audit_events"
    id: Mapped[str]=mapped_column(String(36),primary_key=True,default=lambda:str(uuid.uuid4())); request_id: Mapped[str]=mapped_column(ForeignKey("operation_requests.id"),index=True)
    event_type: Mapped[str]=mapped_column(String(100)); actor: Mapped[str]=mapped_column(String(200)); details: Mapped[dict]=mapped_column(JSON,default=dict); created_at: Mapped[datetime]=mapped_column(DateTime(timezone=True),default=utcnow)
    request: Mapped[OperationRequest]=relationship(back_populates="events")
