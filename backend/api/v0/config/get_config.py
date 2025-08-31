"""
Get configuration endpoint.
"""
from fastapi import APIRouter, HTTPException, status, Depends
from typing import Optional
from sqlmodel import Session

from schemas.config import AppConfig
from .utils import get_current_config, is_config_empty, get_user_email
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
    Requires admin privileges if configs are already available
    """
    try:
        config = get_current_config()
        
        # If config is not empty, check if user is admin
        if not is_config_empty(config):
            if not token:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Authentication required"
                )
            
            # Get user's email using the utility function
            user_email = await get_user_email(token, db)
            
            if not user_email:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Unable to retrieve user email"
                )
            
            # Check if user email is in admin list
            if user_email not in settings.app_config.adminEmails:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Admin privileges required to access configuration"
                )
        
        return config
    except HTTPException:
        # Re-raise HTTP exceptions (like 401)
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to get config: {str(e)}"
        )