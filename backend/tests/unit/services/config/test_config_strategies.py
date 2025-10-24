"""
Test suite for configuration strategies
Tests IndividualConfig, OrganizationConfig, and MultiTenantConfig strategies
"""
import pytest
import os
from unittest.mock import patch
from services.config import ConfigStrategyFactory
from schemas.hosting_type_enum import HostingType
from services.config.models import LLMConfig, OAuthConfig, RepoConfig, LLMConfigScope


class TestIndividualConfigStrategy:
    """Test cases for IndividualConfig strategy"""
    
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
    
    def test_oauth_configs_returns_none(self):
        """Test OAuth configs returns None for individual"""
        oauth_configs = self.strategy.get_oauth_configs()
        assert oauth_configs is None
    
    def test_set_and_get_llm_configs(self):
        """Test setting and getting LLM configs from ENV"""
        from unittest.mock import Mock, MagicMock
        llm_configs = [
            LLMConfig(
                id="test-llm-1",
                provider="openai",
                model="gpt-4",
                api_key="test-key-individual",
                api_base_url="https://api.openai.com",
                scope=LLMConfigScope.USER  # Set scope to user for individual strategy
            )
        ]
        
        # Mock database session and user_id
        mock_db = Mock()
        mock_user_id = "test-user-1"
        
        # Mock the UserLLMDAO methods
        mock_user_llm_dao = Mock()
        mock_user_llm_dao.get_llm_configs_for_user.return_value = []  # Empty list initially
        mock_user_llm_dao.add_llm_config.return_value = None
        mock_user_llm_dao.update_llm_config.return_value = None
        mock_user_llm_dao.delete_llm_config.return_value = None
        
        # Mock the UserDAO methods
        mock_user_dao = Mock()
        mock_user_dao.get_user_by_id.return_value = None  # User doesn't exist initially
        mock_user_dao.save_user.return_value = None
        
        # Patch the DAO imports
        with patch('services.config.strategies.individual.UserLLMDAO') as mock_user_llm_dao_class:
            mock_user_llm_dao_class.return_value = mock_user_llm_dao
            with patch('services.config.strategies.individual.UserDAO') as mock_user_dao_class:
                mock_user_dao_class.return_value = mock_user_dao
                
                try:
                    set_result = self.strategy.set_llm_configs(mock_db, mock_user_id, llm_configs)
                    assert set_result == llm_configs
                    
                    # Mock the returned config for get_llm_configs
                    mock_db_config = Mock()
                    mock_db_config.id = "test-llm-1"
                    mock_db_config.provider = "openai"
                    mock_db_config.model_name = "gpt-4"
                    mock_db_config.api_key = "test-key-individual"
                    mock_db_config.base_url = "https://api.openai.com"
                    mock_user_llm_dao.get_llm_configs_for_user.return_value = [mock_db_config]
                    
                    retrieved_llm = self.strategy.get_llm_configs(mock_db, mock_user_id)
                    assert retrieved_llm is not None
                    assert len(retrieved_llm) == 1
                    assert retrieved_llm[0].provider == "openai"
                    assert retrieved_llm[0].api_key == "test-key-individual"
                finally:
                    # No need to restore - patch handles this automatically
                    pass
    
    def test_repo_configs_returns_none(self):
        """Test repo configs returns None for individual"""
        from unittest.mock import Mock
        mock_db = Mock()
        mock_user_id = "test-user-1"
        repo_configs = self.strategy.get_repo_configs(mock_db, mock_user_id)
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
        from unittest.mock import Mock
        mock_db = Mock()
        mock_user_id = "test-user-1"
        repo_set_result = self.strategy.set_repo_configs(mock_db, mock_user_id, [
            RepoConfig(id="test-repo-1", repo_url="https://github.com/test/repo", base_branch="main", current_branch="main")
        ])
        assert repo_set_result is None


