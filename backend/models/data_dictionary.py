# -------------------------------------------------------
# คอลัมน์ใน data dictionary ต่อหนึ่ง dataset version — แยกตารางเพราะจำนวนคอลัมน์ไม่คงที่
# -------------------------------------------------------
from __future__ import annotations

import uuid
from enum import Enum as PyEnum

from sqlalchemy import Boolean, Enum as SQLEnum, ForeignKey, Index, Integer, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base, SoftDeleteMixin, TimestampMixin


class ColumnDataType(str, PyEnum):
    string = "string"
    integer = "integer"
    float = "float"
    date = "date"
    boolean = "boolean"


class DataDictionaryColumn(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "data_dictionary_columns"
    __table_args__ = (Index("ix_data_dictionary_columns_version_id", "version_id"),)

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    version_id: Mapped[uuid.UUID] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("dataset_versions.id", ondelete="CASCADE"),
        nullable=False,
    )
    column_key: Mapped[str] = mapped_column(String(128), nullable=False)
    display_name: Mapped[str] = mapped_column(String(255), nullable=False)
    data_type: Mapped[ColumnDataType] = mapped_column(
        SQLEnum(ColumnDataType, name="column_data_type", native_enum=False, length=32),
        nullable=False,
    )
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    is_pii: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    sort_order: Mapped[int] = mapped_column(Integer, nullable=False, default=0)

    version: Mapped["DatasetVersion"] = relationship(
        "DatasetVersion",
        back_populates="dictionary_columns",
        lazy="joined",
    )
