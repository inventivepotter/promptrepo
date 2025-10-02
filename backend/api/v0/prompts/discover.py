"""
Prompt discovery endpoints.

Handles discovering prompts from repositories.
"""

from fastapi import APIRouter, Request, status
from pydantic import BaseModel, Field
from typing import List
import logging

from api.deps import CurrentUserDep, PromptServiceDep
from services.prompt.models import PromptMeta
from middlewares.rest import (
    StandardResponse,
    success_response,
    AppException,
    BadRequestException
)

logger = logging.getLogger(__name__)
router = APIRouter()


class DiscoverRepositoriesRequest(BaseModel):
    """Request model for discovering prompts from repositories."""
    repo_names: List[str] = Field(
        ...,
        description="List of repository names to discover prompts from (supports 'owner/repo' or 'repo' format)",
        min_length=1
    )


@router.post(
    "/discover",
    response_model=StandardResponse[List[PromptMeta]],
    status_code=status.HTTP_200_OK,
    responses={
        400: {
            "description": "Bad request or all repositories failed to discover prompts",
            "content": {
                "application/json": {
                    "example": {
                        "status": "error",
                        "type": "/errors/bad-request",
                        "title": "Bad Request",
                        "detail": "Failed to discover prompts from all repositories"
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
                        "detail": "Failed to discover prompts"
                    }
                }
            }
        }
    },
    summary="Discover repository prompts",
    description="Discover prompts from one or more repositories. Scans and retrieves all prompt YAML/YML files from the specified repositories.",
)
async def discover_repository_prompts(
    request: Request,
    user_id: CurrentUserDep,
    prompt_service: PromptServiceDep,
    request_body: DiscoverRepositoriesRequest
) -> StandardResponse[List[PromptMeta]]:
    """
    Discover prompts from one or more repositories.
    
    Scans and retrieves all prompt YAML/YML files from the specified repositories.
    Accepts repository names in 'owner/repo' or 'repo' format.
    
    Returns:
        StandardResponse[List[PromptMeta]]: Standardized response containing list of prompts
    
    Raises:
        BadRequestException: When all repositories fail to discover prompts
        AppException: When discovery operation fails
    """
    request_id = request.state.request_id
    
    try:
        logger.info(
            f"Discovering prompts from {len(request_body.repo_names)} repositories",
            extra={"request_id": request_id, "user_id": user_id}
        )
        
        all_prompts = []
        failed_repos = []
        
        for repo_name in request_body.repo_names:
            try:
                discovered_prompts = await prompt_service.discover_prompts(
                    user_id=user_id,
                    repo_name=repo_name
                )
                all_prompts.extend(discovered_prompts)
                
            except Exception as e:
                logger.error(
                    f"Failed to discover repository {repo_name} prompts: {e}",
                    extra={"request_id": request_id, "user_id": user_id}
                )
                failed_repos.append(repo_name)
        
        # If all repos failed, raise exception
        if len(failed_repos) == len(request_body.repo_names):
            raise BadRequestException(
                message=f"Failed to discover prompts from all repositories: {', '.join(failed_repos)}"
            )
        
        # Build success message
        message = f"Successfully discovered {len(all_prompts)} prompts from {len(request_body.repo_names) - len(failed_repos)} repository/repositories"
        if failed_repos:
            message += f". Failed repositories: {', '.join(failed_repos)}"
        
        logger.info(
            message,
            extra={"request_id": request_id, "user_id": user_id}
        )
        
        return success_response(
            data=[prompt.model_dump(mode='json') for prompt in all_prompts],
            message=message,
            meta={"request_id": request_id}
        )
        
    except (BadRequestException, AppException):
        # These will be handled by the global exception handlers
        raise
    except Exception as e:
        logger.error(
            f"Failed to discover prompts: {str(e)}",
            exc_info=True,
            extra={"request_id": request_id, "user_id": user_id}
        )
        raise AppException(
            message="Failed to discover prompts",
            detail=str(e)
        )