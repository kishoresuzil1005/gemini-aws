from celery import Celery

celery = Celery(
    "cloudops",
    broker="redis://localhost:6379/0"
)

# Optional: Configure more advanced settings
celery.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="UTC",
    enable_utc=True,
)
