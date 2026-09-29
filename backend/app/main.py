from collections.abc import AsyncIterator
from contextlib import asynccontextmanager
from typing import Annotated

from fastapi import Depends, FastAPI, HTTPException, status
from sqlalchemy import select
from sqlalchemy.orm import Session, selectinload

from app.db import Base, engine, get_db
from app.models import OperationRequest
from app.schemas import RequestCreate, RequestRead
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

    statement = (
        select(OperationRequest)
        .where(OperationRequest.id == request.id)
        .options(selectinload(OperationRequest.events))
    )
    stored_request = db.scalar(statement)
    if stored_request is None:
        raise HTTPException(status_code=500, detail="Request persistence failed")
    return stored_request


@app.get("/requests", response_model=list[RequestRead])
def list_requests(db: DatabaseSession) -> list[OperationRequest]:
    statement = (
        select(OperationRequest)
        .options(selectinload(OperationRequest.events))
        .order_by(OperationRequest.created_at.desc())
    )
    return list(db.scalars(statement).all())


@app.get("/requests/{request_id}", response_model=RequestRead)
def get_request(request_id: str, db: DatabaseSession) -> OperationRequest:
    statement = (
        select(OperationRequest)
        .where(OperationRequest.id == request_id)
        .options(selectinload(OperationRequest.events))
    )
    request = db.scalar(statement)
    if request is None:
        raise HTTPException(status_code=404, detail="Request not found")
    return request
