"""
Chat completions endpoint with standardized responses.
"""
from fastapi import APIRouter, Request, status
from fastapi.responses import StreamingResponse
from typing import List
import uuid
import time
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
from api.deps import ChatCompletionServiceDep, CurrentUserDep, ToolExecutionServiceDep

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
    request: Request,
    chat_completion_service: ChatCompletionServiceDep,
    user_id: CurrentUserDep,
    tool_execution_service: ToolExecutionServiceDep
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
        
        # Handle non-streaming response with automatic tool call loop
        try:
            content, finish_reason, usage_stats, inference_time_ms, tool_calls = await chat_completion_service.execute_non_streaming_completion(request_body, user_id)
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
        
        # Create initial assistant message with tool_calls if present
        assistant_message = ChatMessage(
            role="assistant",
            content=content,
            tool_calls=tool_calls
        )
        
        # Initialize tool_responses list for messages to return
        tool_responses_list: List[ChatMessage] = []
        
        # If tool_calls are present, delegate to ToolExecutionService for automatic tool loop
        if tool_calls and request_body.tools:
            logger.info(
                "Tool calls detected in completion - starting automatic tool loop",
                extra={
                    "request_id": request_id,
                    "tool_call_count": len(tool_calls),
                    "tool_names": [tc.get("function", {}).get("name") for tc in tool_calls]
                }
            )
            
            try:
                # Execute tool call loop through service
                final_assistant_message, tool_responses_list = await tool_execution_service.execute_tool_call_loop(
                    initial_tool_calls=tool_calls,
                    request_body=request_body,
                    assistant_message=assistant_message,
                    user_id=user_id,
                    request_id=request_id
                )
                
                # Update content from final assistant message
                content = final_assistant_message.content
                finish_reason = "stop"  # Tool loop completed successfully
                
                # Keep original tool_calls in assistant_message for frontend to display
                # but use content from final answer
                assistant_message.content = content
                
            except Exception as tool_loop_error:
                logger.error(
                    f"Error in tool execution loop: {tool_loop_error}",
                    exc_info=True,
                    extra={"request_id": request_id}
                )
                # If tool loop fails, continue with original assistant message
                # (frontend will at least see the tool calls)
        
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
            inference_time_ms=inference_time_ms,
            tool_responses=tool_responses_list if tool_responses_list else None
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