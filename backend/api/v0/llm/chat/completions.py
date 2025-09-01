"""
Chat completions endpoint using any-llm SDK.
"""
from fastapi import APIRouter, HTTPException, Depends
from fastapi.responses import StreamingResponse
from typing import Optional
import uuid
import time
import logging
from datetime import datetime

# Import schemas from main schemas folder
from schemas.chat import (
    ChatCompletionRequest,
    ChatCompletionResponse,
    ChatCompletionChoice,
    ChatMessage,
    ErrorResponse
)

# Import service classes
from utils.auth_utils import verify_session
from services.completion_service import chat_completion_service

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post("/completions", response_model=ChatCompletionResponse)
async def chat_completions(
    request: ChatCompletionRequest,
    username: str = Depends(verify_session)
):
    """
    Create a chat completion using any-llm.
    Supports both streaming and non-streaming responses.
    """
    try:
        # Generate completion ID
        completion_id = f"chatcmpl-{uuid.uuid4().hex[:29]}"
        
        # Validate required fields
        chat_completion_service.validate_provider_and_model(request.provider, request.model)

        logger.info(f"Chat completion request from {username} using {request.provider}/{request.model}")
        
        # Handle streaming response
        if request.stream:
            return StreamingResponse(
                chat_completion_service.stream_completion(request, f"{request.provider}/{request.model}", completion_id),
                media_type="text/plain",
                headers={
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive",
                    "Content-Type": "text/event-stream"
                }
            )
        
        # Handle non-streaming response
        try:
            content, finish_reason, usage_stats = await chat_completion_service.execute_non_streaming_completion(request)
        except Exception as e:
            logger.error(f"Error in acompletion call or response processing: {e}")
            logger.error(f"Exception type: {type(e)}")
            raise HTTPException(
                status_code=500,
                detail=f"Completion failed: {str(e)}"
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
            model=f"{request.provider}/{request.model}",
            choices=[
                ChatCompletionChoice(
                    index=0,
                    message=assistant_message,
                    finish_reason=finish_reason
                )
            ],
            usage=usage_stats
        )
        
        logger.info(f"Chat completion successful for {username}")
        return completion_response
        
    except HTTPException:
        # Re-raise FastAPI HTTP exceptions
        raise
    except Exception as e:
        logger.error(f"Error in chat completion: {e}")
        raise HTTPException(
            status_code=500,
            detail=f"Completion failed: {str(e)}"
        )


@router.get("/health")
async def chat_health_check():
    """Health check for chat endpoints."""
    return {
        "status": "healthy",
        "service": "chat",
        "endpoints": [
            "POST /completions"
        ],
        "timestamp": datetime.utcnow().isoformat()
    }