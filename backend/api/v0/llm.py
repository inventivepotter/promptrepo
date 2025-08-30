"""
LLM-related API endpoints for PromptRepo.
Provides information about available LLM providers and models.
"""
from fastapi import APIRouter
from typing import Dict, List
import logging

from settings.base_settings import settings
from schemas.config import ProvidersResponse, ProviderInfo, ModelInfo
from utils.constants import PROVIDER_NAMES_MAP

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/providers/available", response_model=ProvidersResponse)
async def get_available_providers() -> ProvidersResponse:
    """
    Get available LLM providers and their models.
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
        
        logger.info(f"Returning {len(providers)} available providers")
        return ProvidersResponse(providers=providers)
        
    except Exception as e:
        logger.error(f"Error getting available providers: {e}")
        return ProvidersResponse(providers=[])