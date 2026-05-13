# -------------------------------------------------------
# หน่วยงานเจ้าของข้อมูล — แยกตารางเพราะสิทธิ์และประเภทหน่วยงานกำหนด workflow คนละแบบ
# -------------------------------------------------------
from __future__ import annotations

import uuid
from enum import Enum as PyEnum

from sqlalchemy import Enum as SQLEnum, Index, String, Text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base, SoftDeleteMixin, TimestampMixin


class AgencyType(str, PyEnum):
    ministry = "ministry"
    department = "department"
    obec = "obec"
    university = "university"
    private = "private"
    other = "other"


class AgencyStatus(str, PyEnum):
    active = "active"
    suspended = "suspended"


class Agency(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "agencies"
    __table_args__ = (
        Index("ix_agencies_status", "status"),
        Index("ix_agencies_type", "type"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    name: Mapped[str] = mapped_column(String(255), nullable=False)
    code: Mapped[str | None] = mapped_column(String(64), nullable=True, unique=True)
    type: Mapped[AgencyType] = mapped_column(
        SQLEnum(AgencyType, name="agency_type", native_enum=True),
        nullable=False,
    )
    status: Mapped[AgencyStatus] = mapped_column(
        SQLEnum(AgencyStatus, name="agency_status", native_enum=True),
        nullable=False,
        default=AgencyStatus.active,
    )
    contact_email: Mapped[str | None] = mapped_column(String(320), nullable=True)
    address: Mapped[str | None] = mapped_column(Text, nullable=True)

    users: Mapped[list["User"]] = relationship("User", back_populates="agency", lazy="selectin")
    datasets: Mapped[list["Dataset"]] = relationship("Dataset", back_populates="agency", lazy="selectin")
