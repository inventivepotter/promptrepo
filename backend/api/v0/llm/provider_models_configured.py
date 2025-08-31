"""
Configured LLM providers endpoint.
Returns standardized provider information based on AppConfig.
"""
from fastapi import APIRouter
from typing import Dict, List
import logging

from settings.base_settings import settings
from schemas.config import ProvidersResponse, ProviderInfo, ModelInfo
from utils.constants import PROVIDER_NAMES_MAP

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/providers/configured", response_model=ProvidersResponse)
async def get_configured_providers() -> ProvidersResponse:
    """
    Get configured LLM providers and their models.
    Returns standardized provider information based on AppConfig.
    """
    try:
        app_config = settings.app_config
        provider_models: Dict[str, List[ModelInfo]] = {}
        
        # Group models by provider
        for llm_config in app_config.llmConfigs:
            # Ensure provider is a string
            provider_id = llm_config.provider
            if isinstance(provider_id, dict):
                logger.warning(f"Skipping invalid provider configuration: provider is a dict")
                continue
            elif not isinstance(provider_id, str):
                provider_id = str(provider_id)
            
            # Ensure model is a string
            model_name = llm_config.model
            if isinstance(model_name, dict):
                logger.warning(f"Skipping invalid model configuration for provider {provider_id}: model is a dict")
                continue
            elif not isinstance(model_name, str):
                model_name = str(model_name)
            
            model_info = ModelInfo(id=model_name, name=model_name)
            
            if provider_id not in provider_models:
                provider_models[provider_id] = []
            
            existing_models = [m.id for m in provider_models[provider_id]]
            if model_info.id not in existing_models:
                provider_models[provider_id].append(model_info)
        
        providers = [
            ProviderInfo(
                id=provider_id,
                name=PROVIDER_NAMES_MAP.get(provider_id, {}).get("name", provider_id.replace("_", " ").title()),
                models=models
            )
            for provider_id, models in provider_models.items()
        ]
        
        logger.info(f"Returning {len(providers)} configured providers")
        return ProvidersResponse(providers=providers)
        
    except Exception as e:
        logger.error(f"Error getting configured providers: {e}")
        return ProvidersResponse(providers=[])