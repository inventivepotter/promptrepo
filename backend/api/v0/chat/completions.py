"""
Chat completions endpoint using any-llm SDK.
"""
from fastapi import APIRouter, HTTPException, Depends, Header
from fastapi.responses import StreamingResponse
from sqlmodel import Session
from typing import AsyncGenerator, Optional, Annotated, Union, cast, AsyncIterator
import uuid
import time
import json
import logging
from datetime import datetime
from any_llm import acompletion, types as any_llm_types
from any_llm.types.completion import ChatCompletion, ChatCompletionChunk

# Import schemas from main schemas folder
from schemas.chat import (
    ChatCompletionRequest,
    ChatCompletionResponse,
    ChatCompletionChoice,
    ChatCompletionStreamResponse,
    ChatCompletionStreamChoice,
    ChatMessage,
    UsageStats,
    PromptTokensDetails,
    CompletionTokensDetails,
    ErrorResponse
)
from models.database import get_session
from services.session_service import SessionService
from settings.base_settings import settings

logger = logging.getLogger(__name__)
router = APIRouter()


# Authentication dependency
async def get_bearer_token(authorization: Annotated[str | None, Header()] = None) -> str:
    """Extract Bearer token from Authorization header."""
    if not authorization:
        raise HTTPException(
            status_code=401,
            detail="Authorization header required"
        )

    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Invalid authorization header format"
        )

    return authorization.replace("Bearer ", "")


async def verify_session(
    token: str = Depends(get_bearer_token), 
    db: Session = Depends(get_session)
) -> str:
    """Verify session token and return username."""
    if not SessionService.is_session_valid(db, token):
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired session token"
        )
    
    user_session = SessionService.get_session_by_id(db, token)
    if not user_session:
        raise HTTPException(
            status_code=401,
            detail="Session not found"
        )
    
    return user_session.username


def validate_system_message(messages: list[ChatMessage]) -> None:
    """Validate that the first message is a system message."""
    if not messages:
        raise HTTPException(
            status_code=400,
            detail="Messages array cannot be empty. A system message is required to define the AI assistant's behavior."
        )
    
    if messages[0].role != "system":
        raise HTTPException(
            status_code=400,
            detail="First message must be a system message with role 'system'. Please provide a system prompt to define the AI assistant's behavior."
        )
        
    if not messages[0].content or not messages[0].content.strip():
        raise HTTPException(
            status_code=400,
            detail="System message content cannot be empty. Please provide a valid system prompt."
        )

def validate_provider_and_model(provider: str, model: str) -> None:
    """Validate provider and model fields."""
    if not provider or not provider.strip():
        raise HTTPException(
            status_code=400,
            detail="Provider field is required and cannot be empty"
        )
    
    if not model or not model.strip():
        raise HTTPException(
            status_code=400,
            detail="Model field is required and cannot be empty"
        )


def get_api_config_for_provider_model(provider: str, model: str) -> tuple[str, str | None]:
    """Get API key and base URL from settings for the given provider/model combination."""
    llm_configs = settings.llm_settings.llm_configs
    
    for config in llm_configs:
        if config.get("provider") == provider and config.get("model") == model:
            api_key = config.get("apiKey")
            if api_key:
                api_base_url = config.get("apiBaseUrl")
                return api_key, api_base_url
            break
    
    raise HTTPException(
        status_code=400,
        detail=f"No API key found for provider '{provider}' and model '{model}'. Please configure the API key in settings."
    )


def convert_to_any_llm_messages(messages: list[ChatMessage]) -> list[dict]:
    """Convert our ChatMessage format to any-llm format."""
    converted_messages = []
    for msg in messages:
        any_llm_msg: dict = {
            "role": msg.role,
            "content": msg.content
        }
        if msg.tool_call_id:
            any_llm_msg["tool_call_id"] = msg.tool_call_id
        if msg.tool_calls:
            any_llm_msg["tool_calls"] = msg.tool_calls
        converted_messages.append(any_llm_msg)
    return converted_messages


