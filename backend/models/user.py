# -------------------------------------------------------
# ผู้ใช้ระบบ — role/status แยก enum เพราะสิทธิ์และการล็อกบัญชีไม่ใช่คอลัมน์เดียวกัน
# -------------------------------------------------------
from __future__ import annotations

import uuid
from enum import Enum as PyEnum

from sqlalchemy import Enum as SQLEnum, ForeignKey, Index, String, Uuid
from sqlalchemy.orm import Mapped, mapped_column, relationship

from models.base import Base, SoftDeleteMixin, TimestampMixin


class UserRole(str, PyEnum):
    visitor = "visitor"
    agency = "agency"
    admin = "admin"


class UserStatus(str, PyEnum):
    active = "active"
    pending = "pending"
    suspended = "suspended"


class User(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "users"
    __table_args__ = (
        Index("ix_users_email", "email"),
        Index("ix_users_role", "role"),
        Index("ix_users_status", "status"),
        Index("ix_users_agency_id", "agency_id"),
    )

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    email: Mapped[str] = mapped_column(String(320), nullable=False, unique=True)
    password_hash: Mapped[str] = mapped_column(String(255), nullable=False)
    full_name: Mapped[str] = mapped_column(String(255), nullable=False)
    role: Mapped[UserRole] = mapped_column(
        SQLEnum(UserRole, name="user_role", native_enum=False, length=32),
        nullable=False,
        default=UserRole.visitor,
    )
    status: Mapped[UserStatus] = mapped_column(
        SQLEnum(UserStatus, name="user_status", native_enum=False, length=32),
        nullable=False,
        default=UserStatus.pending,
    )
    agency_id: Mapped[uuid.UUID | None] = mapped_column(
        Uuid(as_uuid=True),
        ForeignKey("agencies.id", ondelete="SET NULL"),
        nullable=True,
    )

    agency: Mapped["Agency | None"] = relationship("Agency", back_populates="users", lazy="joined")
    owned_datasets: Mapped[list["Dataset"]] = relationship(
        "Dataset",
        back_populates="owner",
        foreign_keys="Dataset.owner_id",
        lazy="selectin",
    )
