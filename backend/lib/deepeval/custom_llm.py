"""
Custom LLM wrapper for DeepEval metrics.

This module provides a custom LLM class that integrates with DeepEval's
metric evaluation system using our existing any_llm infrastructure.
"""

import asyncio
import logging
from typing import Optional

from deepeval.models import DeepEvalBaseLLM

from lib.any_llm.any_llm_adapter import acompletion

logger = logging.getLogger(__name__)


class CustomDeepEvalLLM(DeepEvalBaseLLM):
    """
    Custom LLM wrapper for DeepEval that uses our any_llm infrastructure.

    This allows DeepEval metrics to use any provider configured in the system,
    not just OpenAI with environment variables.
    """

    def __init__(
        self,
        provider: str,
        model: str,
        api_key: str,
        api_base: Optional[str] = None,
        temperature: float = 0.0,
        max_tokens: int = 2000,
    ):
        """
        Initialize the custom LLM.

        Args:
            provider: LLM provider (e.g., "openai", "anthropic", "syntheticsnew")
            model: Model name (e.g., "gpt-4", "claude-3-opus")
            api_key: API key for the provider
            api_base: Optional base URL for the provider API
            temperature: Temperature for generation (default 0.0 for deterministic)
            max_tokens: Maximum tokens for generation
        """
        self.provider = provider
        self.model_name = model
        self.api_key = api_key
        self.api_base = api_base
        self.temperature = temperature
        self.max_tokens = max_tokens

        # Build the model string in the format expected by any_llm
        self._full_model_id = f"{provider}/{model}"

    def load_model(self):
        """Load model - not needed for API-based models."""
        return self

    def generate(self, prompt: str, schema: Optional[dict] = None) -> str:
        """
        Generate completion for the given prompt (synchronous).

        Args:
            prompt: The prompt to generate completion for
            schema: Optional JSON schema for structured output

        Returns:
            Generated text response
        """
        # Run async method in sync context
        try:
            loop = asyncio.get_event_loop()
            if loop.is_running():
                # If we're in an async context, create a new loop
                import concurrent.futures
                with concurrent.futures.ThreadPoolExecutor() as executor:
                    future = executor.submit(
                        asyncio.run,
                        self.a_generate(prompt, schema)
                    )
                    return future.result()
            else:
                return loop.run_until_complete(self.a_generate(prompt, schema))
        except RuntimeError:
            # No event loop exists, create one
            return asyncio.run(self.a_generate(prompt, schema))

    async def a_generate(self, prompt: str, schema: Optional[dict] = None) -> str:
        """
        Generate completion for the given prompt (asynchronous).

        Args:
            prompt: The prompt to generate completion for
            schema: Optional JSON schema for structured output

        Returns:
            Generated text response
        """
        messages = [{"role": "user", "content": prompt}]

        kwargs = {
            "temperature": self.temperature,
            "max_tokens": self.max_tokens,
        }

        # Add structured output if schema provided (OpenAI-style)
        if schema:
            kwargs["response_format"] = {
                "type": "json_schema",
                "json_schema": schema
            }

        try:
            response = await acompletion(
                model=self._full_model_id,
                messages=messages,
                api_key=self.api_key,
                api_base=self.api_base,
                **kwargs
            )

            # Extract content from response
            if hasattr(response, 'choices') and response.choices:
                content = response.choices[0].message.content
                return content or ""

            logger.warning(f"Unexpected response format from {self._full_model_id}")
            return ""

        except Exception as e:
            logger.error(f"Error generating with {self._full_model_id}: {e}")
            raise

    def get_model_name(self) -> str:
        """Return the model identifier."""
        return self._full_model_id
