"""
PromptOptimizer Agent for enhancing system prompts.

This agent uses the any_agent framework with LANGCHAIN to generate
optimized prompts based on user ideas and provider-specific best practices.
"""
from typing import Optional, Dict, Any

# Monkeypatch any_llm module BEFORE importing any_agent
# This ensures any-agent frameworks use our custom any_llm_adapter
import any_llm
from lib.any_llm import any_llm_adapter

# Replace any_llm's functions with our custom versions
any_llm.acompletion = any_llm_adapter.acompletion
any_llm.alist_models = any_llm_adapter.alist_models

# Now import any_agent - it will use our patched any_llm
from any_agent import AgentConfig, AnyAgent, AgentFramework, AgentTrace


class PromptOptimizerAgent:
    """
    Agent for optimizing and enhancing prompts based on provider-specific best practices.

    This agent uses the any_agent framework with LANGCHAIN to generate
    well-structured, provider-optimized system prompts from user ideas.
    """

    def __init__(self, agent: AnyAgent):
        """
        Initialize PromptOptimizerAgent with a pre-created agent.

        Args:
            agent: Pre-initialized AnyAgent instance
        """
        self.agent = agent

    @classmethod
    async def create(
        cls,
        model_id: str,
        api_key: str,
        api_base: Optional[str] = None,
        instructions: str = "",
        model_args: Optional[Dict[str, Any]] = None,
    ) -> "PromptOptimizerAgent":
        """
        Create PromptOptimizerAgent with configuration.

        Args:
            model_id: Model identifier in format "provider/model"
            api_key: API key for the model provider
            api_base: Optional API base URL for custom providers
            instructions: System instructions for the optimizer agent
            model_args: Optional model arguments (temperature, max_tokens, etc.)

        Returns:
            PromptOptimizerAgent instance
        """
        config = AgentConfig(
            model_id=model_id,
            api_key=api_key,
            api_base=api_base,
            instructions=instructions,
            model_args=model_args or {"temperature": 0.7},
            tools=[],
        )

        agent = await AnyAgent.create_async(
            AgentFramework.LANGCHAIN,
            agent_config=config,
        )

        return cls(agent)

    async def run(self, prompt: str) -> AgentTrace:
        """
        Run the agent with a prompt asynchronously.

        Args:
            prompt: The complete prompt string (may include formatted conversation history)

        Returns:
            AgentTrace containing the execution trace with output and usage stats
        """
        return await self.agent.run_async(prompt)
