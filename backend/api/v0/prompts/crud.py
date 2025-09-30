"""
CRUD operations for prompts.

Handles create, read, update, delete operations for individual prompts.
"""

from fastapi import APIRouter, Path as PathParam
import logging

from api.deps import CurrentUserDep, PromptServiceDep
from middlewares.rest.responses import success_response, error_response
from services.prompt.models import PromptCreate, PromptUpdate

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get("/{prompt_id}")
async def get_prompt(
    user_id: CurrentUserDep,
    prompt_service: PromptServiceDep,
    prompt_id: str = PathParam(..., description="Unique prompt identifier")
):
    """
    Get a specific prompt by ID.
    
    Checks user permissions based on hosting type.
    """
    try:
        prompt = await prompt_service.get_prompt(
            user_id=user_id,
            prompt_id=prompt_id
        )
        
        if not prompt:
            return error_response(
                error_type="/errors/not-found",
                title="Prompt Not Found",
                detail=f"Prompt with ID '{prompt_id}' not found or access denied",
                status_code=404
            )
        
        return success_response(
            data=prompt.model_dump(mode='json'),
            message="Prompt retrieved successfully"
        )
        
    except Exception as e:
        logger.error(f"Failed to get prompt {prompt_id}: {e}")
        return error_response(
            error_type="/errors/internal-error",
            title="Internal Server Error",
            detail=str(e),
            status_code=500
        )


@router.post("/")
async def create_prompt(
    user_id: CurrentUserDep,
    prompt_service: PromptServiceDep,
    prompt_data: PromptCreate
):
    """
    Create a new prompt.
    
    The prompt will be saved to the specified repository and file path.
    """
    try:
        prompt = await prompt_service.create_prompt(
            user_id=user_id,
            prompt_data=prompt_data
        )
        
        return success_response(
            data=prompt.model_dump(mode='json'),
            message="Prompt created successfully",
            status_code=201
        )
        
    except ValueError as e:
        return error_response(
            error_type="/errors/validation-failed",
            title="Validation Error",
            detail=str(e),
            status_code=400
        )
    except Exception as e:
        logger.error(f"Failed to create prompt: {e}")
        return error_response(
            error_type="/errors/internal-error",
            title="Internal Server Error",
            detail=str(e),
            status_code=500
        )


@router.put("/{prompt_id}")
async def update_prompt(
    user_id: CurrentUserDep,
    prompt_service: PromptServiceDep,
    prompt_id: str,
    prompt_data: PromptUpdate
):
    """
    Update an existing prompt.
    
    All fields in the update are optional.
    """
    try:
        prompt = await prompt_service.update_prompt(
            user_id=user_id,
            prompt_id=prompt_id,
            prompt_data=prompt_data
        )
        
        if not prompt:
            return error_response(
                error_type="/errors/not-found",
                title="Prompt Not Found",
                detail=f"Prompt with ID '{prompt_id}' not found or access denied",
                status_code=404
            )
        
        return success_response(
            data=prompt.model_dump(mode='json'),
            message="Prompt updated successfully"
        )
        
    except ValueError as e:
        return error_response(
            error_type="/errors/validation-failed",
            title="Validation Error",
            detail=str(e),
            status_code=400
        )
    except Exception as e:
        logger.error(f"Failed to update prompt {prompt_id}: {e}")
        return error_response(
            error_type="/errors/internal-error",
            title="Internal Server Error",
            detail=str(e),
            status_code=500
        )


@router.delete("/{prompt_id}")
async def delete_prompt(
    user_id: CurrentUserDep,
    prompt_service: PromptServiceDep,
    prompt_id: str
):
    """
    Delete a prompt.
    
    Removes the prompt file from the repository.
    """
    try:
        success = await prompt_service.delete_prompt(
            user_id=user_id,
            prompt_id=prompt_id
        )
        
        if not success:
            return error_response(
                error_type="/errors/not-found",
                title="Prompt Not Found",
                detail=f"Prompt with ID '{prompt_id}' not found or access denied",
                status_code=404
            )
        
        return success_response(
            message="Prompt deleted successfully",
            status_code=204
        )
        
    except Exception as e:
        logger.error(f"Failed to delete prompt {prompt_id}: {e}")
        return error_response(
            error_type="/errors/internal-error",
            title="Internal Server Error",
            detail=str(e),
            status_code=500
        )