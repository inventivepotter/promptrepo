"""
Chat completions endpoint with standardized responses.
"""
from fastapi import APIRouter, Request, status
from fastapi.responses import StreamingResponse
import uuid
import time
import json
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
    ChatCompletionChoice,
    ChatMessage,
)
from services.llm.completion_service import chat_completion_service

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
                        "detail": "Invalid provider or model"
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
    description="Create a chat completion using any-llm. Supports both streaming and non-streaming responses."
)
async def chat_completions(
    request_body: ChatCompletionRequest,
    request: Request
):
    """
    Create a chat completion using any-llm.
    Supports both streaming and non-streaming responses.
    
    Returns:
        StandardResponse[ChatCompletionResponse]: Standardized response containing completion
        StreamingResponse: When stream=true is requested
    
    Raises:
        BadRequestException: When provider/model validation fails
        AppException: When completion fails
    """
    request_id = getattr(request.state, "request_id", None)
    
    try:
        # Generate completion ID
        completion_id = f"chatcmpl-{uuid.uuid4().hex[:29]}"
        
        # Validate required fields
        try:
            chat_completion_service.validate_provider_and_model(request_body.provider, request_body.model)
        except Exception as e:
            raise BadRequestException(
                message="Invalid provider or model",
                context={
                    "provider": request_body.provider,
                    "model": request_body.model,
                    "error": str(e)
                }
            )

        logger.info(
            f"Chat completion request",
            extra={
                "request_id": request_id,
                "provider": request_body.provider,
                "model": request_body.model,
                "stream": request_body.stream,
                "message_count": len(request_body.messages) if request_body.messages else 0
            }
        )
        
        # Handle streaming response
        if request_body.stream:
            logger.info(
                "Returning streaming response",
                extra={
                    "request_id": request_id,
                    "completion_id": completion_id
                }
            )
            return StreamingResponse(
                chat_completion_service.stream_completion(
                    request_body,
                    f"{request_body.provider}/{request_body.model}",
                    completion_id
                ),
                media_type="text/plain",
                headers={
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive",
                    "Content-Type": "text/event-stream",
                    "X-Request-Id": request_id or ""
                }
            )
        
        # Handle non-streaming response
        try:
            content, finish_reason, usage_stats, inference_time_ms = await chat_completion_service.execute_non_streaming_completion(request_body)
        except Exception as e:
            logger.error(
                f"Error in completion processing: {e}",
                exc_info=True,
                extra={
                    "request_id": request_id,
                    "provider": request_body.provider,
                    "model": request_body.model
                }
            )
            raise AppException(
                message="Completion failed",
                detail=str(e)
            )
        
        # Create response message
        assistant_message = ChatMessage(
            role="assistant",
            content=content,
            tool_calls=None  # Add tool_calls support if needed
        )
        
        # Create completion response
        completion_response = ChatCompletionResponse(
            id=completion_id,
            created=int(time.time()),
            model=f"{request_body.provider}/{request_body.model}",
            choices=[
                ChatCompletionChoice(
                    index=0,
                    message=assistant_message,
                    finish_reason=finish_reason
                )
            ],
            usage=usage_stats,
            inference_time_ms=inference_time_ms
        )
        
        logger.info(
            "Chat completion successful",
            extra={
                "request_id": request_id,
                "completion_id": completion_id,
                "provider": request_body.provider,
                "model": request_body.model,
                "usage": usage_stats.dict() if usage_stats else None
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
                "provider": request_body.provider if hasattr(request_body, 'provider') else None,
                "model": request_body.model if hasattr(request_body, 'model') else None
            }
        )
        raise AppException(
            message="Completion failed",
            detail=str(e)
        )