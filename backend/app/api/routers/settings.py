"""
Settings API routes.

Provides endpoints for application settings management.
"""
from fastapi import APIRouter, HTTPException

from app.models.settings import Settings
from app.services.settings import SettingsService
from app.utils.errors import ResourceNotFoundError

router = APIRouter()

# Service instance
settings_service = SettingsService()


@router.get("", response_model=Settings, summary="Get all settings")
async def get_settings():
    """
    Retrieve all application settings.

    Returns:
        Current application settings
    """
    return settings_service.get()


@router.put("", response_model=Settings, summary="Update all settings")
async def update_settings(settings_data: Settings):
    """
    Update all application settings.

    Args:
        settings_data: New settings values

    Returns:
        Updated settings
    """
    try:
        return settings_service.update(settings_data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.patch("", response_model=Settings, summary="Patch settings")
async def patch_settings(settings_data: Settings):
    """
    Partially update application settings.

    Args:
        settings_data: Settings values to update (only specified fields)

    Returns:
        Updated settings
    """
    try:
        return settings_service.patch(settings_data)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
