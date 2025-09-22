"""
Get available repositories endpoint with standardized responses.
"""
import logging
from fastapi import APIRouter, Request, status
from pydantic import BaseModel
from typing import List

from middlewares.rest import (
    StandardResponse,
    success_response,
    AppException
)
from api.deps import SessionServiceDep, RepoLocatorServiceDep, CurrentUserDep, BearerTokenDep

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
    description="Get list of available repositories"
)
async def get_available_repositories(
    request: Request,
    session_service: SessionServiceDep,
    repo_locator_service: RepoLocatorServiceDep,
    user_id: CurrentUserDep,
    session_token: BearerTokenDep,
) -> StandardResponse[AvailableRepositoriesResponse]:
    """
    Get available repositories.
    
    Returns:
        StandardResponse[AvailableRepositoriesResponse]: Standardized response containing repos
        
    Raises:
        AppException: When repository retrieval fails
    """
    request_id = getattr(request.state, "request_id", None)
    
    try:
        logger.info(
            "Fetching available repositories",
            extra={
                "request_id": request_id,
                "user_id": user_id
            }
        )
        
        repos_list = []
    
        # Get OAuth token and user info
        data = session_service.get_oauth_token_and_user_info(session_token)
        if data:
            repos_dict = await repo_locator_service.get_repositories(
                oauth_provider=data.oauth_provider,
                username=data.username,
                oauth_token=data.oauth_token
            )
            repos_list = list(repos_dict.keys())
        else:
            raise AppException(
                message="Session not found"
            )
        
        logger.info(
            f"Retrieved {len(repos_list)} repositories",
            extra={
                "request_id": request_id,
                "repo_count": len(repos_list),
                "user_id": user_id
            }
        )
        
        return success_response(
            data=AvailableRepositoriesResponse(repos=repos_list),
            message="Repositories retrieved successfully",
            meta={"request_id": request_id}
        )
        
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