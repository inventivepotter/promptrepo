"""
Unit tests for chat completion service

Tests the ChatCompletionService functionality including streaming and non-streaming
chat completions, validation, and error handling.
"""

import pytest
from unittest.mock import Mock, patch, MagicMock

from services.llm.completion_service import ChatCompletionService
from services.llm.models import (
    ChatCompletionRequest,
    ChatMessage,
    UsageStats
)
from services.config.models import LLMConfig
from middlewares.rest.exceptions import (
    BadRequestException,
    ServiceUnavailableException
)
from fastapi import HTTPException


class TestChatCompletionService:
    """Test the ChatCompletionService class"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.mock_config_service = Mock()
        self.service = ChatCompletionService(config_service=self.mock_config_service)
    
    def test_init(self):
        """Test ChatCompletionService initialization"""
        mock_config = Mock()
        service = ChatCompletionService(config_service=mock_config)
        assert hasattr(service, 'logger')
        assert hasattr(service, 'config_service')
        assert service.config_service == mock_config
    
    def test_build_completion_params_basic(self):
        """Test build_completion_params with basic parameters"""
        request = ChatCompletionRequest(
            provider="openai",
            model="gpt-4",
            messages=[
                ChatMessage(role="system", content="You are a helpful assistant"),
                ChatMessage(role="user", content="Hello")
            ],
            prompt_id=None,
            repo_name=None,
            tools=None,
            stream=False,
            temperature=None,
            max_tokens=None,
            top_p=None,
            frequency_penalty=None,
            presence_penalty=None,
            stop=None
        )
        
        result = self.service.build_completion_params(
            request, "test-api-key", None, stream=False
        )
        
        expected = {
            "model": "openai/gpt-4",
            "messages": [
                {"role": "system", "content": "You are a helpful assistant"},
                {"role": "user", "content": "Hello"}
            ],
            "api_key": "test-api-key"
        }
        assert result == expected
    
    def test_build_completion_params_with_stream(self):
        """Test build_completion_params with streaming enabled"""
        request = ChatCompletionRequest(
            provider="anthropic",
            model="claude-3",
            messages=[ChatMessage(role="system", content="Test")],
            prompt_id=None,
            repo_name=None,
            tools=None,
            stream=False,
            temperature=None,
            max_tokens=None,
            top_p=None,
            frequency_penalty=None,
            presence_penalty=None,
            stop=None
        )
        
        result = self.service.build_completion_params(
            request, "test-key", "https://api.test.com", stream=True
        )
        
        assert result["stream"] is True
        assert result["api_base"] == "https://api.test.com"
        assert result["model"] == "anthropic/claude-3"
    
    def test_build_completion_params_with_optional_params(self):
        """Test build_completion_params with all optional parameters"""
        request = ChatCompletionRequest(
            provider="openai",
            model="gpt-4",
            messages=[ChatMessage(role="system", content="Test")],
            prompt_id=None,
            repo_name=None,
            tools=None,
            stream=False,
            temperature=0.7,
            max_tokens=150,
            top_p=0.9,
            frequency_penalty=0.1,
            presence_penalty=0.2,
            stop=["END"]
        )
        
        result = self.service.build_completion_params(
            request, "test-key", None, stream=False
        )
        
        assert result["temperature"] == 0.7
        assert result["max_tokens"] == 150
        assert result["top_p"] == 0.9
        assert result["frequency_penalty"] == 0.1
        assert result["presence_penalty"] == 0.2
        assert result["stop"] == ["END"]
    
    def test_get_api_details_success(self):
        """Test _get_api_details with valid configuration"""
        llm_config = LLMConfig(
            id="test-config-1",
            provider="openai",
            model="gpt-4",
            api_key="test-api-key",
            api_base_url="https://api.test.com"
        )
        self.mock_config_service.get_llm_configs.return_value = [llm_config]
        
        api_key, api_base_url = self.service._get_api_details("openai", "gpt-4", "user123")
        
        assert api_key == "test-api-key"
        assert api_base_url == "https://api.test.com"
        self.mock_config_service.get_llm_configs.assert_called_once_with(user_id="user123")
    
    def test_get_api_details_no_base_url(self):
        """Test _get_api_details with no base URL configured"""
        llm_config = LLMConfig(
            id="test-config-2",
            provider="openai",
            model="gpt-4",
            api_key="test-api-key",
            api_base_url=""
        )
        self.mock_config_service.get_llm_configs.return_value = [llm_config]
        
        api_key, api_base_url = self.service._get_api_details("openai", "gpt-4", "user123")
        
        assert api_key == "test-api-key"
        assert api_base_url is None
    
    def test_get_api_details_no_matching_config(self):
        """Test _get_api_details when no matching configuration is found"""
        other_config = LLMConfig(
            id="test-config-3",
            provider="anthropic",
            model="claude-3",
            api_key="other-key"
        )
        self.mock_config_service.get_llm_configs.return_value = [other_config]
        
        with pytest.raises(HTTPException) as exc_info:
            self.service._get_api_details("openai", "gpt-4", "user123")
        
        assert exc_info.value.status_code == 400
        assert "No configuration found" in str(exc_info.value.detail)
    
    def test_get_api_details_no_configs(self):
        """Test _get_api_details when no configurations exist"""
        self.mock_config_service.get_llm_configs.return_value = []
        
        with pytest.raises(HTTPException):
            self.service._get_api_details("openai", "gpt-4", "user123")
    
    def test_validate_system_message_success(self):
        """Test _validate_system_message with valid system message"""
        messages = [
            ChatMessage(role="system", content="You are a helpful assistant"),
            ChatMessage(role="user", content="Hello")
        ]
        
        # Should not raise any exception
        self.service._validate_system_message(messages)
    
    def test_validate_system_message_empty_messages(self):
        """Test _validate_system_message with empty messages"""
        with pytest.raises(BadRequestException, match="Messages array cannot be empty"):
            self.service._validate_system_message([])
    
    def test_validate_system_message_no_system_role(self):
        """Test _validate_system_message when first message is not system"""
        messages = [ChatMessage(role="user", content="Hello")]
        
        with pytest.raises(BadRequestException, match="First message must be a system message"):
            self.service._validate_system_message(messages)
    
    def test_validate_system_message_empty_content(self):
        """Test _validate_system_message with empty system content"""
        messages = [ChatMessage(role="system", content="   ")]
        
        with pytest.raises(BadRequestException, match="System message content cannot be empty"):
            self.service._validate_system_message(messages)
    
    def test_validate_provider_and_model_success(self):
        """Test validate_provider_and_model with valid inputs"""
        # Should not raise any exception
        self.service.validate_provider_and_model("openai", "gpt-4")
    
    def test_validate_provider_and_model_empty_provider(self):
        """Test validate_provider_and_model with empty provider"""
        with pytest.raises(BadRequestException, match="Provider field is required"):
            self.service.validate_provider_and_model("", "gpt-4")
        
        with pytest.raises(BadRequestException, match="Provider field is required"):
            self.service.validate_provider_and_model("   ", "gpt-4")
    
    def test_validate_provider_and_model_empty_model(self):
        """Test validate_provider_and_model with empty model"""
        with pytest.raises(BadRequestException, match="Model field is required"):
            self.service.validate_provider_and_model("openai", "")
        
        with pytest.raises(BadRequestException, match="Model field is required"):
            self.service.validate_provider_and_model("openai", "   ")
    
    def test_convert_to_any_llm_messages_basic(self):
        """Test _convert_to_any_llm_messages with basic messages"""
        messages = [
            ChatMessage(role="system", content="You are helpful"),
            ChatMessage(role="user", content="Hello")
        ]
        
        result = self.service._convert_to_any_llm_messages(messages)
        
        expected = [
            {"role": "system", "content": "You are helpful"},
            {"role": "user", "content": "Hello"}
        ]
        assert result == expected
    
    def test_convert_to_any_llm_messages_with_tool_calls(self):
        """Test _convert_to_any_llm_messages with tool calls"""
        # Create proper tool_calls as dicts (what ChatMessage expects)
        messages = [
            ChatMessage(
                role="assistant",
                content="I'll help you",
                tool_calls=[{"function": "get_weather", "id": "call_1"}]
            ),
            ChatMessage(
                role="tool",
                content="Weather data",
                tool_call_id="call_123"
            )
        ]
        
        result = self.service._convert_to_any_llm_messages(messages)
        
        expected = [
            {
                "role": "assistant",
                "content": "I'll help you",
                "tool_calls": [{"function": "get_weather", "id": "call_1"}]
            },
            {
                "role": "tool",
                "content": "Weather data",
                "tool_call_id": "call_123"
            }
        ]
        assert result == expected
    
    def test_process_usage_stats_complete(self):
        """Test process_usage_stats with complete usage data"""
        # Mock usage data
        mock_usage = Mock()
        mock_usage.prompt_tokens = 10
        mock_usage.completion_tokens = 20
        mock_usage.total_tokens = 30
        
        # Mock prompt tokens details
        mock_prompt_details = Mock()
        mock_prompt_details.audio_tokens = 1
        mock_prompt_details.cached_tokens = 2
        mock_usage.prompt_tokens_details = mock_prompt_details
        
        # Mock completion tokens details
        mock_completion_details = Mock()
        mock_completion_details.accepted_prediction_tokens = 3
        mock_completion_details.audio_tokens = 4
        mock_completion_details.reasoning_tokens = 5
        mock_completion_details.rejected_prediction_tokens = 6
        mock_usage.completion_tokens_details = mock_completion_details
        
        result = self.service.process_usage_stats(mock_usage)
        
        assert isinstance(result, UsageStats)
        assert result.prompt_tokens == 10
        assert result.completion_tokens == 20
        assert result.total_tokens == 30
        assert result.prompt_tokens_details is not None
        assert result.prompt_tokens_details.audio_tokens == 1
        assert result.prompt_tokens_details.cached_tokens == 2
        assert result.completion_tokens_details is not None
        assert result.completion_tokens_details.accepted_prediction_tokens == 3
        assert result.completion_tokens_details.audio_tokens == 4
        assert result.completion_tokens_details.reasoning_tokens == 5
        assert result.completion_tokens_details.rejected_prediction_tokens == 6
    
    def test_process_usage_stats_minimal(self):
        """Test process_usage_stats with minimal usage data"""
        mock_usage = Mock()
        mock_usage.prompt_tokens = 10
        mock_usage.completion_tokens = 20
        mock_usage.total_tokens = 30
        mock_usage.prompt_tokens_details = None
        mock_usage.completion_tokens_details = None
        
        result = self.service.process_usage_stats(mock_usage)
        
        assert isinstance(result, UsageStats)
        assert result.prompt_tokens == 10
        assert result.completion_tokens == 20
        assert result.total_tokens == 30
        assert result.prompt_tokens_details is None
        assert result.completion_tokens_details is None
    
    def test_process_usage_stats_none(self):
        """Test process_usage_stats with None input"""
        result = self.service.process_usage_stats(None)
        assert result is None
    
    def test_process_usage_stats_exception(self):
        """Test process_usage_stats when exception occurs"""
        mock_usage = Mock()
        mock_usage.prompt_tokens = 10
        # Simulate exception during attribute access
        type(mock_usage).completion_tokens = Mock(side_effect=Exception("Test error"))
        
        result = self.service.process_usage_stats(mock_usage)
        assert result is None
    
    @pytest.mark.asyncio
    async def test_process_streaming_chunk_with_choices(self):
        """Test _process_streaming_chunk with choices format"""
        # Mock chunk with choices
        mock_choice = Mock()
        mock_choice.delta = Mock()
        mock_choice.delta.content = "Hello world"
        mock_choice.finish_reason = None
        
        mock_chunk = Mock()
        mock_chunk.choices = [mock_choice]
        
        result = await self.service._process_streaming_chunk(
            mock_chunk, "completion_123", "gpt-4"
        )
        
        assert "data: " in result
        assert "Hello world" in result
        assert "completion_123" in result
        assert "gpt-4" in result
    
    @pytest.mark.asyncio
    async def test_process_streaming_chunk_with_content(self):
        """Test _process_streaming_chunk with direct content format"""
        mock_chunk = Mock()
        mock_chunk.content = "Direct content"
        # No choices attribute
        del mock_chunk.choices
        
        result = await self.service._process_streaming_chunk(
            mock_chunk, "completion_456", "claude-3"
        )
        
        assert "data: " in result
        assert "Direct content" in result
    
    @pytest.mark.asyncio
    async def test_process_streaming_chunk_malformed(self):
        """Test _process_streaming_chunk with malformed chunk"""
        mock_chunk = Mock()
        # Simulate attribute error
        type(mock_chunk).choices = Mock(side_effect=AttributeError("No choices"))
        
        result = await self.service._process_streaming_chunk(
            mock_chunk, "completion_789", "gpt-4"
        )
        
        assert result == ""
    
    @pytest.mark.asyncio
    async def test_process_streaming_chunk_exception(self):
        """Test _process_streaming_chunk when exception occurs"""
        mock_chunk = Mock()
        # Simulate general exception
        type(mock_chunk).choices = Mock(side_effect=Exception("Processing error"))
        
        result = await self.service._process_streaming_chunk(
            mock_chunk, "completion_error", "gpt-4"
        )
        
        assert result == ""
    
    @patch('services.llm.completion_service.acompletion')
    @pytest.mark.asyncio
    async def test_execute_non_streaming_completion_success(self, mock_acompletion):
        """Test execute_non_streaming_completion with successful response"""
        # Setup mocks
        llm_config = LLMConfig(id="test-config-4", provider="openai", model="gpt-4", api_key="test-key")
        self.mock_config_service.get_llm_configs.return_value = [llm_config]
        
        # Mock successful response
        mock_choice = Mock()
        mock_choice.message = Mock()
        mock_choice.message.content = "Hello! How can I help you?"
        mock_choice.message.tool_calls = None  # No tool calls
        mock_choice.finish_reason = "stop"
        
        mock_usage = Mock()
        mock_usage.prompt_tokens = 10
        mock_usage.completion_tokens = 8
        mock_usage.total_tokens = 18
        mock_usage.prompt_tokens_details = None
        mock_usage.completion_tokens_details = None
        
        mock_response = Mock()
        mock_response.choices = [mock_choice]
        mock_response.usage = mock_usage
        
        mock_acompletion.return_value = mock_response
        
        # Create request
        request = ChatCompletionRequest(
            provider="openai",
            model="gpt-4",
            messages=[
                ChatMessage(role="system", content="You are helpful"),
                ChatMessage(role="user", content="Hello")
            ],
            prompt_id=None,
            repo_name=None,
            tools=None,
            stream=False,
            temperature=None,
            max_tokens=None,
            top_p=None,
            frequency_penalty=None,
            presence_penalty=None,
            stop=None
        )
        
        # Execute
        content, finish_reason, usage_stats, inference_time, tool_calls = await self.service.execute_non_streaming_completion(
            request, "user123"
        )
        
        # Verify
        assert content == "Hello! How can I help you?"
        assert finish_reason == "stop"
        assert isinstance(usage_stats, UsageStats)
        assert usage_stats.total_tokens == 18
        assert inference_time > 0
        
        # Verify any-llm was called correctly
        mock_acompletion.assert_called_once()
        call_args = mock_acompletion.call_args[1]
        assert call_args["model"] == "openai/gpt-4"
        assert call_args["api_key"] == "test-key"
    
    @patch('services.llm.completion_service.acompletion')
    @pytest.mark.asyncio
    async def test_execute_non_streaming_completion_no_content(self, mock_acompletion):
        """Test execute_non_streaming_completion when no content is returned"""
        # Setup mocks
        llm_config = LLMConfig(id="test-config-5", provider="openai", model="gpt-4", api_key="test-key")
        self.mock_config_service.get_llm_configs.return_value = [llm_config]
        
        # Mock response with no content
        mock_response = Mock()
        mock_response.choices = []
        mock_acompletion.return_value = mock_response
        
        request = ChatCompletionRequest(
            provider="openai",
            model="gpt-4",
            messages=[ChatMessage(role="system", content="You are helpful")],
            prompt_id=None,
            repo_name=None,
            tools=None,
            stream=False,
            temperature=None,
            max_tokens=None,
            top_p=None,
            frequency_penalty=None,
            presence_penalty=None,
            stop=None
        )
        
        with pytest.raises(ServiceUnavailableException) as exc_info:
            await self.service.execute_non_streaming_completion(request, "user123")
        
        assert "Completion error" in str(exc_info.value)
        assert "Unexpected response format from completion API" in str(exc_info.value)
    
    @patch('services.llm.completion_service.acompletion')
    @pytest.mark.asyncio
    async def test_stream_completion_success(self, mock_acompletion):
        """Test stream_completion with successful streaming"""
        # Setup mocks
        llm_config = LLMConfig(id="test-config-6", provider="openai", model="gpt-4", api_key="test-key")
        self.mock_config_service.get_llm_configs.return_value = [llm_config]
        
        # Mock streaming chunks
        mock_chunk1 = Mock()
        mock_choice1 = Mock()
        mock_choice1.delta = Mock()
        mock_choice1.delta.content = "Hello"
        mock_choice1.finish_reason = None
        mock_chunk1.choices = [mock_choice1]
        
        mock_chunk2 = Mock()
        mock_choice2 = Mock()
        mock_choice2.delta = Mock()
        mock_choice2.delta.content = " world"
        mock_choice2.finish_reason = "stop"
        mock_chunk2.choices = [mock_choice2]
        
        async def mock_stream():
            yield mock_chunk1
            yield mock_chunk2
        
        mock_acompletion.return_value = mock_stream()
        
        request = ChatCompletionRequest(
            provider="openai",
            model="gpt-4",
            messages=[
                ChatMessage(role="system", content="You are helpful"),
                ChatMessage(role="user", content="Hello")
            ],
            prompt_id=None,
            repo_name=None,
            tools=None,
            stream=False,
            temperature=None,
            max_tokens=None,
            top_p=None,
            frequency_penalty=None,
            presence_penalty=None,
            stop=None
        )
        
        # Collect streamed responses
        responses = []
        async for chunk in self.service.stream_completion(request, "user123", "completion_123"):
            responses.append(chunk)
        
        # Verify
        assert len(responses) == 2
        assert "Hello" in responses[0]
        assert " world" in responses[1]
        assert "completion_123" in responses[0]
        
        # Verify any-llm was called with streaming
        mock_acompletion.assert_called_once()
        call_args = mock_acompletion.call_args[1]
        assert call_args["stream"] is True
    
    @patch('services.llm.completion_service.acompletion')
    @pytest.mark.asyncio
    async def test_stream_completion_exception(self, mock_acompletion):
        """Test stream_completion when any-llm raises exception"""
        # Setup mocks
        llm_config = LLMConfig(id="test-config-7", provider="openai", model="gpt-4", api_key="test-key")
        self.mock_config_service.get_llm_configs.return_value = [llm_config]
        
        mock_acompletion.side_effect = Exception("API error")
        
        request = ChatCompletionRequest(
            provider="openai",
            model="gpt-4",
            messages=[ChatMessage(role="system", content="You are helpful")],
            prompt_id=None,
            repo_name=None,
            tools=None,
            stream=False,
            temperature=None,
            max_tokens=None,
            top_p=None,
            frequency_penalty=None,
            presence_penalty=None,
            stop=None
        )
        
        with pytest.raises(ServiceUnavailableException) as exc_info:
            async for _ in self.service.stream_completion(request, "user123", "completion_123"):
                pass
        
        assert "Completion error" in str(exc_info.value)
    
    @pytest.mark.asyncio
    async def test_stream_completion_invalid_system_message(self):
        """Test stream_completion with invalid system message"""
        request = ChatCompletionRequest(
            provider="openai",
            model="gpt-4",
            messages=[ChatMessage(role="user", content="Hello")],  # No system message
            prompt_id=None,
            repo_name=None,
            tools=None,
            stream=False,
            temperature=None,
            max_tokens=None,
            top_p=None,
            frequency_penalty=None,
            presence_penalty=None,
            stop=None
        )
        
        with pytest.raises(BadRequestException):
            async for _ in self.service.stream_completion(request, "user123", "completion_123"):
                pass
    
    @pytest.mark.asyncio
    async def test_execute_non_streaming_completion_invalid_system_message(self):
        """Test execute_non_streaming_completion with invalid system message"""
        request = ChatCompletionRequest(
            provider="openai",
            model="gpt-4",
            messages=[],  # Empty messages
            prompt_id=None,
            repo_name=None,
            tools=None,
            stream=False,
            temperature=None,
            max_tokens=None,
            top_p=None,
            frequency_penalty=None,
            presence_penalty=None,
            stop=None
        )
        
        with pytest.raises(BadRequestException):
            await self.service.execute_non_streaming_completion(request, "user123")