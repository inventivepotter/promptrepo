"""
Get configuration endpoint.
"""
from fastapi import APIRouter, HTTPException, status

from schemas.config import AppConfig
from services.config_service import config_service

router = APIRouter()

@router.get("/", response_model=AppConfig)
async def get_config():
    """
    Get current application configuration
    No authorization required - anyone can read config
    """
    try:
        return config_service.get_current_config()
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get config: {str(e)}"
        )