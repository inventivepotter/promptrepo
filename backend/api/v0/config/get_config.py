"""
Get configuration endpoint.
"""
from fastapi import APIRouter, HTTPException, status, Depends
from typing import Optional
from sqlmodel import Session

from schemas.config import AppConfig
from .utils import get_current_config, is_config_empty, validate_hosting_authorization
from .auth import get_bearer_token
from models.database import get_session
from settings.base_settings import settings

router = APIRouter()

@router.get("/", response_model=AppConfig)
async def get_config(
    token: Optional[str] = Depends(get_bearer_token),
    db: Session = Depends(get_session)
):
    """
    Get current application configuration
    Requires admin privileges for org/multi-tenant hosting when config is not empty
    """
    try:
        config = get_current_config()
        hosting_type = getattr(config, 'hostingType', '') or ''
        
        # Only validate authorization for non-individual hosting types
        # when config is not empty
        if hosting_type != "individual" and not is_config_empty(config):
                # Use hosting-aware authorization validation
                await validate_hosting_authorization(config, token, db)
        
        return config
    except HTTPException:
        # Re-raise HTTP exceptions (like 401)
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get config: {str(e)}"
        )