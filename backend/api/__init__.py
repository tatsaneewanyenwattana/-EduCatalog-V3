# -------------------------------------------------------
# Module : api
# หน้าที่ : รวม router ทุก version ของ HTTP API (transport layer)
# -------------------------------------------------------
from api.v1.router import router as v1_router

__all__ = ("v1_router",)
