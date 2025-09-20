"""
Standalone test suite for configuration strategies
Tests IndividualConfig, OrganizationConfig, and MultiTenantConfig strategies
"""
import pytest
import os
from services.config import IndividualConfig, OrganizationConfig, MultiTenantConfig
from schemas.config import HostingType, LLMConfig, OAuthConfig, RepoConfig
from typing import List


# Now create a simplified version of the factory
class ConfigStrategyFactory:
    """Simplified factory for testing."""
    
    _strategies = {
        HostingType.INDIVIDUAL: IndividualConfig,
        HostingType.ORGANIZATION: OrganizationConfig,
        HostingType.MULTI_TENANT: MultiTenantConfig
    }
    
    @classmethod
    def get_strategy(cls):
        """Create appropriate configuration strategy for the hosting type."""
        hosting_type = os.environ.get("HOSTING_TYPE", "individual")
        try:
            hosting_type_enum = HostingType(hosting_type)
        except ValueError:
            raise ValueError(f"Unsupported hosting type: {hosting_type}")
        
        strategy_class = cls._strategies.get(hosting_type_enum)
        if not strategy_class:
            raise ValueError(f"Unsupported hosting type: {hosting_type}")
        
        return strategy_class()
    
    @classmethod
    def get_supported_types(cls) -> List[str]:
        """Get list of all supported hosting types."""
        return HostingType._member_names_


class TestIndividualConfigStrategyStandalone:
    """Test cases for IndividualConfig strategy (standalone)"""
    
    def setup_method(self):
        """Setup before each test"""
        # Clean environment variables
        self.env_vars_to_clean = [
            "HOSTING_TYPE",
            "GITHUB_CLIENT_ID",
            "GITHUB_CLIENT_SECRET",
            "LLM_CONFIGS",
            "TENANT_ID"
        ]
        for var in self.env_vars_to_clean:
            if var in os.environ:
                del os.environ[var]
        
        # Set hosting type
        os.environ["HOSTING_TYPE"] = "individual"
        
        # Get strategy from factory
        self.strategy = ConfigStrategyFactory.get_strategy()
    
    def teardown_method(self):
        """Cleanup after each test"""
        for var in self.env_vars_to_clean:
            if var in os.environ:
                del os.environ[var]
    
    def test_factory_creates_individual_strategy(self):
        """Test factory creates IndividualConfig strategy"""
        assert self.strategy.__class__.__name__ == "IndividualConfig"
    
    def test_get_hosting_config(self):
        """Test getting hosting config from ENV"""
        hosting_config = self.strategy.get_hosting_config()
        assert hosting_config.type == HostingType.INDIVIDUAL
    
    def test_oauth_config_returns_none(self):
        """Test OAuth config returns None for individual"""
        oauth_config = self.strategy.get_oauth_config()
        assert oauth_config is None
    
    def test_set_and_get_llm_config(self):
        """Test setting and getting LLM config from ENV"""
        llm_configs = [
            LLMConfig(
                provider="openai",
                model="gpt-4",
                apiKey="test-key-individual",
                apiBaseUrl="https://api.openai.com"
            )
        ]
        
        set_result = self.strategy.set_llm_config(llm_configs)
        assert set_result == llm_configs
        
        retrieved_llm = self.strategy.get_llm_config()
        assert retrieved_llm is not None
        assert len(retrieved_llm) == 1
        assert retrieved_llm[0].provider == "openai"
        assert retrieved_llm[0].apiKey == "test-key-individual"
    
    def test_repo_config_returns_none(self):
        """Test repo config returns None for individual"""
        repo_config = self.strategy.get_repo_config()
        assert repo_config is None
    
    def test_oauth_setter_returns_none(self):
        """Test OAuth setter returns None for individual"""
        oauth_set_result = self.strategy.set_oauth_config("test-id", "test-secret")
        assert oauth_set_result is None
    
    def test_repo_setter_returns_none(self):
        """Test repo setter returns None for individual"""
        repo_set_result = self.strategy.set_repo_config([
            RepoConfig(repo_url="https://github.com/test/repo", base_branch="main", current_branch="main")
        ])
        assert repo_set_result is None


