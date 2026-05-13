# -------------------------------------------------------
# initial_schema — migration แรกของ EduCatalog V3
#
# สรุปตาราง (ลำดับสร้างตาม FK):
#   agencies              — หน่วยงานเจ้าของข้อมูล (กำหนดประเภท/สถานะหน่วยงาน)
#   categories            — หมวดหมู่แคตตาล็อก (slug ใช้ URL และกรอง)
#   users                 — บัญชีผู้ใช้ (role/status + ผูก agency ได้)
#   announcements         — ประกาศบนหน้าเว็บ (ช่วงเวลาแสดงผล)
#   feature_flags         — สวิตช์เปิด/ปิดฟีเจอร์จาก DB
#   datasets              — เรกคอร์ดชุดข้อมูลหลัก (เชื่อม agency/category/owner)
#   dataset_versions      — ไฟล์แต่ละเวอร์ชันของชุดข้อมูล (MinIO key, สแกนไวรัส)
#   data_dictionary_columns — นิยามคอลัมน์ต่อเวอร์ชัน (data dictionary)
#   quality_reports       — คะแนนคุณภาพ + สถิติรายคอลัมน์ (JSONB)
#   approval_logs         — ประวัติ submit/approve/reject จากแอดมิน
#   download_logs         — บันทึกดาวน์โหลด (rate limit / สถิติ, user ว่างได้)
#   audit_logs            — audit ระดับระบบ (action + resource + JSONB detail)
#   password_reset_tokens — โทเคนรีเซ็ตรหัส (เก็บแค่ hash)
# -------------------------------------------------------
from __future__ import annotations

from typing import Sequence, Union

import sqlalchemy as sa
from alembic import op
from sqlalchemy.dialects import postgresql

