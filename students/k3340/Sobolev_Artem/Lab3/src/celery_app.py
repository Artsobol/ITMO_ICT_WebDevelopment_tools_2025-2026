from celery import Celery

from core.config import settings

periodic_parse_urls = settings.celery.get_periodic_parse_urls()

celery_app = Celery(
    "lab3",
    broker=settings.celery.broker_url,
    backend=settings.celery.result_backend,
    include=["tasks.parser_tasks"],
)

celery_app.conf.update(
    task_default_queue=settings.celery.task_default_queue,
    task_track_started=True,
    broker_connection_retry_on_startup=True,
    accept_content=["json"],
    task_serializer="json",
    result_serializer="json",
    result_expires=3600,
    beat_schedule=(
        {
            "enqueue-periodic-book-parsing": {
                "task": "parser.enqueue_periodic_parse_batch",
                "schedule": settings.celery.periodic_parse_interval_seconds,
            }
        }
        if periodic_parse_urls
        else {}
    ),
)
