"""
Conversation Simulator Service for goal-based conversation generation.

This service simulates multi-turn conversations by having an AI simulate
a user with a specific goal interacting with the actual chatbot being tested.
"""

import logging
from typing import Optional, List

from services.config.config_service import ConfigService
from services.artifacts.prompt.prompt_meta_service import PromptMetaService
from services.llm.chat_completion_service import ChatCompletionService
from services.conversational.models import (
    SimulateConversationRequest,
    SimulateConversationResponse,
)
from services.artifacts.evals.models import Turn, TurnRole
from agents.promptimizer.promptimizer_agent import PromptOptimizerAgent
from middlewares.rest.exceptions import BadRequestException, ServiceUnavailableException, NotFoundException

logger = logging.getLogger(__name__)


USER_SIMULATOR_INSTRUCTIONS = """You are simulating a user interacting with an AI assistant. Your goal is to act as a realistic user with a specific objective.

## Your Role

You are playing the role of a user who has a specific goal they want to achieve through this conversation. You should:

1. **Stay in Character**: Maintain your assigned persona throughout the conversation
2. **Be Natural**: Use realistic language, including occasional typos, follow-up questions, or clarifications
3. **Pursue Your Goal**: Keep working toward your objective, but react naturally to the assistant's responses
4. **Be Responsive**: Acknowledge helpful responses and push back on unhelpful ones

## Your Goal

{user_goal}

## Your Persona

{user_persona}

## Instructions

Based on the conversation history, generate your next message as the user.

IMPORTANT:
- Output ONLY the user message text
- Do NOT include any role labels, quotes, or formatting
- Do NOT include explanation or meta-commentary
- Just write what the user would naturally say next

## Stopping Criteria

{stopping_criteria}

If you believe the goal has been achieved or the stopping criteria is met, respond with exactly:
[GOAL_ACHIEVED]

If the conversation cannot proceed (assistant refuses, dead end, etc.), respond with exactly:
[CANNOT_CONTINUE]
"""


