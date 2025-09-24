"""
Get configured repositories endpoint with standardized responses.
"""
import logging
from fastapi import APIRouter, Request, status
from pydantic import BaseModel, Field
from typing import List

from middlewares.rest import (
    StandardResponse,
    success_response,
    AppException
)
from api.deps import ConfigServiceDep, CurrentUserDep
from services.config.models import RepoConfig

logger = logging.getLogger(__name__)
router = APIRouter()

class ConfiguredReposResponse(BaseModel):
    """Response for configured repositories endpoint"""
    repositories: List[RepoConfig] = Field(..., description="List of configured repositories")


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
    config_service: ConfigServiceDep,
    user_id: CurrentUserDep
) -> StandardResponse[ConfiguredReposResponse]:
    """
    Get configured repositories for the authenticated user.
    
    Returns:
        StandardResponse[ConfiguredReposResponse]: Standardized response containing configured repos
    
    Raises:
        AppException: When repository retrieval fails
    """
    request_id = request.state.request_id
    
    try:
        # Get repository configurations for the user
        configured_repos = config_service.get_repo_configs(user_id) or []
        
        logger.info(
            f"Retrieved {len(configured_repos)} configured repositories for user {user_id}",
            extra={"request_id": request_id, "user_id": user_id}
        )
        
        return success_response(
            data=ConfiguredReposResponse(repositories=configured_repos),
            message=f"Found {len(configured_repos)} configured repositories",
            meta={"request_id": request_id, "count": len(configured_repos)}
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