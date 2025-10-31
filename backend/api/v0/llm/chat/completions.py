"""
Chat completions endpoint with standardized responses.
"""
from fastapi import APIRouter, Request, status
import logging

from middlewares.rest import (
    StandardResponse,
    success_response,
    BadRequestException,
    AppException
)
from services.llm.models import (
    ChatCompletionRequest,
    ChatCompletionResponse,
)
from api.deps import ChatCompletionServiceDep, CurrentUserDep

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post(
    "/completions",
    response_model=StandardResponse[ChatCompletionResponse],
    status_code=status.HTTP_200_OK,
    responses={
        400: {
            "description": "Bad request",
            "content": {
                "application/json": {
                    "example": {
                        "status": "error",
                        "type": "/errors/bad-request",
                        "title": "Bad request",
                        "detail": "Invalid prompt_meta or messages"
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
                        "detail": "Completion failed"
                    }
                }
            }
        }
    },
    summary="Create chat completion",
    description="Create a chat completion using PromptMeta configuration and optional conversation history."
)
async def chat_completions(
    request_body: ChatCompletionRequest,
    request: Request,
    chat_completion_service: ChatCompletionServiceDep,
    user_id: CurrentUserDep
) -> StandardResponse[ChatCompletionResponse]:
    """
    Create a chat completion using PromptMeta configuration.
    
    Args:
        request_body: ChatCompletionRequest with prompt_meta and optional messages
        request: FastAPI Request object
        chat_completion_service: Injected chat completion service
        user_id: Current user ID from auth
    
    Returns:
        StandardResponse[ChatCompletionResponse]: Standardized response containing completion
    
    Raises:
        BadRequestException: When validation fails
        AppException: When completion fails
    """
    request_id = getattr(request.state, "request_id", None)
    
    try:
        # Validate prompt_meta
        if not request_body.prompt_meta:
            raise BadRequestException(
                message="prompt_meta is required",
                context={"request_id": request_id}
            )
        
        # Extract provider and model from prompt_meta for validation
        prompt_data = request_body.prompt_meta.prompt
        provider = prompt_data.provider
        model = prompt_data.model
        
        # Validate provider and model
        try:
            chat_completion_service.validate_provider_and_model(provider, model)
        except Exception as e:
            raise BadRequestException(
                message="Invalid provider or model",
                context={
                    "provider": provider,
                    "model": model,
                    "error": str(e)
                }
            )

        logger.info(
            "Chat completion request",
            extra={
                "request_id": request_id,
                "user_id": user_id,
                "provider": provider,
                "model": model,
                "message_count": len(request_body.messages) if request_body.messages else 0
            }
        )
        
        # Execute completion using the service
        try:
            completion_response = await chat_completion_service.execute_completion(
                request=request_body,
                user_id=user_id
            )
        except Exception as e:
            logger.error(
                f"Error in completion processing: {e}",
                exc_info=True,
                extra={
                    "request_id": request_id,
                    "user_id": user_id,
                    "provider": provider,
                    "model": model
                }
            )
            raise AppException(
                message="Completion failed",
                detail=str(e)
            )
        
        logger.info(
            "Chat completion successful",
            extra={
                "request_id": request_id,
                "user_id": user_id,
                "provider": provider,
                "model": model,
                "usage": completion_response.usage.dict() if completion_response.usage else None
            }
        )
        
        return success_response(
            data=completion_response,
            message="Chat completion created successfully",
            meta={"request_id": request_id}
        )
        
    except (BadRequestException, AppException):
        # Re-raise our custom exceptions
        raise
    except Exception as e:
        logger.error(
            f"Unexpected error in chat completion: {e}",
            exc_info=True,
            extra={
                "request_id": request_id,
                "user_id": user_id
            }
        )
        raise AppException(
            message="Completion failed",
            detail=str(e)
        )