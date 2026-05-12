# -------------------------------------------------------
# feature flag ใน DB — ให้ admin เปิด/ปิดได้โดยไม่ deploy ใหม่ (ตรงกับ .cursorrules FEATURE FLAGS)
# -------------------------------------------------------
from __future__ import annotations

import uuid

from sqlalchemy import Boolean, String, Text
from sqlalchemy.dialects.postgresql import JSONB
from sqlalchemy.orm import Mapped, mapped_column

from models.base import Base, SoftDeleteMixin, TimestampMixin


class FeatureFlag(Base, TimestampMixin, SoftDeleteMixin):
    __tablename__ = "feature_flags"

    id: Mapped[uuid.UUID] = mapped_column(primary_key=True, default=uuid.uuid4)
    key: Mapped[str] = mapped_column(String(128), nullable=False, unique=True)
    enabled: Mapped[bool] = mapped_column(Boolean, nullable=False, default=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    config: Mapped[dict | None] = mapped_column(JSONB, nullable=True)
