from typing import List
from services.config import ConfigStrategyFactory
from services.config.models import OAuthConfig, LLMConfig, RepoConfig, HostingConfig

class ConfigService:
    def __init__(self):
        self.config = ConfigStrategyFactory.get_strategy()

    def get_config(self):
        return self.config.get_config()
    
    def get_hosting_config(self) -> HostingConfig:
        return self.config.get_hosting_config()
    
    def get_oauth_configs(self) -> List[OAuthConfig] | None:
        return self.config.get_oauth_configs()
    
    def get_llm_configs(self) -> List[LLMConfig] | None:
        return self.config.get_llm_configs()
    
    def get_repo_configs(self) -> List[RepoConfig] | None:
        return self.config.get_repo_configs()
    
    def set_hosting_type(self) -> HostingConfig:
        return self.config.set_hosting_type()
    
    def set_oauth_configs(self, oauth_configs: List[OAuthConfig]) -> List[OAuthConfig] | None:
        return self.config.set_oauth_configs(oauth_configs)
    
    def set_llm_configs(self, llm_configs: List[LLMConfig]) -> List[LLMConfig] | None:
        return self.config.set_llm_configs(llm_configs)
    
    def set_repo_configs(self, repo_configs: List[RepoConfig]) -> List[RepoConfig] | None:
        return self.config.set_repo_configs(repo_configs)
    
    @classmethod
    def get_supported_types(cls) -> List[str]:
        """Get list of all supported hosting types."""
        return ConfigStrategyFactory.get_supported_types()
