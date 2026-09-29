from celery import Celery

from app.config import get_settings
from app.tasks import process_request

settings = get_settings()
celery_app = Celery(
    "operations_agent",
    broker=settings.redis_url,
    backend=settings.redis_url,
)


@celery_app.task(name="process_operation_request")
def process_operation_request(request_id: str) -> None:
    process_request(request_id)
