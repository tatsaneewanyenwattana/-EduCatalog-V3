# -------------------------------------------------------
# บันทึกการดาวน์โหลด — user_id ว่างได้เพราะ visitor ไม่ล็อกอิน (ตามสเปก)
# -------------------------------------------------------
from __future__ import annotations

import uuid
from datetime import datetime

from sqlalchemy import DateTime, ForeignKey, Index, String, Text, Uuid, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base, SoftDeleteMixin, TimestampMixin


class DownloadLog(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "download_logs"
    __table_args__ = (
        Index("ix_download_logs_dataset_id", "dataset_id"),
        Index("ix_download_logs_ip_address", "ip_address"),
        Index("ix_download_logs_downloaded_at", "downloaded_at"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    dataset_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("datasets.id", ondelete="CASCADE"),
        nullable=False,
    )
    user_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="SET NULL"),
        nullable=True,
    )
    ip_address: Mapped[str] = mapped_column(String(45), nullable=False)
    user_agent: Mapped[str | None] = mapped_column(Text, nullable=True)
    downloaded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True),
        server_default=func.now(),
        nullable=False,
    )

    dataset: Mapped["Dataset"] = relationship("Dataset", back_populates="download_logs", lazy="joined")
    user: Mapped["User | None"] = relationship("User", lazy="joined", foreign_keys=[user_id])
