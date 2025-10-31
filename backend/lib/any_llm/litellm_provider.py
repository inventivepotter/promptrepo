"""
LiteLLM provider implementation following AnyLLM standard pattern.
Provides OpenAI-compatible interface through httpx client.
"""
from __future__ import annotations

import json
import logging
from typing import TYPE_CHECKING, Any

import httpx
from pydantic import BaseModel

from any_llm.any_llm import AnyLLM

logger = logging.getLogger(__name__)

if TYPE_CHECKING:
    from collections.abc import AsyncIterator, Sequence

    from any_llm.types.completion import (
        ChatCompletion,
        ChatCompletionChunk,
        CompletionParams,
        CreateEmbeddingResponse,
    )
    from any_llm.types.model import Model


class LiteLLMProvider(AnyLLM):
    """
    LiteLLM Provider following AnyLLM standard pattern.
    
    Uses httpx client to communicate with LiteLLM proxy server.
    Read more here - https://docs.litellm.ai/
    """

    PROVIDER_NAME = "litellm"
    PROVIDER_DOCUMENTATION_URL = "https://docs.litellm.ai/"
    ENV_API_KEY_NAME = "LITELLM_API_KEY"

    SUPPORTS_COMPLETION_STREAMING = True
    SUPPORTS_COMPLETION = True
    SUPPORTS_RESPONSES = False
    SUPPORTS_COMPLETION_REASONING = False
    SUPPORTS_COMPLETION_IMAGE = True
    SUPPORTS_COMPLETION_PDF = False
    SUPPORTS_EMBEDDING = True
    SUPPORTS_LIST_MODELS = False

    MISSING_PACKAGES_ERROR = None

    client: httpx.AsyncClient

    @staticmethod
    def _convert_completion_params(params: CompletionParams, **kwargs: Any) -> dict[str, Any]:
        """Convert CompletionParams to kwargs for LiteLLM API."""
        converted_params = params.model_dump(
            exclude_none=True, exclude={"model_id", "messages", "stream"}
        )
        converted_params.update(kwargs)
        return converted_params

    @staticmethod
    def _convert_completion_response(response: dict[str, Any]) -> ChatCompletion:
        """Convert LiteLLM response to OpenAI format ChatCompletion."""
        from any_llm.types.completion import (
            ChatCompletion,
            ChatCompletionMessage,
            Choice,
            CompletionUsage,
        )

        choices = []
        for choice_data in response.get("choices", []):
            message_data = choice_data.get("message", {})
            message = ChatCompletionMessage(
                role=message_data.get("role", "assistant"),
                content=message_data.get("content", ""),
                tool_calls=message_data.get("tool_calls"),
            )
            choice = Choice(
                index=choice_data.get("index", 0),
                message=message,
                finish_reason=choice_data.get("finish_reason"),
            )
            choices.append(choice)

        usage_data = response.get("usage")
        usage = None
        if usage_data:
            usage = CompletionUsage(
                prompt_tokens=usage_data.get("prompt_tokens", 0),
                completion_tokens=usage_data.get("completion_tokens", 0),
                total_tokens=usage_data.get("total_tokens", 0),
            )

        return ChatCompletion(
            id=response.get("id", "litellm-completion"),
            object=response.get("object", "chat.completion"),
            created=response.get("created", 0),
            model=response.get("model", ""),
            choices=choices,
            usage=usage,
        )

    @staticmethod
    def _convert_completion_chunk_response(response: dict[str, Any], **kwargs: Any) -> ChatCompletionChunk:
        """Convert LiteLLM chunk response to OpenAI format ChatCompletionChunk."""
        from any_llm.types.completion import (
            ChatCompletionChunk,
            ChoiceDelta,
            ChunkChoice,
        )

        choices = []
        for choice_data in response.get("choices", []):
            delta_data = choice_data.get("delta", {})
            delta = ChoiceDelta(
                role=delta_data.get("role"),
                content=delta_data.get("content", ""),
                tool_calls=delta_data.get("tool_calls"),
            )
            choice = ChunkChoice(
                index=choice_data.get("index", 0),
                delta=delta,
                finish_reason=choice_data.get("finish_reason"),
            )
            choices.append(choice)

        return ChatCompletionChunk(
            id=response.get("id", "litellm-chunk"),
            object=response.get("object", "chat.completion.chunk"),
            created=response.get("created", 0),
            model=response.get("model", ""),
            choices=choices,
        )

    @staticmethod
    def _convert_embedding_params(params: Any, **kwargs: Any) -> dict[str, Any]:
        """Convert embedding parameters for LiteLLM."""
        converted_params = {"input": params}
        converted_params.update(kwargs)
        return converted_params

    @staticmethod
    def _convert_embedding_response(response: dict[str, Any]) -> CreateEmbeddingResponse:
        """Convert LiteLLM embedding response to OpenAI format."""
        from any_llm.types.completion import (
            CreateEmbeddingResponse,
            Embedding,
            Usage,
        )

        embeddings = []
        for emb_data in response.get("data", []):
            embedding = Embedding(
                object="embedding",
                embedding=emb_data.get("embedding", []),
                index=emb_data.get("index", 0),
            )
            embeddings.append(embedding)

        usage_data = response.get("usage", {})
        usage = Usage(
            prompt_tokens=usage_data.get("prompt_tokens", 0),
            total_tokens=usage_data.get("total_tokens", 0),
        )

        return CreateEmbeddingResponse(
            object="list",
            data=embeddings,
            model=response.get("model", ""),
            usage=usage,
        )

    @staticmethod
    def _convert_list_models_response(response: Any) -> Sequence[Model]:
        """Convert LiteLLM list models response to OpenAI format."""
        # LiteLLM doesn't support list_models by default
        return []

    def _init_client(self, api_key: str | None = None, api_base: str | None = None, **kwargs: Any) -> None:
        """Initialize httpx async client for LiteLLM API."""
        if not api_base:
            raise ValueError("api_base is required for LiteLLM provider")

        headers = {
            "content-type": "application/json",
            "accept-language": "en-US,en",
        }
        
        if api_key:
            headers["authorization"] = f"Bearer {api_key}"

        self.client = httpx.AsyncClient(
            base_url=api_base,
            headers=headers,
            timeout=kwargs.get("timeout", 60.0),
        )

    def _verify_and_set_api_key(self, api_key: str | None = None) -> str | None:
        """Verify and return API key (optional for LiteLLM)."""
        return api_key

    def _convert_messages_to_litellm_format(self, messages: list[dict[str, Any]]) -> list[dict[str, Any]]:
        """Convert messages to LiteLLM format (OpenAI-compatible)."""
        return messages

    async def _stream_completion_async(
        self,
        model: str,
        messages: list[dict[str, Any]],
        **kwargs: Any,
    ) -> AsyncIterator[ChatCompletionChunk]:
        """Handle streaming completion."""
        payload = {
            "model": model,
            "messages": messages,
            "stream": True,
            **kwargs,
        }

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
                            yield self._convert_completion_chunk_response(data)
                        except json.JSONDecodeError:
                            logger.warning(f"Failed to parse streaming data: {data_str}")
                            continue

        except httpx.HTTPStatusError as e:
            logger.error(f"LiteLLM streaming API error: {e.response.status_code} - {e.response.text}")
            raise Exception(f"LiteLLM streaming API error: {e.response.status_code}")
        except Exception as e:
            logger.error(f"Error creating LiteLLM streaming completion: {e}")
            raise

    async def _acompletion(
        self,
        params: CompletionParams,
        **kwargs: Any,
    ) -> ChatCompletion | AsyncIterator[ChatCompletionChunk]:
        """Create a chat completion using LiteLLM."""
        # Handle response_format
        response_format = None
        if params.response_format is not None:
            if isinstance(params.response_format, type) and issubclass(params.response_format, BaseModel):
                response_format = params.response_format.model_json_schema()
            else:
                response_format = params.response_format

        # Convert messages to LiteLLM format
        messages = [
            {
                "role": msg.get("role"),
                "content": msg.get("content", ""),
                **({"tool_call_id": msg["tool_call_id"]} if msg.get("tool_call_id") else {}),
                **({"tool_calls": msg["tool_calls"]} if msg.get("tool_calls") else {}),
            }
            for msg in params.messages
        ]

        completion_kwargs = self._convert_completion_params(params, **kwargs)

        # Add response_format if specified
        if response_format:
            completion_kwargs["response_format"] = response_format

        if params.stream:
            return self._stream_completion_async(params.model_id, messages, **completion_kwargs)

        # Non-streaming completion
        payload = {
            "model": params.model_id,
            "messages": messages,
            "stream": False,
            **completion_kwargs,
        }

        try:
            response = await self.client.post("/chat/completions", json=payload)
            response.raise_for_status()
            data = response.json()
            return self._convert_completion_response(data)

        except httpx.HTTPStatusError as e:
            logger.error(f"LiteLLM API error: {e.response.status_code} - {e.response.text}")
            raise Exception(f"LiteLLM API error: {e.response.status_code}")
        except Exception as e:
            logger.error(f"Error creating LiteLLM completion: {e}")
            raise

    async def _aembedding(
        self,
        model: str,
        inputs: str | list[str],
        **kwargs: Any,
    ) -> CreateEmbeddingResponse:
        """Generate embeddings using LiteLLM."""
        embedding_kwargs = self._convert_embedding_params(inputs, **kwargs)
        
        payload = {
            "model": model,
            **embedding_kwargs,
        }

        try:
            response = await self.client.post("/embeddings", json=payload)
            response.raise_for_status()
            data = response.json()
            return self._convert_embedding_response(data)

        except httpx.HTTPStatusError as e:
            logger.error(f"LiteLLM embedding API error: {e.response.status_code} - {e.response.text}")
            raise Exception(f"LiteLLM embedding API error: {e.response.status_code}")
        except Exception as e:
            logger.error(f"Error creating LiteLLM embedding: {e}")
            raise

    async def _alist_models(self, **kwargs: Any) -> Sequence[Model]:
        """List available models (not supported by LiteLLM by default)."""
        return self._convert_list_models_response([])

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.client.aclose()