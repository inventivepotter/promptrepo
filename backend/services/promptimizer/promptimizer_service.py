"""
Promptimizer service for AI-powered prompt optimization.

This service uses the PromptOptimizerAgent to generate enhanced system prompts
based on user ideas, provider-specific best practices, and optional OWASP guardrails.
"""
import json
import logging
from typing import Optional, List

from services.config.config_service import ConfigService
from services.promptimizer.models import PromptOptimizerRequest, PromptOptimizerResponse
from services.promptimizer.instructions import (
    OPENAI_INSTRUCTIONS,
    ANTHROPIC_INSTRUCTIONS,
    GOOGLE_INSTRUCTIONS,
    DEFAULT_INSTRUCTIONS,
    OWASP_2025_GUARDRAILS,
)
from agents.promptimizer.promptimizer_agent import PromptOptimizerAgent
from schemas.messages import MessageSchema
from middlewares.rest.exceptions import BadRequestException, ServiceUnavailableException

logger = logging.getLogger(__name__)


class PromptOptimizerService:
    """Service class for optimizing prompts using AI assistance."""

    def __init__(self, config_service: ConfigService):
        """
        Initialize PromptOptimizerService.

        Args:
            config_service: ConfigService for retrieving LLM configurations
        """
        self.config_service = config_service
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    def _get_provider_instructions(self, provider: str) -> str:
        """
        Get provider-specific optimization instructions.

        Args:
            provider: LLM provider name (e.g., 'openai', 'anthropic', 'google')

        Returns:
            Provider-specific instruction string
        """
        provider_lower = provider.lower()

        if provider_lower == "openai":
            return OPENAI_INSTRUCTIONS
        elif provider_lower == "anthropic":
            return ANTHROPIC_INSTRUCTIONS
        elif provider_lower in ("google", "gemini", "google_ai_studio"):
            return GOOGLE_INSTRUCTIONS
        else:
            return DEFAULT_INSTRUCTIONS

    def _build_system_instructions(self, provider: str, expects_user_message: bool) -> str:
        """
        Build the complete system instructions for the optimizer agent.

        Args:
            provider: Target LLM provider
            expects_user_message: Whether to include OWASP guardrails

        Returns:
            Complete system instruction string
        """
        provider_instructions = self._get_provider_instructions(provider)

        base_instructions = f"""You are an expert prompt engineer specializing in creating effective system prompts for AI assistants.

Your task is to enhance and optimize system prompts based on the user's idea and best practices for the target LLM provider.

{provider_instructions}

## Your Task

1. If the user provides an existing prompt to enhance:
   - Analyze the current prompt structure and purpose
   - Apply the user's requested improvements
   - Preserve the core intent and functionality
   - Enhance based on provider-specific best practices

2. If creating a new prompt from an idea:
   - Create a comprehensive, well-structured system prompt
   - Apply provider-specific best practices from the guidelines above

3. Ensure the prompt is:
   - Clear and unambiguous
   - Well-structured with appropriate formatting
   - Specific about the expected behavior and output
   - Appropriate for the target use case

4. Return ONLY the optimized system prompt text
5. Do NOT wrap the prompt in code blocks, quotes, or add meta-commentary
6. Do NOT include explanations unless the user specifically asks for them

## Multi-turn Conversation

If the user provides follow-up messages to refine the prompt:
- Build upon the previous version
- Address the specific feedback or changes requested
- Maintain the overall structure while making improvements
- Return the complete updated prompt (not just the changes)
"""

        if expects_user_message:
            base_instructions += f"""

## Security Requirements

This system prompt will receive user messages directly. You MUST add appropriate security guardrails to protect against prompt injection attacks.

{OWASP_2025_GUARDRAILS}

IMPORTANT: Integrate the security rules naturally into the prompt structure. Place them after the role definition but before the main task instructions.
"""

        return base_instructions

    def _get_api_details(self, provider: str, model: str, user_id: str) -> tuple[str, Optional[str]]:
        """
        Get API key and base URL for the specified provider and model.

        Args:
            provider: LLM provider name
            model: Model name
            user_id: User ID for configuration lookup

        Returns:
            Tuple of (api_key, api_base_url)

        Raises:
            BadRequestException: If no configuration found
        """
        llm_configs = self.config_service.get_llm_configs(user_id=user_id) or []

        # Try to find exact match for provider and model
        for config in llm_configs:
            if config.provider == provider and config.model == model:
                return config.api_key, config.api_base_url if config.api_base_url else None

        # Fallback: find first matching provider (user might not have configured exact model)
        for config in llm_configs:
            if config.provider == provider:
                self.logger.info(
                    f"Using fallback configuration for provider '{provider}' "
                    f"(requested model: {model}, using model: {config.model})"
                )
                return config.api_key, config.api_base_url if config.api_base_url else None

        raise BadRequestException(
            message=f"No LLM configuration found for provider '{provider}'",
            context={"provider": provider, "model": model}
        )

    def _format_conversation(
        self,
        history: Optional[List[MessageSchema]],
        user_message: str,
        current_prompt: Optional[str] = None
    ) -> str:
        """
        Format conversation history for the agent.

        Args:
            history: Previous conversation messages
            user_message: Current user message
            current_prompt: Existing prompt to enhance (optional)

        Returns:
            Formatted prompt string
        """
        parts = []

        # Add current prompt context if this is the first message and we have an existing prompt
        if current_prompt and current_prompt.strip() and not history:
            parts.append(f"## Existing Prompt to Enhance\n\n```\n{current_prompt}\n```\n")

        # Add conversation history if present
        if history:
            conversation = []
            for msg in history:
                conversation.append({
                    "role": msg.role,
                    "content": msg.content
                })
            history_json = json.dumps(conversation, ensure_ascii=False)
            parts.append(f"Previous conversation:\n{history_json}\n")

        # Add the current user request
        if history:
            parts.append(f"User's current request: {user_message}")
        else:
            parts.append(f"User's request: {user_message}")

        return "\n".join(parts)

    async def optimize_prompt(
        self,
        request: PromptOptimizerRequest,
        user_id: str
    ) -> PromptOptimizerResponse:
        """
        Optimize a prompt based on user's idea.

        Args:
            request: PromptOptimizerRequest with idea, provider, model, etc.
            user_id: User ID for configuration lookup

        Returns:
            PromptOptimizerResponse with the optimized prompt

        Raises:
            BadRequestException: If request validation fails
            ServiceUnavailableException: If optimization fails
        """
        # Validate request
        if not request.idea or not request.idea.strip():
            raise BadRequestException(
                message="Idea is required and cannot be empty"
            )

        if not request.provider or not request.provider.strip():
            raise BadRequestException(
                message="Provider is required and cannot be empty"
            )

        if not request.model or not request.model.strip():
            raise BadRequestException(
                message="Model is required and cannot be empty"
            )

        has_current_prompt = bool(request.current_prompt and request.current_prompt.strip())
        self.logger.info(
            f"Optimizing prompt for provider={request.provider}, model={request.model}, "
            f"expects_user_message={request.expects_user_message}, has_current_prompt={has_current_prompt}",
            extra={"user_id": user_id}
        )

        try:
            # Get API details
            api_key, api_base = self._get_api_details(
                request.provider,
                request.model,
                user_id
            )

            # Build system instructions
            system_instructions = self._build_system_instructions(
                request.provider,
                request.expects_user_message
            )

            # Create agent
            model_id = f"{request.provider}/{request.model}"
            agent = await PromptOptimizerAgent.create(
                model_id=model_id,
                api_key=api_key,
                api_base=api_base,
                instructions=system_instructions,
                model_args={"temperature": 0.7}
            )

            # Format the prompt
            prompt_text = self._format_conversation(
                request.conversation_history,
                request.idea,
                request.current_prompt
            )

            # Run agent
            trace = await agent.run(prompt_text)

            # Extract response content
            content = ""
            if trace.final_output:
                if isinstance(trace.final_output, str):
                    content = trace.final_output
                elif isinstance(trace.final_output, dict):
                    content = str(trace.final_output.get("content", trace.final_output))
                else:
                    content = str(trace.final_output)

            # If no content from final_output, try to extract from messages
            if not content:
                try:
                    messages = trace.spans_to_messages()
                    for msg in reversed(messages or []):
                        if hasattr(msg, 'role') and msg.role == "assistant":
                            content = msg.content if isinstance(msg.content, str) else str(msg.content)
                            break
                except Exception as e:
                    self.logger.warning(f"Failed to extract content from trace messages: {e}")

            if not content:
                raise ServiceUnavailableException(
                    message="Failed to generate optimized prompt - no content returned"
                )

            self.logger.info(
                f"Successfully optimized prompt, output length: {len(content)} chars",
                extra={"user_id": user_id}
            )

            return PromptOptimizerResponse(
                optimized_prompt=content,
                explanation=None
            )

        except (BadRequestException, ServiceUnavailableException):
            raise
        except Exception as e:
            self.logger.error(f"Prompt optimization failed: {e}", exc_info=True)
            raise ServiceUnavailableException(
                message=f"Prompt optimization failed: {str(e)}",
                context={"provider": request.provider, "model": request.model}
            )
