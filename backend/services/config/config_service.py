from typing import List, Optional, TYPE_CHECKING
from sqlmodel import Session
from services.config.config_factory import ConfigStrategyFactory
from schemas.hosting_type_enum import HostingType
from services.config.models import OAuthConfig, LLMConfig, LLMConfigScope, RepoConfig, HostingConfig, AppConfig
from services.config.config_interface import IConfig

if TYPE_CHECKING:
    from services.remote_repo.remote_repo_service import RemoteRepoService

class ConfigService:
    def __init__(
        self,
        db: Optional[Session] = None,
        config_strategy: Optional[IConfig] = None
    ):
        """
        Initialize ConfigService with dependencies.
        
        Args:
            db: Database session (optional, required for repo configs)
            config_strategy: Configuration strategy (optional, defaults to factory-created)
        """
        self.db = db
        self.config = config_strategy or ConfigStrategyFactory.get_strategy()

    def get_hosting_config(self) -> HostingConfig:
        return self.config.get_hosting_config()
    
    def get_oauth_configs(self) -> List[OAuthConfig] | None:
        return self.config.get_oauth_configs()
    
    def get_llm_configs(self, user_id: str) -> List[LLMConfig] | None:
        if not self.db:
            raise ValueError("Database session required for LLM configs")
        return self.config.get_llm_configs(self.db, user_id)
    
    def get_repo_configs(self, user_id: str) -> List[RepoConfig] | None:
        if not self.db:
            raise ValueError("Database session required for repo configs")
        return self.config.get_repo_configs(self.db, user_id)

    def get_app_config(self, user_id: str) -> AppConfig:
        """
        Constructs the full AppConfig object by calling individual getters.
        This method replaces the previous get_config() which was on the interface.
        """
        hosting_config = self.get_hosting_config()
        oauth_configs = self.get_oauth_configs()
        llm_configs = self.get_llm_configs(user_id)
        repo_configs = self.get_repo_configs(user_id)
        
        return AppConfig(
            hosting_config=hosting_config,
            oauth_configs=oauth_configs,
            llm_configs=llm_configs,
            repo_configs=repo_configs
        )
    
    def set_oauth_configs(self, oauth_configs: List[OAuthConfig]) -> List[OAuthConfig] | None:
        return self.config.set_oauth_configs(oauth_configs)
    
    def set_llm_configs(self, user_id: str, llm_configs: List[LLMConfig]) -> List[LLMConfig] | None:
        if not self.db:
            raise ValueError("Database session required for LLM configs")
        return self.config.set_llm_configs(self.db, user_id, llm_configs)
    
    def set_repo_configs(self, user_id: str, repo_configs: List[RepoConfig], remote_repo_service: Optional['RemoteRepoService'] = None) -> List[RepoConfig] | None:
        if not self.db:
            raise ValueError("Database session required for repo configs")
        return self.config.set_repo_configs(self.db, user_id, repo_configs, remote_repo_service)
    
    @classmethod
    def get_supported_types(cls) -> List[str]:
        """Get list of all supported hosting types."""
        return ConfigStrategyFactory.get_supported_types()
    
    def get_configs_for_public_api(self) -> AppConfig:
        hosting_config = self.get_hosting_config()
        oauth_configs = None
        if hosting_config.type == HostingType.ORGANIZATION:
            raw_oauth_configs = self.get_oauth_configs()
            if raw_oauth_configs:
                oauth_configs = [OAuthConfig(provider=config.provider) for config in raw_oauth_configs]
        
        return AppConfig(
            hosting_config=hosting_config,
            oauth_configs=oauth_configs,  # Include OAuth configs in API response
            llm_configs=None,
            repo_configs=None
        )
    
    def get_configs_for_api(self, user_id: str) -> AppConfig:
        """
        Get configuration tailored for API response based on hosting type.
        This method applies business logic to determine which configs are relevant.
        Strips api_key and api_base_url from organization-scoped LLM configs.
        """
        configs = self.get_configs_for_public_api()
        
        raw_llm_configs = self.get_llm_configs(user_id)
        if raw_llm_configs:
            configs.llm_configs = []
            for config in raw_llm_configs:
                # Strip sensitive info from oauth configs
                sanitized_config = LLMConfig(
                    id=config.id,
                    provider=config.provider,
                    model=config.model,
                    api_key="",  # Strip api_key
                    api_base_url="",  # Strip api_base_url
                    scope=config.scope
                )
                configs.llm_configs.append(sanitized_config)
        
        # Apply business rules: individual hosting doesn't need repo configs
        if configs.hosting_config and configs.hosting_config.type == HostingType.ORGANIZATION:
            # Get repo configs
            configs.repo_configs = self.get_repo_configs(user_id)
        
        return configs

    def save_configs_for_api(
        self,
        user_id: str,
        llm_configs: List[LLMConfig] | None,
        repo_configs: List[RepoConfig] | None,
        remote_repo_service: Optional['RemoteRepoService'] = None
    ) -> AppConfig:
        """
        Save configurations based on hosting type with validation.
        
        Args:
            user_id: The user ID to save configurations for
            llm_configs: LLM configurations to save (optional)
            repo_configs: Repository configurations to save (optional)
            remote_repo_service: Optional RemoteRepoService for cloning repositories
            
        Returns:
            AppConfig: Updated configuration after saving
            
        Raises:
            ValueError: If validation fails or required database session is missing
        """
        hosting_type = self.get_hosting_config().type
        
        # Validate and save LLM configs for all hosting types
        if llm_configs is not None:
            self._validate_llm_configs(llm_configs)
            self.set_llm_configs(user_id=user_id, llm_configs=llm_configs)
        
        # Validate and save repo configs only for appropriate hosting types
        if repo_configs is not None and hosting_type != HostingType.INDIVIDUAL:
            self._validate_repo_configs(repo_configs)
            self.set_repo_configs(user_id=user_id, repo_configs=repo_configs, remote_repo_service=remote_repo_service)

        return self.get_configs_for_api(user_id=user_id)
    
    def _validate_llm_configs(self, llm_configs: List[LLMConfig]) -> None:
        """Validate LLM configurations before saving."""
        for config in llm_configs:
            if not config.provider:
                raise ValueError("LLM provider is required")
            if not config.model:
                raise ValueError("LLM model is required")
    
    def _validate_repo_configs(self, repo_configs: List[RepoConfig]) -> None:
        """Validate repository configurations before saving."""
        for config in repo_configs:
            if not config.repo_name:
                raise ValueError("Repository name is required")
            if not config.repo_url:
                raise ValueError("Repository URL is required")
