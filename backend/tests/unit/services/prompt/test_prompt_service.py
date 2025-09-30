"""
Comprehensive unit tests for PromptService.

Tests CRUD operations, repository synchronization, and multi-hosting support.
"""

import pytest
import json
from datetime import datetime
from pathlib import Path
from unittest.mock import Mock, AsyncMock, patch, MagicMock

from services.prompt.prompt_service import PromptService
from services.prompt.prompt_discovery_service import PromptDiscoveryService
from services.prompt.models import (
    Prompt,
    PromptCreate,
    PromptUpdate,
    PromptList,
    PromptSearchParams,
    PromptFile
)
from schemas.hosting_type_enum import HostingType
from services.config.models import HostingConfig


class TestPromptService:
    """Comprehensive test suite for PromptService."""
    
    @pytest.fixture
    def mock_config_service_individual(self):
        """Mock config service for individual hosting."""
        config_service = Mock()
        config_service.get_hosting_config.return_value = HostingConfig(
            type=HostingType.INDIVIDUAL
        )
        return config_service
    
    @pytest.fixture
    def mock_config_service_organization(self):
        """Mock config service for organization hosting."""
        config_service = Mock()
        config_service.get_hosting_config.return_value = HostingConfig(
            type=HostingType.ORGANIZATION
        )
        return config_service
    
    @pytest.fixture
    def mock_repo_service(self):
        """Mock repository service."""
        return Mock()
    
    @pytest.fixture
    def mock_repo_locator_service(self):
        """Mock repository locator service."""
        return Mock()
    
    @pytest.fixture
    def mock_session_service(self):
        """Mock session service."""
        return Mock()
    
    @pytest.fixture
    def prompt_service_individual(
        self,
        mock_config_service_individual,
        mock_repo_service,
        mock_repo_locator_service,
        mock_session_service
    ):
        """Create PromptService with individual hosting."""
        service = PromptService(
            config_service=mock_config_service_individual,
            repo_service=mock_repo_service,
            repo_locator_service=mock_repo_locator_service,
            session_service=mock_session_service
        )
        return service
    
    @pytest.fixture
    def prompt_service_organization(
        self,
        mock_config_service_organization,
        mock_repo_service,
        mock_repo_locator_service,
        mock_session_service
    ):
        """Create PromptService with organization hosting."""
        service = PromptService(
            config_service=mock_config_service_organization,
            repo_service=mock_repo_service,
            repo_locator_service=mock_repo_locator_service,
            session_service=mock_session_service
        )
        return service
    
    @pytest.fixture
    def sample_prompt_data(self):
        """Sample prompt creation data."""
        return PromptCreate(
            name="Test Prompt",
            description="A test prompt",
            repo_name="test-repo",
            file_path="prompts/test.yaml",
            category="testing",
            tags=["test", "sample"],
            system_prompt="You are a test assistant",
            user_prompt="Help with testing"
        )
    
    # Test: create_prompt - Individual hosting
    @pytest.mark.asyncio
    @patch('services.prompt.prompt_service.RepoService')
    @patch('services.prompt.prompt_service.settings')
    async def test_create_prompt_individual_success(
        self,
        mock_settings,
        mock_repo_service_class,
        prompt_service_individual,
        sample_prompt_data,
        tmp_path
    ):
        """Test creating a prompt in individual hosting mode."""
        # Setup
        mock_settings.local_repo_path = str(tmp_path)
        repo_path = tmp_path / "test-repo"
        repo_path.mkdir()
        
        mock_repo_instance = Mock()
        mock_repo_instance.save_data.return_value = True
        mock_repo_service_class.return_value = mock_repo_instance
        
        # Execute
        result = await prompt_service_individual.create_prompt("user1", sample_prompt_data)
        
        # Assert
        assert isinstance(result, Prompt)
        assert result.name == "Test Prompt"
        assert result.repo_name == "test-repo"
        assert result.owner is None  # No owner in individual mode
        assert result.system_prompt == "You are a test assistant"
        assert mock_repo_instance.save_data.called
    
    @pytest.mark.asyncio
    @patch('services.prompt.prompt_service.settings')
    async def test_create_prompt_repo_not_found(
        self,
        mock_settings,
        prompt_service_individual,
        sample_prompt_data,
        tmp_path
    ):
        """Test creating prompt when repository doesn't exist."""
        mock_settings.local_repo_path = str(tmp_path)
        
        with pytest.raises(ValueError, match="Repository .* not found"):
            await prompt_service_individual.create_prompt("user1", sample_prompt_data)
    
    @pytest.mark.asyncio
    @patch('services.prompt.prompt_service.RepoService')
    @patch('services.prompt.prompt_service.settings')
    async def test_create_prompt_save_failure(
        self,
        mock_settings,
        mock_repo_service_class,
        prompt_service_individual,
        sample_prompt_data,
        tmp_path
    ):
        """Test creating prompt when save fails."""
        mock_settings.local_repo_path = str(tmp_path)
        repo_path = tmp_path / "test-repo"
        repo_path.mkdir()
        
        mock_repo_instance = Mock()
        mock_repo_instance.save_data.return_value = False
        mock_repo_service_class.return_value = mock_repo_instance
        
        with pytest.raises(ValueError, match="Failed to save prompt"):
            await prompt_service_individual.create_prompt("user1", sample_prompt_data)
    
    # Test: create_prompt - Organization hosting
    @pytest.mark.asyncio
    @patch('services.prompt.prompt_service.RepoService')
    @patch('services.prompt.prompt_service.settings')
    async def test_create_prompt_organization_with_owner(
        self,
        mock_settings,
        mock_repo_service_class,
        prompt_service_organization,
        sample_prompt_data,
        tmp_path
    ):
        """Test creating prompt in organization mode sets owner."""
        mock_settings.multi_user_repo_path = str(tmp_path)
        user_repo_path = tmp_path / "user1" / "test-repo"
        user_repo_path.mkdir(parents=True)
        
        mock_repo_instance = Mock()
        mock_repo_instance.save_data.return_value = True
        mock_repo_service_class.return_value = mock_repo_instance
        
        result = await prompt_service_organization.create_prompt("user1", sample_prompt_data)
        
        assert result.owner == "user1"
    
    # Test: get_prompt
    @pytest.mark.asyncio
    async def test_get_prompt_success(self, prompt_service_individual):
        """Test retrieving an existing prompt."""
        # Create a prompt first
        prompt = Prompt(
            id="test-id",
            name="Test",
            content="{}",
            repo_name="test-repo",
            file_path="test.yaml",
            tags=[],
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        prompt_service_individual._prompts["test-id"] = prompt
        
        result = await prompt_service_individual.get_prompt("user1", "test-id")
        
        assert result is not None
        assert result.id == "test-id"
        assert result.name == "Test"
    
    @pytest.mark.asyncio
    async def test_get_prompt_not_found(self, prompt_service_individual):
        """Test retrieving non-existent prompt returns None."""
        result = await prompt_service_individual.get_prompt("user1", "nonexistent")
        
        assert result is None
    
    @pytest.mark.asyncio
    async def test_get_prompt_no_access_organization(self, prompt_service_organization):
        """Test user cannot access another user's prompt in organization mode."""
        # Create prompt owned by user1
        prompt = Prompt(
            id="test-id",
            name="Test",
            content="{}",
            repo_name="test-repo",
            file_path="test.yaml",
            owner="user1",
            tags=[],
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        prompt_service_organization._prompts["test-id"] = prompt
        
        # Try to access as user2
        result = await prompt_service_organization.get_prompt("user2", "test-id")
        
        assert result is None
    
    # Test: update_prompt
    @pytest.mark.asyncio
    @patch('services.prompt.prompt_service.RepoService')
    @patch('services.prompt.prompt_service.settings')
    async def test_update_prompt_success(
        self,
        mock_settings,
        mock_repo_service_class,
        prompt_service_individual,
        tmp_path
    ):
        """Test updating an existing prompt."""
        mock_settings.local_repo_path = str(tmp_path)
        repo_path = tmp_path / "test-repo"
        repo_path.mkdir()
        
        # Create existing prompt
        prompt = Prompt(
            id="test-id",
            name="Original Name",
            description="Original desc",
            content=json.dumps({"name": "Original Name"}),
            repo_name="test-repo",
            file_path="test.yaml",
            tags=["old"],
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        prompt_service_individual._prompts["test-id"] = prompt
        
        # Mock repo service
        mock_repo_instance = Mock()
        mock_repo_instance.get_data.return_value = {"name": "Original Name"}
        mock_repo_instance.save_data.return_value = True
        mock_repo_service_class.return_value = mock_repo_instance
        
        # Update
        update_data = PromptUpdate(
            name="Updated Name",
            tags=["new", "updated"]
        )
        result = await prompt_service_individual.update_prompt("user1", "test-id", update_data)
        
        assert result is not None
        assert result.name == "Updated Name"
        assert result.tags == ["new", "updated"]
        assert mock_repo_instance.save_data.called
    
    @pytest.mark.asyncio
    async def test_update_prompt_not_found(self, prompt_service_individual):
        """Test updating non-existent prompt returns None."""
        update_data = PromptUpdate(name="Updated")
        result = await prompt_service_individual.update_prompt("user1", "nonexistent", update_data)
        
        assert result is None
    
    @pytest.mark.asyncio
    @patch('services.prompt.prompt_service.RepoService')
    @patch('services.prompt.prompt_service.settings')
    async def test_update_prompt_partial_update(
        self,
        mock_settings,
        mock_repo_service_class,
        prompt_service_individual,
        tmp_path
    ):
        """Test partial update only changes specified fields."""
        mock_settings.local_repo_path = str(tmp_path)
        repo_path = tmp_path / "test-repo"
        repo_path.mkdir()
        
        # Create prompt
        prompt = Prompt(
            id="test-id",
            name="Original",
            description="Keep this",
            content=json.dumps({"description": "Keep this"}),
            repo_name="test-repo",
            file_path="test.yaml",
            tags=[],
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        prompt_service_individual._prompts["test-id"] = prompt
        
        mock_repo_instance = Mock()
        mock_repo_instance.get_data.return_value = {"description": "Keep this"}
        mock_repo_instance.save_data.return_value = True
        mock_repo_service_class.return_value = mock_repo_instance
        
        # Update only name
        update_data = PromptUpdate(name="Updated")
        result = await prompt_service_individual.update_prompt("user1", "test-id", update_data)
        
        assert result.name == "Updated"
        assert result.description == "Keep this"  # Unchanged
    
    # Test: delete_prompt
    @pytest.mark.asyncio
    @patch('services.prompt.prompt_service.settings')
    async def test_delete_prompt_success(
        self,
        mock_settings,
        prompt_service_individual,
        tmp_path
    ):
        """Test deleting an existing prompt."""
        mock_settings.local_repo_path = str(tmp_path)
        repo_path = tmp_path / "test-repo"
        repo_path.mkdir()
        file_path = repo_path / "test.yaml"
        file_path.write_text("test")
        
        # Create prompt
        prompt = Prompt(
            id="test-id",
            name="Test",
            content="{}",
            repo_name="test-repo",
            file_path="test.yaml",
            tags=[],
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        prompt_service_individual._prompts["test-id"] = prompt
        
        result = await prompt_service_individual.delete_prompt("user1", "test-id")
        
        assert result is True
        assert "test-id" not in prompt_service_individual._prompts
        assert not file_path.exists()
    
    @pytest.mark.asyncio
    async def test_delete_prompt_not_found(self, prompt_service_individual):
        """Test deleting non-existent prompt returns False."""
        result = await prompt_service_individual.delete_prompt("user1", "nonexistent")
        
        assert result is False
    
    # Test: list_prompts
    @pytest.mark.asyncio
    async def test_list_prompts_no_filters(self, prompt_service_individual):
        """Test listing all accessible prompts."""
        # Create multiple prompts
        for i in range(5):
            prompt = Prompt(
                id=f"prompt-{i}",
                name=f"Prompt {i}",
                content="{}",
                repo_name="test-repo",
                file_path=f"prompt{i}.yaml",
                tags=[],
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            prompt_service_individual._prompts[prompt.id] = prompt
        
        result = await prompt_service_individual.list_prompts("user1")
        
        assert result.total == 5
        assert len(result.prompts) == 5
    
    @pytest.mark.asyncio
    async def test_list_prompts_with_query_filter(self, prompt_service_individual):
        """Test listing prompts with query filter."""
        # Create prompts with different names
        prompts_data = [
            ("prompt-1", "Python Helper", "Helps with Python"),
            ("prompt-2", "JavaScript Guide", "Helps with JS"),
            ("prompt-3", "Python Expert", "Advanced Python")
        ]
        
        for pid, name, desc in prompts_data:
            prompt = Prompt(
                id=pid,
                name=name,
                description=desc,
                content="{}",
                repo_name="test-repo",
                file_path=f"{pid}.yaml",
                tags=[],
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            prompt_service_individual._prompts[pid] = prompt
        
        # Search for "python"
        search_params = PromptSearchParams(query="python")
        result = await prompt_service_individual.list_prompts("user1", search_params)
        
        assert result.total == 2
        assert all("python" in p.name.lower() or "python" in (p.description or "").lower() 
                  for p in result.prompts)
    
    @pytest.mark.asyncio
    async def test_list_prompts_with_repo_filter(self, prompt_service_individual):
        """Test listing prompts filtered by repository."""
        # Create prompts in different repos
        for i in range(3):
            prompt = Prompt(
                id=f"prompt-{i}",
                name=f"Prompt {i}",
                content="{}",
                repo_name=f"repo-{i % 2}",  # repo-0 and repo-1
                file_path=f"prompt{i}.yaml",
                tags=[],
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            prompt_service_individual._prompts[prompt.id] = prompt
        
        search_params = PromptSearchParams(repo_name="repo-0")
        result = await prompt_service_individual.list_prompts("user1", search_params)
        
        assert result.total == 2
        assert all(p.repo_name == "repo-0" for p in result.prompts)
    
    @pytest.mark.asyncio
    async def test_list_prompts_with_pagination(self, prompt_service_individual):
        """Test listing prompts with pagination."""
        # Create 25 prompts
        for i in range(25):
            prompt = Prompt(
                id=f"prompt-{i}",
                name=f"Prompt {i}",
                content="{}",
                repo_name="test-repo",
                file_path=f"prompt{i}.yaml",
                tags=[],
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            prompt_service_individual._prompts[prompt.id] = prompt
        
        # Get first page
        search_params = PromptSearchParams(page=1, page_size=10)
        result = await prompt_service_individual.list_prompts("user1", search_params)
        
        assert result.total == 25
        assert len(result.prompts) == 10
        assert result.page == 1
        
        # Get second page
        search_params = PromptSearchParams(page=2, page_size=10)
        result = await prompt_service_individual.list_prompts("user1", search_params)
        
        assert result.total == 25
        assert len(result.prompts) == 10
        assert result.page == 2
    
    @pytest.mark.asyncio
    async def test_list_prompts_organization_mode_filters_by_owner(
        self,
        prompt_service_organization
    ):
        """Test that organization mode only shows user's own prompts."""
        # Create prompts for different users
        for i, user in enumerate(["user1", "user1", "user2"]):
            prompt = Prompt(
                id=f"prompt-{i}",
                name=f"Prompt {i}",
                content="{}",
                repo_name="test-repo",
                file_path=f"prompt{i}.yaml",
                owner=user,
                tags=[],
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            prompt_service_organization._prompts[prompt.id] = prompt
        
        result = await prompt_service_organization.list_prompts("user1")
        
        assert result.total == 2
        assert all(p.owner == "user1" for p in result.prompts)
    
    # Test: discover_prompts
    @pytest.mark.asyncio
    @patch('services.prompt.prompt_service.settings')
    async def test_discover_prompts_success(
        self,
        mock_settings,
        prompt_service_individual,
        tmp_path
    ):
        """Test discovering prompts in a repository."""
        mock_settings.local_repo_path = str(tmp_path)
        repo_path = tmp_path / "test-repo"
        repo_path.mkdir()
        
        # Create a YAML file with prompts
        import yaml
        prompt_file = repo_path / "prompt.yaml"
        prompt_file.write_text(yaml.dump({
            "system_prompt": "Test",
            "user_prompt": "User test"
        }))
        
        result = await prompt_service_individual.discover_prompts("user1", "test-repo")
        
        assert len(result) > 0
        assert isinstance(result[0], PromptFile)
    
    @pytest.mark.asyncio
    @patch('services.prompt.prompt_service.settings')
    async def test_discover_prompts_repo_not_found(
        self,
        mock_settings,
        prompt_service_individual,
        tmp_path
    ):
        """Test discovering prompts in non-existent repository."""
        mock_settings.local_repo_path = str(tmp_path)
        
        with pytest.raises(ValueError, match="Repository .* not found"):
            await prompt_service_individual.discover_prompts("user1", "nonexistent")
    
    # Test: sync_repository_prompts
    @pytest.mark.asyncio
    @patch('services.prompt.prompt_service.settings')
    async def test_sync_repository_prompts_creates_new(
        self,
        mock_settings,
        prompt_service_individual,
        tmp_path
    ):
        """Test syncing creates new prompts."""
        mock_settings.local_repo_path = str(tmp_path)
        repo_path = tmp_path / "test-repo"
        repo_path.mkdir()
        
        # Create prompt files
        import yaml
        (repo_path / "prompt1.yaml").write_text(yaml.dump({
            "system_prompt": "Test 1",
            "category": "test"
        }))
        (repo_path / "prompt2.yaml").write_text(yaml.dump({
            "user_prompt": "Test 2"
        }))
        
        result = await prompt_service_individual.sync_repository_prompts("user1", "test-repo")
        
        assert result == 2
        assert len(prompt_service_individual._prompts) == 2
    
    @pytest.mark.asyncio
    @patch('services.prompt.prompt_service.settings')
    async def test_sync_repository_prompts_updates_existing(
        self,
        mock_settings,
        prompt_service_individual,
        tmp_path
    ):
        """Test syncing updates existing prompts."""
        mock_settings.local_repo_path = str(tmp_path)
        repo_path = tmp_path / "test-repo"
        repo_path.mkdir()
        
        # Create initial prompt
        import yaml
        prompt_file = repo_path / "prompt.yaml"
        prompt_file.write_text(yaml.dump({
            "system_prompt": "Original"
        }))
        
        # First sync
        await prompt_service_individual.sync_repository_prompts("user1", "test-repo")
        original_count = len(prompt_service_individual._prompts)
        
        # Update prompt file
        prompt_file.write_text(yaml.dump({
            "system_prompt": "Updated",
            "user_prompt": "New content"
        }))
        
        # Second sync
        result = await prompt_service_individual.sync_repository_prompts("user1", "test-repo")
        
        assert result == 1
        assert len(prompt_service_individual._prompts) == original_count
        # Verify prompt was updated
        prompt = list(prompt_service_individual._prompts.values())[0]
        assert prompt.system_prompt == "Updated"
    
    @pytest.mark.asyncio
    @patch('services.prompt.prompt_service.settings')
    async def test_sync_repository_prompts_removes_deleted(
        self,
        mock_settings,
        prompt_service_individual,
        tmp_path
    ):
        """Test syncing removes prompts no longer in repository."""
        mock_settings.local_repo_path = str(tmp_path)
        repo_path = tmp_path / "test-repo"
        repo_path.mkdir()
        
        # Create and sync initial prompts
        import yaml
        (repo_path / "prompt1.yaml").write_text(yaml.dump({"system_prompt": "Test 1"}))
        (repo_path / "prompt2.yaml").write_text(yaml.dump({"system_prompt": "Test 2"}))
        
        await prompt_service_individual.sync_repository_prompts("user1", "test-repo")
        assert len(prompt_service_individual._prompts) == 2
        
        # Remove one file
        (repo_path / "prompt2.yaml").unlink()
        
        # Sync again
        await prompt_service_individual.sync_repository_prompts("user1", "test-repo")
        
        assert len(prompt_service_individual._prompts) == 1