# -------------------------------------------------------
# ประกาศบนเว็บ — ends_at ใช้ปิดการแสดงอัตโนมัติโดยไม่ต้องลบแถว
# -------------------------------------------------------
from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import Boolean, DateTime, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column

from models.base import Base, SoftDeleteMixin, TimestampMixin


class Announcement(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "announcements"
    __table_args__ = (
        Index("ix_announcements_is_active", "is_active"),
        Index("ix_announcements_ends_at", "ends_at"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    title: Mapped[str] = mapped_column(String(255), nullable=False)
    body: Mapped[str] = mapped_column(Text, nullable=False)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    starts_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    ends_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