class TestOrganizationConfigStrategyStandalone:
    """Test cases for OrganizationConfig strategy (standalone)"""
    
    def setup_method(self):
        """Setup before each test"""
        # Clean environment variables
        self.env_vars_to_clean = [
            "HOSTING_TYPE",
            "GITHUB_CLIENT_ID",
            "GITHUB_CLIENT_SECRET",
            "LLM_CONFIGS",
            "TENANT_ID"
        ]
        for var in self.env_vars_to_clean:
            if var in os.environ:
                del os.environ[var]
        
        # Set hosting type
        os.environ["HOSTING_TYPE"] = "organization"
        
        # Get strategy from factory
        self.strategy = ConfigStrategyFactory.get_strategy()
    
    def teardown_method(self):
        """Cleanup after each test"""
        for var in self.env_vars_to_clean:
            if var in os.environ:
                del os.environ[var]
    
    def test_factory_creates_organization_strategy(self):
        """Test factory creates OrganizationConfig strategy"""
        assert self.strategy.__class__.__name__ == "OrganizationConfig"
    
    def test_get_hosting_config(self):
        """Test getting hosting config from ENV"""
        hosting_config = self.strategy.get_hosting_config()
        assert hosting_config.type == HostingType.ORGANIZATION
    
    def test_set_and_get_oauth_config(self):
        """Test setting and getting OAuth config from ENV"""
        oauth_set_result = self.strategy.set_oauth_config("org-client-id", "org-client-secret")
        assert oauth_set_result is not None
        assert oauth_set_result.github_client_id == "org-client-id"
        
        retrieved_oauth = self.strategy.get_oauth_config()
        assert retrieved_oauth is not None
        assert retrieved_oauth.github_client_id == "org-client-id"
        assert retrieved_oauth.github_client_secret == "org-client-secret"
    
    def test_set_and_get_llm_config(self):
        """Test setting and getting LLM config from ENV"""
        llm_configs = [
            LLMConfig(
                provider="anthropic",
                model="claude-3",
                apiKey="test-key-org",
                apiBaseUrl="https://api.anthropic.com"
            )
        ]
        
        set_result = self.strategy.set_llm_config(llm_configs)
        assert set_result == llm_configs
        
        retrieved_llm = self.strategy.get_llm_config()
        assert retrieved_llm is not None
        assert len(retrieved_llm) == 1
        assert retrieved_llm[0].provider == "anthropic"
        assert retrieved_llm[0].apiKey == "test-key-org"
    
    def test_set_and_get_repo_config(self):
        """Test setting and getting repo config (in-memory)"""
        repo_configs = [
            RepoConfig(repo_url="https://github.com/org/repo1", base_branch="main", current_branch="main"),
            RepoConfig(repo_url="https://github.com/org/repo2", base_branch="develop", current_branch="develop")
        ]
        
        # Set repo config - should return first config
        repo_set_result = self.strategy.set_repo_config(repo_configs)
        assert repo_set_result is not None
        assert repo_set_result.repo_url == "https://github.com/org/repo1"
        
        # Get repo config - currently returns None as it's user-specific
        retrieved_repo = self.strategy.get_repo_config()
        assert retrieved_repo is None  # Expected as it's user-specific


