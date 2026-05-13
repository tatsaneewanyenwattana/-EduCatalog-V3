# -------------------------------------------------------
# ประวัติการอนุมัติชุดข้อมูล — เก็บ action เป็น enum เพราะ dashboard กรองตามชุดค่าคงที่
# -------------------------------------------------------
from __future__ import annotations

import uuid
from enum import Enum as PyEnum

from sqlalchemy import Enum as SQLEnum, ForeignKey, Index, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base, SoftDeleteMixin, TimestampMixin


class ApprovalAction(str, PyEnum):
    submitted = "submitted"
    approved = "approved"
    rejected = "rejected"
    resubmitted = "resubmitted"


class ApprovalLog(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "approval_logs"
    __table_args__ = (
        Index("ix_approval_logs_dataset_id", "dataset_id"),
        Index("ix_approval_logs_admin_id", "admin_id"),
        Index("ix_approval_logs_created_at", "created_at"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    dataset_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("datasets.id", ondelete="CASCADE"),
        nullable=False,
    )
    admin_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
    )
    action: Mapped[ApprovalAction] = mapped_column(
        SQLEnum(ApprovalAction, name="approval_action", native_enum=True),
        nullable=False,
    )
    comment: Mapped[str | None] = mapped_column(Text, nullable=True)

    dataset: Mapped["Dataset"] = relationship("Dataset", back_populates="approval_logs", lazy="joined")
    admin: Mapped["User"] = relationship("User", lazy="joined", foreign_keys=[admin_id])
