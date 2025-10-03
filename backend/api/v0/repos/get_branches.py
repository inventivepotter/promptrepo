"""
Get repository branches endpoint.
"""
import logging
from typing import List
from fastapi import APIRouter, Request, status, Query
from pydantic import BaseModel, Field

from middlewares.rest import (
    StandardResponse,
    success_response,
    AppException,
    OAuthTokenInvalidException
)
from api.deps import CurrentSessionDep, RemoteRepoServiceDep
from services.oauth.models import OAuthError

logger = logging.getLogger(__name__)
router = APIRouter()


class BranchInfo(BaseModel):
    """Information about a repository branch"""
    name: str = Field(..., description="Branch name")
    is_default: bool = Field(default=False, description="Whether this is the default branch")


class RepositoryBranchesResponse(BaseModel):
    """Response for repository branches endpoint"""
    branches: List[BranchInfo] = Field(..., description="List of repository branches")
    default_branch: str = Field(..., description="The default branch name")


@router.get(
    "/branches",
    response_model=StandardResponse[RepositoryBranchesResponse],
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
        404: {
            "description": "Repository not found",
            "content": {
                "application/json": {
                    "example": {
                        "status": "error",
                        "type": "/errors/not-found",
                        "title": "Not Found",
                        "detail": "Repository not found"
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
                        "detail": "Failed to retrieve repository branches"
                    }
                }
            }
        }
    },
    summary="Get repository branches",
    description="Get list of branches for a specific repository"
)
async def get_repository_branches(
    request: Request,
    remote_repo_service: RemoteRepoServiceDep,
    user_session: CurrentSessionDep,
    owner: str = Query(..., description="Repository owner/organization"),
    repo: str = Query(..., description="Repository name")
) -> StandardResponse[RepositoryBranchesResponse]:
    """
    Get branches for a specific repository.
    
    Args:
        owner: Repository owner/organization
        repo: Repository name
    
    Returns:
        StandardResponse[RepositoryBranchesResponse]: Standardized response containing branches
        
    Raises:
        AppException: When branch retrieval fails
    """
    request_id = getattr(request.state, "request_id", None)
    
    try:
        logger.info(
            f"Fetching branches for repository {owner}/{repo}",
            extra={
                "request_id": request_id,
                "user_id": user_session.user_id,
                "repository": f"{owner}/{repo}"
            }
        )
        
        branches_data = await remote_repo_service.get_repository_branches(
            user_session=user_session,
            owner=owner,
            repo=repo
        )
        
        logger.info(
            f"Retrieved {len(branches_data.branches)} branches for {owner}/{repo}",
            extra={
                "request_id": request_id,
                "branch_count": len(branches_data.branches),
                "user_id": user_session.user_id,
            }
        )
        
        return success_response(
            data=branches_data,
            message="Branches retrieved successfully",
            meta={"request_id": request_id}
        )
        
    except OAuthError as e:
        # Convert OAuth errors to OAuthTokenInvalidException for automatic session invalidation
        logger.error(
            f"OAuth error retrieving branches: {e.message}",
            extra={
                "request_id": request_id,
                "provider": e.provider,
                "user_id": user_session.user_id,
                "session_id": user_session.id
            }
        )
        raise OAuthTokenInvalidException(
            message=e.message,
            provider=e.provider,
            session_id=user_session.id
        )
        
    except Exception as e:
        logger.error(
            f"Failed to retrieve branches for {owner}/{repo}: {e}",
            exc_info=True,
            extra={"request_id": request_id}
        )
        raise AppException(
            message=f"Failed to retrieve branches for {owner}/{repo}",
            detail=str(e)
        )