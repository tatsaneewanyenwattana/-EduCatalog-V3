# -------------------------------------------------------
# งานส่งอีเมลแบบ async — ตอนนี้เป็น placeholder รอเชื่อม Resend ใน service จริง
# -------------------------------------------------------
from core.celery_app import celery_app


@celery_app.task(name="tasks.email_tasks.send_email_task")
def send_email_task() -> None:
    pass
