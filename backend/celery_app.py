"""
MediTrace Celery Configuration
===============================
Minimal broker config. Points to local Redis instance.
Auto-discovers tasks from the worker module.
"""

from celery import Celery

celery = Celery(
    "meditrace",
    broker="redis://localhost:6379/0",
    backend="redis://localhost:6379/0",
    include=["worker"]
)

# Serialization config — JSON only, no pickle exploits
celery.conf.update(
    task_serializer="json",
    accept_content=["json"],
    result_serializer="json",
    timezone="Asia/Kolkata",
    enable_utc=True,
    # Prevent tasks from running indefinitely on corrupted images
    task_soft_time_limit=120,   # 2 min soft limit (raises SoftTimeLimitExceeded)
    task_time_limit=180,        # 3 min hard kill
)
