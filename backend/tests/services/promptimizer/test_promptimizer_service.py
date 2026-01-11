"""
Unit tests for PromptOptimizerService.
"""
import pytest
from unittest.mock import Mock, AsyncMock, patch

from services.promptimizer.promptimizer_service import PromptOptimizerService
from services.promptimizer.models import PromptOptimizerRequest, PromptOptimizerResponse
from services.promptimizer.instructions import (
    OPENAI_INSTRUCTIONS,
    ANTHROPIC_INSTRUCTIONS,
    GOOGLE_INSTRUCTIONS,
    DEFAULT_INSTRUCTIONS,
    OWASP_2025_GUARDRAILS,
)
from services.config.config_service import ConfigService
from middlewares.rest.exceptions import BadRequestException


class TestPromptOptimizerService:
    """Test cases for PromptOptimizerService"""

    def test_init(self):
        """Test PromptOptimizerService initialization"""
        config_service = Mock(spec=ConfigService)
        service = PromptOptimizerService(config_service)
        assert service.config_service == config_service

    def test_get_provider_instructions_openai(self):
        """Test getting OpenAI-specific instructions"""
        config_service = Mock(spec=ConfigService)
        service = PromptOptimizerService(config_service)

        result = service._get_provider_instructions("openai")
        assert result == OPENAI_INSTRUCTIONS

        # Test case insensitivity
        result = service._get_provider_instructions("OpenAI")
        assert result == OPENAI_INSTRUCTIONS

    def test_get_provider_instructions_anthropic(self):
        """Test getting Anthropic-specific instructions"""
        config_service = Mock(spec=ConfigService)
        service = PromptOptimizerService(config_service)

        result = service._get_provider_instructions("anthropic")
        assert result == ANTHROPIC_INSTRUCTIONS

    def test_get_provider_instructions_google(self):
        """Test getting Google/Gemini-specific instructions"""
        config_service = Mock(spec=ConfigService)
        service = PromptOptimizerService(config_service)

        # Test different Google provider names
        assert service._get_provider_instructions("google") == GOOGLE_INSTRUCTIONS
        assert service._get_provider_instructions("gemini") == GOOGLE_INSTRUCTIONS
        assert service._get_provider_instructions("google_ai_studio") == GOOGLE_INSTRUCTIONS

    def test_get_provider_instructions_default(self):
        """Test getting default instructions for unknown providers"""
        config_service = Mock(spec=ConfigService)
        service = PromptOptimizerService(config_service)

        result = service._get_provider_instructions("unknown_provider")
        assert result == DEFAULT_INSTRUCTIONS

        result = service._get_provider_instructions("groq")
        assert result == DEFAULT_INSTRUCTIONS

    def test_build_system_instructions_without_guardrails(self):
        """Test building system instructions without OWASP guardrails"""
        config_service = Mock(spec=ConfigService)
        service = PromptOptimizerService(config_service)

        result = service._build_system_instructions("openai", expects_user_message=False)

        assert "expert prompt engineer" in result
        assert OPENAI_INSTRUCTIONS in result
        assert OWASP_2025_GUARDRAILS not in result

    def test_build_system_instructions_with_guardrails(self):
        """Test building system instructions with OWASP guardrails"""
        config_service = Mock(spec=ConfigService)
        service = PromptOptimizerService(config_service)

        result = service._build_system_instructions("openai", expects_user_message=True)

        assert "expert prompt engineer" in result
        assert OPENAI_INSTRUCTIONS in result
        assert "Security Requirements" in result
        assert "OWASP" in result

    def test_get_api_details_success(self):
        """Test successfully getting API details"""
        config_service = Mock(spec=ConfigService)
        service = PromptOptimizerService(config_service)

        mock_config = Mock()
        mock_config.provider = "openai"
        mock_config.model = "gpt-4"
        mock_config.api_key = "sk-test-key"
        mock_config.api_base_url = None

        config_service.get_llm_configs.return_value = [mock_config]

        api_key, api_base = service._get_api_details("openai", "gpt-4", "user_123")

        assert api_key == "sk-test-key"
        assert api_base is None

    def test_get_api_details_with_custom_base(self):
        """Test getting API details with custom base URL"""
        config_service = Mock(spec=ConfigService)
        service = PromptOptimizerService(config_service)

        mock_config = Mock()
        mock_config.provider = "openai"
        mock_config.model = "gpt-4"
        mock_config.api_key = "sk-test-key"
        mock_config.api_base_url = "https://custom.api.com"

        config_service.get_llm_configs.return_value = [mock_config]

        api_key, api_base = service._get_api_details("openai", "gpt-4", "user_123")

        assert api_key == "sk-test-key"
        assert api_base == "https://custom.api.com"

    def test_get_api_details_fallback_to_provider(self):
        """Test fallback to any matching provider config when exact model not found"""
        config_service = Mock(spec=ConfigService)
        service = PromptOptimizerService(config_service)

        # Config for different model but same provider
        mock_config = Mock()
        mock_config.provider = "openai"
        mock_config.model = "gpt-3.5-turbo"
        mock_config.api_key = "sk-fallback-key"
        mock_config.api_base_url = None

        config_service.get_llm_configs.return_value = [mock_config]

        # Request for gpt-4 but only gpt-3.5-turbo is configured
        api_key, api_base = service._get_api_details("openai", "gpt-4", "user_123")

        assert api_key == "sk-fallback-key"

    def test_get_api_details_no_config_found(self):
        """Test error when no configuration found"""
        config_service = Mock(spec=ConfigService)
        service = PromptOptimizerService(config_service)

        config_service.get_llm_configs.return_value = []

        with pytest.raises(BadRequestException) as exc_info:
            service._get_api_details("openai", "gpt-4", "user_123")

        assert "No LLM configuration found" in str(exc_info.value.message)

    def test_format_conversation_without_history(self):
        """Test formatting conversation without history"""
        config_service = Mock(spec=ConfigService)
        service = PromptOptimizerService(config_service)

        result = service._format_conversation(None, "Create a helpful assistant")

        assert "User's request: Create a helpful assistant" in result

    def test_format_conversation_with_history(self):
        """Test formatting conversation with history"""
        config_service = Mock(spec=ConfigService)
        service = PromptOptimizerService(config_service)

        mock_msg1 = Mock()
        mock_msg1.role = "user"
        mock_msg1.content = "Create a customer service bot"

        mock_msg2 = Mock()
        mock_msg2.role = "assistant"
        mock_msg2.content = "Here is your prompt..."

        history = [mock_msg1, mock_msg2]

        result = service._format_conversation(history, "Make it more friendly")

        assert "Previous conversation:" in result
        assert "customer service bot" in result
        assert "Make it more friendly" in result

    def test_format_conversation_with_current_prompt(self):
        """Test formatting conversation with existing prompt to enhance"""
        config_service = Mock(spec=ConfigService)
        service = PromptOptimizerService(config_service)

        current_prompt = "You are a helpful assistant."
        result = service._format_conversation(None, "Make it more formal", current_prompt)

        assert "Existing Prompt to Enhance" in result
        assert "You are a helpful assistant." in result
        assert "Make it more formal" in result

    def test_format_conversation_current_prompt_only_on_first_message(self):
        """Test that current prompt is only included when there's no history"""
        config_service = Mock(spec=ConfigService)
        service = PromptOptimizerService(config_service)

        mock_msg = Mock()
        mock_msg.role = "user"
        mock_msg.content = "First request"

        history = [mock_msg]
        current_prompt = "You are a helpful assistant."

        result = service._format_conversation(history, "Second request", current_prompt)

        # Current prompt should NOT be included when there's history
        assert "Existing Prompt to Enhance" not in result
        assert "Previous conversation:" in result

    def test_request_model_validates_empty_idea(self):
        """Test that empty idea fails Pydantic validation"""
        from pydantic import ValidationError

        with pytest.raises(ValidationError) as exc_info:
            PromptOptimizerRequest(
                idea="",
                provider="openai",
                model="gpt-4",
                expects_user_message=False
            )

        assert "string_too_short" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_optimize_prompt_validates_whitespace_idea(self):
        """Test that whitespace-only idea raises BadRequestException"""
        config_service = Mock(spec=ConfigService)
        service = PromptOptimizerService(config_service)

        request = PromptOptimizerRequest(
            idea="   ",  # Only whitespace
            provider="openai",
            model="gpt-4",
            expects_user_message=False
        )

        with pytest.raises(BadRequestException) as exc_info:
            await service.optimize_prompt(request, "user_123")

        assert "Idea is required" in str(exc_info.value.message)

    @pytest.mark.asyncio
    async def test_optimize_prompt_validates_empty_provider(self):
        """Test that empty provider raises BadRequestException"""
        config_service = Mock(spec=ConfigService)
        service = PromptOptimizerService(config_service)

        request = PromptOptimizerRequest(
            idea="Create a helpful assistant",
            provider="",
            model="gpt-4",
            expects_user_message=False
        )

        with pytest.raises(BadRequestException) as exc_info:
            await service.optimize_prompt(request, "user_123")

        assert "Provider is required" in str(exc_info.value.message)

    @pytest.mark.asyncio
    async def test_optimize_prompt_validates_empty_model(self):
        """Test that empty model raises BadRequestException"""
        config_service = Mock(spec=ConfigService)
        service = PromptOptimizerService(config_service)

        request = PromptOptimizerRequest(
            idea="Create a helpful assistant",
            provider="openai",
            model="",
            expects_user_message=False
        )

        with pytest.raises(BadRequestException) as exc_info:
            await service.optimize_prompt(request, "user_123")

        assert "Model is required" in str(exc_info.value.message)

    @pytest.mark.asyncio
    @patch('services.promptimizer.promptimizer_service.PromptOptimizerAgent')
    async def test_optimize_prompt_success(self, mock_agent_class):
        """Test successful prompt optimization"""
        config_service = Mock(spec=ConfigService)
        service = PromptOptimizerService(config_service)

        # Mock LLM config
        mock_config = Mock()
        mock_config.provider = "openai"
        mock_config.model = "gpt-4"
        mock_config.api_key = "sk-test-key"
        mock_config.api_base_url = None
        config_service.get_llm_configs.return_value = [mock_config]

        # Mock agent
        mock_agent = AsyncMock()
        mock_trace = Mock()
        mock_trace.final_output = "You are a helpful customer service assistant..."
        mock_agent.run = AsyncMock(return_value=mock_trace)
        mock_agent_class.create = AsyncMock(return_value=mock_agent)

        request = PromptOptimizerRequest(
            idea="Create a customer service assistant",
            provider="openai",
            model="gpt-4",
            expects_user_message=False
        )

        result = await service.optimize_prompt(request, "user_123")

        assert isinstance(result, PromptOptimizerResponse)
        assert "helpful customer service assistant" in result.optimized_prompt
        mock_agent_class.create.assert_called_once()

    @pytest.mark.asyncio
    @patch('services.promptimizer.promptimizer_service.PromptOptimizerAgent')
    async def test_optimize_prompt_with_guardrails(self, mock_agent_class):
        """Test prompt optimization with OWASP guardrails"""
        config_service = Mock(spec=ConfigService)
        service = PromptOptimizerService(config_service)

        # Mock LLM config
        mock_config = Mock()
        mock_config.provider = "anthropic"
        mock_config.model = "claude-3-opus"
        mock_config.api_key = "sk-test-key"
        mock_config.api_base_url = None
        config_service.get_llm_configs.return_value = [mock_config]

        # Mock agent
        mock_agent = AsyncMock()
        mock_trace = Mock()
        mock_trace.final_output = "You are a secure assistant with guardrails..."
        mock_agent.run = AsyncMock(return_value=mock_trace)
        mock_agent_class.create = AsyncMock(return_value=mock_agent)

        request = PromptOptimizerRequest(
            idea="Create a chat assistant",
            provider="anthropic",
            model="claude-3-opus",
            expects_user_message=True
        )

        result = await service.optimize_prompt(request, "user_123")

        assert isinstance(result, PromptOptimizerResponse)

        # Verify agent was created with guardrails in instructions
        create_call = mock_agent_class.create.call_args
        assert "Security Requirements" in create_call.kwargs.get('instructions', '')
