# -------------------------------------------------------
# Module : tasks
# หน้าที่ : Celery async tasks — งานส่งเมล, export, ประมวลผลหนักนอก request cycle
# -------------------------------------------------------
from core.celery_app import celery_app

__all__ = ("celery_app",)
