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
        assert SyntheticsNewProvider.SUPPORTS_LIST_MODELS is True

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
    async def test_completion_with_hf_prefix(self, provider):
        """Test that completion adds hf: prefix to model if not present."""
        from any_llm.types.completion import CompletionParams

        # Create params with model without hf: prefix
        params = CompletionParams(
            model_id="deepseek-ai/DeepSeek-V3.1",
            messages=[{"role": "user", "content": "Hello"}]
        )

        mock_response_data = {
            "id": "test-id",
            "object": "chat.completion",
            "created": 1234567890,
            "model": "hf:deepseek-ai/DeepSeek-V3.1",
            "choices": [
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": "Hello!"
                    },
                    "finish_reason": "stop"
                }
            ]
        }

        mock_response = MagicMock()
        mock_response.json.return_value = mock_response_data
        mock_response.raise_for_status = MagicMock()

        with patch.object(provider.client, 'post', new_callable=AsyncMock) as mock_post:
            mock_post.return_value = mock_response

            result = await provider._acompletion(params)

            # Verify the API was called with hf: prefix
            call_args = mock_post.call_args[1]["json"]
            assert call_args["model"] == "hf:deepseek-ai/DeepSeek-V3.1"
            assert result.choices[0].message.content == "Hello!"

    @pytest.mark.asyncio
    async def test_completion_preserves_hf_prefix(self, provider):
        """Test that completion preserves existing hf: prefix."""
        from any_llm.types.completion import CompletionParams

        # Create params with model that already has hf: prefix
        params = CompletionParams(
            model_id="hf:deepseek-ai/DeepSeek-V3.1",
            messages=[{"role": "user", "content": "Hello"}]
        )

        mock_response_data = {
            "id": "test-id",
            "object": "chat.completion",
            "created": 1234567890,
            "model": "hf:deepseek-ai/DeepSeek-V3.1",
            "choices": [
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": "Hello!"
                    },
                    "finish_reason": "stop"
                }
            ]
        }

        mock_response = MagicMock()
        mock_response.json.return_value = mock_response_data
        mock_response.raise_for_status = MagicMock()

        with patch.object(provider.client, 'post', new_callable=AsyncMock) as mock_post:
            mock_post.return_value = mock_response

            result = await provider._acompletion(params)

            # Verify the API was called with hf: prefix (not doubled)
            call_args = mock_post.call_args[1]["json"]
            assert call_args["model"] == "hf:deepseek-ai/DeepSeek-V3.1"
            assert not call_args["model"].startswith("hf:hf:")
            assert result.choices[0].message.content == "Hello!"

    @pytest.mark.asyncio
    async def test_completion_excludes_reasoning_effort(self, provider):
        """Test that completion excludes reasoning_effort parameter."""
        from any_llm.types.completion import CompletionParams

        # Create params that would normally include reasoning_effort
        params = CompletionParams(
            model_id="hf:deepseek-ai/DeepSeek-V3.1",
            messages=[{"role": "user", "content": "Hello"}]
        )

        mock_response_data = {
            "id": "test-id",
            "object": "chat.completion",
            "created": 1234567890,
            "model": "hf:deepseek-ai/DeepSeek-V3.1",
            "choices": [
                {
                    "index": 0,
                    "message": {
                        "role": "assistant",
                        "content": "Hello!"
                    },
                    "finish_reason": "stop"
                }
            ]
        }

        mock_response = MagicMock()
        mock_response.json.return_value = mock_response_data
        mock_response.raise_for_status = MagicMock()

        with patch.object(provider.client, 'post', new_callable=AsyncMock) as mock_post:
            mock_post.return_value = mock_response

            await provider._acompletion(params)

            # Verify reasoning_effort is NOT in the payload
            call_args = mock_post.call_args[1]["json"]
            assert "reasoning_effort" not in call_args
            assert call_args["model"] == "hf:deepseek-ai/DeepSeek-V3.1"

    @pytest.mark.asyncio
    async def test_list_models(self, provider):
        """Test listing available models."""
        # Mock the API response
        mock_response_data = {
            "data": [
                {
                    "id": "hf:deepseek-ai/DeepSeek-V3.1",
                    "object": "model"
                },
                {
                    "id": "hf:Qwen/Qwen3-235B-A22B-Instruct-2507",
                    "object": "model"
                },
                {
                    "id": "hf:zai-org/GLM-4.6",
                    "object": "model"
                }
            ]
        }

        mock_response = MagicMock()
        mock_response.json.return_value = mock_response_data
        mock_response.raise_for_status = MagicMock()

        with patch.object(provider.client, 'get', new_callable=AsyncMock) as mock_get:
            mock_get.return_value = mock_response

            models = await provider._alist_models()

            # Verify the result
            assert len(models) == 3
            assert models[0].id == "hf:deepseek-ai/DeepSeek-V3.1"
            assert models[1].id == "hf:Qwen/Qwen3-235B-A22B-Instruct-2507"
            assert models[2].id == "hf:zai-org/GLM-4.6"
            assert all(model.object == "model" for model in models)

            # Verify the API call
            mock_get.assert_called_once_with("/models")
