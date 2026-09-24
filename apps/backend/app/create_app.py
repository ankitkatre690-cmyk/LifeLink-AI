from fastapi import FastAPI

from app.modules.admin.router import router as admin_router
from app.modules.ai.router import router as ai_router
from app.modules.auth.router import router as auth_router
from app.modules.citizen.router import router as citizen_router
from app.modules.dispatch.router import router as dispatch_router
from app.modules.emergency.router import router as emergency_router
from app.modules.family.router import router as family_router
from app.modules.hospital.router import router as hospital_router
from app.modules.notifications.router import router as notifications_router
from app.modules.notifications.device_token_router import router as device_token_router
from app.modules.police.router import router as police_router
from app.modules.responder.router import router as responder_router
from app.realtime.router import router as realtime_router


def create_app():
    app = FastAPI(
        title="LifeLink AI",
        version="1.0.0",
    )

    api_prefix = "/api/v1"

    app.include_router(auth_router, prefix=api_prefix)
    app.include_router(citizen_router, prefix=api_prefix)
    app.include_router(family_router, prefix=api_prefix)
    app.include_router(emergency_router, prefix=api_prefix)

    app.include_router(responder_router, prefix=api_prefix)
    app.include_router(hospital_router, prefix=api_prefix)
    app.include_router(dispatch_router, prefix=api_prefix)
    app.include_router(notifications_router, prefix=api_prefix)
    app.include_router(device_token_router, prefix=api_prefix)
    app.include_router(police_router, prefix=api_prefix)
    app.include_router(admin_router, prefix=api_prefix)
    app.include_router(ai_router, prefix=api_prefix)

    app.include_router(realtime_router)

    return app
