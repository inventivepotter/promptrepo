"""
Completion utilities for chat endpoints.
"""
import time
import json
import logging
from typing import AsyncGenerator, cast, AsyncIterator
from any_llm import acompletion
from any_llm.types.completion import ChatCompletion, ChatCompletionChunk

from schemas.chat import (
    ChatCompletionRequest,
    ChatCompletionStreamResponse,
    ChatCompletionStreamChoice,
    ChatMessage,
    UsageStats,
    PromptTokensDetails,
    CompletionTokensDetails
)
from .validation_utils import validate_system_message
from .message_utils import convert_to_any_llm_messages
from .config_utils import get_api_config_for_provider_model

logger = logging.getLogger(__name__)


def build_completion_params(request: ChatCompletionRequest, api_key: str, api_base_url: str | None, stream: bool = False) -> dict:
    """Build completion parameters for any-llm API call."""
    model_identifier = f"{request.provider}/{request.model}"
    completion_params = {
        "model": model_identifier,
        "messages": convert_to_any_llm_messages(request.messages),
        "api_key": api_key
    }
    
    if stream:
        completion_params["stream"] = True
    
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
    
    return completion_params


async def stream_chat_completion(
    request: ChatCompletionRequest,
    model: str,
    completion_id: str
) -> AsyncGenerator[str, None]:
    """Generate streaming chat completion responses."""
    try:
        # Validate system message is present
        validate_system_message(request.messages)
        
        # Get API key and base URL for this provider/model combination
        api_key, api_base_url = get_api_config_for_provider_model(request.provider, request.model)
        
        # Build completion parameters
        completion_params = build_completion_params(request, api_key, api_base_url, stream=True)
        
        # Debug logging
        logger.info(f"Calling any-llm completion with params: {completion_params}")
        logger.info(f"Provider: '{request.provider}', Model: '{request.model}', Model Identifier: '{completion_params['model']}'")

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


def process_usage_stats(usage_data) -> UsageStats | None:
    """Process usage statistics from any-llm response."""
    if not usage_data:
        return None
    
    try:
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
        return UsageStats(
            prompt_tokens=usage_data.prompt_tokens,
            completion_tokens=usage_data.completion_tokens,
            total_tokens=usage_data.total_tokens,
            prompt_tokens_details=prompt_details,
            completion_tokens_details=completion_details
        )
    except Exception as usage_error:
        logger.warning(f"Error processing usage statistics: {usage_error}")
        return None


async def execute_non_streaming_completion(request: ChatCompletionRequest) -> tuple[str, str | None, UsageStats | None]:
    """Execute non-streaming completion and return content, finish_reason, and usage stats."""
    # Validate system message is present
    validate_system_message(request.messages)
    
    # Get API key and base URL for this provider/model combination
    api_key, api_base_url = get_api_config_for_provider_model(request.provider, request.model)
    
    # Build completion parameters
    completion_params = build_completion_params(request, api_key, api_base_url, stream=False)
    
    # Debug logging
    logger.info(f"Calling any-llm completion with params: {completion_params}")
    logger.info(f"Provider: '{request.provider}', Model: '{request.model}', Model Identifier: '{completion_params['model']}'")

    # Call any-llm completion (non-streaming)
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
        from fastapi import HTTPException
        raise HTTPException(
            status_code=500,
            detail="Unexpected response format from completion API"
        )
    
    # Process usage statistics
    usage_stats = process_usage_stats(response.usage)
    
    return content, finish_reason, usage_stats