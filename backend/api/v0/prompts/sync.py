"""
Prompt synchronization endpoints.

Handles syncing prompts from repositories.
"""

from fastapi import APIRouter, Path as PathParam
import logging

from api.deps import CurrentUserDep, PromptServiceDep
from middlewares.rest.responses import success_response, error_response

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/sync/{repo_name}")
async def sync_repository_prompts(
    user_id: CurrentUserDep,
    prompt_service: PromptServiceDep,
    repo_name: str = PathParam(..., description="Repository name to sync")
):
    """
    Sync prompts from a repository.
    
    Discovers and imports all prompt YAML/YML files from the specified repository.
    """
    try:
        synced_count = await prompt_service.sync_repository_prompts(
            user_id=user_id,
            repo_name=repo_name
        )
        
        return success_response(
            data={"synced_count": synced_count, "repository": repo_name},
            message=f"Successfully synchronized {synced_count} prompts from {repo_name}"
        )
        
    except ValueError as e:
        return error_response(
            error_type="/errors/not-found",
            title="Repository Not Found",
            detail=str(e),
            status_code=404
        )
    except Exception as e:
        logger.error(f"Failed to sync repository {repo_name}: {e}")
        return error_response(
            error_type="/errors/internal-error",
            title="Internal Server Error",
            detail=str(e),
            status_code=500
        )