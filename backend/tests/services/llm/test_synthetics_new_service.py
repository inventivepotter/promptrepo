"""
Unit tests for Synthetics.New provider service.
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch

from lib.any_llm.synthetics_new_provider import SyntheticsNewProvider


class TestSyntheticsNewProvider:
    """Test cases for SyntheticsNewProvider."""

    @pytest.fixture
    def provider(self):
        """Create Synthetics.New provider instance for testing."""
        return SyntheticsNewProvider(
            api_key="test-api-key",
            api_base="https://api.synthetic.new/openai/v1"
        )

    def test_init(self):
        """Test Synthetics.New provider initialization."""
        provider = SyntheticsNewProvider(
            api_key="test-key",
            api_base="https://api.synthetic.new/openai/v1"
        )
        assert provider.client is not None
        assert provider.client.headers["authorization"] == "Bearer test-key"
        assert provider.client.headers["content-type"] == "application/json"
        assert str(provider.client.base_url) == "https://api.synthetic.new/openai/v1/"

    def test_provider_metadata(self):
        """Test provider metadata constants."""
        assert SyntheticsNewProvider.PROVIDER_NAME == "syntheticsNew"
        assert SyntheticsNewProvider.ENV_API_KEY_NAME == "SYNTHETICS_NEW_API_KEY"
        assert SyntheticsNewProvider.SUPPORTS_COMPLETION is True
        assert SyntheticsNewProvider.SUPPORTS_COMPLETION_STREAMING is True
        assert SyntheticsNewProvider.SUPPORTS_EMBEDDING is False

    def test_init_without_api_key(self):
        """Test initialization without API key raises error."""
        with pytest.raises(ValueError, match="API key is required"):
            SyntheticsNewProvider()

    def test_convert_completion_response(self, provider):
        """Test converting response to ChatCompletion format."""
        response = {
            "id": "test-id",
            "object": "chat.completion",
            "created": 1234567890,
            "model": "gpt-4",
            "choices": [
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": "Hello! How can I help you?"
                    },
                    "finish_reason": "stop"
                }
            ],
            "usage": {
                "prompt_tokens": 10,
                "completion_tokens": 15,
                "total_tokens": 25
            }
        }

        result = provider._convert_completion_response(response)

        assert result.id == "test-id"
        assert result.model == "gpt-4"
        assert len(result.choices) == 1
        assert result.choices[0].message.content == "Hello! How can I help you?"
        assert result.choices[0].finish_reason == "stop"
        assert result.usage.prompt_tokens == 10
        assert result.usage.completion_tokens == 15
        assert result.usage.total_tokens == 25

    def test_convert_completion_chunk_response(self, provider):
        """Test converting chunk response to ChatCompletionChunk format."""
        response = {
            "id": "test-id",
            "object": "chat.completion.chunk",
            "created": 1234567890,
            "model": "gpt-4",
            "choices": [
                {
                    "index": 0,
                    "delta": {
                        "role": "assistant",
                        "content": "Hello"
                    },
                    "finish_reason": None
                }
            ]
        }

        result = provider._convert_completion_chunk_response(response)

        assert result.id == "test-id"
        assert result.model == "gpt-4"
        assert len(result.choices) == 1
        assert result.choices[0].delta.content == "Hello"
        assert result.choices[0].finish_reason is None

    @pytest.mark.asyncio
    async def test_context_manager(self):
        """Test Synthetics.New provider as async context manager."""
        async with SyntheticsNewProvider(api_key="test-key") as provider:
            assert provider.client is not None
            assert provider.client.headers["authorization"] == "Bearer test-key"

    def test_embedding_not_supported(self, provider):
        """Test that embedding operations raise NotImplementedError."""
        with pytest.raises(NotImplementedError, match="does not support embeddings"):
            provider._convert_embedding_params({})

        with pytest.raises(NotImplementedError, match="does not support embeddings"):
            provider._convert_embedding_response({})

    @pytest.mark.asyncio
    async def test_list_models(self, provider):
        """Test listing available models."""
        models = await provider._alist_models()

        assert len(models) > 0
        assert any(model.id == "gpt-4" for model in models)
        assert all(model.owned_by == "synthetics-new" for model in models)
