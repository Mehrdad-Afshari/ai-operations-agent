from datetime import datetime

from pydantic import BaseModel, ConfigDict, Field

from app.models import RequestStatus, RiskLevel


class RequestCreate(BaseModel):
    title: str = Field(min_length=3, max_length=200)
    description: str = Field(min_length=10, max_length=5000)
    requester: str = Field(min_length=3, max_length=200)


class AuditEventRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    event_type: str
    actor: str
    details: dict
    created_at: datetime


class RequestRead(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: str
    title: str
    description: str
    requester: str
    status: RequestStatus
    risk_level: RiskLevel | None
    proposed_tool: str | None
    proposed_arguments: dict | None
    created_at: datetime
    updated_at: datetime
    events: list[AuditEventRead] = Field(default_factory=list)


class AgentDecision(BaseModel):
    category: str
    risk_level: RiskLevel
    proposed_tool: str
    tool_arguments: dict
    rationale: str
    confidence: float = Field(ge=0.0, le=1.0)
