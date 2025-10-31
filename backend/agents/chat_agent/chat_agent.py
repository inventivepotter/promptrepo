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


class ChatAgent:
    """
    Simple agent wrapper for handling chat completions using any_agent framework.
    
    This agent is a thin wrapper that accepts a prompt string and system instructions.
    Message formatting and conversation history management is handled by the calling service.
    """
    
    def __init__(self, agent: AnyAgent):
        """
        Initialize ChatAgent with a pre-created agent.
        
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
        instructions: Optional[str] = None,
        model_args: Optional[Dict[str, Any]] = None,
        tools: Optional[list] = None,
    ) -> "ChatAgent":
        """
        Create ChatAgent with configuration.
        
        Args:
            model_id: Model identifier in format "provider/model"
            api_key: API key for the model provider
            api_base: Optional API base URL for custom providers
            instructions: Optional system instructions/prompt
            model_args: Optional model arguments (temperature, max_tokens, etc.)
            tools: Optional list of tools for the agent
            
        Returns:
            ChatAgent instance
        """
        # Build AgentConfig - uses our monkeypatched any_llm which supports custom providers
        config = AgentConfig(
            model_id=model_id,
            api_key=api_key,
            api_base=api_base,
            instructions=instructions,
            model_args=model_args or {},
            tools=tools or [],
        )
        
        # Create agent using AGNO framework asynchronously
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
            AgentTrace containing the execution trace with usage stats and messages
        """
        return await self.agent.run_async(prompt)