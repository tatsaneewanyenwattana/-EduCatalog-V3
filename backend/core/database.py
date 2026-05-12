# -------------------------------------------------------
# engine/session แยกไฟล์เพราะ router ห้าม import engine โดยตรง — ใช้แค่ get_db
# -------------------------------------------------------
from collections.abc import AsyncGenerator

from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine

from core.config import get_settings

_settings = get_settings()

engine = create_async_engine(
    _settings.database_url,
    pool_size=_settings.db_pool_size,
    max_overflow=_settings.db_max_overflow,
    pool_timeout=_settings.db_pool_timeout,
    echo=_settings.debug,
)

AsyncSessionLocal = async_sessionmaker(
    engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False,
)


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    """แยก session ต่อ request — ไม่ commit ที่นี่เพราะให้ service เป็นคนกำหนดขอบเขตธุรกรรม"""
    async with AsyncSessionLocal() as session:
        yield session
