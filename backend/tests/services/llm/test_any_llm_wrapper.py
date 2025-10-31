"""
Tests for any_llm_wrapper that includes custom providers.
"""
import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from lib.any_llm.any_llm_adapter import (
    acompletion,
    alist_models,
    get_supported_providers,
    is_custom_provider,
    CUSTOM_PROVIDERS
)
from any_llm.types.completion import ChatCompletion, ChatCompletionMessage, Choice
from any_llm.types.model import Model


class TestAnyLLMWrapper:
    """Test suite for any_llm_wrapper."""
    
    def test_get_supported_providers(self):
        """Test getting list of all supported providers."""
        providers = get_supported_providers()
        
        # Should include built-in providers
        assert "openai" in providers
        assert "anthropic" in providers
        
        # Should include custom providers
        assert "zai" in providers
        assert "litellm" in providers
    
    def test_is_custom_provider(self):
        """Test checking if a provider is custom."""
        assert is_custom_provider("zai") is True
        assert is_custom_provider("ZAI") is True
        assert is_custom_provider("litellm") is True
        assert is_custom_provider("LITELLM") is True
        
        assert is_custom_provider("openai") is False
        assert is_custom_provider("anthropic") is False
    
    @pytest.mark.asyncio
    async def test_acompletion_with_custom_provider_zai(self):
        """Test acompletion with ZAI custom provider."""
        # Mock the ZAI provider
        mock_response = ChatCompletion(
            id="test-id",
            object="chat.completion",
            created=0,
            model="glm-4.6",
            choices=[
                Choice(
                    index=0,
                    message=ChatCompletionMessage(
                        role="assistant",
                        content="Test response",
                        tool_calls=None
                    ),
                    finish_reason="stop"
                )
            ],
            usage=None
        )
        
        with patch.object(CUSTOM_PROVIDERS["zai"], 'acompletion', new_callable=AsyncMock) as mock_acompletion:
            mock_acompletion.return_value = mock_response
            
            result = await acompletion(
                model="zai/glm-4.6",
                messages=[{"role": "user", "content": "test"}],
                api_key="test-key"
            )
            
            assert mock_acompletion.called
            assert result == mock_response
    
    @pytest.mark.asyncio
    async def test_acompletion_with_custom_provider_litellm(self):
        """Test acompletion with LiteLLM custom provider."""
        mock_response = ChatCompletion(
            id="test-id",
            object="chat.completion",
            created=0,
            model="gpt-4",
            choices=[
                Choice(
                    index=0,
                    message=ChatCompletionMessage(
                        role="assistant",
                        content="Test response",
                        tool_calls=None
                    ),
                    finish_reason="stop"
                )
            ],
            usage=None
        )
        
        with patch.object(CUSTOM_PROVIDERS["litellm"], 'acompletion', new_callable=AsyncMock) as mock_acompletion:
            mock_acompletion.return_value = mock_response
            
            result = await acompletion(
                model="litellm/gpt-4",
                messages=[{"role": "user", "content": "test"}],
                api_key="test-key",
                api_base="http://localhost:4000"
            )
            
            assert mock_acompletion.called
            assert result == mock_response
    
    @pytest.mark.asyncio
    async def test_acompletion_with_builtin_provider(self):
        """Test acompletion with built-in any_llm provider."""
        mock_response = ChatCompletion(
            id="test-id",
            object="chat.completion",
            created=0,
            model="gpt-4",
            choices=[
                Choice(
                    index=0,
                    message=ChatCompletionMessage(
                        role="assistant",
                        content="Test response",
                        tool_calls=None
                    ),
                    finish_reason="stop"
                )
            ],
            usage=None
        )
        
        with patch('services.llm.any_llm_wrapper.any_llm_acompletion', new_callable=AsyncMock) as mock_any_llm:
            mock_any_llm.return_value = mock_response
            
            result = await acompletion(
                model="openai/gpt-4",
                messages=[{"role": "user", "content": "test"}],
                api_key="test-key"
            )
            
            assert mock_any_llm.called
            assert result == mock_response
    
    @pytest.mark.asyncio
    async def test_alist_models_with_custom_provider(self):
        """Test alist_models with custom provider."""
        mock_models = [
            Model(id="glm-4.6", object="model", created=0, owned_by="zai"),
            Model(id="glm-4.5", object="model", created=0, owned_by="zai"),
        ]
        
        with patch.object(CUSTOM_PROVIDERS["zai"], 'alist_models', new_callable=AsyncMock) as mock_alist:
            mock_alist.return_value = mock_models
            
            result = await alist_models(
                provider="zai",
                api_key="test-key"
            )
            
            assert mock_alist.called
            assert result == mock_models
    
    @pytest.mark.asyncio
    async def test_alist_models_with_builtin_provider(self):
        """Test alist_models with built-in provider."""
        mock_models = [
            Model(id="gpt-4", object="model", created=0, owned_by="openai"),
            Model(id="gpt-3.5-turbo", object="model", created=0, owned_by="openai"),
        ]
        
        with patch('services.llm.any_llm_wrapper.any_llm_alist_models', new_callable=AsyncMock) as mock_any_llm:
            mock_any_llm.return_value = mock_models
            
            result = await alist_models(
                provider="openai",
                api_key="test-key"
            )
            
            assert mock_any_llm.called
            assert result == mock_models