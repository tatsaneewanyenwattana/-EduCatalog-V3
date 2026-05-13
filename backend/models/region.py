# -------------------------------------------------------
# ภูมิภาคระดับ master — แยกตารางเพราะจังหวัดอ้างอิง FK เดียวกันทุกระบบ (รายงาน/กรอง)
# -------------------------------------------------------
from __future__ import annotations

import uuid

from sqlalchemy import Index, Integer, String
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base, SoftDeleteMixin, TimestampMixin


class Region(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "regions"
    __table_args__ = (Index("ix_regions_slug", "slug"),)

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    slug: Mapped[str] = mapped_column(String(32), nullable=False, unique=True)
    name_th: Mapped[str] = mapped_column(String(64), nullable=False)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    provinces: Mapped[list["Province"]] = relationship(
        "Province",
        back_populates="region",
        lazy="selectin",
    )
