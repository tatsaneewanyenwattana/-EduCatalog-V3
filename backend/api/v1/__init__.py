# -------------------------------------------------------
# Module : api/v1
# หน้าที่ : รับ HTTP request, validate input, ส่งต่อให้ service (ห้าม query DB เอง)
# -------------------------------------------------------
from api.v1.router import router

__all__ = ("router",)
