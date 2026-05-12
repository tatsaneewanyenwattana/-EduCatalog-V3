# -------------------------------------------------------
# รวม router ของ v1 — แยกไฟล์ย่อยทีหลังได้โดย include_router ที่นี่อย่างเดียว
# -------------------------------------------------------
from fastapi import APIRouter

router = APIRouter(prefix="/api/v1", tags=["v1"])

_placeholder = APIRouter(prefix="/placeholder", tags=["placeholder"])


@_placeholder.get("", summary="Placeholder จนกว่าจะมี feature จริง")
async def placeholder_root() -> dict[str, str]:
    return {"message": "v1 placeholder"}


router.include_router(_placeholder)
