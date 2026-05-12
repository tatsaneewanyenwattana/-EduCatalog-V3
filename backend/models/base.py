# -------------------------------------------------------
# Base + mixin รวมศูนย์ เพราะทุกตารางใช้รูปแบบเวลา/soft delete เหมือนกัน
# และ Alembic จะอ้างอิง Base.metadata เดียว
# -------------------------------------------------------
from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, Uuid, func
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column


class Base(DeclarativeBase):
    """Base declarative สำหรับ metadata เดียวของโปรเจกต์"""

    type_annotation_map = {
        uuid.UUID: Uuid(as_uuid=True),
    }


class TimestampMixin:
    """เวลาสร้าง/แก้ไข + เครื่องหมาย soft delete — ใช้ deleted_at IS NULL ใน query (กฎ B1/C7)"""

    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        onupdate=func.now(),
        nullable=False,
    )
    deleted_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True),
        nullable=True,
        default=None,
    )


class SoftDeleteMixin:
    """อ่านสถานะลบแบบสั้นๆ เพราะ repository จะกรอง deleted_at บ่อย — property ลดการเขียนซ้ำ"""

    @property
    def is_deleted(self) -> bool:
        return self.deleted_at is not None