class ConversationSimulatorService:
    """Service for simulating conversations based on user goals."""

    def __init__(
        self,
        config_service: ConfigService,
        prompt_service: PromptMetaService,
        chat_completion_service: ChatCompletionService,
    ):
        """
        Initialize ConversationSimulatorService.

        Args:
            config_service: ConfigService for retrieving LLM configurations
            prompt_service: PromptMetaService for loading prompt definitions
            chat_completion_service: ChatCompletionService for executing prompts
        """
        self.config_service = config_service
        self.prompt_service = prompt_service
        self.chat_completion_service = chat_completion_service
        self.logger = logging.getLogger(f"{__name__}.{self.__class__.__name__}")

    def _get_api_details(self, provider: str, model: str, user_id: str) -> tuple[str, Optional[str]]:
        """Get API key and base URL for the specified provider and model."""
        llm_configs = self.config_service.get_llm_configs(user_id=user_id) or []

        # First try to find exact match (provider + model)
        for config in llm_configs:
            if config.provider == provider and config.model == model:
                if config.api_key:
                    return config.api_key, config.api_base_url if config.api_base_url else None

        # Then try to find by provider only
        for config in llm_configs:
            if config.provider == provider:
                if config.api_key:
                    return config.api_key, config.api_base_url if config.api_base_url else None

        # Log available providers for debugging
        available_providers = [c.provider for c in llm_configs]
        self.logger.warning(
            f"No API key found for provider '{provider}'. Available providers: {available_providers}"
        )

        raise BadRequestException(
            message=f"No API key configured for provider '{provider}'. Please configure an API key in your LLM settings.",
            context={"provider": provider, "model": model, "available_providers": available_providers}
        )

    def _build_user_simulator_prompt(
        self,
        user_goal: str,
        user_persona: Optional[str],
        stopping_criteria: Optional[str],
        conversation_history: List[Turn],
    ) -> str:
        """Build the prompt for the user simulator."""
        # Format the instructions
        persona_text = user_persona if user_persona else "A typical user seeking assistance"
        stopping_text = stopping_criteria if stopping_criteria else "When the user's goal has been satisfactorily addressed"

        instructions = USER_SIMULATOR_INSTRUCTIONS.format(
            user_goal=user_goal,
            user_persona=persona_text,
            stopping_criteria=stopping_text,
        )

        # Add conversation history
        if conversation_history:
            history_text = "\n## Conversation So Far\n\n"
            for turn in conversation_history:
                role_label = "User" if turn.role == TurnRole.USER else "Assistant"
                history_text += f"**{role_label}**: {turn.content}\n\n"
            instructions += history_text
            instructions += "\n## Your Next Message\n\nWhat would you say next as the user?"
        else:
            instructions += "\n## Start the Conversation\n\nGenerate the opening message to start pursuing your goal."

        return instructions

    async def _generate_user_message(
        self,
        request: SimulateConversationRequest,
        conversation_history: List[Turn],
        user_id: str,
    ) -> tuple[str, bool, Optional[str]]:
        """
        Generate the next user message.

        Returns:
            Tuple of (message, should_stop, stopping_reason)
        """
        api_key, api_base = self._get_api_details(
            request.provider,
            request.model,
            user_id
        )

        model_id = f"{request.provider}/{request.model}"
        agent = await PromptOptimizerAgent.create(
            model_id=model_id,
            api_key=api_key,
            api_base=api_base,
            instructions="",  # Instructions will be in the prompt
            model_args={"temperature": 0.8}
        )

        prompt = self._build_user_simulator_prompt(
            request.user_goal,
            request.user_persona,
            request.stopping_criteria,
            conversation_history,
        )

        trace = await agent.run(prompt)

        # Extract response content
        content = ""
        if trace.final_output:
            if isinstance(trace.final_output, str):
                content = trace.final_output
            elif isinstance(trace.final_output, dict):
                content = str(trace.final_output.get("content", trace.final_output))
            else:
                content = str(trace.final_output)

        if not content:
            try:
                messages = trace.spans_to_messages()
                for msg in reversed(messages or []):
                    if hasattr(msg, 'role') and msg.role == "assistant":
                        content = msg.content if isinstance(msg.content, str) else str(msg.content)
                        break
            except Exception:
                pass

        content = content.strip()

        # Check for stopping signals
        if "[GOAL_ACHIEVED]" in content:
            return "", True, "Goal was achieved"
        if "[CANNOT_CONTINUE]" in content:
            return "", True, "Conversation cannot continue"

        return content, False, None

    async def simulate_conversation(
        self,
        request: SimulateConversationRequest,
        user_id: str,
        repo_name: str,
    ) -> SimulateConversationResponse:
        """
        Simulate a conversation based on user goal.

        This method alternates between:
        1. Generating a user message (using AI to simulate the user)
        2. Getting the assistant response (using the actual chatbot)

        Args:
            request: SimulateConversationRequest with simulation parameters
            user_id: User ID for configuration lookup
            repo_name: Repository name for prompt lookup

        Returns:
            SimulateConversationResponse with simulated conversation

        Raises:
            BadRequestException: If request validation fails
            ServiceUnavailableException: If simulation fails
        """
        self.logger.info(
            f"Simulating conversation for prompt {request.prompt_reference} with goal: {request.user_goal}",
            extra={"user_id": user_id}
        )

        # Parse prompt reference to get file path
        prompt_reference = request.prompt_reference
        if prompt_reference.startswith("file:///"):
            prompt_file_path = prompt_reference.replace("file:///", "")
        else:
            prompt_file_path = prompt_reference

        # Build prompt_id for chat completion service
        prompt_id = f"{repo_name}:{prompt_file_path}"

        # Get provider/model from request or from the prompt's configuration
        provider = request.provider
        model = request.model

        if not provider or not model:
            # Load the prompt to get its LLM configuration
            try:
                prompt_meta = await self.prompt_service.get(
                    user_id=user_id,
                    repo_name=repo_name,
                    file_path=prompt_file_path
                )
                if prompt_meta and prompt_meta.prompt:
                    if not provider:
                        provider = prompt_meta.prompt.provider
                    if not model:
                        model = prompt_meta.prompt.model
            except Exception as e:
                self.logger.warning(f"Failed to load prompt config: {e}")

        if not provider or not model:
            raise BadRequestException(
                message="LLM provider and model are required but not configured",
                context={"prompt_reference": prompt_reference}
            )

        # Update request with resolved provider/model for downstream use
        request.provider = provider
        request.model = model

        turns: List[Turn] = []
        goal_achieved = False
        stopping_reason = None
        turn_count = 0

        try:
            while turn_count < request.max_turns:
                # Generate user message
                user_message, should_stop, stop_reason = await self._generate_user_message(
                    request,
                    turns,
                    user_id,
                )

                if should_stop:
                    goal_achieved = stop_reason == "Goal was achieved"
                    stopping_reason = stop_reason
                    break

                if not user_message:
                    stopping_reason = "Failed to generate user message"
                    break

                # Add user turn
                turns.append(Turn(role=TurnRole.USER, content=user_message))
                turn_count += 1

                # Check if we've reached max turns after user message
                if turn_count >= request.max_turns:
                    stopping_reason = "Maximum turns reached"
                    break

                # Get assistant response using the actual chatbot
                try:
                    # Convert turns to conversation history format
                    from schemas.messages import UserMessageSchema, AIMessageSchema

                    conversation_history = []
                    for t in turns[:-1]:  # Exclude the current user message
                        if t.role == TurnRole.USER:
                            conversation_history.append(UserMessageSchema(content=t.content))
                        else:
                            conversation_history.append(AIMessageSchema(content=t.content))

                    completion_response = await self.chat_completion_service.execute_completion_from_saved_prompt(
                        user_id=user_id,
                        prompt_id=prompt_id,
                        last_user_message=user_message,
                        conversation_history=conversation_history if conversation_history else None,
                    )

                    assistant_content = completion_response.content or ""

                    # Add assistant turn
                    turns.append(Turn(
                        role=TurnRole.ASSISTANT,
                        content=assistant_content,
                        tools_called=[tc.model_dump() for tc in completion_response.tool_calls] if completion_response.tool_calls else None,
                    ))
                    turn_count += 1

                except Exception as e:
                    self.logger.error(f"Failed to get assistant response: {e}")
                    stopping_reason = f"Assistant response failed: {str(e)}"
                    break

                # Check minimum turns
                if turn_count >= request.min_turns:
                    # Check if goal seems achieved in the last exchange
                    # Generate one more user message to check
                    _, should_stop, stop_reason = await self._generate_user_message(
                        request,
                        turns,
                        user_id,
                    )
                    if should_stop:
                        goal_achieved = stop_reason == "Goal was achieved"
                        stopping_reason = stop_reason
                        break

            if not stopping_reason and turn_count >= request.max_turns:
                stopping_reason = "Maximum turns reached"

            self.logger.info(
                f"Simulation completed with {len(turns)} turns, goal_achieved={goal_achieved}",
                extra={"user_id": user_id}
            )

            return SimulateConversationResponse(
                turns=turns,
                goal_achieved=goal_achieved,
                stopping_reason=stopping_reason,
            )

        except (BadRequestException, ServiceUnavailableException):
            raise
        except Exception as e:
            self.logger.error(f"Conversation simulation failed: {e}", exc_info=True)
            raise ServiceUnavailableException(
                message=f"Conversation simulation failed: {str(e)}",
                context={"provider": request.provider, "model": request.model}
            )
