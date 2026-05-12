# -------------------------------------------------------
# กำหนดรหัสข้อผิดพลาดแบบ enum เพราะ router ต้องอ้างอิงค่าคงที่
# ไม่ hardcode string ใน response (กฎ C3)
# -------------------------------------------------------
from enum import Enum


class ErrorCode(str, Enum):
    """รหัส error ที่ client ใช้แยกประเภท — ตรงกับ API contract"""

    DATASET_NOT_FOUND = "DATASET_NOT_FOUND"
    UNAUTHORIZED = "UNAUTHORIZED"
    FORBIDDEN = "FORBIDDEN"
    VALIDATION_ERROR = "VALIDATION_ERROR"
    RATE_LIMIT_EXCEEDED = "RATE_LIMIT_EXCEEDED"
    FILE_TOO_LARGE = "FILE_TOO_LARGE"
    INVALID_FORMAT = "INVALID_FORMAT"
    VIRUS_DETECTED = "VIRUS_DETECTED"
    AGENCY_PENDING = "AGENCY_PENDING"
    ACCOUNT_SUSPENDED = "ACCOUNT_SUSPENDED"
    INTERNAL_ERROR = "INTERNAL_ERROR"


# แมป default HTTP status ต่อรหัส — service สามารถส่ง status_code เข้า AppException เพื่อ override ได้
_ERROR_DEFAULT_STATUS: dict[ErrorCode, int] = {
    ErrorCode.DATASET_NOT_FOUND: 404,
    ErrorCode.UNAUTHORIZED: 401,
    ErrorCode.FORBIDDEN: 403,
    ErrorCode.VALIDATION_ERROR: 422,
    ErrorCode.RATE_LIMIT_EXCEEDED: 429,
    ErrorCode.FILE_TOO_LARGE: 413,
    ErrorCode.INVALID_FORMAT: 400,
    ErrorCode.VIRUS_DETECTED: 400,
    ErrorCode.AGENCY_PENDING: 403,
    ErrorCode.ACCOUNT_SUSPENDED: 403,
    ErrorCode.INTERNAL_ERROR: 500,
}


class AppException(Exception):
    """ข้อยกเว้นระดับแอป — ให้ global handler แปลงเป็น JSON รูปแบบเดียวกันทั้งระบบ"""

    __slots__ = ("code", "detail", "status_code")

    def __init__(
        self,
        code: ErrorCode,
        detail: str,
        *,
        status_code: int | None = None,
    ) -> None:
        self.code = code
        self.detail = detail
        self.status_code = status_code if status_code is not None else _ERROR_DEFAULT_STATUS[code]
        super().__init__(detail)
