# -------------------------------------------------------
# ชุดข้อมูลหลัก — tags ใช้ GIN เพราะ filter แบบ overlap ใน Postgres เร็วกว่า LIKE
# download_count อัปเดตด้วย atomic SQL ใน service (กฎ B6) ไม่ใช้ ORM read-modify-write
# -------------------------------------------------------
from __future__ import annotations

import uuid
from datetime import datetime
from enum import Enum as PyEnum

from sqlalchemy import DateTime, Enum as SQLEnum, ForeignKey, Index, Integer, Numeric, String, Text, Uuid, text
from sqlalchemy.dialects.postgresql import ARRAY
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base, SoftDeleteMixin, TimestampMixin


class DatasetStatus(str, PyEnum):
    draft = "draft"
    pending = "pending"
    published = "published"
    rejected = "rejected"
    unpublished = "unpublished"


class Dataset(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "datasets"
    __table_args__ = (
        Index("ix_datasets_status", "status"),
        Index("ix_datasets_category_id", "category_id"),
        Index("ix_datasets_agency_id", "agency_id"),
        Index("ix_datasets_owner_id", "owner_id"),
        Index("ix_datasets_published_at", "published_at"),
        Index("ix_datasets_quality_score", "quality_score"),
        Index("ix_datasets_download_count", "download_count"),
        Index("ix_datasets_tags_gin", "tags", postgresql_using="gin"),
        Index("uq_datasets_agency_slug", "agency_id", "slug", unique=True),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    agency_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("agencies.id", ondelete="RESTRICT"),
        nullable=False,
    )
    category_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("categories.id", ondelete="RESTRICT"),
        nullable=False,
    )
    owner_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("users.id", ondelete="RESTRICT"),
        nullable=False,
    )
    title: Mapped[str] = mapped_column(String(500), nullable=False)
    slug: Mapped[str] = mapped_column(String(200), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    status: Mapped[DatasetStatus] = mapped_column(
        SQLEnum(DatasetStatus, name="dataset_status", native_enum=True),
        nullable=False,
        default=DatasetStatus.draft,
    )
    tags: Mapped[list[str]] = mapped_column(
        ARRAY(String(128)),
        nullable=False,
        server_default=text("'{}'"),
    )
    published_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), nullable=True)
    quality_score: Mapped[float | None] = mapped_column(Numeric(5, 2), nullable=True)
    download_count: Mapped[int] = mapped_column(Integer, nullable=False, default=0)
    row_version: Mapped[int] = mapped_column(Integer, nullable=False, default=1)

    agency: Mapped["Agency"] = relationship("Agency", back_populates="datasets", lazy="joined")
    category: Mapped["Category"] = relationship("Category", back_populates="datasets", lazy="joined")
    owner: Mapped["User"] = relationship(
        "User",
        back_populates="owned_datasets",
        foreign_keys=[owner_id],
        lazy="joined",
    )
    versions: Mapped[list["DatasetVersion"]] = relationship(
        "DatasetVersion",
        back_populates="dataset",
        lazy="selectin",
    )
    approval_logs: Mapped[list["ApprovalLog"]] = relationship(
        "ApprovalLog",
        back_populates="dataset",
        lazy="selectin",
    )
    download_logs: Mapped[list["DownloadLog"]] = relationship(
        "DownloadLog",
        back_populates="dataset",
        lazy="selectin",
    )
