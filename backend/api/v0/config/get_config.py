"""
Get configuration endpoint.
"""
from fastapi import APIRouter, HTTPException, status

from schemas.config import AppConfig
from .utils import get_current_config

router = APIRouter()

@router.get("/", response_model=AppConfig)
async def get_config():
    """
    Get current application configuration
    No authorization required - anyone can read config
    """
    try:
        config = get_current_config()
        return config
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get config: {str(e)}"
        )