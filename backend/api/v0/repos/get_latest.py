"""
Get Latest Repository Content Endpoint

This endpoint handles fetching the latest version of a prompt from the base branch,
discarding any local changes.
"""

from fastapi import APIRouter, Query, Request, status
import logging

from api.deps import CurrentUserDep, LocalRepoServiceDep, CurrentSessionDep
from middlewares.rest import (
    StandardResponse,
    success_response,
    AppException,
    NotFoundException
)

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post(
    "/get_latest",
    response_model=StandardResponse[dict],
    status_code=status.HTTP_200_OK,
    responses={
        404: {
            "description": "Prompt not found",
            "content": {
                "application/json": {
                    "example": {
                        "status": "error",
                        "type": "/errors/not-found",
                        "title": "Prompt Not Found",
                        "detail": "Prompt with ID 'xxx' not found or access denied"
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
                        "detail": "Failed to fetch latest prompt"
                    }
                }
            }
        }
    },
    summary="Fetch latest prompt from base branch",
    description="Fetch the latest version of a prompt from the configured base branch, discarding any local changes. This will reset the prompt to the latest version from the remote repository.",
)
async def get_latest_prompt(
    request: Request,
    user_id: CurrentUserDep,
    local_repo_service: LocalRepoServiceDep,
    user_session: CurrentSessionDep,
    repo_name: str = Query(...)
) -> StandardResponse[dict]:
    """
    Fetch the latest version of a prompt from the base branch.
    
    This operation will:
    1. Switch to the base branch
    2. Pull the latest changes from the remote
    3. Load the prompt from the base branch
    
    Any local changes will be discarded.
    
    Raises:
        NotFoundException: When the prompt is not found or access is denied
        AppException: When fetching the latest prompt fails
    """
    request_id = request.state.request_id
    
    try:
        logger.info(
            f"Fetching latest prompts from {repo_name} base branch",
            extra={"request_id": request_id, "user_id": user_id}
        )
        
        # Fetch latest prompts from base branch
        result = await local_repo_service.get_latest_base_branch_content(
            user_id=user_id,
            repo_name=repo_name,
            oauth_token=user_session.oauth_token
        )
        
        logger.info(
            f"Successfully fetched latest prompts from {repo_name}",
            extra={"request_id": request_id, "user_id": user_id}
        )
        
        return success_response(
            data=result,
            message="Latest prompts fetched successfully",
            meta={"request_id": request_id}
        )
        
    except (NotFoundException, AppException):
        # These will be handled by the global exception handlers
        raise
    except Exception as e:
        logger.error(
            f"Failed to fetch latest prompts from {repo_name}: {str(e)}",
            exc_info=True,
            extra={"request_id": request_id, "user_id": user_id}
        )
        raise AppException(
            message="Failed to fetch latest prompts",
            detail=str(e)
        )