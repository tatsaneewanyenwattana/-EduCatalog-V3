# -------------------------------------------------------
# Module : models
# หน้าที่ : SQLAlchemy ORM models — กำหนดโครงสร้างตารางใน database
# import ครบที่นี่เพราะ Alembic ใช้ Base.metadata — ถ้าไม่ import โมดูล model จะไม่ถูก register
# -------------------------------------------------------
from models.agency import Agency, AgencyStatus, AgencyType
from models.announcement import Announcement
from models.approval_log import ApprovalAction, ApprovalLog
from models.audit_log import AuditLog
from models.base import Base, SoftDeleteMixin, TimestampMixin
from models.category import Category
from models.data_dictionary import ColumnDataType, DataDictionaryColumn
from models.dataset import Dataset, DatasetStatus
from models.dataset_version import DatasetVersion, FileFormat, ScanStatus
from models.download_log import DownloadLog
from models.feature_flag import FeatureFlag
from models.password_reset_token import PasswordResetToken
from models.province import Province
from models.quality_report import QualityReport
from models.region import Region
from models.user import User, UserRole, UserStatus

__all__ = (
    "Agency",
    "AgencyStatus",
    "AgencyType",
    "Announcement",
    "ApprovalAction",
    "ApprovalLog",
    "AuditLog",
    "Base",
    "Category",
    "ColumnDataType",
    "DataDictionaryColumn",
    "Dataset",
    "DatasetStatus",
    "DatasetVersion",
    "DownloadLog",
    "FeatureFlag",
    "FileFormat",
    "PasswordResetToken",
    "Province",
    "QualityReport",
    "Region",
    "ScanStatus",
    "SoftDeleteMixin",
    "TimestampMixin",
    "User",
    "UserRole",
    "UserStatus",
)
