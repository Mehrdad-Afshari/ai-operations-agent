from unittest.mock import patch

import pytest
from sqlalchemy import create_engine
from sqlalchemy.orm import Session, sessionmaker

from app.db import Base
from app.models import OperationRequest, RequestStatus
from app.tasks import process_request


@pytest.fixture
def session_factory(tmp_path):
    engine = create_engine(f"sqlite:///{tmp_path / 'tasks.db'}")
    Base.metadata.create_all(engine)
    return sessionmaker(bind=engine)


def test_completed_request_is_not_processed_twice(session_factory) -> None:
    with session_factory() as db:
        request = OperationRequest(
            title="Find laptop",
            description="Find assigned laptop",
            requester="tester@example.com",
            status=RequestStatus.COMPLETED,
        )
        db.add(request)
        db.commit()
        request_id = request.id

    with (
        patch("app.tasks.SessionLocal", session_factory),
        patch("app.tasks.run_workflow") as run_workflow,
    ):
        process_request(request_id)

    run_workflow.assert_not_called()


def test_pending_approval_request_is_not_reprocessed(session_factory) -> None:
    with session_factory() as db:
        request = OperationRequest(
            title="Disable access",
            description="Disable account",
            requester="tester@example.com",
            status=RequestStatus.PENDING_APPROVAL,
        )
        db.add(request)
        db.commit()
        request_id = request.id

    with (
        patch("app.tasks.SessionLocal", session_factory),
        patch("app.tasks.run_workflow") as run_workflow,
    ):
        process_request(request_id)

    run_workflow.assert_not_called()

    with Session(session_factory.kw["bind"]) as db:
        stored = db.get(OperationRequest, request_id)
        assert stored is not None
        assert stored.status == RequestStatus.PENDING_APPROVAL
