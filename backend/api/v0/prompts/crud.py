"""
CRUD operations for prompts.

Handles create, read, update, delete operations for individual prompts.
"""

from fastapi import APIRouter, Query, Request, status
import logging

from api.deps import CurrentUserDep, PromptServiceDep, CurrentSessionDep
from middlewares.rest import (
    StandardResponse,
    success_response,
    AppException,
    NotFoundException,
    ValidationException,
)
from services.prompt.models import PromptMeta, PromptData, PromptDataUpdate

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get(
    "/",
    response_model=StandardResponse[PromptMeta],
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
                        "detail": "Failed to retrieve prompt"
                    }
                }
            }
        }
    },
    summary="Get prompt",
    description="Get a specific prompt by repository name and file path. Checks user permissions based on hosting type.",
)
async def get_prompt(
    request: Request,
    user_id: CurrentUserDep,
    prompt_service: PromptServiceDep,
    repo_name: str = Query(...),
    file_path: str = Query(...)
) -> StandardResponse[PromptMeta]:
    """
    Get a specific prompt by repository name and file path.
    
    Checks user permissions based on hosting type.
    
    Returns:
        StandardResponse[PromptMeta]: Standardized response containing the prompt
    
    Raises:
        NotFoundException: When prompt is not found or access denied
        AppException: When prompt retrieval fails
    """
    request_id = request.state.request_id
    
    try:
        logger.info(
            f"Fetching prompt {repo_name}:{file_path}",
            extra={"request_id": request_id, "user_id": user_id}
        )
        
        prompt = await prompt_service.get_prompt(
            user_id=user_id,
            repo_name=repo_name,
            file_path=file_path
        )
        
        if not prompt:
            raise NotFoundException(
                resource="Prompt",
                identifier=f"{repo_name}:{file_path}"
            )
        
        logger.info(
            f"Successfully retrieved prompt {repo_name}:{file_path}",
            extra={"request_id": request_id, "user_id": user_id}
        )
        
        return success_response(
            data=prompt.model_dump(mode='json'),
            message="Prompt retrieved successfully",
            meta={"request_id": request_id}
        )
        
    except (NotFoundException, AppException):
        # These will be handled by the global exception handlers
        raise
    except Exception as e:
        logger.error(
            f"Failed to get prompt {repo_name}:{file_path}: {str(e)}",
            exc_info=True,
            extra={"request_id": request_id, "user_id": user_id}
        )
        raise AppException(
            message="Failed to retrieve prompt",
            detail=str(e)
        )


@router.post(
    "/",
    response_model=StandardResponse[PromptMeta],
    status_code=status.HTTP_200_OK,
    responses={
        400: {
            "description": "Invalid prompt data",
            "content": {
                "application/json": {
                    "example": {
                        "status": "error",
                        "type": "/errors/validation-failed",
                        "title": "Validation Error",
                        "detail": "Invalid prompt data"
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
                        "title": "Repository Not Found",
                        "detail": "Repository 'xxx' not found or access denied"
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
                        "detail": "Failed to save prompt"
                    }
                }
            }
        }
    },
    summary="Save prompt",
    description="Save a prompt (create or update). If the file doesn't exist, creates a new prompt. If it exists, updates it.",
)
async def save_prompt(
    request: Request,
    user_id: CurrentUserDep,
    user_session: CurrentSessionDep,
    prompt_service: PromptServiceDep,
    prompt_data: PromptDataUpdate,
    repo_name: str = Query(...),
    file_path: str = Query(...)
) -> StandardResponse[PromptMeta]:
    """
    Save a prompt (create or update).
    
    If the file doesn't exist, creates a new prompt.
    If the file exists, updates the existing prompt.
    
    Returns:
        StandardResponse[PromptMeta]: Standardized response containing the saved prompt
    
    Raises:
        ValidationException: When prompt validation fails
        NotFoundException: When repository is not found
        AppException: When save operation fails
    """
    request_id = request.state.request_id
    
    try:
        logger.info(
            f"Saving prompt {repo_name}:{file_path}",
            extra={"request_id": request_id, "user_id": user_id}
        )
        
        # Get OAuth token and user info from session
        oauth_token = getattr(user_session, 'oauth_token', None)
        
        # Get user information for git commit author
        user = user_session.user if hasattr(user_session, 'user') else None
        author_name = user.oauth_name or user.oauth_username if user else None
        author_email = user.oauth_email if user else None
        
        prompt, pr_info = await prompt_service.save_prompt(
            user_id=user_id,
            repo_name=repo_name,
            file_path=file_path,
            prompt_data=prompt_data,
            oauth_token=oauth_token,
            author_name=author_name,
            author_email=author_email,
            user_session=user_session
        )
        
        logger.info(
            f"Successfully saved prompt {repo_name}:{file_path}",
            extra={"request_id": request_id, "user_id": user_id}
        )
        
        # PR info is already attached to the prompt data object
        return success_response(
            data=prompt.model_dump(mode='json'),
            message="Prompt saved successfully",
            meta={"request_id": request_id}
        )
        
    except ValueError as e:
        raise ValidationException(
            message="Invalid prompt data",
            errors=[{
                "code": "VALIDATION_ERROR",
                "message": str(e),
                "field": "prompt_data"
            }]
        )
    except (ValidationException, NotFoundException, AppException):
        # These will be handled by the global exception handlers
        raise
    except Exception as e:
        logger.error(
            f"Failed to save prompt {repo_name}:{file_path}: {str(e)}",
            exc_info=True,
            extra={"request_id": request_id, "user_id": user_id}
        )
        raise AppException(
            message="Failed to save prompt",
            detail=str(e)
        )


@router.delete(
    "/",
    response_model=StandardResponse[None],
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
                        "detail": "Failed to delete prompt"
                    }
                }
            }
        }
    },
    summary="Delete prompt",
    description="Delete a prompt. Removes the prompt file from the repository.",
)
async def delete_prompt(
    request: Request,
    user_id: CurrentUserDep,
    prompt_service: PromptServiceDep,
    repo_name: str = Query(...),
    file_path: str = Query(...)
) -> StandardResponse[None]:
    """
    Delete a prompt.
    
    Removes the prompt file from the repository.
    
    Returns:
        StandardResponse[None]: Standardized response confirming deletion
    
    Raises:
        NotFoundException: When prompt is not found or access denied
        AppException: When prompt deletion fails
    """
    request_id = request.state.request_id
    
    try:
        logger.info(
            f"Deleting prompt {repo_name}:{file_path}",
            extra={"request_id": request_id, "user_id": user_id}
        )
        
        success = await prompt_service.delete_prompt(
            user_id=user_id,
            repo_name=repo_name,
            file_path=file_path
        )
        
        if not success:
            raise NotFoundException(
                resource="Prompt",
                identifier=f"{repo_name}:{file_path}"
            )
        
        logger.info(
            f"Successfully deleted prompt {repo_name}:{file_path}",
            extra={"request_id": request_id, "user_id": user_id}
        )
        
        return success_response(
            message="Prompt deleted successfully",
            meta={"request_id": request_id}
        )
        
    except (NotFoundException, AppException):
        # These will be handled by the global exception handlers
        raise
    except Exception as e:
        logger.error(
            f"Failed to delete prompt {repo_name}:{file_path}: {str(e)}",
            exc_info=True,
            extra={"request_id": request_id, "user_id": user_id}
        )
        raise AppException(
            message="Failed to delete prompt",
            detail=str(e)
        )