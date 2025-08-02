from celery import Celery
from app.core.config import settings

celery_app = Celery(
    "email_tasks",
    broker=settings.celery_broker_url,
    backend=settings.celery_backend_url
)

celery_app.conf.update(
    task_routes={
        "app.services.email.tasks.*": {"queue": "email"},
    },
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="Asia/Shanghai",
    enable_utc=False,
)
