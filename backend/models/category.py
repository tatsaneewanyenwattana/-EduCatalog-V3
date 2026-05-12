# -------------------------------------------------------
# หมวดหมู่ชุดข้อมูล — slug ใช้ URL/ค้นหา เลย index แยกจากชื่อที่อ่านมนุษย์
# -------------------------------------------------------
from __future__ import annotations

import uuid

from sqlalchemy import Boolean, Index, Integer, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base, SoftDeleteMixin, TimestampMixin


class Category(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "categories"
    __table_args__ = (
        Index("ix_categories_slug", "slug"),
        Index("ix_categories_is_active", "is_active"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    slug: Mapped[str] = mapped_column(String(128), nullable=False, unique=True)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_active: Mapped[bool] = mapped_column(Boolean, nullable=False, default=True)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    datasets: Mapped[list["Dataset"]] = relationship("Dataset", back_populates="category", lazy="selectin")
