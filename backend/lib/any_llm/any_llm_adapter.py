"""
Wrapper around any_llm that includes custom providers (ZAI, LiteLLM).
Provides unified interface for all providers including custom ones.
"""
from __future__ import annotations

from typing import TYPE_CHECKING, Any, Sequence, Union

from any_llm.api import acompletion as any_llm_acompletion
from any_llm.api import alist_models as any_llm_alist_models
from any_llm.constants import LLMProvider

from lib.any_llm.litellm_provider import LiteLLMProvider
from lib.any_llm.synthetics_new_provider import SyntheticsNewProvider
from lib.any_llm.zai_provider import ZAIProvider

if TYPE_CHECKING:
    from collections.abc import AsyncIterator

    from any_llm.types.completion import ChatCompletion, ChatCompletionChunk, ChatCompletionMessage
    from any_llm.types.model import Model


# Custom provider instances registry
CUSTOM_PROVIDERS = {
    "zai": ZAIProvider,
    "litellm": LiteLLMProvider,
    "syntheticsnew": SyntheticsNewProvider,
}


async def acompletion(
    model: str,
    messages: Sequence[Union[dict[str, Any], "ChatCompletionMessage"]],
    api_key: str | None = None,
    api_base: str | None = None,
    **kwargs: Any,
) -> Union[ChatCompletion, AsyncIterator[ChatCompletionChunk]]:
    """
    Unified completion function that supports both any_llm providers and custom providers.
    
    Args:
        model: Model ID in format "provider/model" or just "model"
        messages: List of message dictionaries
        api_key: API key for the provider
        api_base: Base URL for the provider API
        **kwargs: Additional parameters (temperature, max_tokens, stream, etc.)
    
    Returns:
        ChatCompletion for non-streaming, AsyncIterator[ChatCompletionChunk] for streaming
    """
    # Extract provider from model string
    provider = None
    model_id = model
    
    if "/" in model:
        provider, model_id = model.split("/", 1)
    elif ":" in model:
        provider, model_id = model.split(":", 1)
    
    # Check if this is a custom provider
    if provider and provider.lower() in CUSTOM_PROVIDERS:
        provider_class = CUSTOM_PROVIDERS[provider.lower()]
        provider_instance = provider_class(api_key=api_key, api_base=api_base)
        
        # Use the provider's acompletion method directly with model and messages
        # Convert Sequence to list for provider compatibility
        return await provider_instance.acompletion(
            model=model_id,
            messages=list(messages),
            **kwargs
        )
    
    # Use any_llm for built-in providers
    return await any_llm_acompletion(
        model=model,
        messages=list(messages),
        api_key=api_key,
        api_base=api_base,
        **kwargs,
    )


async def alist_models(
    provider: str,
    api_key: str | None = None,
    api_base: str | None = None,
    **kwargs: Any,
) -> Sequence["Model"]:
    """
    Unified list models function that supports both any_llm providers and custom providers.
    
    Args:
        provider: Provider name (e.g., "openai", "zai", "litellm")
        api_key: API key for the provider
        api_base: Base URL for the provider API
        **kwargs: Additional parameters
    
    Returns:
        Sequence of Model objects
    """
    # Check if this is a custom provider
    if provider.lower() in CUSTOM_PROVIDERS:
        provider_class = CUSTOM_PROVIDERS[provider.lower()]
        provider_instance = provider_class(api_key=api_key, api_base=api_base, **kwargs)
        return await provider_instance.alist_models(**kwargs)
    
    # Use any_llm for built-in providers
    return await any_llm_alist_models(
        provider=provider,
        api_key=api_key,
        api_base=api_base,
        **kwargs,
    )


def get_supported_providers() -> list[str]:
    """
    Get list of all supported providers (built-in + custom).
    
    Returns:
        List of provider names
    """
    builtin_providers = [p for p in LLMProvider]
    custom_provider_names = list(CUSTOM_PROVIDERS.keys())
    return builtin_providers + custom_provider_names


def is_custom_provider(provider: str) -> bool:
    """
    Check if a provider is a custom provider.
    
    Args:
        provider: Provider name
    
    Returns:
        True if custom provider, False otherwise
    """
    return provider.lower() in CUSTOM_PROVIDERS