from fastapi import FastAPI

from app.modules.auth.router import router as auth_router
from app.modules.citizen.router import router as citizen_router
from app.modules.family.router import router as family_router
from app.modules.emergency.router import router as emergency_router
from app.realtime.router import router as realtime_router

def create_app():

    app = FastAPI(
        title="LifeLink AI",
        version="1.0.0",
    )

    app.include_router(
        auth_router,
        prefix="/api/v1",
    )

    app.include_router(
        citizen_router,
        prefix="/api/v1",
    )

    app.include_router(
        family_router,
        prefix="/api/v1",
    )
    app.include_router(
        emergency_router,
        prefix="/api/v1",
    )
    app.include_router(realtime_router)
    return app