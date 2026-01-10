"""
Provider service for LLM providers and models.
Handles provider information, configured providers, and model fetching.
"""
from typing import Dict, List, Any
import logging
from any_llm.constants import LLMProvider
from lib.any_llm.any_llm_adapter import alist_models

from services.config.config_service import ConfigService
from services.llm.models import ProviderInfo, ModelInfo, ProvidersResponse
from utils.constants import PROVIDER_NAMES_MAP

logger = logging.getLogger(__name__)


class ModelProviderService:
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
            existing_ids = set()
            
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
                existing_ids.add(provider_enum)
            
            # Add Z.AI provider only if not already in any_llm
            if "zai" not in existing_ids:
                zai_info = PROVIDER_NAMES_MAP.get("zai")
                if zai_info:
                    providers.append({
                        "id": "zai",
                        "name": zai_info.get("name", "Z.AI"),
                        "custom_api_base": zai_info.get("custom_api_base", False)
                    })
            
            # Add LiteLLM provider only if not already in any_llm
            if "litellm" not in existing_ids:
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
            
            # Handle all providers with any-llm unified interface
            # For custom providers (zai, litellm), they're now part of any-llm ecosystem
            raw_models = await alist_models(provider_id, api_key, api_base=api_base or "")
            models = [
                ModelInfo(id=model.id, name=model.id)
                for model in raw_models
                if model.id and model.object == 'model'
            ]
            
            logger.info(f"Returning {len(models)} models for provider {provider_id}")
            return models
            
        except Exception as e:
            logger.error(f"Error fetching models for provider {provider_id}: {e}")
            return []