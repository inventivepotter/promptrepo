"""
Unit tests for LiteLLM provider service.
"""
import pytest
import json
from unittest.mock import AsyncMock, patch, MagicMock
from services.llm.providers.litellm_provider import LiteLLMProvider
from services.llm.models import ChatMessage, ChatCompletionRequest


class TestLiteLLMProvider:
    """Test cases for LiteLLMProvider."""
    
    @pytest.fixture
    def litellm_service(self):
        """Create LiteLLM service instance for testing."""
        return LiteLLMProvider(api_key="test-api-key", api_base="https://api.litellm.com")
    
    def test_init(self):
        """Test LiteLLM service initialization."""
        service = LiteLLMProvider(api_key="test-key", api_base="https://test.com")
        assert service.api_key == "test-key"
        assert service.api_base == "https://test.com"
        assert service.client.headers["authorization"] == "Bearer test-key"
        assert service.client.headers["content-type"] == "application/json"
    
    def test_get_available_models(self, litellm_service):
        """Test getting available models."""
        models = litellm_service.get_available_models()
        # LiteLLM should return empty list to let users specify their own models
        assert models == []
    
    def test_convert_messages_to_litellm_format(self, litellm_service):
        """Test converting messages to LiteLLM format."""
        messages = [
            ChatMessage(role="system", content="You are a helpful assistant."),
            ChatMessage(role="user", content="Hello!")
        ]
        
        result = litellm_service._convert_messages_to_litellm_format(messages)
        expected = [
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": "Hello!"}
        ]
        assert result == expected
    
    def test_convert_usage_stats(self, litellm_service):
        """Test converting usage statistics."""
        litellm_usage = {
            "prompt_tokens": 10,
            "completion_tokens": 20,
            "total_tokens": 30
        }
        
        result = litellm_service._convert_usage_stats(litellm_usage)
        assert result.prompt_tokens == 10
        assert result.completion_tokens == 20
        assert result.total_tokens == 30
    
    def test_convert_usage_stats_none(self, litellm_service):
        """Test converting None usage statistics."""
        result = litellm_service._convert_usage_stats(None)
        assert result is None
    
    @pytest.mark.asyncio
    async def test_create_completion_success(self, litellm_service):
        """Test successful completion creation."""
        # Mock response data
        mock_response_data = {
            "id": "test-id",
            "object": "chat.completion",
            "created": 1234567890,
            "model": "gpt-3.5-turbo",
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
        
        # Create mock request
        request = ChatCompletionRequest(
            provider="litellm",
            model="gpt-3.5-turbo",
            messages=[
                ChatMessage(role="system", content="You are a helpful assistant."),
                ChatMessage(role="user", content="Hello!")
            ],
            prompt_id=None,
            stream=False,
            temperature=0.7,
            max_tokens=None,
            top_p=None,
            frequency_penalty=None,
            presence_penalty=None,
            stop=None
        )
        
        # Mock HTTP client response
        mock_response = MagicMock()
        mock_response.json.return_value = mock_response_data
        mock_response.raise_for_status = MagicMock()
        
        with patch.object(litellm_service.client, 'post', new_callable=AsyncMock) as mock_post:
            mock_post.return_value = mock_response
            
            result = await litellm_service.create_completion(request, stream=False)
            
            # Verify result
            assert result.id == "test-id"
            assert result.model == "gpt-3.5-turbo"
            assert len(result.choices) == 1
            assert result.choices[0].message.content == "Hello! How can I help you?"
            assert result.choices[0].finish_reason == "stop"
            assert result.usage.prompt_tokens == 10
            assert result.usage.completion_tokens == 15
            assert result.usage.total_tokens == 25
            
            # Verify API call
            mock_post.assert_called_once_with(
                "/chat/completions",
                json={
                    "model": "gpt-3.5-turbo",
                    "messages": [
                        {"role": "system", "content": "You are a helpful assistant."},
                        {"role": "user", "content": "Hello!"}
                    ],
                    "stream": False,
                    "temperature": 0.7
                }
            )
    
    @pytest.mark.asyncio
    async def test_create_completion_with_optional_params(self, litellm_service):
        """Test completion creation with optional parameters."""
        request = ChatCompletionRequest(
            provider="litellm",
            model="gpt-3.5-turbo",
            messages=[
                ChatMessage(role="system", content="You are a helpful assistant."),
                ChatMessage(role="user", content="Hello!")
            ],
            prompt_id=None,
            stream=False,
            temperature=0.7,
            max_tokens=100,
            top_p=0.9,
            frequency_penalty=0.1,
            presence_penalty=0.2,
            stop=["\n"]
        )
        
        mock_response_data = {
            "id": "test-id",
            "object": "chat.completion",
            "created": 1234567890,
            "model": "gpt-3.5-turbo",
            "choices": [
                {
                    "index": 0,
                    "message": {"role": "assistant", "content": "Response"},
                    "finish_reason": "stop"
                }
            ]
        }
        
        mock_response = MagicMock()
        mock_response.json.return_value = mock_response_data
        mock_response.raise_for_status = MagicMock()
        
        with patch.object(litellm_service.client, 'post', new_callable=AsyncMock) as mock_post:
            mock_post.return_value = mock_response
            
            await litellm_service.create_completion(request, stream=False)
            
            # Verify all optional parameters are included
            call_args = mock_post.call_args[1]["json"]
            assert call_args["max_tokens"] == 100
            assert call_args["top_p"] == 0.9
            assert call_args["frequency_penalty"] == 0.1
            assert call_args["presence_penalty"] == 0.2
            assert call_args["stop"] == ["\n"]
    
    @pytest.mark.asyncio
    async def test_create_completion_http_error(self, litellm_service):
        """Test completion creation with HTTP error."""
        request = ChatCompletionRequest(
            provider="litellm",
            model="gpt-3.5-turbo",
            messages=[ChatMessage(role="user", content="Hello!")],
            prompt_id=None,
            stream=False,
            temperature=None,
            max_tokens=None,
            top_p=None,
            frequency_penalty=None,
            presence_penalty=None,
            stop=None
        )
        
        # Mock HTTP error
        with patch.object(litellm_service.client, 'post', new_callable=AsyncMock) as mock_post:
            mock_post.return_value.raise_for_status.side_effect = Exception("401 - Unauthorized")
            
            with pytest.raises(Exception) as exc_info:
                await litellm_service.create_completion(request, stream=False)
            
            assert "Error creating LiteLLM completion" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_create_streaming_completion(self, litellm_service):
        """Test streaming completion creation."""
        request = ChatCompletionRequest(
            provider="litellm",
            model="gpt-3.5-turbo",
            messages=[
                ChatMessage(role="system", content="You are a helpful assistant."),
                ChatMessage(role="user", content="Hello!")
            ],
            prompt_id=None,
            stream=False,
            temperature=None,
            max_tokens=None,
            top_p=None,
            frequency_penalty=None,
            presence_penalty=None,
            stop=None
        )
        
        # Mock streaming response
        mock_stream_response = AsyncMock()
        mock_stream_response.raise_for_status = MagicMock()
        
        # Mock streaming lines
        streaming_lines = [
            'data: {"id": "test-id", "object": "chat.completion.chunk", "created": 1234567890, "model": "gpt-3.5-turbo", "choices": [{"index": 0, "delta": {"role": "assistant", "content": "Hello"}, "finish_reason": null}]}',
            'data: {"id": "test-id", "object": "chat.completion.chunk", "created": 1234567890, "model": "gpt-3.5-turbo", "choices": [{"index": 0, "delta": {"role": "assistant", "content": "!"}, "finish_reason": null}]}',
            'data: {"id": "test-id", "object": "chat.completion.chunk", "created": 1234567890, "model": "gpt-3.5-turbo", "choices": [{"index": 0, "delta": {"role": "assistant", "content": ""}, "finish_reason": "stop"}]}',
            'data: [DONE]'
        ]
        
        async def mock_aiter_lines():
            for line in streaming_lines:
                yield line
        
        mock_stream_response.aiter_lines = mock_aiter_lines
        
        with patch.object(litellm_service.client, 'stream') as mock_stream:
            mock_stream.return_value.__aenter__ = AsyncMock(return_value=mock_stream_response)
            mock_stream.return_value.__aexit__ = AsyncMock(return_value=None)
            
            chunks = []
            async for chunk in litellm_service.create_streaming_completion(request):
                chunks.append(chunk)
            
            # Verify chunks are formatted correctly
            assert len(chunks) == 3  # Should not include [DONE]
            assert all(chunk.startswith("data: ") for chunk in chunks)
            assert "Hello" in chunks[0]
            assert "!" in chunks[1]
            assert "stop" in chunks[2]
    
    @pytest.mark.asyncio
    async def test_create_streaming_completion_json_error(self, litellm_service):
        """Test streaming completion with JSON parsing error."""
        request = ChatCompletionRequest(
            provider="litellm",
            model="gpt-3.5-turbo",
            messages=[ChatMessage(role="user", content="Hello!")],
            prompt_id=None,
            stream=False,
            temperature=None,
            max_tokens=None,
            top_p=None,
            frequency_penalty=None,
            presence_penalty=None,
            stop=None
        )
        
        mock_stream_response = AsyncMock()
        mock_stream_response.raise_for_status = MagicMock()
        
        # Mock malformed JSON line
        streaming_lines = [
            'data: {"invalid": json}',
            'data: [DONE]'
        ]
        
        async def mock_aiter_lines():
            for line in streaming_lines:
                yield line
        
        mock_stream_response.aiter_lines = mock_aiter_lines
        
        with patch.object(litellm_service.client, 'stream') as mock_stream:
            mock_stream.return_value.__aenter__ = AsyncMock(return_value=mock_stream_response)
            mock_stream.return_value.__aexit__ = AsyncMock(return_value=None)
            
            chunks = []
            async for chunk in litellm_service.create_streaming_completion(request):
                chunks.append(chunk)
            
            # Should skip malformed JSON and continue
            assert len(chunks) == 0  # No valid chunks
    
    @pytest.mark.asyncio
    async def test_context_manager(self):
        """Test LiteLLM service as context manager."""
        async with LiteLLMProvider(api_key="test-key", api_base="https://test.com") as service:
            assert service.api_key == "test-key"
            assert service.api_base == "https://test.com"
            assert service.client is not None
        
        # Client should be closed after context exit
        # Note: We can't easily test if client is closed without more complex mocking