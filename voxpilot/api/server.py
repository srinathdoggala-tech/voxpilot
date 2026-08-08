"""VoxPilot AI FastAPI Server Application Entrypoint."""

import os
from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles

from voxpilot.config import settings
from voxpilot.observability.logger import setup_logger
from voxpilot.db.database import db_manager
from voxpilot.api.v1 import health, knowledge, evals, voice

logger = setup_logger("voxpilot.server")


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager for database and service lifecycle."""
    logger.info(f"Starting {settings.app_name} server in {settings.environment} mode...")
    await db_manager.initialize()
    yield
    logger.info(f"Shutting down {settings.app_name} server...")
    await db_manager.close()


def create_app() -> FastAPI:
    """Construct FastAPI application with routers, middleware, and static file mounts."""
    app = FastAPI(
        title=settings.app_name,
        description="Enterprise Real-Time Voice AI Agent Platform",
        version="0.1.0",
        lifespan=lifespan
    )

    # Attach CORS middleware for cross-origin frontend clients
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )

    # Include REST & WebSocket API Routers
    app.include_router(health.router)
    app.include_router(knowledge.router)
    app.include_router(evals.router)
    app.include_router(voice.router)

    # Mount static frontend directory if present
    frontend_path = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(__file__))), "frontend")
    if os.path.exists(frontend_path):
        app.mount("/app", StaticFiles(directory=frontend_path, html=True), name="frontend")

    return app


app = create_app()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("voxpilot.api.server:app", host=settings.host, port=settings.port, reload=settings.debug)
