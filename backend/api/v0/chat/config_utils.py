"""
Configuration utilities for chat completions.
"""
from fastapi import HTTPException
from settings.base_settings import settings


def get_api_config_for_provider_model(provider: str, model: str) -> tuple[str, str | None]:
    """Get API key and base URL from settings for the given provider/model combination."""
    llm_configs = settings.llm_settings.llm_configs
    
    for config in llm_configs:
        if config.get("provider") == provider and config.get("model") == model:
            api_key = config.get("apiKey")
            if api_key:
                api_base_url = config.get("apiBaseUrl")
                return api_key, api_base_url
            break
    
    raise HTTPException(
        status_code=400,
        detail=f"No API key found for provider '{provider}' and model '{model}'. Please configure the API key in settings."
    )