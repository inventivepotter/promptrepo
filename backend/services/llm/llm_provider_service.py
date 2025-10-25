"""
Provider service for LLM providers and models.
Handles provider information, configured providers, and model fetching.
"""
from typing import Dict, List, Any
import logging
from any_llm.constants import LLMProvider
from any_llm.api import list_models, alist_models

from services.config.config_service import ConfigService
from services.llm.models import ProviderInfo, ModelInfo, ProvidersResponse
from services.llm.providers.zai_llm_provider import ZAILlmProvider
from services.llm.providers.litellm_provider import LiteLLMProvider
from utils.constants import PROVIDER_NAMES_MAP

logger = logging.getLogger(__name__)


class LLMProviderService:
    """Service for handling LLM provider operations."""
    
    def __init__(self, config_service: ConfigService):
        self.config_service = config_service
    
    def get_configured_providers(self, user_id: str) -> ProvidersResponse:
        """
        Get configured LLM providers and their models.
        Returns standardized provider information based on AppConfig.
        """
        try:
            llm_configs = self.config_service.get_llm_configs(user_id=user_id) or []
            provider_models: Dict[str, List[ModelInfo]] = {}

            # Group models by provider
            for llm_config in llm_configs:
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
    
    def get_available_providers(self) -> List[Dict[str, Any]]:
        """
        Get all available LLM providers without models.
        Returns predefined providers without requiring API keys.
        """
        try:
            providers = []
            # Add providers from any_llm
            for provider_enum in LLMProvider:
                provider_info = PROVIDER_NAMES_MAP.get(provider_enum)
                provider_default_name = provider_enum.replace("_", " ").title()
                display_name = provider_info.get("name", provider_default_name) if provider_info else provider_default_name
                
                providers.append({
                    "id": provider_enum,
                    "name": display_name,
                    "custom_api_base": provider_info.get("custom_api_base", False) if provider_info else False
                })
            
            # Add Z.AI provider (not in any_llm)
            zai_info = PROVIDER_NAMES_MAP.get("zai")
            if zai_info:
                providers.append({
                    "id": "zai",
                    "name": zai_info.get("name", "Z.AI"),
                    "custom_api_base": zai_info.get("custom_api_base", False)
                })
            
            # Add LiteLLM provider (not in any_llm)
            litellm_info = PROVIDER_NAMES_MAP.get("litellm")
            if litellm_info:
                providers.append({
                    "id": "litellm",
                    "name": litellm_info.get("name", "LiteLLM"),
                    "custom_api_base": litellm_info.get("custom_api_base", True)
                })
            
            return providers
            
        except Exception as e:
            logger.error(f"Error getting available providers: {e}")
            return []

    async def fetch_models_by_provider(self, provider_id: str, api_key: str, api_base: str = "") -> List[ModelInfo]:
        """
        Fetch available models for a specific provider using API key.
        Connects to the actual provider APIs to get real-time model information.
        """
        try:
            models = []
            
            # Handle Z.AI provider separately
            if provider_id == "zai":
                zai_service = ZAILlmProvider(api_key=api_key, api_base=api_base or "https://api.z.ai/api/coding/paas/v4")
                available_models = zai_service.get_available_models()
                models = [
                    ModelInfo(id=model_id, name=model_id)
                    for model_id in available_models
                ]
            elif provider_id == "litellm":
                # Handle LiteLLM provider separately
                if not api_base:
                    raise ValueError(f"API base URL is required for LiteLLM provider")
                litellm_service = LiteLLMProvider(api_key=api_key, api_base=api_base)
                available_models = litellm_service.get_available_models()
                models = [
                    ModelInfo(id=model_id, name=model_id)
                    for model_id in available_models
                ]
            elif provider_id in LLMProvider.__members__.values():
                # Handle any_llm providers
                raw_models = await alist_models(provider_id, api_key, api_base=api_base)
                models = [
                    ModelInfo(id=model.id, name=model.id)
                    for model in raw_models
                    if model.id and model.object == 'model'
                ]
            else:
                logger.error(f"Unsupported provider: {provider_id}")
                raise ValueError(f"Unsupported provider: {provider_id}")
            
            logger.info(f"Returning {len(models)} models for provider {provider_id}")
            return models
            
        except Exception as e:
            logger.error(f"Error fetching models for provider {provider_id}: {e}")
            return []