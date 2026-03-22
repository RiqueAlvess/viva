from celery import Celery
from app.core.config import settings

celery_app = Celery(
    "viva",
    broker=settings.CELERY_BROKER_URL,
    backend=settings.CELERY_RESULT_BACKEND,
    include=[
        "app.workers.tasks.email_tasks",
        "app.workers.tasks.score_tasks",
        "app.workers.tasks.report_tasks",
        "app.workers.tasks.invite_delay_tasks",
    ],
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    task_track_started=True,
    task_acks_late=True,
    worker_prefetch_multiplier=1,
    task_routes={
        "app.workers.tasks.email_tasks.*": {"queue": "email"},
        "app.workers.tasks.score_tasks.*": {"queue": "scoring"},
        "app.workers.tasks.report_tasks.*": {"queue": "reports"},
        "app.workers.tasks.invite_delay_tasks.*": {"queue": "default"},
    },
)
