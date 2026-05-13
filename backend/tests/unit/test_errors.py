# -------------------------------------------------------
# เทสต์เลเยอร์ core/errors — ไม่ import main.py เลย (กัน lifespan ไป ping DB/Redis)
# -------------------------------------------------------
from core.errors import AppException, ErrorCode


def test_app_exception_uses_default_http_status() -> None:
    exc = AppException(ErrorCode.DATASET_NOT_FOUND, "ไม่พบชุดข้อมูล")
    assert exc.status_code == 404
    assert exc.code is ErrorCode.DATASET_NOT_FOUND


def test_app_exception_respects_status_override() -> None:
    exc = AppException(ErrorCode.INTERNAL_ERROR, "ซ่อมบำรุง", status_code=503)
    assert exc.status_code == 503
