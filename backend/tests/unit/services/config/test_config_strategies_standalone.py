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
        assert str(hosting_config.type) == str(HostingType.INDIVIDUAL)
    
    def test_oauth_configs_returns_none(self):
        """Test OAuth configs returns None for individual"""
        oauth_configs = self.strategy.get_oauth_configs()
        assert oauth_configs is None
    
    def test_set_and_get_llm_configs(self):
        """Test setting and getting LLM configs from ENV"""
        from unittest.mock import Mock, patch
        from services.config.models import LLMConfigScope
        llm_configs = [
            LLMConfig(
                id="test-llm-1",
                provider="openai",
                model="gpt-4",
                api_key="test-key-individual",
                api_base_url="https://api.openai.com",
                scope=LLMConfigScope.USER
            )
        ]
        
        # Mock database session and user_id
        mock_db = Mock()
        mock_user_id = "test-user-1"
        
        # Mock the UserLLMDAO to avoid database interactions
        with patch('services.config.strategies.individual.UserLLMDAO') as mock_dao_class, \
             patch('services.config.strategies.individual.UserDAO') as mock_user_dao_class:
            
            mock_dao = Mock()
            mock_dao_class.return_value = mock_dao
            
            mock_user_dao = Mock()
            mock_user_dao_class.return_value = mock_user_dao
            mock_user_dao.get_user_by_id.return_value = None  # User doesn't exist initially
            
            # Mock user creation
            mock_user = Mock()
            mock_user.id = mock_user_id
            mock_user_dao.save_user.return_value = mock_user
            
            # Mock the add_llm_config method to return a mock config
            mock_config = Mock()
            mock_config.id = "test-llm-1"
            mock_config.provider = "openai"
            mock_config.model_name = "gpt-4"
            mock_config.api_key = "test-key-individual"
            mock_config.base_url = "https://api.openai.com"
            mock_dao.add_llm_config.return_value = mock_config
            
            # First call returns empty list (no existing configs)
            # Second call returns the created config
            mock_dao.get_llm_configs_for_user.side_effect = [[], [mock_config]]
            
            set_result = self.strategy.set_llm_configs(mock_db, mock_user_id, llm_configs)
            # The strategy returns the input configs that have USER scope
            assert set_result is not None
            assert len(set_result) == 1
            assert set_result[0].id == "test-llm-1"
            assert set_result[0].provider == "openai"
            assert set_result[0].model == "gpt-4"
            
            # Verify that the DAO methods were called correctly
            mock_dao.add_llm_config.assert_called_once_with(
                user_id=mock_user_id,
                provider="openai",
                model_name="gpt-4",
                api_key="test-key-individual",
                base_url="https://api.openai.com"
            )
            
        # Mock the get_llm_configs method as well
        with patch('services.config.strategies.individual.UserLLMDAO') as mock_dao_class, \
             patch('os.environ.get', return_value="[]"):
            mock_dao = Mock()
            mock_dao_class.return_value = mock_dao
            mock_dao.get_llm_configs_for_user.return_value = []
            
            retrieved_llm = self.strategy.get_llm_configs(mock_db, mock_user_id)
            # For individual strategy, LLM configs come from environment, not database
            # So the mock database won't affect the result
            # The strategy returns None when no configs are found
            assert retrieved_llm is None or retrieved_llm == []
    
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
        assert str(hosting_config.type) == str(HostingType.ORGANIZATION)
    
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
        from unittest.mock import Mock, patch
        from services.config.models import LLMConfigScope
        llm_configs = [
            LLMConfig(
                id="test-llm-2",
                provider="anthropic",
                model="claude-3",
                api_key="test-key-org",
                api_base_url="https://api.anthropic.com",
                scope=LLMConfigScope.USER
            )
        ]
        
        # Mock database session and user_id
        mock_db = Mock()
        mock_user_id = "test-user-2"
        
        # Mock the UserLLMDAO to avoid database interactions
        with patch('services.config.strategies.organization.UserLLMDAO') as mock_dao_class:
            
            mock_dao = Mock()
            mock_dao_class.return_value = mock_dao
            
            # Mock the add_llm_config method to return a mock config
            mock_config = Mock()
            mock_config.id = "test-llm-2"
            mock_config.provider = "anthropic"
            mock_config.model_name = "claude-3"
            mock_config.api_key = "test-key-org"
            mock_config.base_url = "https://api.anthropic.com"
            mock_dao.add_llm_config.return_value = mock_config
            
            # First call returns empty list (no existing configs)
            # Second call returns created config
            mock_dao.get_llm_configs_for_user.side_effect = [[], [mock_config]]
            
            set_result = self.strategy.set_llm_configs(mock_db, mock_user_id, llm_configs)
            # The strategy returns the input configs that have USER scope
            assert set_result is not None
            assert len(set_result) == 1
            assert set_result[0].id == "test-llm-2"
            assert set_result[0].provider == "anthropic"
            assert set_result[0].model == "claude-3"
            
            # Verify that the DAO methods were called correctly
            mock_dao.add_llm_config.assert_called_once_with(
                user_id=mock_user_id,
                provider="anthropic",
                model_name="claude-3",
                api_key="test-key-org",
                base_url="https://api.anthropic.com"
            )
            
        # Mock the get_llm_configs method as well
        with patch('services.config.strategies.organization.UserLLMDAO') as mock_dao_class, \
             patch('os.environ.get', return_value="[]"):
            mock_dao = Mock()
            mock_dao_class.return_value = mock_dao
            mock_dao.get_llm_configs_for_user.return_value = []
            
            retrieved_llm = self.strategy.get_llm_configs(mock_db, mock_user_id)
            # For organization strategy, LLM configs come from environment, not database
            # So the mock database won't affect the result
            # The strategy returns None when no configs are found
            assert retrieved_llm is None or retrieved_llm == []
    
    def test_set_and_get_repo_configs(self):
        """Test setting and getting repo configs (in-memory)"""
        from unittest.mock import Mock, patch
        repo_configs = [
            RepoConfig(id="test-repo-2", repo_url="https://github.com/org/repo1", base_branch="main", current_branch="main"),
            RepoConfig(id="test-repo-3", repo_url="https://github.com/org/repo2", base_branch="develop", current_branch="develop")
        ]
        
        # Mock database session and user_id
        mock_db = Mock()
        mock_user_id = "test-user-2"
        
        # Mock the UserReposDAO and FileOperationsService to avoid database interactions
        with patch('services.config.strategies.organization.UserReposDAO') as mock_dao_class, \
             patch('services.config.strategies.organization.FileOperationsService') as mock_file_ops:
            
            mock_dao = Mock()
            mock_dao_class.return_value = mock_dao
            mock_dao.get_user_repositories.return_value = []  # No existing repos
            
            # Mock the add_repository method to return a mock repo object
            mock_repo = Mock()
            mock_repo.id = "test-repo-id"
            mock_dao.add_repository.return_value = mock_repo
            
            # Mock the FileOperationsService to avoid file system operations
            mock_file_ops_instance = Mock()
            mock_file_ops.return_value = mock_file_ops_instance
            
            # Set repo configs
            repo_set_result = self.strategy.set_repo_configs(mock_db, mock_user_id, repo_configs)
            # For organization strategy, this should return the input configs
            assert repo_set_result is not None
            assert len(repo_set_result) == 2
            
        # Mock the get_repo_configs method as well
        with patch('services.config.strategies.organization.UserReposDAO') as mock_dao_class:
            mock_dao = Mock()
            mock_dao_class.return_value = mock_dao
            # Create mock repo objects that match what the actual DAO would return
            mock_repo1 = Mock()
            mock_repo1.id = "test-repo-id-1"
            mock_repo1.repo_name = "org/repo1"
            mock_repo1.repo_clone_url = "https://github.com/org/repo1"
            mock_repo1.branch = "main"
            
            mock_repo2 = Mock()
            mock_repo2.id = "test-repo-id-2"
            mock_repo2.repo_name = "org/repo2"
            mock_repo2.repo_clone_url = "https://github.com/org/repo2"
            mock_repo2.branch = "develop"
            
            mock_dao.get_user_repositories.return_value = [mock_repo1, mock_repo2]  # Return repos
            
            # Get repo configs - should return the repos we just added
            retrieved_repo = self.strategy.get_repo_configs(mock_db, mock_user_id)
            assert retrieved_repo is not None
            assert len(retrieved_repo) == 2
            assert retrieved_repo[0].repo_name == "org/repo1"
            assert retrieved_repo[1].repo_name == "org/repo2"


