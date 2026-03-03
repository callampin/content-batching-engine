import logging
from celery import Celery

from app.config import settings

logger = logging.getLogger(__name__)

celery_app = Celery(
    "content_batching_engine",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=["workers.tasks"]
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_soft_time_limit=settings.celery_task_soft_time_limit,
    task_time_limit=settings.celery_task_time_limit,
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    worker_max_tasks_per_child=50,
)

logger.info(f"Celery app configured with broker: {settings.redis_url}")
