"""
Repository-related prompt endpoints.

Handles listing repositories and discovering prompts within them.
"""

from fastapi import APIRouter, Path as PathParam
import logging

from api.deps import CurrentUserDep, PromptServiceDep, RemoteRepoServiceDep
from middlewares.rest.responses import success_response, error_response

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/repositories/list")
async def list_repositories(
    user_id: CurrentUserDep,
    remote_repo_service: RemoteRepoServiceDep,
):
    """
    List available repositories.
    
    Returns repositories accessible to the current user based on hosting type.
    """
    try:
        # Get repositories from the locator service
        repo_list_response = await remote_repo_service.get_repositories(user_id)
        
        # Convert to simple format for API response
        repo_list = [
            {
                "id": repo.id,
                "name": repo.name,
                "full_name": repo.full_name,
                "clone_url": repo.clone_url,
                "owner": repo.owner,
                "private": repo.private if hasattr(repo, 'private') else False,
                "default_branch": repo.default_branch if hasattr(repo, 'default_branch') else "main",
                "language": repo.language if hasattr(repo, 'language') else None,
                "size": repo.size if hasattr(repo, 'size') else 0,
                "updated_at": repo.updated_at if hasattr(repo, 'updated_at') else None
            }
            for repo in repo_list_response.repositories
        ]
        
        return success_response(
            data=repo_list,
            message=f"Found {len(repo_list)} repositories"
        )
        
    except Exception as e:
        logger.error(f"Failed to list repositories: {e}")
        return error_response(
            error_type="/errors/internal-error",
            title="Internal Server Error",
            detail=str(e),
            status_code=500
        )


@router.get("/repositories/{repo_name}/prompts")
async def list_repository_prompts(
    user_id: CurrentUserDep,
    prompt_service: PromptServiceDep,
    repo_name: str = PathParam(..., description="Repository name")
):
    """
    List all prompts in a specific repository.
    
    Returns only prompts accessible to the current user.
    """
    try:
        prompts = await prompt_service.list_repository_prompts(
            user_id=user_id,
            repo_name=repo_name
        )
        
        # Convert prompts to dict for JSON serialization
        prompts_data = [prompt.model_dump(mode='json') for prompt in prompts]
        
        return success_response(
            data=prompts_data,
            message=f"Found {len(prompts)} prompts in repository {repo_name}"
        )
        
    except ValueError as e:
        return error_response(
            error_type="/errors/not-found",
            title="Repository Not Found",
            detail=str(e),
            status_code=404
        )
    except Exception as e:
        logger.error(f"Failed to list repository prompts for {repo_name}: {e}")
        return error_response(
            error_type="/errors/internal-error",
            title="Internal Server Error",
            detail=str(e),
            status_code=500
        )


@router.get("/repositories/{repo_name}/discover")
async def discover_repository_prompts(
    user_id: CurrentUserDep,
    prompt_service: PromptServiceDep,
    repo_name: str = PathParam(..., description="Repository name")
):
    """
    Discover prompt files in a repository.
    
    Scans the repository for YAML/YML files containing prompts without importing them.
    """
    try:
        prompt_files = await prompt_service.discover_prompts(
            user_id=user_id,
            repo_name=repo_name
        )
        
        # Convert prompt files to dict for JSON serialization
        files_data = [
            {
                "path": pf.path,
                "name": pf.name,
                "system_prompt": pf.system_prompt,
                "user_prompt": pf.user_prompt,
                "metadata": pf.metadata
            }
            for pf in prompt_files
        ]
        
        return success_response(
            data=files_data,
            message=f"Discovered {len(files_data)} prompt files in repository {repo_name}"
        )
        
    except ValueError as e:
        return error_response(
            error_type="/errors/not-found",
            title="Repository Not Found",
            detail=str(e),
            status_code=404
        )
    except Exception as e:
        logger.error(f"Failed to discover prompts in {repo_name}: {e}")
        return error_response(
            error_type="/errors/internal-error",
            title="Internal Server Error",
            detail=str(e),
            status_code=500
        )