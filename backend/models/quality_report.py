# -------------------------------------------------------
# รายงานคุณภาพต่อหนึ่ง version — column_stats เป็น JSONB เพราะโครงสร้างย่อยเปลี่ยนตาม dataset
# -------------------------------------------------------
from __future__ import annotations

import uuid

from sqlalchemy import ForeignKey, Index, Numeric, Uuid, text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base, SoftDeleteMixin, TimestampMixin


class QualityReport(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "quality_reports"
    __table_args__ = (
        Index("ix_quality_reports_version_id", "version_id"),
        Index("ix_quality_reports_overall_score", "overall_score"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    version_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("dataset_versions.id", ondelete="CASCADE"),
        nullable=False,
        unique=True,
    )
    overall_score: Mapped[float | None] = mapped_column(Numeric(5, 2), nullable=True)
    column_stats: Mapped[dict] = mapped_column(JSONB, nullable=False, server_default=text("'{}'::jsonb"))

    version: Mapped["DatasetVersion"] = relationship(
        "DatasetVersion",
        back_populates="quality_report",
        lazy="joined",
    )
