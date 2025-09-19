"""
Get configuration endpoint.
"""
import logging
from fastapi import APIRouter, HTTPException, status

from schemas.config import AppConfig
from services.config import config_service

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get("/", response_model=AppConfig)
async def get_config():
    """
    Get current application configuration
    Only allowed for individual hosting type
    """
    try:
        # Check current hosting type
        current_hosting_type = config_service.get_hosting_type()
        logger.info(f"get_config: Current hosting type = {current_hosting_type}")
        
        # Only allow config access for individual hosting
        if current_hosting_type != "individual":
            logger.warning(f"get_config: Blocking config access for hosting type: {current_hosting_type}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Configuration access is only allowed for individual hosting type. Current hosting type: {current_hosting_type}"
            )
        
        config = config_service.get_current_config()
        logger.info("get_config: Returning config for individual hosting")
        return config
    except HTTPException:
        # Re-raise HTTP exceptions
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get config: {str(e)}"
        )