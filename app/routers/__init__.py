from fastapi import APIRouter

from app.routers.horoscop import router as horoscope_router
from app.routers.status import router as status_router

api_router = APIRouter(prefix="/api")

# Include all routers here
api_router.include_router(horoscope_router)
