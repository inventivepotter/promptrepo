"""
Provider service for LLM providers and models.
Handles provider information, configured providers, and model fetching.
"""
from typing import Dict, List, Any
import logging
from any_llm import LLMProvider
from any_llm.api import list_models

from services.config.config_service import ConfigService
from services.llm.models import ProviderInfo, ModelInfo, ProvidersResponse
from utils.constants import PROVIDER_NAMES_MAP

logger = logging.getLogger(__name__)


class ProviderService:
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
            for provider_enum in LLMProvider:
                provider_info = PROVIDER_NAMES_MAP.get(provider_enum)
                provider_default_name = provider_enum.replace("_", " ").title()
                display_name = provider_info.get("name", provider_default_name) if provider_info else provider_default_name
                
                providers.append({
                    "id": provider_enum,
                    "name": display_name,
                    "custom_api_base": provider_info.get("custom_api_base", False) if provider_info else False
                })
            
            return providers
            
        except Exception as e:
            logger.error(f"Error getting available providers: {e}")
            return []

    def fetch_models_by_provider(self, provider_id: str, user_id: str) -> List[ModelInfo]:
        """
        Fetch available models for a specific provider using API key.
        Connects to the actual provider APIs to get real-time model information.
        """
        try:
            models = []
            if provider_id not in LLMProvider.__members__.values():
                logger.error(f"Unsupported provider: {provider_id}")
                raise ValueError(f"Unsupported provider: {provider_id}")
            
            llm_configs = self.config_service.get_llm_configs(user_id=user_id) or []
            matching_configs = [cfg for cfg in llm_configs if cfg.provider == provider_id]
            if not matching_configs:
                logger.warning(f"No configuration found for provider {provider_id} for user {user_id}")
                raise ValueError(f"No configuration found for provider {provider_id}")
            llm_config = matching_configs[0]

            raw_models = list_models(provider_id, llm_config.api_key, api_base=llm_config.api_base_url)
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