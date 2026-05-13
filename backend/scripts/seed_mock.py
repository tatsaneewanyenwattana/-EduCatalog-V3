# -------------------------------------------------------
# ข้อมูลปลอม — เก็บ logic จาก master seed ไม่ให้เข้ากันเพื่อกันพลาดเขียน postgres จาก dev เข้า prod
# -------------------------------------------------------
from __future__ import annotations

import asyncio
from decimal import Decimal
from uuid import UUID

import bcrypt
from sqlalchemy import func, select
from sqlalchemy.dialects.postgresql import insert as pg_insert
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import get_settings
from core.database import AsyncSessionLocal
from models.agency import Agency, AgencyStatus, AgencyType
from models.category import Category
from models.dataset import Dataset, DatasetStatus
from models.user import User, UserRole, UserStatus

# stable code ใน DB — conflict ที่ code; ชื่อภาษาไทยรวมคำย่อใน name เพราะ schema ไม่มีคอลัมน์ short_name แยก
AGENCY_ROWS: list[tuple[str, str, AgencyType]] = [
    ("mock-agency-obec", "สำนักงานคณะกรรมการการศึกษาขั้นพื้นฐาน (สพฐ.)", AgencyType.obec),
    ("mock-agency-moe", "กระทรวงศึกษาธิการ (ศธ.)", AgencyType.ministry),
    ("mock-agency-uni", "มหาวิทยาลัยทดสอบ (มทด.)", AgencyType.university),
]

def main() -> None:
    settings = get_settings()
    if settings.env.strip().lower() != "development":
        print("❌ ห้ามรัน seed_mock.py บน production")
        raise SystemExit(1)
    print("⚠️  MOCK DATA — ใช้เฉพาะ dev เท่านั้น")
    asyncio.run(_run())


def _hash_password(pw: str) -> str:
    rounds = get_settings().bcrypt_rounds
    return bcrypt.hashpw(pw.encode("utf-8"), bcrypt.gensalt(rounds=rounds)).decode("ascii")


DATASET_ROWS: list[
    tuple[str, str, str, str, list[str], Decimal]
] = [
    (
        "สถิตินักเรียนประถมศึกษาภาคเหนือ ปี 2567",
        "mock-ds-primary-north-2567",
        "primary",
        "mock-agency-obec",
        ["ประถมศึกษา", "ภาคเหนือ", "นักเรียน"],
        Decimal("87.5"),
    ),
    (
        "ข้อมูลครูมัธยมศึกษาทั่วประเทศ ปี 2567",
        "mock-ds-teachers-nation-2567",
        "teachers",
        "mock-agency-moe",
        ["ครู", "มัธยมศึกษา", "บุคลากร"],
        Decimal("92.0"),
    ),
    (
        "จำนวนโรงเรียนจำแนกตามขนาด ปี 2567",
        "mock-ds-schools-by-size-2567",
        "schools",
        "mock-agency-obec",
        ["โรงเรียน", "ขนาด", "สถิติ"],
        Decimal("78.5"),
    ),
    (
        "อัตราการเรียนต่อระดับมัธยมศึกษา ปี 2566-2567",
        "mock-ds-transition-lower-sec-2567",
        "lower-secondary",
        "mock-agency-obec",
        ["มัธยมศึกษา", "อัตราเรียนต่อ"],
        Decimal("83.0"),
    ),
    (
        "ข้อมูลนักศึกษาอุดมศึกษาภาคใต้ ปี 2567",
        "mock-ds-highed-south-2567",
        "higher-education",
        "mock-agency-uni",
        ["อุดมศึกษา", "ภาคใต้", "นักศึกษา"],
        Decimal("71.5"),
    ),
]


async def _exec_count_returning(session: AsyncSession, stmt) -> int:
    res = await session.execute(stmt)
    return len(res.fetchall())


