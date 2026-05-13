# -------------------------------------------------------
# อ่านค่าจาก .env ผ่าน pydantic-settings เพราะ validate ชนิดตอน boot
# และกันค่า default กระจัดกระจายในโค้ด (กฎ A5)
# -------------------------------------------------------
from functools import lru_cache
from urllib.parse import quote

from pydantic import Field, field_validator
from pydantic_settings import BaseSettings, SettingsConfigDict


class Settings(BaseSettings):
    """ค่าคอนฟิกทั้งหมดจาก environment / backend/.env"""

    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    # --- Application ---
    app_name: str = Field(validation_alias="APP_NAME")
    app_version: str = Field(validation_alias="APP_VERSION")
    env: str = Field(validation_alias="ENV")
    debug: bool = Field(validation_alias="DEBUG")
    host: str = Field(validation_alias="HOST")
    port: int = Field(validation_alias="PORT")
    secret_key: str = Field(validation_alias="SECRET_KEY")

    # --- PostgreSQL ---
    postgres_host: str = Field(validation_alias="POSTGRES_HOST")
    postgres_port: int = Field(validation_alias="POSTGRES_PORT")
    postgres_user: str = Field(validation_alias="POSTGRES_USER")
    postgres_password: str = Field(validation_alias="POSTGRES_PASSWORD")
    postgres_db: str = Field(validation_alias="POSTGRES_DB")
    database_url_env: str | None = Field(default=None, validation_alias="DATABASE_URL")
    db_pool_size: int = Field(validation_alias="DB_POOL_SIZE")
    db_max_overflow: int = Field(validation_alias="DB_MAX_OVERFLOW")
    db_pool_timeout: int = Field(validation_alias="DB_POOL_TIMEOUT")

    # --- Redis ---
    redis_host: str = Field(validation_alias="REDIS_HOST")
    redis_port: int = Field(validation_alias="REDIS_PORT")
    redis_password: str = Field(validation_alias="REDIS_PASSWORD")
    redis_db: int = Field(validation_alias="REDIS_DB")
    redis_url_env: str | None = Field(default=None, validation_alias="REDIS_URL")

    # --- Celery ---
    celery_broker_url: str = Field(validation_alias="CELERY_BROKER_URL")
    celery_result_backend: str = Field(validation_alias="CELERY_RESULT_BACKEND")

    # --- Elasticsearch ---
    es_host: str = Field(validation_alias="ES_HOST")
    es_port: int = Field(validation_alias="ES_PORT")
    es_scheme: str = Field(validation_alias="ES_SCHEME")
    es_user: str = Field(validation_alias="ES_USER")
    es_password: str = Field(validation_alias="ES_PASSWORD")
    es_index_datasets: str = Field(validation_alias="ES_INDEX_DATASETS")

    # --- MinIO ---
    minio_endpoint: str = Field(validation_alias="MINIO_ENDPOINT")
    minio_access_key: str = Field(validation_alias="MINIO_ACCESS_KEY")
    minio_secret_key: str = Field(validation_alias="MINIO_SECRET_KEY")
    minio_secure: bool = Field(validation_alias="MINIO_SECURE")
    minio_bucket_datasets: str = Field(validation_alias="MINIO_BUCKET_DATASETS")
    minio_bucket_temp: str = Field(validation_alias="MINIO_BUCKET_TEMP")

    # --- JWT ---
    jwt_secret: str = Field(validation_alias="JWT_SECRET")
    jwt_algorithm: str = Field(validation_alias="JWT_ALGORITHM")
    jwt_access_expire_minutes: int = Field(validation_alias="JWT_ACCESS_EXPIRE_MINUTES")
    jwt_refresh_expire_days: int = Field(validation_alias="JWT_REFRESH_EXPIRE_DAYS")

    # --- Encryption ---
    encryption_key: str = Field(validation_alias="ENCRYPTION_KEY")

    # --- Email ---
    resend_api_key: str = Field(validation_alias="RESEND_API_KEY")
    email_from: str = Field(validation_alias="EMAIL_FROM")
    email_from_name: str = Field(validation_alias="EMAIL_FROM_NAME")

    # --- ClamAV ---
    clamav_host: str = Field(validation_alias="CLAMAV_HOST")
    clamav_port: int = Field(validation_alias="CLAMAV_PORT")

    # --- CKAN ---
    ckan_url: str = Field(validation_alias="CKAN_URL")
    ckan_api_key: str = Field(validation_alias="CKAN_API_KEY")

    # --- Upload ---
    upload_max_size_mb: int = Field(validation_alias="UPLOAD_MAX_SIZE_MB")
    upload_allowed_formats: str = Field(validation_alias="UPLOAD_ALLOWED_FORMATS")

    # --- Rate limit ---
    rate_limit_api_per_min: int = Field(validation_alias="RATE_LIMIT_API_PER_MIN")
    rate_limit_download_files_per_hour: int = Field(
        validation_alias="RATE_LIMIT_DOWNLOAD_FILES_PER_HOUR"
    )
    rate_limit_download_mb_per_hour: int = Field(
        validation_alias="RATE_LIMIT_DOWNLOAD_MB_PER_HOUR"
    )

    # --- Cache TTL (วินาที) ---
    cache_ttl_search: int = Field(validation_alias="CACHE_TTL_SEARCH")
    cache_ttl_dataset: int = Field(validation_alias="CACHE_TTL_DATASET")
    cache_ttl_schema: int = Field(validation_alias="CACHE_TTL_SCHEMA")
    cache_ttl_flags: int = Field(validation_alias="CACHE_TTL_FLAGS")

    # --- Pagination ---
    pagination_default_limit: int = Field(validation_alias="PAGINATION_DEFAULT_LIMIT")
    pagination_max_limit: int = Field(validation_alias="PAGINATION_MAX_LIMIT")

    # --- Security ---
    bcrypt_rounds: int = Field(validation_alias="BCRYPT_ROUNDS")
    cors_origins: str = Field(validation_alias="CORS_ORIGINS")

    # --- Logging ---
    log_level: str = Field(validation_alias="LOG_LEVEL")
    log_format: str = Field(validation_alias="LOG_FORMAT")

    # --- Bootstrap admin — ใช้ `python -m scripts.seed_master` (รัน production ได้)
    admin_email: str = Field(default="", validation_alias="ADMIN_EMAIL")
    admin_password: str = Field(default="", validation_alias="ADMIN_PASSWORD")
    # รหัส bcrypt ผู้ใช้ mock เท่านั้น (`seed_mock`) — แยกจากผู้ใช้จริงเพื่อตัดออกเมื่อมีข้อมูลโปรดักชัน
    mock_users_password: str = Field(default="", validation_alias="MOCK_USERS_PASSWORD")

    @field_validator("debug", "minio_secure", mode="before")
    @classmethod
    def _coerce_bool(cls, v: object) -> bool:
        # รับทั้ง string จาก .env และ bool จาก environment อื่น
        if isinstance(v, bool):
            return v
        return str(v).lower() in ("true", "1", "yes", "on")

    @property
    def database_url(self) -> str:
        """URL async สำหรับ SQLAlchemy — ใช้ DATABASE_URL จาก .env ถ้ามี ไม่งั้นประกอบจาก POSTGRES_*"""
        if self.database_url_env and self.database_url_env.strip():
            return self.database_url_env.strip()
        user_q = quote(self.postgres_user, safe="")
        if self.postgres_password:
            pwd_q = quote(self.postgres_password, safe="")
            auth = f"{user_q}:{pwd_q}@"
        else:
            # คงรูปแบบ user:@host เพราะ asyncpg คาด colon แม้รหัสว่าง
            auth = f"{user_q}:@"
        return (
            f"postgresql+asyncpg://{auth}"
            f"{self.postgres_host}:{self.postgres_port}/{self.postgres_db}"
        )

    @property
    def redis_url(self) -> str:
        """URL Redis สำหรับ client — ใช้ REDIS_URL จาก .env ถ้ามี ไม่งั้นประกอบจาก host/port/db/password"""
        if self.redis_url_env and self.redis_url_env.strip():
            return self.redis_url_env.strip()
        password = quote(self.redis_password, safe="") if self.redis_password else ""
        auth = f":{password}@" if password else ""
        return f"redis://{auth}{self.redis_host}:{self.redis_port}/{self.redis_db}"


@lru_cache
def get_settings() -> Settings:
    # lru_cache เพราะ Settings อ่านจาก disk ครั้งเดียวพอ — ลดการสร้าง instance ซ้ำตอน inject
    return Settings()
