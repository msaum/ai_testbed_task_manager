"""
Main application entry point for the Local Task Manager.

This module initializes the FastAPI application and includes all routers,
middleware, and event handlers.
"""
import sys
import os

# Add the backend directory to the path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.core import config as app_config
from app.api.routers import tasks, projects, settings


def create_application() -> FastAPI:
    """
    Create and configure the FastAPI application.

    Returns:
        Configured FastAPI application instance
    """
    application = FastAPI(
        title=app_config.settings.APP_NAME,
        description=app_config.settings.APP_DESCRIPTION,
        version=app_config.settings.APP_VERSION,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
    )

    # Configure CORS
    application.add_middleware(
        CORSMiddleware,
        allow_origins=app_config.settings.ALLOWED_ORIGINS,
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
        expose_headers=["X-Request-ID"],
    )

    # Include routers
    application.include_router(tasks.router, prefix="/api/v1/tasks", tags=["tasks"])
    application.include_router(projects.router, prefix="/api/v1/projects", tags=["projects"])
    application.include_router(settings.router, prefix="/api/v1/settings", tags=["settings"])

    return application


# Create the application instance
app = create_application()


@app.get("/health")
async def health_check():
    """
    Health check endpoint for monitoring.

    Returns:
        Health status information
    """
    return {
        "status": "healthy",
        "service": app_config.settings.APP_NAME,
        "version": app_config.settings.APP_VERSION,
    }


@app.get("/")
async def root():
    """
    Root endpoint with API information.

    Returns:
        API metadata and documentation links
    """
    return {
        "name": app_config.settings.APP_NAME,
        "version": app_config.settings.APP_VERSION,
        "docs": "/docs",
        "health": "/health",
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "app.main:app",
        host=app_config.settings.HOST,
        port=app_config.settings.PORT,
        reload=app_config.settings.DEBUG,
    )
