# -------------------------------------------------------
# Celery app อยู่ที่ core เพราะ broker/backend อ่านจาก settings เดียวกับ FastAPI
# แยกจาก tasks/ เพราะ tasks เป็นแค่ handler — หลีกเลี่ยงวงจร import ย้อนกลับ
# -------------------------------------------------------
from celery import Celery

from core.config import get_settings

_settings = get_settings()

celery_app = Celery(
    "educatalog",
    broker=_settings.celery_broker_url,
    backend=_settings.celery_result_backend,
)

celery_app.conf.update(
    task_serializer="json",
    result_serializer="json",
    accept_content=["json"],
    timezone="Asia/Bangkok",
    enable_utc=True,
    task_track_started=True,
)
