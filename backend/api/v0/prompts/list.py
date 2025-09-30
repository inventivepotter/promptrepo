"""
List and search prompts endpoints.

Handles listing prompts with pagination, filtering, and search.
"""

from typing import List, Optional
from fastapi import APIRouter, Query
import logging

from api.deps import CurrentUserDep, PromptServiceDep
from middlewares.rest.responses import paginated_response, error_response
from services.prompt.models import PromptSearchParams

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/")
async def list_prompts(
    user_id: CurrentUserDep,
    prompt_service: PromptServiceDep,
    query: Optional[str] = Query(None, description="Search query string"),
    repo_name: Optional[str] = Query(None, description="Filter by repository name"),
    category: Optional[str] = Query(None, description="Filter by category"),
    tags: Optional[List[str]] = Query(None, description="Filter by tags"),
    owner: Optional[str] = Query(None, description="Filter by owner (organization mode)"),
    page: int = Query(1, ge=1, description="Page number"),
    page_size: int = Query(20, ge=1, le=100, description="Items per page"),
):
    """
    List all prompts with pagination and filtering.
    
    Organization mode: Users only see their own prompts
    Individual mode: All users see all prompts
    """
    try:
        # Build search parameters
        search_params = PromptSearchParams(
            query=query,
            repo_name=repo_name,
            category=category,
            tags=tags,
            owner=owner,
            page=page,
            page_size=page_size
        )
        
        # Get prompts from service
        result = await prompt_service.list_prompts(
            user_id=user_id,
            search_params=search_params
        )
        
        # Convert prompts to dict for JSON serialization
        prompts_data = [prompt.model_dump(mode='json') for prompt in result.prompts]
        
        return paginated_response(
            items=prompts_data,
            page=result.page,
            page_size=result.page_size,
            total_items=result.total,
            message="Prompts retrieved successfully"
        )
        
    except Exception as e:
        logger.error(f"Failed to list prompts: {e}")
        return error_response(
            error_type="/errors/internal-error",
            title="Internal Server Error",
            detail=str(e),
            status_code=500
        )