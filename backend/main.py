# -------------------------------------------------------
# Entry FastAPI — จัดลำดับ middleware / exception ก่อน include router
# เพราะลำดับมีผลต่อ response ที่ client ได้รับ (CORS + security headers)
# -------------------------------------------------------
from contextlib import asynccontextmanager

import redis.asyncio as redis
from redis.asyncio import Redis
from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy import text

from api.v1.router import router as api_v1_router
from core.config import get_settings
from core.database import engine
from core.errors import AppException


@asynccontextmanager
async def lifespan(app: FastAPI):
    # ping DB/Redis ตอน boot เพราะถ้า config ผิดจะ fail เร็ว ไม่ปล่อยให้ request แรกค้นหาเอง
    settings = get_settings()
    r: Redis | None = None
    try:
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        r = redis.from_url(settings.redis_url, decode_responses=True)
        await r.ping()
        app.state.redis = r
        yield
    finally:
        if r is not None:
            await r.aclose()
        await engine.dispose()


app = FastAPI(
    title=get_settings().app_name,
    version=get_settings().app_version,
    lifespan=lifespan,
)


@app.exception_handler(AppException)
async def app_exception_handler(_request: Request, exc: AppException) -> JSONResponse:
    # รูปแบบเดียวกับกฎ C3 — ไม่ส่ง stack trace ออกไปนอกแอป
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": exc.code.value,
            "code": exc.status_code,
            "detail": exc.detail,
        },
    )


_cors_origins = [o.strip() for o in get_settings().cors_origins.split(",") if o.strip()]
app.add_middleware(
    CORSMiddleware,
    allow_origins=_cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.middleware("http")
async def security_headers_middleware(request: Request, call_next):
    # ใส่หลัง CORS เพราะ header ความปลอดภัยต้องไปกับทุก response รวม error (กฎ D5)
    response = await call_next(request)
    response.headers["Strict-Transport-Security"] = "max-age=31536000"
    response.headers["X-Frame-Options"] = "DENY"
    response.headers["X-Content-Type-Options"] = "nosniff"
    response.headers["Content-Security-Policy"] = "default-src 'none'; frame-ancestors 'none'"
    return response


app.include_router(api_v1_router)


@app.get("/health")
async def health() -> dict[str, str]:
    return {"status": "ok", "version": get_settings().app_version}
