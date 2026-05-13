# -------------------------------------------------------
# จังหวัด 77 แห่ง — slug ใช้รหัสสั้น (เช่น RTGS) เพราะ URL/API อ่านง่ายกว่าชื่อไทย
# -------------------------------------------------------
from __future__ import annotations

import uuid

from sqlalchemy import ForeignKey, Index, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base, SoftDeleteMixin, TimestampMixin


class Province(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "provinces"
    __table_args__ = (
        Index("ix_provinces_region_id", "region_id"),
        Index("ix_provinces_name_th", "name_th"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    region_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("regions.id", ondelete="RESTRICT"),
        nullable=False,
    )
    name_th: Mapped[str] = mapped_column(String(100), nullable=False, unique=True)
    slug: Mapped[str] = mapped_column(String(64), nullable=False, unique=True)

    region: Mapped["Region"] = relationship("Region", back_populates="provinces", lazy="joined")
