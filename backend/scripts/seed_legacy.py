# -------------------------------------------------------
# เก็บไว้อ้างอิงเท่านั้น — `scripts/seeds/master_data.py` และ `mock_data.py` ลบแล้ว
#
# เดิม orchestrator เดียว parse --master-only / --mock-only แล้วเรียก:
# - master_data.seed_master_tables()  → regions/provinces/categories (ในรุ่นเก่าไม่มี flags)
# - mock_data.seed_mock_tables()      → feature_flags + agencies + users + datasets
#
# ตอนนี้ใช้แทนด้วย:
#   python -m scripts.seed_master    # categories + feature_flags + admin จาก ADMIN_*
#   python -m scripts.seed_mock      # เฉพาะเมื่อ ENV=development (mock agencies/users/datasets)
# -------------------------------------------------------
from __future__ import annotations


def main() -> None:
    print(
        "seed_legacy เลิกใช้แล้ว — รัน: python -m scripts.seed_master และ python -m scripts.seed_mock "
        "(รายละเอียดดูคอมเมนต์ด้านบนไฟล์)"
    )
    raise SystemExit(3)


if __name__ == "__main__":
    main()