async def stream_chat_completion(
    request: ChatCompletionRequest,
    model: str,
    completion_id: str
) -> AsyncGenerator[str, None]:
    """Generate streaming chat completion responses."""
    try:
        # Validate system message is present
        validate_system_message(request.messages)
        
        # Convert messages to any-llm format
        any_llm_messages = convert_to_any_llm_messages(request.messages)
        
        # Get API key and base URL for this provider/model combination
        api_key, api_base_url = get_api_config_for_provider_model(request.provider, request.model)
        
        # Prepare completion parameters with model in provider/model format
        model_identifier = f"{request.provider}/{request.model}"
        completion_params = {
            "model": model_identifier,
            "messages": any_llm_messages,
            "stream": True,
            "api_key": api_key
        }
        
        # Add API base URL if configured
        if api_base_url:
            completion_params["api_base"] = api_base_url
        
        # Add optional parameters if provided
        if request.temperature is not None:
            completion_params["temperature"] = request.temperature
        if request.max_tokens is not None:
            completion_params["max_tokens"] = request.max_tokens
        if request.top_p is not None:
            completion_params["top_p"] = request.top_p
        if request.frequency_penalty is not None:
            completion_params["frequency_penalty"] = request.frequency_penalty
        if request.presence_penalty is not None:
            completion_params["presence_penalty"] = request.presence_penalty
        if request.stop is not None:
            completion_params["stop"] = request.stop

        # Debug logging
        logger.info(f"Calling any-llm completion with params: {completion_params}")
        logger.info(f"Provider: '{request.provider}', Model: '{request.model}', Model Identifier: '{model_identifier}'")

        # Call any-llm completion with streaming
        stream_response = await acompletion(**completion_params)
        stream_iterator = cast(AsyncIterator[ChatCompletionChunk], stream_response)
        async for chunk in stream_iterator:
            # Handle streaming response chunks from any-llm
            try:
                # Extract content from chunk - any-llm streaming format may vary
                delta_content = ""
                finish_reason = None
                
                try:
                    if hasattr(chunk, 'choices'):
                        choices = getattr(chunk, 'choices', None)
                        if choices and len(choices) > 0:
                            choice = choices[0]
                            if hasattr(choice, 'delta') and choice.delta:
                                delta_content = getattr(choice.delta, 'content', '') or ""
                            finish_reason = getattr(choice, 'finish_reason', None)
                    elif hasattr(chunk, 'content'):
                        # Some streaming APIs return content directly
                        delta_content = getattr(chunk, 'content', '') or ""
                except (AttributeError, IndexError, TypeError):
                    # Skip malformed chunks
                    continue
                
                # Create streaming response
                stream_response_chunk = ChatCompletionStreamResponse(
                    id=completion_id,
                    created=int(time.time()),
                    model=model,
                    choices=[
                        ChatCompletionStreamChoice(
                            index=0,
                            delta=ChatMessage(
                                role="assistant",
                                content=delta_content
                            ),
                            finish_reason=finish_reason
                        )
                    ]
                )
                
                # Yield the chunk as server-sent event
                yield f"data: {stream_response_chunk.model_dump_json()}\n\n"
                
            except Exception as chunk_error:
                logger.warning(f"Error processing streaming chunk: {chunk_error}")
                continue
        
        # Send the final [DONE] message
        yield "data: [DONE]\n\n"
        
    except Exception as e:
        logger.error(f"Error in streaming completion: {e}")
        error_response = {
            "error": {
                "message": f"Completion error: {str(e)}",
                "type": "completion_error"
            }
        }
        yield f"data: {json.dumps(error_response)}\n\n"


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
        validate_provider_and_model(request.provider, request.model)
        
        logger.info(f"Chat completion request from {username} using {request.provider}/{request.model}")
        
        # Handle streaming response
        if request.stream:
            return StreamingResponse(
                stream_chat_completion(request, f"{request.provider}/{request.model}", completion_id),
                media_type="text/plain",
                headers={
                    "Cache-Control": "no-cache",
                    "Connection": "keep-alive",
                    "Content-Type": "text/event-stream"
                }
            )
        
        # Handle non-streaming response
        # Validate system message is present
        validate_system_message(request.messages)
        
        # Convert messages to any-llm format
        any_llm_messages = convert_to_any_llm_messages(request.messages)
        
        # Get API key and base URL for this provider/model combination
        api_key, api_base_url = get_api_config_for_provider_model(request.provider, request.model)
        
        # Prepare completion parameters with model in provider/model format
        model_identifier = f"{request.provider}/{request.model}"
        completion_params = {
            "model": model_identifier,
            "messages": any_llm_messages,
            "api_key": api_key
        }
        
        # Add API base URL if configured
        if api_base_url:
            completion_params["api_base"] = api_base_url
        
        # Add optional parameters if provided
        if request.temperature is not None:
            completion_params["temperature"] = request.temperature
        if request.max_tokens is not None:
            completion_params["max_tokens"] = request.max_tokens
        if request.top_p is not None:
            completion_params["top_p"] = request.top_p
        if request.frequency_penalty is not None:
            completion_params["frequency_penalty"] = request.frequency_penalty
        if request.presence_penalty is not None:
            completion_params["presence_penalty"] = request.presence_penalty
        if request.stop is not None:
            completion_params["stop"] = request.stop

        # Debug logging
        logger.info(f"Calling any-llm completion with params: {completion_params}")
        logger.info(f"Provider: '{request.provider}', Model: '{request.model}', Model Identifier: '{model_identifier}'")

        # Call any-llm completion (non-streaming)
        try:
            completion_result = await acompletion(**completion_params)
            response = cast(ChatCompletion, completion_result)  # Safe because stream=False
            
            # Debug logging to understand response structure
            logger.info(f"Response type: {type(response)}")
            
            # Handle response - any-llm follows OpenAI format for non-streaming
            content = ""
            finish_reason = None
            
            # any-llm returns ChatCompletion object with choices[0].message.content
            if hasattr(response, 'choices') and response.choices and len(response.choices) > 0:
                choice = response.choices[0]
                logger.info(f"Choice found: {choice}")
                
                if hasattr(choice, 'message') and hasattr(choice.message, 'content'):
                    content = choice.message.content or ""
                    logger.info(f"Extracted content: {repr(content[:200])}")
                    
                if hasattr(choice, 'finish_reason'):
                    finish_reason = choice.finish_reason
            else:
                logger.error(f"No choices in response or choices is empty. Response: {response}")
            
            if not content:
                logger.error(f"No content extracted from response")
                raise HTTPException(
                    status_code=500,
                    detail="Unexpected response format from completion API"
                )
                
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
        
        # Handle usage statistics properly
        usage_stats = None
        if response.usage:
            try:
                usage_data = response.usage  # This is OpenAI CompletionUsage object
                
                # Convert prompt_tokens_details
                prompt_details = None
                if usage_data.prompt_tokens_details:
                    prompt_details = PromptTokensDetails(
                        audio_tokens=getattr(usage_data.prompt_tokens_details, 'audio_tokens', None),
                        cached_tokens=getattr(usage_data.prompt_tokens_details, 'cached_tokens', None)
                    )
                
                # Convert completion_tokens_details
                completion_details = None
                if usage_data.completion_tokens_details:
                    completion_details = CompletionTokensDetails(
                        accepted_prediction_tokens=getattr(usage_data.completion_tokens_details, 'accepted_prediction_tokens', None),
                        audio_tokens=getattr(usage_data.completion_tokens_details, 'audio_tokens', None),
                        reasoning_tokens=getattr(usage_data.completion_tokens_details, 'reasoning_tokens', None),
                        rejected_prediction_tokens=getattr(usage_data.completion_tokens_details, 'rejected_prediction_tokens', None)
                    )
                
                # Create UsageStats with proper types
                usage_stats = UsageStats(
                    prompt_tokens=usage_data.prompt_tokens,
                    completion_tokens=usage_data.completion_tokens,
                    total_tokens=usage_data.total_tokens,
                    prompt_tokens_details=prompt_details,
                    completion_tokens_details=completion_details
                )
            except Exception as usage_error:
                logger.warning(f"Error processing usage statistics: {usage_error}")
                usage_stats = None
        
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