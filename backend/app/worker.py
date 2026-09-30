from celery import Celery  # type: ignore[import-untyped]

from app.config import get_settings
from app.tasks import process_request

settings = get_settings()
celery_app = Celery(
    "operations_agent",
    broker=settings.redis_url,
    backend=settings.redis_url,
)
celery_app.conf.update(
    task_acks_late=True,
    task_reject_on_worker_lost=True,
    worker_prefetch_multiplier=1,
    broker_connection_retry_on_startup=True,
)


@celery_app.task(
    name="process_operation_request",
    autoretry_for=(ConnectionError, TimeoutError),
    retry_backoff=True,
    retry_jitter=True,
    max_retries=3,
)
def process_operation_request(request_id: str) -> None:
    process_request(request_id)