revision: str = "a001_initial_schema"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.execute('CREATE EXTENSION IF NOT EXISTS "uuid-ossp"')
    op.execute("CREATE EXTENSION IF NOT EXISTS pg_trgm")

    bind = op.get_bind()

    # --- PostgreSQL ENUM (ชื่อ type ต้องตรงกับ SQLAlchemy models native_enum=True) ---
    postgresql.ENUM(
        "ministry",
        "department",
        "obec",
        "university",
        "private",
        "other",
        name="agency_type",
    ).create(bind, checkfirst=True)
    postgresql.ENUM("active", "suspended", name="agency_status").create(bind, checkfirst=True)
    postgresql.ENUM("visitor", "agency", "admin", name="user_role").create(bind, checkfirst=True)
    postgresql.ENUM("active", "pending", "suspended", name="user_status").create(bind, checkfirst=True)
    postgresql.ENUM(
        "draft",
        "pending",
        "published",
        "rejected",
        "unpublished",
        name="dataset_status",
    ).create(bind, checkfirst=True)
    postgresql.ENUM("csv", "excel", "json", name="file_format").create(bind, checkfirst=True)
    postgresql.ENUM("pending", "passed", "failed", "infected", name="scan_status").create(
        bind,
        checkfirst=True,
    )
    postgresql.ENUM("string", "integer", "float", "date", "boolean", name="column_data_type").create(
        bind,
        checkfirst=True,
    )
    postgresql.ENUM(
        "submitted",
        "approved",
        "rejected",
        "resubmitted",
        name="approval_action",
    ).create(bind, checkfirst=True)

    agency_type = postgresql.ENUM(
        "ministry",
        "department",
        "obec",
        "university",
        "private",
        "other",
        name="agency_type",
        create_type=False,
    )
    agency_status = postgresql.ENUM("active", "suspended", name="agency_status", create_type=False)
    user_role = postgresql.ENUM("visitor", "agency", "admin", name="user_role", create_type=False)
    user_status = postgresql.ENUM("active", "pending", "suspended", name="user_status", create_type=False)
    dataset_status = postgresql.ENUM(
        "draft",
        "pending",
        "published",
        "rejected",
        "unpublished",
        name="dataset_status",
        create_type=False,
    )
    file_format = postgresql.ENUM("csv", "excel", "json", name="file_format", create_type=False)
    scan_status = postgresql.ENUM(
        "pending",
        "passed",
        "failed",
        "infected",
        name="scan_status",
        create_type=False,
    )
    column_data_type = postgresql.ENUM(
        "string",
        "integer",
        "float",
        "date",
        "boolean",
        name="column_data_type",
        create_type=False,
    )
    approval_action = postgresql.ENUM(
        "submitted",
        "approved",
        "rejected",
        "resubmitted",
        name="approval_action",
        create_type=False,
    )

    # --- agencies: หน่วยงานลงทะเบียน/เจ้าของชุดข้อมูล ---
    op.create_table(
        "agencies",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("uuid_generate_v4()"),
        ),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("code", sa.String(64), nullable=True, unique=True),
        sa.Column("type", agency_type, nullable=False),
        sa.Column("status", agency_status, nullable=False, server_default="active"),
        sa.Column("contact_email", sa.String(320), nullable=True),
        sa.Column("address", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_agencies_status", "agencies", ["status"])
    op.create_index("ix_agencies_type", "agencies", ["type"])

    # --- categories: หมวดแคตตาล็อก ---
    op.create_table(
        "categories",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("uuid_generate_v4()"),
        ),
        sa.Column("name", sa.String(255), nullable=False),
        sa.Column("slug", sa.String(128), nullable=False, unique=True),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("sort_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_categories_slug", "categories", ["slug"])
    op.create_index("ix_categories_is_active", "categories", ["is_active"])

    # --- users: บัญชี + สิทธิ์ (agency_id ว่างได้สำหรับ visitor/admin ที่ไม่ผูกหน่วยงาน) ---
    op.create_table(
        "users",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("uuid_generate_v4()"),
        ),
        sa.Column("email", sa.String(320), nullable=False, unique=True),
        sa.Column("password_hash", sa.String(255), nullable=False),
        sa.Column("full_name", sa.String(255), nullable=False),
        sa.Column("role", user_role, nullable=False, server_default="visitor"),
        sa.Column("status", user_status, nullable=False, server_default="pending"),
        sa.Column("agency_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("agencies.id", ondelete="SET NULL"), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_users_email", "users", ["email"])
    op.create_index("ix_users_role", "users", ["role"])
    op.create_index("ix_users_status", "users", ["status"])
    op.create_index("ix_users_agency_id", "users", ["agency_id"])

    # --- announcements: ข่าว/ประกาศบนเว็บ ---
    op.create_table(
        "announcements",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("uuid_generate_v4()"),
        ),
        sa.Column("title", sa.String(255), nullable=False),
        sa.Column("body", sa.Text(), nullable=False),
        sa.Column("is_active", sa.Boolean(), nullable=False, server_default=sa.text("true")),
        sa.Column("starts_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("ends_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint(
            "(starts_at IS NULL OR ends_at IS NULL OR ends_at >= starts_at)",
            name="ck_announcements_temporal_window",
        ),
    )
    op.create_index("ix_announcements_is_active", "announcements", ["is_active"])
    op.create_index("ix_announcements_ends_at", "announcements", ["ends_at"])

    # --- feature_flags: สวิตช์ฟีเจอร์ (อ่าน cache ตามกฎ C5) ---
    op.create_table(
        "feature_flags",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("uuid_generate_v4()"),
        ),
        sa.Column("key", sa.String(128), nullable=False, unique=True),
        sa.Column("enabled", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("config", postgresql.JSONB(astext_type=sa.Text()), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )

    # --- datasets: เรกคอร์ดชุดข้อมูลหลัก (workflow publish / quality / tags) ---
    op.create_table(
        "datasets",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("uuid_generate_v4()"),
        ),
        sa.Column("agency_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("agencies.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("category_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("categories.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("owner_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("title", sa.String(500), nullable=False),
        sa.Column("slug", sa.String(200), nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("status", dataset_status, nullable=False, server_default="draft"),
        sa.Column("tags", postgresql.ARRAY(sa.String(128)), nullable=False, server_default=sa.text("'{}'")),
        sa.Column("published_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("quality_score", sa.Numeric(5, 2), nullable=True),
        sa.Column("download_count", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("row_version", sa.Integer(), nullable=False, server_default="1"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint(
            "quality_score IS NULL OR (quality_score >= 0 AND quality_score <= 100)",
            name="ck_datasets_quality_score_range",
        ),
        sa.UniqueConstraint("agency_id", "slug", name="uq_datasets_agency_slug"),
    )
    op.create_index("ix_datasets_status", "datasets", ["status"])
    op.create_index("ix_datasets_category_id", "datasets", ["category_id"])
    op.create_index("ix_datasets_agency_id", "datasets", ["agency_id"])
    op.create_index("ix_datasets_owner_id", "datasets", ["owner_id"])
    op.create_index("ix_datasets_published_at", "datasets", ["published_at"])
    op.create_index("ix_datasets_quality_score", "datasets", ["quality_score"])
    op.create_index("ix_datasets_download_count", "datasets", ["download_count"])
    op.create_index(
        "ix_datasets_tags_gin",
        "datasets",
        ["tags"],
        unique=False,
        postgresql_using="gin",
    )

    # --- dataset_versions: ไฟล์จริงต่อเวอร์ชัน (ClamAV / checksum) ---
    op.create_table(
        "dataset_versions",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("uuid_generate_v4()"),
        ),
        sa.Column("dataset_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("datasets.id", ondelete="CASCADE"), nullable=False),
        sa.Column("version_number", sa.Integer(), nullable=False),
        sa.Column("file_format", file_format, nullable=False),
        sa.Column("storage_key", sa.String(1024), nullable=False),
        sa.Column("file_size_bytes", sa.BigInteger(), nullable=True),
        sa.Column("row_count", sa.Integer(), nullable=True),
        sa.Column("is_current", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("scan_status", scan_status, nullable=False, server_default="pending"),
        sa.Column("virus_signature", sa.String(255), nullable=True),
        sa.Column("checksum_sha256", sa.String(64), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.UniqueConstraint("dataset_id", "version_number", name="uq_dataset_versions_dataset_version"),
        sa.CheckConstraint(
            "file_size_bytes IS NULL OR file_size_bytes > 0",
            name="ck_dataset_versions_file_size_positive",
        ),
    )
    op.create_index("ix_dataset_versions_dataset_id", "dataset_versions", ["dataset_id"])
    op.create_index("ix_dataset_versions_is_current", "dataset_versions", ["is_current"])
    op.create_index("ix_dataset_versions_scan_status", "dataset_versions", ["scan_status"])

    # --- data_dictionary_columns: นิยามฟิลด์ต่อเวอร์ชัน (รวม flag PII) ---
    op.create_table(
        "data_dictionary_columns",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("uuid_generate_v4()"),
        ),
        sa.Column(
            "version_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("dataset_versions.id", ondelete="CASCADE"),
            nullable=False,
        ),
        sa.Column("column_key", sa.String(128), nullable=False),
        sa.Column("display_name", sa.String(255), nullable=False),
        sa.Column("data_type", column_data_type, nullable=False),
        sa.Column("description", sa.Text(), nullable=True),
        sa.Column("is_pii", sa.Boolean(), nullable=False, server_default=sa.text("false")),
        sa.Column("sort_order", sa.Integer(), nullable=False, server_default="0"),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_data_dictionary_columns_version_id", "data_dictionary_columns", ["version_id"])

    # --- quality_reports: คะแนนคุณภาพรวม + สถิติรายคอลัมน์ ---
    op.create_table(
        "quality_reports",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("uuid_generate_v4()"),
        ),
        sa.Column(
            "version_id",
            postgresql.UUID(as_uuid=True),
            sa.ForeignKey("dataset_versions.id", ondelete="CASCADE"),
            nullable=False,
            unique=True,
        ),
        sa.Column("overall_score", sa.Numeric(5, 2), nullable=True),
        sa.Column("column_stats", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
        sa.CheckConstraint(
            "overall_score IS NULL OR (overall_score >= 0 AND overall_score <= 100)",
            name="ck_quality_reports_overall_score_range",
        ),
    )
    op.create_index("ix_quality_reports_version_id", "quality_reports", ["version_id"])
    op.create_index("ix_quality_reports_overall_score", "quality_reports", ["overall_score"])

    # --- approval_logs: workflow อนุมัติชุดข้อมูล ---
    op.create_table(
        "approval_logs",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("uuid_generate_v4()"),
        ),
        sa.Column("dataset_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("datasets.id", ondelete="CASCADE"), nullable=False),
        sa.Column("admin_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="RESTRICT"), nullable=False),
        sa.Column("action", approval_action, nullable=False),
        sa.Column("comment", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_approval_logs_dataset_id", "approval_logs", ["dataset_id"])
    op.create_index("ix_approval_logs_admin_id", "approval_logs", ["admin_id"])
    op.create_index("ix_approval_logs_created_at", "approval_logs", ["created_at"])

    # --- download_logs: ดาวน์โหลด (visitor ไม่มี user_id) ---
    op.create_table(
        "download_logs",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("uuid_generate_v4()"),
        ),
        sa.Column("dataset_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("datasets.id", ondelete="CASCADE"), nullable=False),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("ip_address", sa.String(45), nullable=False),
        sa.Column("user_agent", sa.Text(), nullable=True),
        sa.Column("downloaded_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_download_logs_dataset_id", "download_logs", ["dataset_id"])
    op.create_index("ix_download_logs_ip_address", "download_logs", ["ip_address"])
    op.create_index("ix_download_logs_downloaded_at", "download_logs", ["downloaded_at"])

    # --- audit_logs: audit กว้าง (login, แก้ config, ฯลฯ) ---
    op.create_table(
        "audit_logs",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("uuid_generate_v4()"),
        ),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="SET NULL"), nullable=True),
        sa.Column("action", sa.String(128), nullable=False),
        sa.Column("resource_type", sa.String(64), nullable=False),
        sa.Column("resource_id", postgresql.UUID(as_uuid=True), nullable=True),
        sa.Column("detail", postgresql.JSONB(astext_type=sa.Text()), nullable=False, server_default=sa.text("'{}'::jsonb")),
        sa.Column("ip_address", sa.String(45), nullable=True),
        sa.Column("user_agent", sa.Text(), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_audit_logs_user_id", "audit_logs", ["user_id"])
    op.create_index("ix_audit_logs_action", "audit_logs", ["action"])
    op.create_index("ix_audit_logs_resource_type", "audit_logs", ["resource_type"])
    op.create_index("ix_audit_logs_created_at", "audit_logs", ["created_at"])

    # --- password_reset_tokens: flow ลืมรหัส ---
    op.create_table(
        "password_reset_tokens",
        sa.Column(
            "id",
            postgresql.UUID(as_uuid=True),
            primary_key=True,
            server_default=sa.text("uuid_generate_v4()"),
        ),
        sa.Column("user_id", postgresql.UUID(as_uuid=True), sa.ForeignKey("users.id", ondelete="CASCADE"), nullable=False),
        sa.Column("token_hash", sa.String(128), nullable=False, unique=True),
        sa.Column("expires_at", sa.DateTime(timezone=True), nullable=False),
        sa.Column("used_at", sa.DateTime(timezone=True), nullable=True),
        sa.Column("created_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("updated_at", sa.DateTime(timezone=True), server_default=sa.text("now()"), nullable=False),
        sa.Column("deleted_at", sa.DateTime(timezone=True), nullable=True),
    )
    op.create_index("ix_password_reset_tokens_user_id", "password_reset_tokens", ["user_id"])
    op.create_index("ix_password_reset_tokens_token_hash", "password_reset_tokens", ["token_hash"])
    op.create_index("ix_password_reset_tokens_expires_at", "password_reset_tokens", ["expires_at"])

    # --- trigger: อัปเดต updated_at ทุกตารางที่มีคอลัมน์นี้ (กันค่าเก่าตอน UPDATE แบบ raw SQL) ---
    op.execute(
        """
        CREATE OR REPLACE FUNCTION educatalog_touch_updated_at()
        RETURNS TRIGGER AS $$
        BEGIN
          NEW.updated_at = now();
          RETURN NEW;
        END;
        $$ LANGUAGE plpgsql;
        """
    )
    _tables_with_updated_at = (
        "agencies",
        "categories",
        "users",
        "announcements",
        "feature_flags",
        "datasets",
        "dataset_versions",
        "data_dictionary_columns",
        "quality_reports",
        "approval_logs",
        "download_logs",
        "audit_logs",
        "password_reset_tokens",
    )
    for tbl in _tables_with_updated_at:
        op.execute(
            f"""
            CREATE TRIGGER trg_{tbl}_updated_at
            BEFORE UPDATE ON {tbl}
            FOR EACH ROW
            EXECUTE PROCEDURE educatalog_touch_updated_at();
            """
        )

    # --- seed feature flags 8 ตัว (ตรงกับ .cursorrules FEATURE FLAGS) ---
    op.execute(
        """
        INSERT INTO feature_flags (id, key, enabled, description, config, created_at, updated_at, deleted_at)
        VALUES
          (uuid_generate_v4(), 'download_enabled', false,
           'เปิด/ปิดการดาวน์โหลดไฟล์ชุดข้อมูล', NULL, now(), now(), NULL),
          (uuid_generate_v4(), 'registration_open', false,
           'เปิดรับลงทะเบียนผู้ใช้ทั่วไป', NULL, now(), now(), NULL),
          (uuid_generate_v4(), 'agency_registration', false,
           'เปิดรับลงทะเบียนหน่วยงาน (agency)', NULL, now(), now(), NULL),
          (uuid_generate_v4(), 'search_enabled', false,
           'เปิดใช้งานการค้นหา (Elasticsearch)', NULL, now(), now(), NULL),
          (uuid_generate_v4(), 'preview_enabled', false,
           'แสดงตัวอย่างแถวข้อมูลบนหน้ารายละเอียด', NULL, now(), now(), NULL),
          (uuid_generate_v4(), 'contact_owner', false,
           'แสดงปุ่มติดต่อเจ้าของชุดข้อมูล + ส่งอีเมล', NULL, now(), now(), NULL),
          (uuid_generate_v4(), 'ckan_sync_enabled', false,
           'ซิงค์ metadata ไป data.go.th (CKAN)', NULL, now(), now(), NULL),
          (uuid_generate_v4(), 'maintenance_mode', false,
           'โหมดบำรุงรักษา (redirect ยกเว้น admin / feature-flags)', NULL, now(), now(), NULL);
        """
    )


def downgrade() -> None:
    # ลบ trigger/function ก่อนตาราง — กันฟังก์ชันอ้างอิงตารางที่เหลือ
    _tables_with_updated_at = (
        "password_reset_tokens",
        "audit_logs",
        "download_logs",
        "approval_logs",
        "quality_reports",
        "data_dictionary_columns",
        "dataset_versions",
        "datasets",
        "feature_flags",
        "announcements",
        "users",
        "categories",
        "agencies",
    )
    for tbl in _tables_with_updated_at:
        op.execute(f"DROP TRIGGER IF EXISTS trg_{tbl}_updated_at ON {tbl};")

    op.execute("DROP FUNCTION IF EXISTS educatalog_touch_updated_at();")

    op.drop_table("password_reset_tokens")
    op.drop_table("audit_logs")
    op.drop_table("download_logs")
    op.drop_table("approval_logs")
    op.drop_table("quality_reports")
    op.drop_table("data_dictionary_columns")
    op.drop_table("dataset_versions")
    op.drop_table("datasets")
    op.drop_table("feature_flags")
    op.drop_table("announcements")
    op.drop_table("users")
    op.drop_table("categories")
    op.drop_table("agencies")

    for enum_name in (
        "approval_action",
        "column_data_type",
        "scan_status",
        "file_format",
        "dataset_status",
        "user_status",
        "user_role",
        "agency_status",
        "agency_type",
    ):
        op.execute(f"DROP TYPE IF EXISTS {enum_name} CASCADE")

    op.execute("DROP EXTENSION IF EXISTS pg_trgm;")
    op.execute('DROP EXTENSION IF EXISTS "uuid-ossp";')
