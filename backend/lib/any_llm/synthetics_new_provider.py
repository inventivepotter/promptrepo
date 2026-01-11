"""
Synthetics.New provider implementation following AnyLLM standard pattern.
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


class SyntheticsNewProvider(AnyLLM):
    """
    Synthetics.New Provider following AnyLLM standard pattern.

    Uses httpx client to communicate with Synthetics.New API server.
    Read more here - https://synthetic.new/
    """

    PROVIDER_NAME = "syntheticsNew"
    PROVIDER_DOCUMENTATION_URL = "https://synthetic.new/"
    ENV_API_KEY_NAME = "SYNTHETICS_NEW_API_KEY"

    SUPPORTS_COMPLETION_STREAMING = True
    SUPPORTS_COMPLETION = True
    SUPPORTS_RESPONSES = False
    SUPPORTS_COMPLETION_REASONING = False
    SUPPORTS_COMPLETION_IMAGE = False
    SUPPORTS_COMPLETION_PDF = False
    SUPPORTS_EMBEDDING = False
    SUPPORTS_LIST_MODELS = True

    MISSING_PACKAGES_ERROR = None

    client: httpx.AsyncClient

    @staticmethod
    def _convert_completion_params(params: CompletionParams, **kwargs: Any) -> dict[str, Any]:
        """Convert CompletionParams to kwargs for Synthetics.New API."""
        # Exclude reasoning_effort as Synthetics.New doesn't support it
        converted_params = params.model_dump(
            exclude_none=True, exclude={"model_id", "messages", "stream", "reasoning_effort"}
        )
        converted_params.update(kwargs)
        return converted_params

    @staticmethod
    def _convert_completion_response(response: dict[str, Any]) -> ChatCompletion:
        """Convert Synthetics.New response to OpenAI format ChatCompletion."""
        from any_llm.types.completion import (
            ChatCompletion,
            ChatCompletionMessage,
            Choice,
            CompletionUsage,
        )

        choices = []
        for choice_data in response.get("choices", []):
            message_data = choice_data.get("message", {})

            # Handle None content - use reasoning_content as fallback or empty string
            content = message_data.get("content")
            if content is None:
                # Check if model hit token limit with reasoning but no content
                reasoning_content = message_data.get("reasoning_content")
                finish_reason = choice_data.get("finish_reason")

                if finish_reason == "length" and reasoning_content:
                    # Model ran out of tokens during reasoning - log warning
                    logger.warning(
                        f"Model hit token limit during reasoning without producing content. "
                        f"Consider increasing max_tokens. Reasoning preview: {reasoning_content[:100]}..."
                    )
                    content = ""
                else:
                    content = ""

            message = ChatCompletionMessage(
                role=message_data.get("role", "assistant"),
                content=content,
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
            id=response.get("id", "synthetics-new-completion"),
            object=response.get("object", "chat.completion"),
            created=response.get("created", 0),
            model=response.get("model", ""),
            choices=choices,
            usage=usage,
        )

    @staticmethod
    def _convert_completion_chunk_response(response: dict[str, Any], **kwargs: Any) -> ChatCompletionChunk:
        """Convert Synthetics.New chunk response to OpenAI format ChatCompletionChunk."""
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
            id=response.get("id", "synthetics-new-chunk"),
            object=response.get("object", "chat.completion.chunk"),
            created=response.get("created", 0),
            model=response.get("model", ""),
            choices=choices,
        )

    @staticmethod
    def _convert_embedding_params(params: Any, **kwargs: Any) -> dict[str, Any]:
        """Convert embedding parameters for Synthetics.New (not supported)."""
        raise NotImplementedError("Synthetics.New does not support embeddings")

    @staticmethod
    def _convert_embedding_response(response: dict[str, Any]) -> CreateEmbeddingResponse:
        """Convert Synthetics.New embedding response to OpenAI format (not supported)."""
        raise NotImplementedError("Synthetics.New does not support embeddings")

    @staticmethod
    def _convert_list_models_response(response: dict[str, Any]) -> Sequence[Model]:
        """Convert Synthetics.New list models response to OpenAI format."""
        from any_llm.types.model import Model

        # Parse the actual API response
        models = []
        for model_data in response.get("data", []):
            models.append(
                Model(
                    id=model_data.get("id", ""),
                    object=model_data.get("object", "model"),
                    created=model_data.get("created", 0),
                    owned_by=model_data.get("owned_by", "synthetics-new")
                )
            )
        return models

    def _init_client(self, api_key: str | None = None, api_base: str | None = None, **kwargs: Any) -> None:
        """Initialize httpx async client for Synthetics.New API."""
        if not api_base:
            api_base = "https://api.synthetic.new/openai/v1"

        headers = {
            "content-type": "application/json",
        }

        if api_key:
            headers["authorization"] = f"Bearer {api_key}"

        self.client = httpx.AsyncClient(
            base_url=api_base,
            headers=headers,
            timeout=kwargs.get("timeout", 60.0),
        )

    def _verify_and_set_api_key(self, api_key: str | None = None) -> str | None:
        """Verify and return API key."""
        if not api_key:
            raise ValueError("API key is required for Synthetics.New provider")
        return api_key

    async def _stream_completion_async(
        self,
        model: str,
        messages: list[dict[str, Any]],
        **kwargs: Any,
    ) -> AsyncIterator[ChatCompletionChunk]:
        """Handle streaming completion."""
        # Ensure model has hf: prefix (required by Synthetics.New API)
        if not model.startswith("hf:"):
            model = f"hf:{model}"
            logger.info(f"Added hf: prefix to streaming model: {model}")

        payload = {
            "model": model,
            "messages": messages,
            "stream": True,
            **kwargs,
        }

        try:
            logger.info(f"Synthetics.New streaming request payload: {payload}")
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
            error_detail = e.response.text
            logger.error(f"Synthetics.New streaming API error: {e.response.status_code} - {error_detail}")
            logger.error(f"Request payload was: {payload}")
            raise Exception(f"Synthetics.New streaming API error: {e.response.status_code} - {error_detail}")
        except Exception as e:
            logger.error(f"Error creating Synthetics.New streaming completion: {e}")
            raise

    async def _acompletion(
        self,
        params: CompletionParams,
        **kwargs: Any,
    ) -> ChatCompletion | AsyncIterator[ChatCompletionChunk]:
        """Create a chat completion using Synthetics.New."""
        # Ensure model has hf: prefix (required by Synthetics.New API)
        model_id = params.model_id
        if not model_id.startswith("hf:"):
            model_id = f"hf:{model_id}"
            logger.info(f"Added hf: prefix to model: {params.model_id} -> {model_id}")

        # Handle response_format
        response_format = None
        if params.response_format is not None:
            if isinstance(params.response_format, type) and issubclass(params.response_format, BaseModel):
                response_format = params.response_format.model_json_schema()
            else:
                response_format = params.response_format

        # Convert messages to Synthetics.New format (OpenAI-compatible)
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
            return self._stream_completion_async(model_id, messages, **completion_kwargs)

        # Non-streaming completion
        payload = {
            "model": model_id,
            "messages": messages,
            "stream": False,
            **completion_kwargs,
        }

        try:
            logger.info(f"Synthetics.New request payload: {payload}")
            response = await self.client.post("/chat/completions", json=payload)
            response.raise_for_status()
            data = response.json()

            # Log the raw response for debugging
            logger.info(f"Synthetics.New raw response: {data}")

            return self._convert_completion_response(data)

        except httpx.HTTPStatusError as e:
            error_detail = e.response.text
            logger.error(f"Synthetics.New API error: {e.response.status_code} - {error_detail}")
            logger.error(f"Request payload was: {payload}")
            raise Exception(f"Synthetics.New API error: {e.response.status_code} - {error_detail}")
        except Exception as e:
            logger.error(f"Error creating Synthetics.New completion: {e}")
            raise

    async def _aembedding(
        self,
        model: str,
        inputs: str | list[str],
        **kwargs: Any,
    ) -> CreateEmbeddingResponse:
        """Generate embeddings using Synthetics.New (not supported)."""
        raise NotImplementedError("Synthetics.New does not support embeddings")

    async def _alist_models(self, **kwargs: Any) -> Sequence[Model]:
        """List available models from Synthetics.New API."""
        try:
            response = await self.client.get("/models")
            response.raise_for_status()
            data = response.json()

            logger.info(f"Synthetics.New models response: {data}")

            return self._convert_list_models_response(data)
        except httpx.HTTPStatusError as e:
            logger.error(f"Synthetics.New API error fetching models: {e.response.status_code} - {e.response.text}")
            raise Exception(f"Synthetics.New API error: {e.response.status_code}")
        except Exception as e:
            logger.error(f"Error fetching Synthetics.New models: {e}")
            raise

    async def __aenter__(self):
        """Async context manager entry."""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit."""
        await self.client.aclose()
