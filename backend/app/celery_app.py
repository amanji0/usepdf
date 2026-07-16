"""Celery application configuration."""

from celery import Celery

from app.config import get_settings

settings = get_settings()

celery_app = Celery(
    "usepdf",
    broker=settings.REDIS_URL,
    backend=settings.REDIS_URL,
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="UTC",
    enable_utc=True,
    task_soft_time_limit=300,
    task_time_limit=600,
    task_track_started=True,
    result_extended=True,
    task_routes={
        "app.tasks.office_*": {"queue": "office"},
    },
    task_default_queue="default",
    include=[
        "app.tasks.merge",
        "app.tasks.split",
        "app.tasks.rotate",
        "app.tasks.compress",
        "app.tasks.convert",
        "app.tasks.security",
        "app.tasks.office",
        "app.tasks.edit",
        "app.tasks.advanced",
        "app.tasks.intelligence",
        "app.utils.cleanup",
    ],
    beat_schedule={
        "cleanup-expired-files": {
            "task": "app.utils.cleanup.cleanup_expired_files",
            "schedule": 600.0,
        },
    },
)
