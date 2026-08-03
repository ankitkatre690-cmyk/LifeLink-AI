from fastapi import APIRouter

from app.api.router import api_router

router = APIRouter()

router.include_router(api_router)