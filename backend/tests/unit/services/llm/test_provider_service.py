"""
Unit tests for ProviderService.
"""
import pytest
from unittest.mock import Mock, patch
from typing import List

from services.llm.llm_provider_service import LLMProviderService
from services.config.config_service import ConfigService
from services.llm.models import ProviderInfo, ModelInfo, ProvidersResponse
from database.models.user_llm_configs import UserLLMConfigs


class TestProviderService:
    """Test cases for ProviderService"""

    def test_init(self):
        """Test ProviderService initialization"""
        config_service = Mock(spec=ConfigService)
        service = LLMProviderService(config_service)
        assert service.config_service == config_service

    def test_get_configured_providers_success(self):
        """Test getting configured providers with valid LLM configs"""
        config_service = Mock(spec=ConfigService)
        service = LLMProviderService(config_service)
        
        # Mock LLM configs
        mock_configs = [
            Mock(provider="openai", model="gpt-4"),
            Mock(provider="openai", model="gpt-3.5-turbo"),
            Mock(provider="anthropic", model="claude-3-sonnet"),
        ]
        config_service.get_llm_configs.return_value = mock_configs
        
        result = service.get_configured_providers("user_123")
        
        assert isinstance(result, ProvidersResponse)
        assert len(result.providers) == 2  # openai and anthropic
        
        # Check OpenAI provider
        openai_provider = next(p for p in result.providers if p.id == "openai")
        assert openai_provider.name == "OpenAI"
        assert len(openai_provider.models) == 2
        model_ids = [m.id for m in openai_provider.models]
        assert "gpt-4" in model_ids
        assert "gpt-3.5-turbo" in model_ids
        
        # Check Anthropic provider
        anthropic_provider = next(p for p in result.providers if p.id == "anthropic")
        assert anthropic_provider.name == "Anthropic"
        assert len(anthropic_provider.models) == 1
        assert anthropic_provider.models[0].id == "claude-3-sonnet"

    def test_get_configured_providers_no_configs(self):
        """Test getting configured providers when no LLM configs exist"""
        config_service = Mock(spec=ConfigService)
        service = LLMProviderService(config_service)
        
        config_service.get_llm_configs.return_value = []
        
        result = service.get_configured_providers("user_123")
        
        assert isinstance(result, ProvidersResponse)
        assert len(result.providers) == 0

    def test_get_configured_providers_none_configs(self):
        """Test getting configured providers when get_llm_configs returns None"""
        config_service = Mock(spec=ConfigService)
        service = LLMProviderService(config_service)
        
        config_service.get_llm_configs.return_value = None
        
        result = service.get_configured_providers("user_123")
        
        assert isinstance(result, ProvidersResponse)
        assert len(result.providers) == 0

    def test_get_configured_providers_invalid_provider_type(self):
        """Test handling invalid provider types (dict instead of string)"""
        config_service = Mock(spec=ConfigService)
        service = LLMProviderService(config_service)
        
        # Mock config with invalid provider type
        mock_configs = [
            Mock(provider={"invalid": "dict"}, model="gpt-4"),
            Mock(provider="openai", model="gpt-3.5-turbo"),
        ]
        config_service.get_llm_configs.return_value = mock_configs
        
        result = service.get_configured_providers("user_123")
        
        assert isinstance(result, ProvidersResponse)
        assert len(result.providers) == 1  # Only valid provider
        assert result.providers[0].id == "openai"

    def test_get_configured_providers_invalid_model_type(self):
        """Test handling invalid model types (dict instead of string)"""
        config_service = Mock(spec=ConfigService)
        service = LLMProviderService(config_service)
        
        # Mock config with invalid model type
        mock_configs = [
            Mock(provider="openai", model={"invalid": "dict"}),
            Mock(provider="openai", model="gpt-3.5-turbo"),
        ]
        config_service.get_llm_configs.return_value = mock_configs
        
        result = service.get_configured_providers("user_123")
        
        assert isinstance(result, ProvidersResponse)
        assert len(result.providers) == 1
        assert len(result.providers[0].models) == 1  # Only valid model
        assert result.providers[0].models[0].id == "gpt-3.5-turbo"

    def test_get_configured_providers_deduplicates_models(self):
        """Test that duplicate models for same provider are deduplicated"""
        config_service = Mock(spec=ConfigService)
        service = LLMProviderService(config_service)
        
        # Mock configs with duplicate models
        mock_configs = [
            Mock(provider="openai", model="gpt-4"),
            Mock(provider="openai", model="gpt-4"),  # Duplicate
            Mock(provider="openai", model="gpt-3.5-turbo"),
        ]
        config_service.get_llm_configs.return_value = mock_configs
        
        result = service.get_configured_providers("user_123")
        
        assert isinstance(result, ProvidersResponse)
        assert len(result.providers) == 1
        assert len(result.providers[0].models) == 2  # Deduplicated

    def test_get_configured_providers_exception_handling(self):
        """Test exception handling in get_configured_providers"""
        config_service = Mock(spec=ConfigService)
        service = LLMProviderService(config_service)
        
        config_service.get_llm_configs.side_effect = Exception("Database error")
        
        result = service.get_configured_providers("user_123")
        
        assert isinstance(result, ProvidersResponse)
        assert len(result.providers) == 0

    @patch('services.llm.llm_provider_service.LLMProvider')
    def test_get_available_providers_success(self, mock_llm_provider):
        """Test getting all available providers"""
        config_service = Mock(spec=ConfigService)
        service = LLMProviderService(config_service)
        
        # Mock LLMProvider enum
        mock_llm_provider.__members__ = {
            'OPENAI': 'openai',
            'ANTHROPIC': 'anthropic',
            'GOOGLE': 'google'
        }
        mock_llm_provider.__iter__ = lambda self: iter(['openai', 'anthropic', 'google'])
        
        with patch('services.llm.llm_provider_service.PROVIDER_NAMES_MAP', {
            'openai': {'name': 'OpenAI', 'custom_api_base': False},
            'anthropic': {'name': 'Anthropic', 'custom_api_base': False},
            'google': {'name': 'Google', 'custom_api_base': True}
        }):
            result = service.get_available_providers()
        
        assert isinstance(result, list)
        assert len(result) == 3
        
        openai_provider = next(p for p in result if p['id'] == 'openai')
        assert openai_provider['name'] == 'OpenAI'
        assert openai_provider['custom_api_base'] is False

    @patch('services.llm.llm_provider_service.LLMProvider')
    def test_get_available_providers_exception_handling(self, mock_llm_provider):
        """Test exception handling in get_available_providers"""
        config_service = Mock(spec=ConfigService)
        service = LLMProviderService(config_service)
        
        mock_llm_provider.__iter__ = Mock(side_effect=Exception("Provider error"))
        
        result = service.get_available_providers()
        
        assert isinstance(result, list)
        assert len(result) == 0

    @patch('services.llm.llm_provider_service.alist_models')
    @pytest.mark.asyncio
    async def test_fetch_models_by_provider_success(self, mock_alist_models):
        """Test successfully fetching models for a provider"""
        config_service = Mock(spec=ConfigService)
        service = LLMProviderService(config_service)
        
        # Mock models from API
        mock_model1 = Mock()
        mock_model1.id = "gpt-4"
        mock_model1.object = "model"
        
        mock_model2 = Mock()
        mock_model2.id = "gpt-3.5-turbo"
        mock_model2.object = "model"
        
        mock_alist_models.return_value = [mock_model1, mock_model2]
        
        result = await service.fetch_models_by_provider("openai", "api_key_123", "")
        
        assert isinstance(result, list)
        assert len(result) == 2
        assert all(isinstance(model, ModelInfo) for model in result)
        assert result[0].id == "gpt-4"
        assert result[1].id == "gpt-3.5-turbo"
        
        mock_alist_models.assert_called_once_with("openai", "api_key_123", api_base="")

    @patch('services.llm.llm_provider_service.alist_models')
    @pytest.mark.asyncio
    async def test_fetch_models_by_provider_with_api_base(self, mock_alist_models):
        """Test fetching models with custom API base URL"""
        config_service = Mock(spec=ConfigService)
        service = LLMProviderService(config_service)
        
        mock_model = Mock()
        mock_model.id = "custom-model"
        mock_model.object = "model"
        mock_alist_models.return_value = [mock_model]
        
        result = await service.fetch_models_by_provider("openai", "api_key_123", "https://custom.api.com")
        
        assert len(result) == 1
        mock_alist_models.assert_called_once_with("openai", "api_key_123", api_base="https://custom.api.com")

    @pytest.mark.asyncio
    async def test_fetch_models_by_provider_unsupported_provider(self):
        """Test fetching models for unsupported provider"""
        config_service = Mock(spec=ConfigService)
        service = LLMProviderService(config_service)
        
        result = await service.fetch_models_by_provider("unsupported_provider", "api_key_123", "")
        
        assert isinstance(result, list)
        assert len(result) == 0

    @patch('services.llm.llm_provider_service.alist_models')
    @pytest.mark.asyncio
    async def test_fetch_models_by_provider_api_exception(self, mock_alist_models):
        """Test handling API exceptions when fetching models"""
        config_service = Mock(spec=ConfigService)
        service = LLMProviderService(config_service)
        
        mock_alist_models.side_effect = Exception("API Error")
        
        result = await service.fetch_models_by_provider("openai", "api_key_123", "")
        
        assert isinstance(result, list)
        assert len(result) == 0

    @patch('services.llm.llm_provider_service.alist_models')
    @pytest.mark.asyncio
    async def test_fetch_models_by_provider_filters_invalid_models(self, mock_alist_models):
        """Test that invalid models are filtered out"""
        config_service = Mock(spec=ConfigService)
        service = LLMProviderService(config_service)
        
        # Mock models with various validity states
        valid_model = Mock()
        valid_model.id = "gpt-4"
        valid_model.object = "model"
        
        invalid_model_no_id = Mock()
        invalid_model_no_id.id = None
        invalid_model_no_id.object = "model"
        
        invalid_model_wrong_object = Mock()
        invalid_model_wrong_object.id = "gpt-3.5"
        invalid_model_wrong_object.object = "not_model"
        
        mock_alist_models.return_value = [valid_model, invalid_model_no_id, invalid_model_wrong_object]
        
        result = await service.fetch_models_by_provider("openai", "api_key_123", "")
        
        assert len(result) == 1  # Only valid model
        assert result[0].id == "gpt-4"