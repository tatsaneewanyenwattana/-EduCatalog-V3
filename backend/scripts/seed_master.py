# -------------------------------------------------------
# ข้อมูลหมวด + ธงฟีเจอร์ + admin แรก — ใช้ได้ทั้ง dev และ production
# ถ้ามีคีย์/feature flag อยู่แล้ว insert ไม่เข้า (DO NOTHING); เปลี่ยนค่า enabled เก่าต้องจัดใน admin ไม่ให้แกะในรอบ seed ครั้งถัดไป
# -------------------------------------------------------
from __future__ import annotations

import asyncio

import bcrypt
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import get_settings
from core.database import AsyncSessionLocal
from models.category import Category
from models.feature_flag import FeatureFlag
from models.user import User, UserRole, UserStatus

# slug = คีย์ stable สำหรับเอกสาร/UI — ว่างจาก slug เก่ารุ่นหนึ่ง (preschool …) เพื่อกันชนเมื่อเริ่ม DB ใหม่
CATEGORY_ROWS: list[tuple[str, str, int]] = [
    ("early-childhood", "อนุบาล", 1),
    ("primary", "ประถมศึกษา", 2),
    ("lower-secondary", "มัธยมศึกษาตอนต้น", 3),
    ("upper-secondary", "มัธยมศึกษาตอนปลาย", 4),
    ("higher-education", "อุดมศึกษา", 5),
    ("teachers", "ครูและบุคลากร", 6),
    ("schools", "โรงเรียน", 7),
    ("others", "อื่นๆ", 8),
]

# ค่า enabled เป็น default เฉพาะครั้งที่ยังไม่มี row — ครั้งมีแล้วจะข้าม (กฎ ON CONFLICT DO NOTHING)
_FEATURE_FLAGS: list[tuple[str, str, bool]] = [
    ("download_enabled", "เปิด/ปิดการดาวน์โหลดไฟล์ชุดข้อมูล", True),
    ("registration_open", "เปิดรับลงทะเบียนผู้ใช้ทั่วไป", True),
    ("agency_registration", "เปิดรับลงทะเบียนหน่วยงาน (agency)", True),
    ("search_enabled", "เปิดใช้งานการค้นหา (Elasticsearch)", True),
    ("preview_enabled", "แสดงตัวอย่างแถวข้อมูลบนหน้ารายละเอียด", True),
    ("contact_owner", "แสดงปุ่มติดต่อเจ้าของชุดข้อมูล + ส่งอีเมล", True),
    ("ckan_sync_enabled", "ซิงค์ metadata ไป data.go.th (CKAN)", False),
    ("maintenance_mode", "โหมดบำรุงรักษา (redirect ยกเว้น admin / feature-flags)", False),
]


def _hash_password(pw: str) -> str:
    # rounds จาก config เพื่อให้ verify ภายใน API ด้วยรอบเดียวกัน
    rounds = get_settings().bcrypt_rounds
    return bcrypt.hashpw(pw.encode("utf-8"), bcrypt.gensalt(rounds=rounds)).decode("ascii")


async def _exec_count_returning(session: AsyncSession, stmt) -> int:
    res = await session.execute(stmt)
    return len(res.fetchall())


async def seed_master(session: AsyncSession) -> dict[str, int]:
    counts: dict[str, int] = {
        "categories": 0,
        "feature_flags": 0,
        "admin_user": 0,
    }

    tbl_c = Category.__table__
    for slug, name, sort_order in CATEGORY_ROWS:
        stmt = (
            pg_insert(tbl_c)
            .values(
                slug=slug,
                name=name,
                is_active=True,
                sort_order=sort_order,
            )
            .on_conflict_do_nothing(index_elements=[tbl_c.c.slug])
            .returning(tbl_c.c.slug)
        )
        counts["categories"] += await _exec_count_returning(session, stmt)

    tbl_f = FeatureFlag.__table__
    for key, description, enabled in _FEATURE_FLAGS:
        stmt = (
            pg_insert(tbl_f)
            .values(key=key, enabled=enabled, description=description)
            .on_conflict_do_nothing(index_elements=[tbl_f.c.key])
            .returning(tbl_f.c.key)
        )
        counts["feature_flags"] += await _exec_count_returning(session, stmt)

    settings = get_settings()
    email = settings.admin_email.strip().lower() if settings.admin_email.strip() else ""
    password = settings.admin_password.strip() if settings.admin_password.strip() else ""
    if email and password:
        u = User.__table__
        stmt = (
            pg_insert(u)
            .values(
                email=email,
                password_hash=_hash_password(password),
                full_name="System Admin",
                role=UserRole.admin,
                status=UserStatus.active,
                agency_id=None,
            )
            .on_conflict_do_nothing(index_elements=[u.c.email])
            .returning(u.c.email)
        )
        counts["admin_user"] += await _exec_count_returning(session, stmt)
    else:
        # ให้ข้ามได้เพราะบาง environment จะผูก admin จาก SSO หลังขึ้นระบบ
        print("ข้าม admin — ตั้ง ADMIN_EMAIL และ ADMIN_PASSWORD ใน .env ถ้าต้องการสร้างจาก seed")

    return counts


async def _run() -> None:
    async with AsyncSessionLocal() as session:
        async with session.begin():
            counts = await seed_master(session)

    print(
        "สรุป seed_master (จำนวนแถวที่ insert จริงเท่านั้น — รันซ้ำได้): "
        f"categories={counts['categories']}, feature_flags={counts['feature_flags']}, "
        f"admin_user={counts['admin_user']}"
    )


def main() -> None:
    asyncio.run(_run())


if __name__ == "__main__":
    main()
