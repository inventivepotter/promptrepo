"""
LiteLLM provider service implementation.
Handles LiteLLM-specific LLM operations with OpenAI-compatible interface.
"""
import json
import logging
import time
from typing import List, Dict, Any, AsyncGenerator, Optional
import httpx
from services.llm.models import (
    ChatMessage,
    ChatCompletionRequest,
    ChatCompletionResponse,
    ChatCompletionChoice,
    UsageStats,
    ChatCompletionStreamResponse,
    ChatCompletionStreamChoice
)

logger = logging.getLogger(__name__)


class LiteLLMProvider:
    """Service for handling LiteLLM LLM operations."""
    
    def __init__(self, api_key: str, api_base: str):
        """
        Initialize LiteLLM service.
        
        Args:
            api_key: LiteLLM API key
            api_base: LiteLLM API base URL (required)
        """
        self.api_key = api_key
        self.api_base = api_base
        self.client = httpx.AsyncClient(
            base_url=api_base,
            headers={
                "authorization": f"Bearer {api_key}",
                "content-type": "application/json",
                "accept-language": "en-US,en"
            },
            timeout=60.0
        )
    
    async def __aenter__(self):
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        await self.client.aclose()
    
    def get_available_models(self) -> List[str]:
        """
        Get list of available LiteLLM models.
        LiteLLM doesn't support list_models, so we return empty list
        to let users specify their own models.
        """
        return []
    
    def _convert_messages_to_litellm_format(self, messages: List[ChatMessage]) -> List[Dict[str, str]]:
        """Convert ChatMessage format to LiteLLM format."""
        return [
            {
                "role": msg.role,
                "content": msg.content
            }
            for msg in messages
        ]
    
    def _convert_usage_stats(self, litellm_usage: Optional[Dict[str, Any]]) -> Optional[UsageStats]:
        """Convert LiteLLM usage stats to our format."""
        if not litellm_usage:
            return None
        
        return UsageStats(
            prompt_tokens=litellm_usage.get("prompt_tokens"),
            completion_tokens=litellm_usage.get("completion_tokens"),
            total_tokens=litellm_usage.get("total_tokens")
        )
    
    async def create_completion(
        self,
        request: ChatCompletionRequest,
        stream: bool = False
    ) -> ChatCompletionResponse:
        """
        Create a chat completion with LiteLLM.
        
        Args:
            request: Chat completion request
            stream: Whether to stream the response
            
        Returns:
            Chat completion response
        """
        start_time = time.time()
        
        payload = {
            "model": request.model,
            "messages": self._convert_messages_to_litellm_format(request.messages),
            "stream": stream,
            "temperature": request.temperature if request.temperature is not None else 1.0
        }
        
        # Add optional parameters if provided
        if request.max_tokens is not None:
            payload["max_tokens"] = request.max_tokens
        if request.top_p is not None:
            payload["top_p"] = request.top_p
        if request.frequency_penalty is not None:
            payload["frequency_penalty"] = request.frequency_penalty
        if request.presence_penalty is not None:
            payload["presence_penalty"] = request.presence_penalty
        if request.stop is not None:
            payload["stop"] = request.stop
        
        try:
            response = await self.client.post("/chat/completions", json=payload)
            response.raise_for_status()
            
            data = response.json()
            
            # Calculate inference time
            inference_time_ms = (time.time() - start_time) * 1000
            
            # Convert LiteLLM response to our format
            choices = []
            for choice_data in data.get("choices", []):
                message_data = choice_data.get("message", {})
                choice = ChatCompletionChoice(
                    index=choice_data.get("index", 0),
                    message=ChatMessage(
                        role=message_data.get("role", "assistant"),
                        content=message_data.get("content", "")
                    ),
                    finish_reason=choice_data.get("finish_reason")
                )
                choices.append(choice)
            
            return ChatCompletionResponse(
                id=data.get("id", f"litellm-{int(time.time())}"),
                object=data.get("object", "chat.completion"),
                created=data.get("created", int(time.time())),
                model=data.get("model", request.model),
                choices=choices,
                usage=self._convert_usage_stats(data.get("usage")),
                inference_time_ms=inference_time_ms
            )
            
        except httpx.HTTPStatusError as e:
            logger.error(f"LiteLLM API error: {e.response.status_code} - {e.response.text}")
            raise Exception(f"LiteLLM API error: {e.response.status_code} - {e.response.text}")
        except Exception as e:
            logger.error(f"Error creating LiteLLM completion: {e}")
            raise Exception(f"Error creating LiteLLM completion: {str(e)}")
    
    async def create_streaming_completion(
        self,
        request: ChatCompletionRequest
    ) -> AsyncGenerator[str, None]:
        """
        Create a streaming chat completion with LiteLLM.
        
        Args:
            request: Chat completion request
            
        Yields:
            Server-sent event formatted response chunks
        """
        payload = {
            "model": request.model,
            "messages": self._convert_messages_to_litellm_format(request.messages),
            "stream": True,
            "temperature": request.temperature if request.temperature is not None else 1.0
        }
        
        # Add optional parameters if provided
        if request.max_tokens is not None:
            payload["max_tokens"] = request.max_tokens
        if request.top_p is not None:
            payload["top_p"] = request.top_p
        if request.frequency_penalty is not None:
            payload["frequency_penalty"] = request.frequency_penalty
        if request.presence_penalty is not None:
            payload["presence_penalty"] = request.presence_penalty
        if request.stop is not None:
            payload["stop"] = request.stop
        
        try:
            async with self.client.stream("POST", "/chat/completions", json=payload) as response:
                response.raise_for_status()
                
                async for line in response.aiter_lines():
                    if line.startswith("data: "):
                        data_str = line[6:]  # Remove "data: " prefix
                        
                        if data_str.strip() == "[DONE]":
                            break
                        
                        try:
                            data = json.loads(data_str)
                            
                            # Convert LiteLLM streaming response to our format
                            choices = []
                            for choice_data in data.get("choices", []):
                                delta_data = choice_data.get("delta", {})
                                choice = ChatCompletionStreamChoice(
                                    index=choice_data.get("index", 0),
                                    delta=ChatMessage(
                                        role=delta_data.get("role", "assistant"),
                                        content=delta_data.get("content", "")
                                    ),
                                    finish_reason=choice_data.get("finish_reason")
                                )
                                choices.append(choice)
                            
                            stream_response = ChatCompletionStreamResponse(
                                id=data.get("id", f"litellm-{int(time.time())}"),
                                object=data.get("object", "chat.completion.chunk"),
                                created=data.get("created", int(time.time())),
                                model=data.get("model", request.model),
                                choices=choices
                            )
                            
                            yield f"data: {stream_response.model_dump_json()}\n\n"
                            
                        except json.JSONDecodeError:
                            logger.warning(f"Failed to parse streaming data: {data_str}")
                            continue
                            
        except httpx.HTTPStatusError as e:
            logger.error(f"LiteLLM streaming API error: {e.response.status_code} - {e.response.text}")
            raise Exception(f"LiteLLM streaming API error: {e.response.status_code} - {e.response.text}")
        except Exception as e:
            logger.error(f"Error creating LiteLLM streaming completion: {e}")
            raise Exception(f"Error creating LiteLLM streaming completion: {str(e)}")