async def seed_mock(session: AsyncSession, plain_password: str) -> dict[str, int]:
    counts: dict[str, int] = {
        "agencies": 0,
        "users": 0,
        "datasets": 0,
    }

    tbl_a = Agency.__table__
    for code, name, atype in AGENCY_ROWS:
        stmt = (
            pg_insert(tbl_a)
            .values(
                name=name,
                code=code,
                type=atype,
                status=AgencyStatus.active,
                contact_email=None,
                address=None,
            )
            .on_conflict_do_nothing(index_elements=[tbl_a.c.code])
            .returning(tbl_a.c.code)
        )
        counts["agencies"] += await _exec_count_returning(session, stmt)

    codes = [r[0] for r in AGENCY_ROWS]
    res = await session.execute(select(Agency.id, Agency.code).where(Agency.code.in_(codes)))
    agencies: dict[str, UUID] = {row.code: row.id for row in res.all()}  # type: ignore[attr-defined]

    obec_id = agencies.get("mock-agency-obec")
    moe_id = agencies.get("mock-agency-moe")
    univ_id = agencies.get("mock-agency-uni")
    if not obec_id or not moe_id or not univ_id:
        print("agency mock ไม่ครบจาก DB — ข้าม user/dataset")
        return counts

    hashed = _hash_password(plain_password)
    tbl_u = User.__table__

    stmt_agency = (
        pg_insert(tbl_u)
        .values(
            email="agency@mock.local",
            password_hash=hashed,
            full_name="ผู้ใช้หน่วยงาน (mock)",
            role=UserRole.agency,
            status=UserStatus.active,
            agency_id=obec_id,
        )
        .on_conflict_do_nothing(index_elements=[tbl_u.c.email])
        .returning(tbl_u.c.email)
    )
    counts["users"] += await _exec_count_returning(session, stmt_agency)

    stmt_visitor = (
        pg_insert(tbl_u)
        .values(
            email="visitor@mock.local",
            password_hash=hashed,
            full_name="ผู้ใช้ทั่วไป (mock)",
            role=UserRole.visitor,
            status=UserStatus.active,
            agency_id=None,
        )
        .on_conflict_do_nothing(index_elements=[tbl_u.c.email])
        .returning(tbl_u.c.email)
    )
    counts["users"] += await _exec_count_returning(session, stmt_visitor)

    settings = get_settings()
    emails_lookup = ["agency@mock.local", "visitor@mock.local"]
    admin_lr = settings.admin_email.strip().lower() if settings.admin_email.strip() else ""
    if admin_lr:
        emails_lookup.insert(0, admin_lr)

    ures = await session.execute(select(User.email, User.id).where(User.email.in_(emails_lookup)))
    user_ids: dict[str, UUID] = {email: uid for email, uid in ures.all()}

    owner_id: UUID | None = (
        user_ids.get(admin_lr) if admin_lr and admin_lr in user_ids else None
    ) or user_ids.get("agency@mock.local")
    if owner_id is None:
        print("ไม่มี owner สำหรับ dataset — รัน seed_master (admin) หรือมี agency@mock.local")
        return counts

    cats = await session.execute(select(Category.id, Category.slug).where(Category.deleted_at.is_(None)))
    cat_by_slug = {row.slug: row.id for row in cats.all()}  # type: ignore[attr-defined]

    tbl_d = Dataset.__table__
    for title, dslug, cat_slug, agency_code, tags, qscore in DATASET_ROWS:
        cid = cat_by_slug.get(cat_slug)
        aid = agencies.get(agency_code)
        if cid is None or aid is None:
            print(f"ข้าม dataset เพราะขาด category/agency — ให้รัน seed_master ก่อน: {dslug}")
            continue
        stmt_ds = (
            pg_insert(tbl_d)
            .values(
                agency_id=aid,
                category_id=cid,
                owner_id=owner_id,
                title=title,
                slug=dslug,
                description="ข้อมูลทดสอบจาก seed_mock — ลบเมื่อใช้ข้อมูลโปรดักชัน",
                status=DatasetStatus.published,
                tags=tags,
                published_at=func.now(),
                quality_score=qscore,
                download_count=42,
                row_version=1,
            )
            .on_conflict_do_nothing(index_elements=[tbl_d.c.agency_id, tbl_d.c.slug])
            .returning(tbl_d.c.slug)
        )
        counts["datasets"] += await _exec_count_returning(session, stmt_ds)

    return counts


async def _run() -> None:
    plain = get_settings().mock_users_password.strip()
    if not plain:
        print("ตั้ง MOCK_USERS_PASSWORD ใน .env (เช่น Test1234! ตามสเปก mock) — แล้วรันใหม่")
        raise SystemExit(2)

    async with AsyncSessionLocal() as session:
        async with session.begin():
            counts = await seed_mock(session, plain)

    print(
        "สรุป seed_mock (จำนวนแถวที่ insert จริงเท่านั้น): "
        f"agencies={counts['agencies']}, users={counts['users']}, datasets={counts['datasets']}"
    )


if __name__ == "__main__":
    main()
