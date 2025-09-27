"""
Get available repositories endpoint with standardized responses.
"""
import logging
from fastapi import APIRouter, Request, status

from middlewares.rest import (
    StandardResponse,
    success_response,
    AppException
)
from api.deps import SessionServiceDep, RepoLocatorServiceDep, CurrentUserDep, BearerTokenDep
from services.repo.models import RepositoryList

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get(
    "/available",
    response_model=StandardResponse[RepositoryList],
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
) -> StandardResponse[RepositoryList]:
    """
    Get available repositories.
    
    Returns:
        StandardResponse[RepositoryList]: Standardized response containing repos
        
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
        
        repo_list: RepositoryList = await repo_locator_service.get_repositories(
            user_id=user_id,
        )
        
        logger.info(
            f"Retrieved {len(repo_list.repositories)} repositories",
            extra={
                "request_id": request_id,
                "repo_count": len(repo_list.repositories),
                "user_id": user_id
            }
        )
        
        return success_response(
            data=repo_list,
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