# -------------------------------------------------------
# a002_regions_provinces — ตารางภูมิภาค + จังหวัด สำหรับ seed ข้อมูลอ้างอิงประเทศไทย
# -------------------------------------------------------
from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "a002_regions_provinces"
down_revision: Union[str, None] = "a001_initial_schema"
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "regions",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("uuid_generate_v4()"),
        ),
        sa.Column("slug", sa.String(length=32), nullable=False),
        sa.Column("name_th", sa.String(length=64), nullable=False),
        sa.Column("sort_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.UniqueConstraint("slug"),
    )
    op.create_index("ix_regions_slug", "regions", ["slug"])

    op.create_table(
        "provinces",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("uuid_generate_v4()"),
        ),
        sa.Column(
            "region_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("regions.id", ondelete="RESTRICT"),
            nullable=False,
        ),
        sa.Column("name_th", sa.String(length=100), nullable=False),
        sa.Column("slug", sa.String(length=64), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.UniqueConstraint("name_th"),
        sa.UniqueConstraint("slug"),
    )
    op.create_index("ix_provinces_region_id", "provinces", ["region_id"])
    op.create_index("ix_provinces_name_th", "provinces", ["name_th"])

    op.execute(
        """
        CREATE TRIGGER trg_regions_updated_at
        BEFORE UPDATE ON regions
        FOR EACH ROW
        EXECUTE PROCEDURE educatalog_touch_updated_at();
        """
    )
    op.execute(
        """
        CREATE TRIGGER trg_provinces_updated_at
        BEFORE UPDATE ON provinces
        FOR EACH ROW
        EXECUTE PROCEDURE educatalog_touch_updated_at();
        """
    )


def downgrade() -> None:
    op.execute("DROP TRIGGER IF EXISTS trg_provinces_updated_at ON provinces;")
    op.execute("DROP TRIGGER IF EXISTS trg_regions_updated_at ON regions;")
    op.drop_table("provinces")
    op.drop_table("regions")
