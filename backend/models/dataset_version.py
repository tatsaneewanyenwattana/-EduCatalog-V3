# -------------------------------------------------------
# เวอร์ชันไฟล์ชุดข้อมูล — is_current ทำให้เลือกไฟล์ที่ใช้แสดงได้โดยไม่สแกนทุกแถว
# scan_status แยกจาก status ของ dataset เพราะเป็นผล pipeline ไฟล์เท่านั้น
# -------------------------------------------------------
from __future__ import annotations

import uuid
from enum import Enum as PyEnum

from sqlalchemy import Boolean, Enum as SQLEnum, ForeignKey, Index, BigInteger, Integer, String, UniqueConstraint, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base, SoftDeleteMixin, TimestampMixin


class FileFormat(str, PyEnum):
    csv = "csv"
    excel = "excel"
    json = "json"


class ScanStatus(str, PyEnum):
    pending = "pending"
    passed = "passed"
    failed = "failed"
    infected = "infected"


class DatasetVersion(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "dataset_versions"
    __table_args__ = (
        Index("ix_dataset_versions_dataset_id", "dataset_id"),
        Index("ix_dataset_versions_is_current", "is_current"),
        Index("ix_dataset_versions_scan_status", "scan_status"),
        UniqueConstraint("dataset_id", "version_number", name="uq_dataset_versions_dataset_version"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    dataset_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("datasets.id", ondelete="CASCADE"),
        nullable=False,
    )
    version_number: Mapped[int] = mapped_column(Integer, nullable=False)
    file_format: Mapped[FileFormat] = mapped_column(
        SQLEnum(FileFormat, name="file_format", native_enum=True),
        nullable=False,
    )
    storage_key: Mapped[str] = mapped_column(String(1024), nullable=False)
    file_size_bytes: Mapped[int | None] = mapped_column(BigInteger, nullable=True)
    row_count: Mapped[int | None] = mapped_column(Integer, nullable=True)
    is_current: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    scan_status: Mapped[ScanStatus] = mapped_column(
        SQLEnum(ScanStatus, name="scan_status", native_enum=True),
        nullable=False,
        default=ScanStatus.pending,
    )
    virus_signature: Mapped[str | None] = mapped_column(String(255), nullable=True)
    checksum_sha256: Mapped[str | None] = mapped_column(String(64), nullable=True)

    dataset: Mapped["Dataset"] = relationship("Dataset", back_populates="versions", lazy="joined")
    dictionary_columns: Mapped[list["DataDictionaryColumn"]] = relationship(
        "DataDictionaryColumn",
        back_populates="version",
        lazy="selectin",
        cascade="all, delete-orphan",
    )
    quality_report: Mapped["QualityReport | None"] = relationship(
        "QualityReport",
        back_populates="version",
        lazy="joined",
        uselist=False,
        cascade="all, delete-orphan",
    )
