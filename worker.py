import os
from celery import Celery

redis_url = os.getenv("REDIS_URL", "redis://localhost:6380/0")

celery_app = Celery(
    "worker",
    broker=redis_url,
    backend=redis_url,
    include=['tasks.email_tasks']  
)

celery_app.conf.update(
    task_track_started=True,
    task_serializer='json',
    accept_content=['json'],
    result_serializer='json',
    timezone='UTC',
    enable_utc=True,
)