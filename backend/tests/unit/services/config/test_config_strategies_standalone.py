"""
Standalone test suite for configuration strategies
Tests IndividualConfig, OrganizationConfig, and MultiTenantConfig strategies
"""
import pytest
import os
from services.config import ConfigStrategyFactory
from schemas.hosting_type_enum import HostingType
from services.config.models import LLMConfig, OAuthConfig, RepoConfig


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
        
        # Get strategy from service
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
    
    def test_oauth_configs_returns_none(self):
        """Test OAuth configs returns None for individual"""
        oauth_configs = self.strategy.get_oauth_configs()
        assert oauth_configs is None
    
    def test_set_and_get_llm_configs(self):
        """Test setting and getting LLM configs from ENV"""
        llm_configs = [
            LLMConfig(
                provider="openai",
                model="gpt-4",
                api_key="test-key-individual",
                api_base_url="https://api.openai.com"
            )
        ]
        
        set_result = self.strategy.set_llm_configs(llm_configs)
        assert set_result == llm_configs
        
        retrieved_llm = self.strategy.get_llm_configs()
        assert retrieved_llm is not None
        assert len(retrieved_llm) == 1
        assert retrieved_llm[0].provider == "openai"
        assert retrieved_llm[0].api_key == "test-key-individual"
    
    def test_repo_configs_returns_none(self):
        """Test repo configs returns None for individual"""
        repo_configs = self.strategy.get_repo_configs()
        assert repo_configs is None
    
    def test_oauth_setter_returns_none(self):
        """Test OAuth setter returns None for individual"""
        oauth_config = OAuthConfig(
            provider="github",
            client_id="test-id",
            client_secret="test-secret"
        )
        oauth_set_result = self.strategy.set_oauth_configs([oauth_config])
        assert oauth_set_result is None
    
    def test_repo_setter_returns_none(self):
        """Test repo setter returns None for individual"""
        repo_set_result = self.strategy.set_repo_configs([
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
        
        # Get strategy from service
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
    
    def test_set_and_get_oauth_configs(self):
        """Test setting and getting OAuth configs from ENV"""
        oauth_config = OAuthConfig(
            provider="github",
            client_id="org-client-id",
            client_secret="org-client-secret"
        )
        oauth_set_result = self.strategy.set_oauth_configs([oauth_config])
        assert oauth_set_result is not None
        assert oauth_set_result[0].client_id == "org-client-id"
        
        retrieved_oauth = self.strategy.get_oauth_configs()
        assert retrieved_oauth is not None
        assert retrieved_oauth[0].client_id == "org-client-id"
        assert retrieved_oauth[0].client_secret == "org-client-secret"
    
    def test_set_and_get_llm_configs(self):
        """Test setting and getting LLM configs from ENV"""
        llm_configs = [
            LLMConfig(
                provider="anthropic",
                model="claude-3",
                api_key="test-key-org",
                api_base_url="https://api.anthropic.com"
            )
        ]
        
        set_result = self.strategy.set_llm_configs(llm_configs)
        assert set_result == llm_configs
        
        retrieved_llm = self.strategy.get_llm_configs()
        assert retrieved_llm is not None
        assert len(retrieved_llm) == 1
        assert retrieved_llm[0].provider == "anthropic"
        assert retrieved_llm[0].api_key == "test-key-org"
    
    def test_set_and_get_repo_configs(self):
        """Test setting and getting repo configs (in-memory)"""
        repo_configs = [
            RepoConfig(repo_url="https://github.com/org/repo1", base_branch="main", current_branch="main"),
            RepoConfig(repo_url="https://github.com/org/repo2", base_branch="develop", current_branch="develop")
        ]
        
        # Set repo configs
        repo_set_result = self.strategy.set_repo_configs(repo_configs)
        assert repo_set_result is not None
        assert len(repo_set_result) == 2
        
        # Get repo configs - currently returns None as it's user-specific
        retrieved_repo = self.strategy.get_repo_configs()
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
        
        # Get strategy from service
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
    
    def test_set_and_get_oauth_configs(self):
        """Test setting and getting OAuth configs from ENV (system-wide)"""
        oauth_config = OAuthConfig(
            provider="github",
            client_id="mt-client-id",
            client_secret="mt-client-secret"
        )
        oauth_set_result = self.strategy.set_oauth_configs([oauth_config])
        assert oauth_set_result is not None
        assert oauth_set_result[0].client_id == "mt-client-id"
        
        retrieved_oauth = self.strategy.get_oauth_configs()
        assert retrieved_oauth is not None
        assert retrieved_oauth[0].client_id == "mt-client-id"
        assert retrieved_oauth[0].client_secret == "mt-client-secret"
    
    def test_set_and_get_llm_configs(self):
        """Test setting and getting LLM configs from users (in-memory)"""
        llm_configs = [
            LLMConfig(
                provider="azure",
                model="gpt-4",
                api_key="test-key-tenant1",
                api_base_url="https://tenant1.openai.azure.com"
            ),
            LLMConfig(
                provider="openai",
                model="gpt-3.5-turbo",
                api_key="test-key-tenant1-backup",
                api_base_url="https://api.openai.com"
            )
        ]
        
        set_result = self.strategy.set_llm_configs(llm_configs)
        assert set_result == llm_configs
        
        retrieved_llm = self.strategy.get_llm_configs()
        assert retrieved_llm is not None
        assert len(retrieved_llm) == 2
        assert retrieved_llm[0].provider == "azure"
        assert retrieved_llm[0].api_key == "test-key-tenant1"
    
    def test_set_and_get_repo_configs(self):
        """Test setting and getting repo configs from users (in-memory)"""
        repo_configs = [
            RepoConfig(repo_url="https://github.com/tenant1/repo1", base_branch="main", current_branch="main"),
            RepoConfig(repo_url="https://github.com/tenant1/repo2", base_branch="feature", current_branch="feature")
        ]
        
        # Set repo configs
        repo_set_result = self.strategy.set_repo_configs(repo_configs)
        assert repo_set_result is not None
        assert len(repo_set_result) == 2
        
        # Get repo configs - should retrieve from in-memory storage
        retrieved_repo = self.strategy.get_repo_configs()
        assert retrieved_repo is not None
        assert len(retrieved_repo) == 2
        assert retrieved_repo[0].repo_url == "https://github.com/tenant1/repo1"
    
    def test_tenant_isolation(self):
        """Test tenant isolation by switching tenant"""
        # Set system-wide OAuth config
        oauth_config = OAuthConfig(
            provider="github",
            client_id="mt-client-id",
            client_secret="mt-client-secret"
        )
        self.strategy.set_oauth_configs([oauth_config])

        # First set configs for tenant 1
        llm_configs = [
            LLMConfig(provider="azure", model="gpt-4", api_key="test-key-tenant1")
        ]
        repo_configs = [
            RepoConfig(repo_url="https://github.com/tenant1/repo1", base_branch="main", current_branch="main")
        ]
        
        self.strategy.set_llm_configs(llm_configs)
        self.strategy.set_repo_configs(repo_configs)
        
        # Switch tenant
        os.environ["TENANT_ID"] = "test-tenant-2"
        
        # Get configs for tenant 2 - should be empty/None
        retrieved_llm_t2 = self.strategy.get_llm_configs()
        assert retrieved_llm_t2 is None
        
        retrieved_repo_t2 = self.strategy.get_repo_configs()
        assert retrieved_repo_t2 is None
        
        # OAuth should still be available (system-wide)
        retrieved_oauth_t2 = self.strategy.get_oauth_configs()
        assert retrieved_oauth_t2 is not None
        assert retrieved_oauth_t2[0].client_id == "mt-client-id"


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