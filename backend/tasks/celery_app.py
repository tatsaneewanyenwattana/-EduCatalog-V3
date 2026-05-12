# -------------------------------------------------------
# docker-compose ใช้ celery -A tasks.celery_app — Celery ต้องโหลดโมดูลชื่อ tasks.celery_app
# ถ้าใส่แค่ core.celery_app worker จะไม่ตรงกับคำสั่งใน compose และทีมอ้างอิง path ยาก
# ไฟล์นี้จึง re-export + import task modules เพื่อให้ลงทะเบียนเมื่อ worker start
# -------------------------------------------------------
from core.celery_app import celery_app

import tasks.email_tasks  # noqa: F401 — side-effect: ลงทะเบียน task
import tasks.scan_tasks  # noqa: F401

__all__ = ("celery_app",)
