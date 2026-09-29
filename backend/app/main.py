from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.db import Base, engine, get_db
from app.models import ApprovalOutcome, OperationRequest
from app.schemas import ApprovalAction, RequestCreate, RequestRead
from app.services.approvals import ApprovalConflictError, ApprovalStateError, decide_request
from app.services.audit import record_event
from app.worker import process_operation_request

DatabaseSession = Annotated[Session, Depends(get_db)]


@asynccontextmanager
async def lifespan(_: FastAPI) -> AsyncIterator[None]:
    Base.metadata.create_all(bind=engine)
    yield


app = FastAPI(
    title="AI Operations Agent API",
    version="0.1.0",
    lifespan=lifespan,
)


def request_statement(request_id: str):
    return (
        select(OperationRequest)
        .where(OperationRequest.id == request_id)
        .options(
            selectinload(OperationRequest.events),
            selectinload(OperationRequest.approval),
        )
    )


def load_request(db: Session, request_id: str) -> OperationRequest:
    request = db.scalar(request_statement(request_id))
    if request is None:
        raise HTTPException(status_code=404, detail="Request not found")
    return request


@app.get("/health")
def health() -> dict[str, str]:
    return {"status": "ok"}


@app.post("/requests", response_model=RequestRead, status_code=status.HTTP_201_CREATED)
def create_request(payload: RequestCreate, db: DatabaseSession) -> OperationRequest:
    request = OperationRequest(**payload.model_dump())
    db.add(request)
    db.flush()
    record_event(
        db,
        request_id=request.id,
        event_type="request_received",
        actor=payload.requester,
    )
    db.commit()

    process_operation_request.delay(request.id)
    return load_request(db, request.id)


@app.get("/requests", response_model=list[RequestRead])
def list_requests(db: DatabaseSession) -> list[OperationRequest]:
    statement = (
        select(OperationRequest)
        .options(
            selectinload(OperationRequest.events),
            selectinload(OperationRequest.approval),
        )
        .order_by(OperationRequest.created_at.desc())
    )
    return list(db.scalars(statement).all())


@app.get("/requests/{request_id}", response_model=RequestRead)
def get_request(request_id: str, db: DatabaseSession) -> OperationRequest:
    return load_request(db, request_id)


def apply_approval_action(
    *,
    request_id: str,
    payload: ApprovalAction,
    outcome: ApprovalOutcome,
    db: Session,
) -> OperationRequest:
    request = load_request(db, request_id)
    try:
        decide_request(
            db,
            request=request,
            outcome=outcome,
            actor=payload.actor,
            reason=payload.reason,
        )
    except (ApprovalConflictError, ApprovalStateError) as exc:
        raise HTTPException(status_code=409, detail=str(exc)) from exc
    return load_request(db, request_id)


@app.post("/requests/{request_id}/approve", response_model=RequestRead)
def approve_request(
    request_id: str,
    payload: ApprovalAction,
    db: DatabaseSession,
) -> OperationRequest:
    return apply_approval_action(
        request_id=request_id,
        payload=payload,
        outcome=ApprovalOutcome.APPROVED,
        db=db,
    )


@app.post("/requests/{request_id}/reject", response_model=RequestRead)
def reject_request(
    request_id: str,
    payload: ApprovalAction,
    db: DatabaseSession,
) -> OperationRequest:
    return apply_approval_action(
        request_id=request_id,
        payload=payload,
        outcome=ApprovalOutcome.REJECTED,
        db=db,
    )
