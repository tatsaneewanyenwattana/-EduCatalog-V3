# -------------------------------------------------------
# งานสแกนไฟล์ (เช่น ClamAV) แบบ async — placeholder รอ pipeline จริง
# -------------------------------------------------------
from core.celery_app import celery_app


@celery_app.task(name="tasks.scan_tasks.scan_file_task")
def scan_file_task() -> None:
    pass
