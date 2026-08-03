from fastapi import FastAPI

from app.api.v1.api import router
from app.core.config import settings


def create_app() -> FastAPI:

    app = FastAPI(
        title=settings.PROJECT_NAME,
        version=settings.PROJECT_VERSION,
        docs_url="/docs",
        redoc_url="/redoc",
    )

    @app.get("/")
    async def root():

        return {
            "project": settings.PROJECT_NAME,
            "version": settings.PROJECT_VERSION,
            "status": "running",
        }

    @app.get("/health")
    async def health():

        return {
            "status": "healthy",
            "database": "connected",
        }

    app.include_router(
        router,
        prefix=settings.API_V1_PREFIX,
    )

    return app