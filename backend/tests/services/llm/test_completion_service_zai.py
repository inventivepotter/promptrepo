"""
Test cases for ChatCompletionService using ZAI provider.
Tests the unified AnyLLM interface for ZAI provider - focusing on completion and list models.
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from services.llm.chat_completion_service import ChatCompletionService
from services.llm.model_provider_service import ModelProviderService
from services.llm.models import ChatCompletionRequest, ChatMessage
from services.config.config_service import ConfigService
from services.config.models import LLMConfig


@pytest.fixture
def mock_config_service():
    """Create a mock ConfigService with ZAI configuration."""
    config_service = MagicMock(spec=ConfigService)
    
    # Mock LLM configs with ZAI provider
    llm_config = LLMConfig(
        id="test-llm-config-1",
        provider="zai",
        model="glm-4.6",
        api_key="test-zai-api-key",
        api_base_url="https://api.z.ai/api/coding/paas/v4"
    )
    
    config_service.get_llm_configs.return_value = [llm_config]
    return config_service


@pytest.fixture
def completion_service(mock_config_service):
    """Create ChatCompletionService instance with mocked config."""
    return ChatCompletionService(config_service=mock_config_service)


@pytest.fixture
def llm_provider_service(mock_config_service):
    """Create LLMProviderService instance with mocked config."""
    return ModelProviderService(config_service=mock_config_service)


@pytest.mark.asyncio
async def test_zai_non_streaming_completion(completion_service):
    """Test non-streaming completion with ZAI provider using unified AnyLLM interface."""
    # Prepare test request
    request = ChatCompletionRequest(
        provider="zai",
        model="glm-4.6",
        messages=[
            ChatMessage(role="system", content="You are a helpful assistant."),
            ChatMessage(role="user", content="Hello, how are you?")
        ],
        temperature=0.7,
        max_tokens=100,
        prompt_id=None,
        repo_name=None,
        stream=False,
        top_p=None,
        frequency_penalty=None,
        presence_penalty=None,
        stop=None,
        tools=None
    )
    
    # Mock the acompletion function from any_llm
    mock_response = MagicMock()
    mock_response.choices = [MagicMock()]
    mock_response.choices[0].message.content = "I'm doing great! How can I help you today?"
    mock_response.choices[0].message.tool_calls = None
    mock_response.choices[0].finish_reason = "stop"
    mock_response.usage = MagicMock()
    mock_response.usage.prompt_tokens = 20
    mock_response.usage.completion_tokens = 15
    mock_response.usage.total_tokens = 35
    mock_response.usage.prompt_tokens_details = None
    mock_response.usage.completion_tokens_details = None
    
    with patch('services.llm.completion_service.acompletion', new_callable=AsyncMock) as mock_acompletion:
        mock_acompletion.return_value = mock_response
        
        # Execute non-streaming completion
        content, finish_reason, usage, inference_time, tool_calls = await completion_service.execute_non_streaming_completion(
            request=request,
            user_id="test_user"
        )
        
        # Assertions
        assert content == "I'm doing great! How can I help you today?"
        assert finish_reason == "stop"
        assert usage is not None
        assert usage.prompt_tokens == 20
        assert usage.completion_tokens == 15
        assert usage.total_tokens == 35
        assert tool_calls is None
        assert inference_time > 0
        
        # Verify acompletion was called with correct parameters
        mock_acompletion.assert_called_once()
        call_args = mock_acompletion.call_args
        assert call_args[1]['model'] == "zai/glm-4.6"
        assert call_args[1]['api_key'] == "test-zai-api-key"
        assert call_args[1]['api_base'] == "https://api.z.ai/api/coding/paas/v4"
        assert call_args[1]['temperature'] == 0.7
        assert call_args[1]['max_tokens'] == 100
        assert len(call_args[1]['messages']) == 2


@pytest.mark.asyncio
async def test_zai_list_models(llm_provider_service):
    """Test fetching available models for ZAI provider using unified AnyLLM interface."""
    # Mock the alist_models function from any_llm
    mock_models = [
        MagicMock(id="glm-4.6", object="model"),
        MagicMock(id="glm-4.5", object="model"),
        MagicMock(id="glm-4.5-air", object="model"),
    ]
    
    with patch('services.llm.llm_provider_service.alist_models', new_callable=AsyncMock) as mock_alist_models:
        mock_alist_models.return_value = mock_models
        
        # Fetch models
        models = await llm_provider_service.fetch_models_by_provider(
            provider_id="zai",
            api_key="test-zai-api-key",
            api_base="https://api.z.ai/api/coding/paas/v4"
        )
        
        # Assertions
        assert len(models) == 3
        assert models[0].id == "glm-4.6"
        assert models[1].id == "glm-4.5"
        assert models[2].id == "glm-4.5-air"
        
        # Verify alist_models was called with correct parameters
        mock_alist_models.assert_called_once_with(
            "zai",
            "test-zai-api-key",
            api_base="https://api.z.ai/api/coding/paas/v4"
        )