class TestOrganizationConfigStrategy:
    """Test cases for OrganizationConfig strategy"""
    
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
        from unittest.mock import Mock, MagicMock
        llm_configs = [
            LLMConfig(
                id="test-llm-2",
                provider="anthropic",
                model="claude-3",
                api_key="test-key-org",
                api_base_url="https://api.anthropic.com",
                scope=LLMConfigScope.USER  # Set scope to user for organization strategy
            )
        ]
        
        # Mock database session and user_id
        mock_db = Mock()
        mock_user_id = "test-user-2"
        
        # Mock the UserLLMDAO methods
        mock_user_llm_dao = Mock()
        mock_user_llm_dao.get_llm_configs_for_user.return_value = []  # Empty list initially
        mock_user_llm_dao.add_llm_config.return_value = None
        mock_user_llm_dao.update_llm_config.return_value = None
        mock_user_llm_dao.delete_llm_config.return_value = None
        
        # Patch the DAO import
        with patch('services.config.strategies.organization.UserLLMDAO') as mock_user_llm_dao_class:
            mock_user_llm_dao_class.return_value = mock_user_llm_dao
            
            try:
                set_result = self.strategy.set_llm_configs(mock_db, mock_user_id, llm_configs)
                assert set_result == llm_configs
                
                # Mock the returned config for get_llm_configs
                mock_db_config = Mock()
                mock_db_config.id = "test-llm-2"
                mock_db_config.provider = "anthropic"
                mock_db_config.model_name = "claude-3"
                mock_db_config.api_key = "test-key-org"
                mock_db_config.base_url = "https://api.anthropic.com"
                mock_user_llm_dao.get_llm_configs_for_user.return_value = [mock_db_config]
                
                retrieved_llm = self.strategy.get_llm_configs(mock_db, mock_user_id)
                assert retrieved_llm is not None
                assert len(retrieved_llm) == 1
                assert retrieved_llm[0].provider == "anthropic"
                assert retrieved_llm[0].api_key == "test-key-org"
            finally:
                # No need to restore - patch handles this automatically
                pass
    
    def test_set_and_get_repo_configs(self):
        """Test setting and getting repo configs (in-memory)"""
        from unittest.mock import Mock, MagicMock
        repo_configs = [
            RepoConfig(id="test-repo-2", repo_url="https://github.com/org/repo1", base_branch="main", current_branch="main"),
            RepoConfig(id="test-repo-3", repo_url="https://github.com/org/repo2", base_branch="develop", current_branch="develop")
        ]
        
        # Mock database session and user_id
        mock_db = Mock()
        mock_user_id = "test-user-2"
        
        # Mock the UserReposDAO methods
        mock_user_repos_dao = Mock()
        mock_user_repos_dao.get_user_repositories.return_value = []  # Empty list initially
        mock_user_repos_dao.add_repository.return_value = Mock(id="new-repo-id")
        mock_user_repos_dao.delete_repository.return_value = None
        
        # Mock the FileOperationsService
        mock_file_ops = Mock()
        mock_file_ops.delete_directory.return_value = None
        
        # Patch the imports
        with patch('services.config.strategies.organization.UserReposDAO') as mock_user_repos_dao_class:
            mock_user_repos_dao_class.return_value = mock_user_repos_dao
            with patch('services.config.strategies.organization.FileOperationsService') as mock_file_ops_class:
                mock_file_ops_class.return_value = mock_file_ops
                
                try:
                    # Set repo configs
                    repo_set_result = self.strategy.set_repo_configs(mock_db, mock_user_id, repo_configs)
                    assert repo_set_result is not None
                    assert len(repo_set_result) == 2
                    
                    # Mock the returned repos for get_repo_configs
                    mock_repo1 = Mock()
                    mock_repo1.id = "test-repo-2"
                    mock_repo1.repo_name = "org/repo1"
                    mock_repo1.repo_clone_url = "https://github.com/org/repo1"
                    mock_repo1.branch = "main"
                    
                    mock_repo2 = Mock()
                    mock_repo2.id = "test-repo-3"
                    mock_repo2.repo_name = "org/repo2"
                    mock_repo2.repo_clone_url = "https://github.com/org/repo2"
                    mock_repo2.branch = "develop"
                    
                    mock_user_repos_dao.get_user_repositories.return_value = [mock_repo1, mock_repo2]
                    
                    retrieved_repo = self.strategy.get_repo_configs(mock_db, mock_user_id)
                    assert retrieved_repo is not None
                    assert len(retrieved_repo) == 2
                    assert retrieved_repo[0].repo_url == "https://github.com/org/repo1"
                    assert retrieved_repo[1].repo_url == "https://github.com/org/repo2"
                finally:
                    # No need to restore - patch handles this automatically
                    pass


class TestMultiTenantConfigStrategy:
    """Test cases for MultiTenantConfig strategy - SKIP as MULTI_TENANT is not supported"""
    
    @pytest.mark.skip(reason="MULTI_TENANT hosting type is not supported in the current implementation")
    def test_factory_creates_multi_tenant_strategy(self):
        """Test factory creates MultiTenantConfig strategy"""
        pass
    
    @pytest.mark.skip(reason="MULTI_TENANT hosting type is not supported in the current implementation")
    def test_get_hosting_config(self):
        """Test getting hosting config from ENV"""
        pass
    
    @pytest.mark.skip(reason="MULTI_TENANT hosting type is not supported in the current implementation")
    def test_set_and_get_oauth_configs(self):
        """Test setting and getting OAuth configs from ENV (system-wide)"""
        pass
    
    @pytest.mark.skip(reason="MULTI_TENANT hosting type is not supported in the current implementation")
    def test_set_and_get_llm_configs(self):
        """Test setting and getting LLM configs from users (in-memory)"""
        pass
    
    @pytest.mark.skip(reason="MULTI_TENANT hosting type is not supported in the current implementation")
    def test_set_and_get_repo_configs(self):
        """Test setting and getting repo configs from users (in-memory)"""
        pass
    
    @pytest.mark.skip(reason="MULTI_TENANT hosting type is not supported in the current implementation")
    def test_tenant_isolation(self):
        """Test tenant isolation by switching tenant"""
        pass


class TestConfigStrategyFactory:
    """Test cases for ConfigStrategyFactory"""
    
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
        expected_types = ['INDIVIDUAL', 'ORGANIZATION']  # MULTI_TENANT is not supported
        assert set(supported_types) == set(expected_types)
    
    def test_invalid_hosting_type(self):
        """Test factory behavior with invalid hosting type"""
        # Set invalid hosting type
        os.environ["HOSTING_TYPE"] = "invalid_type"
        
        with pytest.raises(ValueError) as excinfo:
            ConfigStrategyFactory.get_strategy()
        
        assert "Unsupported hosting type" in str(excinfo.value)