class TestMultiTenantConfigStrategyStandalone:
    """Test cases for MultiTenantConfig strategy (standalone)"""
    
    def setup_method(self):
        """Setup before each test"""
        # Clean environment variables
        self.env_vars_to_clean = [
            "HOSTING_TYPE",
            "GITHUB_CLIENT_ID",
            "GITHUB_CLIENT_SECRET",
            "LLM_CONFIGS",
            "TENANT_ID"
        ]
        for var in self.env_vars_to_clean:
            if var in os.environ:
                del os.environ[var]
        
        # Set hosting type and tenant ID
        os.environ["HOSTING_TYPE"] = "multi-tenant"
        os.environ["TENANT_ID"] = "test-tenant-1"
        
        # Get strategy from factory
        self.strategy = ConfigStrategyFactory.get_strategy()
    
    def teardown_method(self):
        """Cleanup after each test"""
        for var in self.env_vars_to_clean:
            if var in os.environ:
                del os.environ[var]
    
    def test_factory_creates_multi_tenant_strategy(self):
        """Test factory creates MultiTenantConfig strategy"""
        assert self.strategy.__class__.__name__ == "MultiTenantConfig"
    
    def test_get_hosting_config(self):
        """Test getting hosting config from ENV"""
        hosting_config = self.strategy.get_hosting_config()
        assert hosting_config.type == HostingType.MULTI_TENANT
    
    def test_set_and_get_oauth_config(self):
        """Test setting and getting OAuth config from ENV (system-wide)"""
        oauth_set_result = self.strategy.set_oauth_config("mt-client-id", "mt-client-secret")
        assert oauth_set_result is not None
        assert oauth_set_result.github_client_id == "mt-client-id"
        
        retrieved_oauth = self.strategy.get_oauth_config()
        assert retrieved_oauth is not None
        assert retrieved_oauth.github_client_id == "mt-client-id"
        assert retrieved_oauth.github_client_secret == "mt-client-secret"
    
    def test_set_and_get_llm_config(self):
        """Test setting and getting LLM config from users (in-memory)"""
        llm_configs = [
            LLMConfig(
                provider="azure",
                model="gpt-4",
                apiKey="test-key-tenant1",
                apiBaseUrl="https://tenant1.openai.azure.com"
            ),
            LLMConfig(
                provider="openai",
                model="gpt-3.5-turbo",
                apiKey="test-key-tenant1-backup",
                apiBaseUrl="https://api.openai.com"
            )
        ]
        
        set_result = self.strategy.set_llm_config(llm_configs)
        assert set_result == llm_configs
        
        retrieved_llm = self.strategy.get_llm_config()
        assert retrieved_llm is not None
        assert len(retrieved_llm) == 2
        assert retrieved_llm[0].provider == "azure"
        assert retrieved_llm[0].apiKey == "test-key-tenant1"
    
    def test_set_and_get_repo_config(self):
        """Test setting and getting repo config from users (in-memory)"""
        repo_configs = [
            RepoConfig(repo_url="https://github.com/tenant1/repo1", base_branch="main", current_branch="main"),
            RepoConfig(repo_url="https://github.com/tenant1/repo2", base_branch="feature", current_branch="feature")
        ]
        
        # Set repo config - should return first config
        repo_set_result = self.strategy.set_repo_config(repo_configs)
        assert repo_set_result is not None
        assert repo_set_result.repo_url == "https://github.com/tenant1/repo1"
        
        # Get repo config - should retrieve from in-memory storage
        retrieved_repo = self.strategy.get_repo_config()
        assert retrieved_repo is not None
        assert len(retrieved_repo) == 2
        assert retrieved_repo[0].repo_url == "https://github.com/tenant1/repo1"
    
    def test_tenant_isolation(self):
        """Test tenant isolation by switching tenant"""
        # Set system-wide OAuth config
        self.strategy.set_oauth_config("mt-client-id", "mt-client-secret")

        # First set configs for tenant 1
        llm_configs = [
            LLMConfig(provider="azure", model="gpt-4", apiKey="test-key-tenant1")
        ]
        repo_configs = [
            RepoConfig(repo_url="https://github.com/tenant1/repo1", base_branch="main", current_branch="main")
        ]
        
        self.strategy.set_llm_config(llm_configs)
        self.strategy.set_repo_config(repo_configs)
        
        # Switch tenant
        os.environ["TENANT_ID"] = "test-tenant-2"
        
        # Get configs for tenant 2 - should be empty/None
        retrieved_llm_t2 = self.strategy.get_llm_config()
        assert retrieved_llm_t2 is None
        
        retrieved_repo_t2 = self.strategy.get_repo_config()
        assert retrieved_repo_t2 is None
        
        # OAuth should still be available (system-wide)
        retrieved_oauth_t2 = self.strategy.get_oauth_config()
        assert retrieved_oauth_t2 is not None
        assert retrieved_oauth_t2.github_client_id == "mt-client-id"


class TestConfigStrategyFactoryStandalone:
    """Test cases for ConfigStrategyFactory (standalone)"""
    
    def setup_method(self):
        """Setup before each test"""
        # Clean environment variables
        self.env_vars_to_clean = ["HOSTING_TYPE"]
        for var in self.env_vars_to_clean:
            if var in os.environ:
                del os.environ[var]
    
    def teardown_method(self):
        """Cleanup after each test"""
        for var in self.env_vars_to_clean:
            if var in os.environ:
                del os.environ[var]
    
    def test_get_supported_types(self):
        """Test factory's supported types method"""
        supported_types = ConfigStrategyFactory.get_supported_types()
        expected_types = ['INDIVIDUAL', 'ORGANIZATION', 'MULTI_TENANT']
        assert set(supported_types) == set(expected_types)
    
    def test_invalid_hosting_type(self):
        """Test factory behavior with invalid hosting type"""
        # Set invalid hosting type
        os.environ["HOSTING_TYPE"] = "invalid_type"
        
        with pytest.raises(ValueError) as excinfo:
            ConfigStrategyFactory.get_strategy()
        
        assert "Unsupported hosting type" in str(excinfo.value)