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
            provider_id = llm_config.provider
            model_info = ModelInfo(id=llm_config.model, name=llm_config.model)
            
            if provider_id not in provider_models:
                provider_models[provider_id] = []
            
            existing_models = [m.id for m in provider_models[provider_id]]
            if model_info.id not in existing_models:
                provider_models[provider_id].append(model_info)
        
        providers = [
            ProviderInfo(
                id=provider_id,
                name=PROVIDER_NAMES_MAP.get(provider_id) or provider_id.replace("_", " ").title(),
                models=models
            )
            for provider_id, models in provider_models.items()
        ]
        
        logger.info(f"Returning {len(providers)} configured providers")
        return ProvidersResponse(providers=providers)
        
    except Exception as e:
        logger.error(f"Error getting configured providers: {e}")
        return ProvidersResponse(providers=[])