"""
Get available repositories endpoint with standardized responses.
"""
import logging
from fastapi import APIRouter, Request, Depends, status
from pydantic import BaseModel
from sqlmodel import Session
from typing import List, Optional

from middlewares.rest import (
    StandardResponse,
    success_response,
    AuthenticationException,
    AppException
)
from models.database import get_session
from services.config.config_service import ConfigService
from services.auth.session_service import SessionService
from services.repo import RepoLocatorService
from services.config.models import HostingType

logger = logging.getLogger(__name__)
router = APIRouter()


class AvailableRepositoriesResponse(BaseModel):
    """Response for available repositories endpoint"""
    repos: List[str]


@router.get(
    "/available",
    response_model=StandardResponse[AvailableRepositoriesResponse],
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
                        "detail": "Session not found or invalid"
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
                        "detail": "Failed to retrieve repositories"
                    }
                }
            }
        }
    },
    summary="Get available repositories",
    description="Get list of available repositories based on hosting type"
)
async def get_available_repositories(
    request: Request,
    db: Session = Depends(get_session)
) -> StandardResponse[AvailableRepositoriesResponse]:
    """
    Get available repositories based on hosting type.
    
    Returns:
        StandardResponse[AvailableRepositoriesResponse]: Standardized response containing repos
        
    Raises:
        AuthenticationException: When authentication is required but not provided
        AppException: When repository retrieval fails
    """
    request_id = getattr(request.state, "request_id", None)
    
    try:
        config_service = ConfigService()
        hosting_config = config_service.get_hosting_config()
        hosting_type = hosting_config.type
        
        logger.info(
            f"Fetching available repositories for hosting type: {hosting_type}",
            extra={
                "request_id": request_id,
                "hosting_type": hosting_type.value
            }
        )
        
        repos_list = []
        
        if hosting_type == HostingType.INDIVIDUAL:
            repo_locator = RepoLocatorService(hosting_type.value)
            # Get repos from the locator - it returns a Dict[str, str]
            if repo_locator:
                repos_dict = await repo_locator.get_repositories()
                repos_list = list(repos_dict.keys())
                
        elif hosting_type == HostingType.ORGANIZATION:
            # Get session from authorization header
            authorization_header = request.headers.get("Authorization")
            session_id = authorization_header.replace("Bearer ", "") if authorization_header else None
            
            if not session_id or not SessionService.is_session_valid(db, session_id):
                logger.warning(
                    "Invalid or missing session for organization hosting",
                    extra={
                        "request_id": request_id,
                        "hosting_type": hosting_type.value
                    }
                )
                raise AuthenticationException(
                    message="Authentication required for organization repositories"
                )
            
            data = SessionService.get_oauth_token_and_username(db, session_id)
            if data:
                repo_locator = RepoLocatorService(
                    hosting_type.value,
                    oauth_token=data['oauth_token'],
                    username=data['username']
                )
                if repo_locator:
                    repos_dict = await repo_locator.get_repositories()
                    repos_list = list(repos_dict.keys())
            else:
                raise AuthenticationException(
                    message="Session not found"
                )
        
        logger.info(
            f"Retrieved {len(repos_list)} repositories",
            extra={
                "request_id": request_id,
                "hosting_type": hosting_type.value,
                "repo_count": len(repos_list)
            }
        )
        
        return success_response(
            data=AvailableRepositoriesResponse(repos=repos_list),
            message="Repositories retrieved successfully",
            meta={"request_id": request_id}
        )
        
    except (AuthenticationException,):
        raise
    except Exception as e:
        logger.error(
            f"Failed to retrieve repositories: {e}",
            exc_info=True,
            extra={"request_id": request_id}
        )
        raise AppException(
            message="Failed to retrieve repositories",
            detail=str(e)
        )