"""
Refactored configuration service using Strategy Pattern.
Delegates hosting-specific logic to strategy objects.
"""

from pathlib import Path
from typing import List, Optional, Any, Dict
from schemas.config import AppConfig
from settings.base_settings import settings
from .strategy_base import ConfigStrategy
from .factory import ConfigStrategyFactory


class ConfigService:
    """
    Refactored configuration service using Strategy Pattern.
    Delegates hosting-specific logic to strategy objects.
    """
    
    def __init__(self):
        """Initialize service with current configuration."""
        self._config = settings.app_config
        self._strategy = ConfigStrategyFactory.create_strategy(
            self._config.hostingType, 
            self._config
        )
    
    def set_strategy(self, strategy: ConfigStrategy) -> None:
        """
        Set a custom strategy (useful for testing).
        
        Args:
            strategy: The configuration strategy to use
        """
        self._strategy = strategy
    
    def validate_app_config(self, config: Optional[AppConfig] = None) -> bool:
        """
        Validate app configuration completeness for hosting type.
        
        Args:
            config: Optional config to validate (defaults to current config)
            
        Returns:
            bool: True if configuration is valid
        """
        if config:
            strategy = ConfigStrategyFactory.create_strategy(
                config.hostingType, 
                config
            )
            return strategy.validate()
        return self._strategy.validate()
    
    def get_missing_config_items(self) -> List[str]:
        """
        Get list of missing required configuration items.
        
        Returns:
            List[str]: List of missing configuration field names
        """
        return self._strategy.get_missing_items()
    
    def is_config_complete(self) -> bool:
        """
        Check if current configuration is complete.
        
        Returns:
            bool: True if configuration is complete
        """
        return self._strategy.validate()
    
    def update_env_vars_from_config(self, config: AppConfig) -> None:
        """
        Update .env file with configuration values.
        
        Args:
            config: The configuration to save to environment
        """
        env_file_path = Path(".env")
        
        # Read existing .env file
        existing_env = {}
        if env_file_path.exists():
            with open(env_file_path, 'r') as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith('#') and '=' in line:
                        key, value = line.split('=', 1)
                        existing_env[key.strip()] = value.strip()
        
        # Create strategy for the config and update env vars
        strategy = ConfigStrategyFactory.create_strategy(
            config.hostingType, 
            config
        )
        updated_env = strategy.set_hosting_type(existing_env)
        updated_env = strategy.set_oauth_config(updated_env)
        updated_env = strategy.set_llm_config(updated_env)
        
        # Write updated .env file
        with open(env_file_path, 'w') as f:
            for key, value in updated_env.items():
                if key == "HOSTING_TYPE":
                    f.write(f'{key}="{value}"\n')
                else:
                    f.write(f"{key}={value}\n")
        
        # Reload settings to reflect changes
        settings.reload_settings()
        
        # Update current strategy if hosting type changed
        if config.hostingType != self._config.hostingType:
            self._config = config
            self._strategy = ConfigStrategyFactory.create_strategy(
                config.hostingType, 
                config
            )
    
    # Additional helper methods leveraging strategy
    def is_oauth_required(self) -> bool:
        """
        Check if OAuth is required for current hosting type.
        
        Returns:
            bool: True if OAuth is required
        """
        return self._strategy.is_oauth_required()
    
    def is_llm_required(self) -> bool:
        """
        Check if LLM configuration is required for current hosting type.
        
        Returns:
            bool: True if LLM configuration is required
        """
        return self._strategy.is_llm_required()
    
    # Backward compatibility methods for LLM configurations
    def get_all_llm_configs(self) -> List:
        """
        Get all configured LLM providers/models.
        For backward compatibility with existing code.
        
        Returns:
            List: List of LLM configurations
        """
        return self._config.llmConfigs if self._config.llmConfigs else []
    
    def get_configured_providers(self) -> List[str]:
        """
        Get list of all configured provider names.
        For backward compatibility with existing code.
        
        Returns:
            List[str]: List of provider names
        """
        providers = set()
        for config in self.get_all_llm_configs():
            providers.add(config.provider)
        return list(providers)
    
    @staticmethod
    def get_api_config_for_provider_model(provider: str, model: str) -> tuple[str, str | None]:
        """
        Get API key and base URL from settings for the given provider/model combination.
        For backward compatibility with existing code.
        
        Args:
            provider: Provider name
            model: Model name
            
        Returns:
            tuple: API key and optional base URL
        """
        from settings.base_settings import settings
        from fastapi import HTTPException
        
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
    
    def get_env_vars(self) -> Dict[str, str]:
        """Get environment variables based on current hosting type."""
        env_dict = {}
        
        if self._strategy:
            env_dict = self._strategy.set_hosting_type(env_dict)
            env_dict = self._strategy.set_oauth_config(env_dict)
            env_dict = self._strategy.set_llm_config(env_dict)
        
        return env_dict
    
    def get_oauth_config(self) -> Dict[str, Any]:
        """Get OAuth configuration."""
        if self._strategy:
            return self._strategy.get_oauth_config()
        return {}
    
    def get_llm_config(self) -> Dict[str, Any]:
        """Get LLM configuration."""
        if self._strategy:
            return self._strategy.get_llm_config()
        return {"llmConfigs": []}
    
    # Existing methods that don't require strategy pattern
    def get_hosting_type(self) -> str:
        """Get current hosting type."""
        if self._strategy:
            return self._strategy.get_hosting_type()
        return self._config.hostingType
    
    def get_current_config(self) -> AppConfig:
        """Get current config from settings."""
        return self._config
    
    def get_config(self) -> AppConfig:
        """
        Get the current configuration.
        Alias for get_current_config() for backward compatibility.
        
        Returns:
            AppConfig: The current application configuration
        """
        return self._config
    
    def get_supported_hosting_types(self) -> List[str]:
        """
        Get list of all supported hosting types.
        
        Returns:
            List[str]: List of supported hosting type identifiers
        """
        return ConfigStrategyFactory.get_supported_types()
    
    def can_switch_hosting_type(self, new_hosting_type: str, config: Optional[AppConfig] = None) -> bool:
        """
        Check if switching to a new hosting type is valid with given config.
        
        Args:
            new_hosting_type: The hosting type to switch to
            config: Optional config to validate (defaults to current config)
            
        Returns:
            bool: True if the switch would result in a valid configuration
        """
        test_config = config or self._config
        # Create a copy with new hosting type
        test_config_dict = test_config.model_dump()
        test_config_dict['hostingType'] = new_hosting_type
        test_config = AppConfig(**test_config_dict)
        
        try:
            strategy = ConfigStrategyFactory.create_strategy(
                new_hosting_type, 
                test_config
            )
            return strategy.validate()
        except ValueError:
            # Unsupported hosting type
            return False
    
    def is_hosting_type(self, hosting_type: str) -> bool:
        """
        Check if current hosting matches specified type.
        For backward compatibility with existing code.
        
        Args:
            hosting_type: The hosting type to check against
            
        Returns:
            bool: True if current hosting type matches
        """
        return self._config.hostingType == hosting_type
    
    def get_github_oauth_config(self) -> tuple[str, str]:
        """
        Get GitHub OAuth client ID and secret.
        For backward compatibility with existing code.
        
        Returns:
            tuple: GitHub client ID and client secret
        """
        return self._config.githubClientId or "", self._config.githubClientSecret or ""
    
    def is_github_oauth_configured(self) -> bool:
        """
        Check if GitHub OAuth is properly configured.
        For backward compatibility with existing code.
        
        Returns:
            bool: True if both client ID and secret are configured
        """
        client_id, client_secret = self.get_github_oauth_config()
        return bool(client_id and client_secret)