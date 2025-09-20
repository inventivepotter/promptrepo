"""
Get configured repositories endpoint with standardized responses.
"""
import logging
from fastapi import APIRouter, Request, Depends, status
from pydantic import BaseModel
from sqlmodel import Session
from typing import List

from middlewares.rest import (
    StandardResponse,
    success_response,
    AppException
)
from models.database import get_session

logger = logging.getLogger(__name__)
router = APIRouter()


class ConfiguredReposResponse(BaseModel):
    """Response for configured repositories endpoint"""
    repos: List[dict]


@router.get(
    "/configured",
    response_model=StandardResponse[ConfiguredReposResponse],
    status_code=status.HTTP_200_OK,
    responses={
        401: {
            "description": "Authentication required",
            "content": {
                "application/json": {
                    "example": {
                        "status": "error",
                        "type": "/errors/authentication-required",
                        "title": "Authentication required",
                        "detail": "Valid session required"
                    }
                }
            }
        },
        500: {
            "description": "Internal server error",
            "content": {
                "application/json": {
                    "example": {
                        "status": "error",
                        "type": "/errors/internal-server-error",
                        "title": "Internal Server Error",
                        "detail": "Failed to retrieve configured repositories"
                    }
                }
            }
        }
    },
    summary="Get configured repositories",
    description="Get list of configured repositories for the authenticated user"
)
async def get_configured_repositories(
    request: Request,
    db: Session = Depends(get_session)
) -> StandardResponse[ConfiguredReposResponse]:
    """
    Get configured repositories for the authenticated user.
    
    Returns:
        StandardResponse[ConfiguredReposResponse]: Standardized response containing configured repos
    
    Raises:
        AppException: When repository retrieval fails
    """
    request_id = getattr(request.state, "request_id", None)
    
    try:
        # TODO: Implement configured repositories logic
        # This would typically involve:
        # 1. Getting the authenticated user from session
        # 2. Fetching their configured repos from database
        # 3. Returning the list
        
        logger.info(
            "Configured repositories endpoint called (not yet implemented)",
            extra={"request_id": request_id}
        )
        
        return success_response(
            data=ConfiguredReposResponse(repos=[]),
            message="No configured repositories found",
            meta={"request_id": request_id}
        )
        
    except Exception as e:
        logger.error(
            f"Failed to retrieve configured repositories: {e}",
            exc_info=True,
            extra={"request_id": request_id}
        )
        raise AppException(
            message="Failed to retrieve configured repositories",
            detail=str(e)
        )