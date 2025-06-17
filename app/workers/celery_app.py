from celery import Celery
from app.core.config import settings
from datetime import timedelta

celery_app = Celery(
    "email_trigger",
    broker=settings.redis_url,
    backend=settings.redis_url,
    include=["app.workers.email_monitor"]
)

celery_app.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
    beat_schedule={
        "check-new-emails": {
            "task": "app.workers.email_monitor.check_all_users_emails",
            "schedule": 30.0,  # Check every 30 seconds
        },
        "process_attachments": {
            "task": "app.workers.email_monitor.process_attachments",
            "schedule": 60.0, # check every minute
        },
    },
)