class TestMultiTenantConfigStrategyStandalone:
    """Test cases for MultiTenantConfig strategy (standalone) - SKIP as MULTI_TENANT is not supported"""
    
    @pytest.mark.skip(reason="MULTI_TENANT hosting type is not supported in current implementation")
    def test_factory_creates_multi_tenant_strategy(self):
        """Test factory creates MultiTenantConfig strategy"""
        pass
    
    @pytest.mark.skip(reason="MULTI_TENANT hosting type is not supported in current implementation")
    def test_get_hosting_config(self):
        """Test getting hosting config from ENV"""
        pass
    
    @pytest.mark.skip(reason="MULTI_TENANT hosting type is not supported in current implementation")
    def test_set_and_get_oauth_configs(self):
        """Test setting and getting OAuth configs from ENV (system-wide)"""
        pass
    
    @pytest.mark.skip(reason="MULTI_TENANT hosting type is not supported in current implementation")
    def test_set_and_get_llm_configs(self):
        """Test setting and getting LLM configs from users (in-memory)"""
        pass
    
    @pytest.mark.skip(reason="MULTI_TENANT hosting type is not supported in current implementation")
    def test_set_and_get_repo_configs(self):
        """Test setting and getting repo configs from users (in-memory)"""
        pass
    
    @pytest.mark.skip(reason="MULTI_TENANT hosting type is not supported in current implementation")
    def test_tenant_isolation(self):
        """Test tenant isolation by switching tenant"""
        pass


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
        expected_types = ['INDIVIDUAL', 'ORGANIZATION']  # MULTI_TENANT is not supported
        assert set(supported_types) == set(expected_types)
    
    def test_invalid_hosting_type(self):
        """Test factory behavior with invalid hosting type"""
        # Set invalid hosting type
        os.environ["HOSTING_TYPE"] = "invalid_type"
        
        with pytest.raises(ValueError) as excinfo:
            ConfigStrategyFactory.get_strategy()
        
        assert "Unsupported hosting type" in str(excinfo.value)