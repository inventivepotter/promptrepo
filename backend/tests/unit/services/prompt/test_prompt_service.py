"""
Unit tests for PromptService.

Tests CRUD operations, file existence validation, and default value handling.
"""
import pytest
from datetime import datetime
from pathlib import Path
from unittest.mock import Mock, MagicMock, patch, AsyncMock
from services.prompt.prompt_service import PromptService
from services.prompt.models import PromptData, PromptMeta, PromptDataUpdate
from middlewares.rest.exceptions import NotFoundException, ConflictException, AppException
from schemas.hosting_type_enum import HostingType


@pytest.fixture
def mock_config_service():
    """Mock ConfigService with individual hosting type."""
    config_service = Mock()
    hosting_config = Mock()
    hosting_config.type = HostingType.INDIVIDUAL
    config_service.get_hosting_config.return_value = hosting_config
    return config_service


@pytest.fixture
def mock_file_ops_service():
    """Mock FileOperationsService."""
    return Mock()


@pytest.fixture
def mock_local_repo_service():
    """Mock LocalRepoService."""
    return Mock()


@pytest.fixture
def prompt_service(mock_config_service, mock_file_ops_service, mock_local_repo_service):
    """Create PromptService instance with mocked dependencies."""
    return PromptService(
        config_service=mock_config_service,
        file_ops_service=mock_file_ops_service,
        local_repo_service=mock_local_repo_service
    )


@pytest.fixture
def sample_prompt_data():
    """Sample PromptData for testing."""
    return PromptData(
        id="test-repo:test.yaml",
        name="Test Prompt",
        description="A test prompt",
        provider="openai",
        model="gpt-4",
        prompt="Test prompt content",
        failover_model=None,
        tool_choice=None,
        temperature=0.7,
        top_p=1.0,
        max_tokens=1000,
        response_format=None,
        stream=False,
        n_completions=1,
        stop=None,
        presence_penalty=0.0,
        frequency_penalty=0.0,
        seed=None,
        api_key=None,
        api_base=None,
        user=None,
        parallel_tool_calls=None,
        logprobs=False,
        top_logprobs=None,
        logit_bias=None,
        stream_options=None,
        max_completion_tokens=None,
        reasoning_effort=None,
        extra_args=None,
        tags=[]
    )


class TestCreatePrompt:
    """Tests for create_prompt method."""
    
    @pytest.mark.asyncio
    async def test_create_prompt_success(self, prompt_service, mock_file_ops_service, sample_prompt_data):
        """Test successful prompt creation with all fields provided."""
        repo_name = "test-repo"
        file_path = "prompts/test.yaml"
        user_id = "test-user"
        
        # Mock repository exists
        with patch('services.prompt.prompt_service.Path') as mock_path:
            mock_repo_path = MagicMock()
            mock_repo_path.exists.return_value = True
            mock_file_path = MagicMock()
            mock_file_path.exists.return_value = False  # File doesn't exist yet
            mock_repo_path.__truediv__ = Mock(return_value=mock_file_path)
            mock_path.return_value.__truediv__ = Mock(return_value=mock_repo_path)
            
            # Mock file save success
            mock_file_ops_service.save_yaml_file.return_value = True
            
            # Mock git service
            with patch.object(prompt_service, '_get_file_commit_history', return_value=[]):
                result = await prompt_service.create_prompt(
                    user_id=user_id,
                    repo_name=repo_name,
                    file_path=file_path,
                    prompt_data=sample_prompt_data
                )
        
        # Assertions
        assert isinstance(result, PromptMeta)
        assert result.repo_name == repo_name
        assert result.file_path == file_path
        assert result.prompt.name == "Test Prompt"
        mock_file_ops_service.save_yaml_file.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_create_prompt_with_defaults(self, prompt_service, mock_file_ops_service):
        """Test prompt creation with default values for new 'Untitled Prompt'."""
        repo_name = "test-repo"
        file_path = "prompts/untitled.yaml"
        user_id = "test-user"
        
        # Create prompt data with defaults
        prompt_data = PromptData(
            failover_model=None,
            tool_choice=None,
            temperature=0.7,
            top_p=1.0,
            max_tokens=1000,
            response_format=None,
            stream=False,
            n_completions=1,
            stop=None,
            presence_penalty=0.0,
            frequency_penalty=0.0,
            seed=None,
            api_key=None,
            api_base=None,
            user=None,
            parallel_tool_calls=None,
            logprobs=False,
            top_logprobs=None,
            logit_bias=None,
            stream_options=None,
            max_completion_tokens=None,
            reasoning_effort=None,
            extra_args=None,
            tags=[]
        )
        
        # Mock repository exists
        with patch('services.prompt.prompt_service.Path') as mock_path:
            mock_repo_path = MagicMock()
            mock_repo_path.exists.return_value = True
            mock_file_path = MagicMock()
            mock_file_path.exists.return_value = False
            mock_repo_path.__truediv__ = Mock(return_value=mock_file_path)
            mock_path.return_value.__truediv__ = Mock(return_value=mock_repo_path)
            
            mock_file_ops_service.save_yaml_file.return_value = True
            
            with patch.object(prompt_service, '_get_file_commit_history', return_value=[]):
                result = await prompt_service.create_prompt(
                    user_id=user_id,
                    repo_name=repo_name,
                    file_path=file_path,
                    prompt_data=prompt_data
                )
        
        # Verify defaults were applied
        assert result.prompt.name == "Untitled Prompt"
        assert result.prompt.description == ""
        assert result.prompt.provider == "openai"
        assert result.prompt.model == "gpt-4"
        assert result.prompt.prompt == ""
    
    @pytest.mark.asyncio
    async def test_create_prompt_file_exists(self, prompt_service, sample_prompt_data):
        """Test that ConflictException is raised when file already exists."""
        repo_name = "test-repo"
        file_path = "prompts/existing.yaml"
        user_id = "test-user"
        
        # Mock repository exists and file exists
        with patch('services.prompt.prompt_service.Path') as mock_path_class:
            mock_path = MagicMock()
            mock_path_class.return_value = mock_path
            
            # Mock the base path construction
            mock_base_path = MagicMock()
            mock_path.__truediv__.return_value = mock_base_path
            
            # Mock the repo path
            mock_repo_path = MagicMock()
            mock_repo_path.exists.return_value = True
            mock_base_path.__truediv__.return_value = mock_repo_path
            
            # Mock the file path
            mock_file_path = MagicMock()
            mock_file_path.exists.return_value = True  # File already exists
            mock_repo_path.__truediv__.return_value = mock_file_path
            
            # Mock the file operations service to raise FileExistsError
            prompt_service.file_ops.save_yaml_file.side_effect = FileExistsError("File already exists")
            
            with pytest.raises(ConflictException) as exc_info:
                await prompt_service.create_prompt(
                    user_id=user_id,
                    repo_name=repo_name,
                    file_path=file_path,
                    prompt_data=sample_prompt_data
                )
            
            assert "already exists" in str(exc_info.value.message)
    
    @pytest.mark.asyncio
    async def test_create_prompt_repo_not_found(self, prompt_service, sample_prompt_data):
        """Test that NotFoundException is raised when repository doesn't exist."""
        repo_name = "nonexistent-repo"
        file_path = "prompts/test.yaml"
        user_id = "test-user"
        
        # Mock repository doesn't exist
        with patch('services.prompt.prompt_service.Path') as mock_path:
            mock_repo_path = MagicMock()
            mock_repo_path.exists.return_value = False
            mock_path.return_value.__truediv__ = Mock(return_value=mock_repo_path)
            
            with pytest.raises(NotFoundException) as exc_info:
                await prompt_service.create_prompt(
                    user_id=user_id,
                    repo_name=repo_name,
                    file_path=file_path,
                    prompt_data=sample_prompt_data
                )
            
            assert "Repository" in str(exc_info.value.message)
    
    @pytest.mark.asyncio
    async def test_create_prompt_save_fails(self, prompt_service, mock_file_ops_service, sample_prompt_data):
        """Test that AppException is raised when file save fails."""
        repo_name = "test-repo"
        file_path = "prompts/test.yaml"
        user_id = "test-user"
        
        # Mock repository exists
        with patch('services.prompt.prompt_service.Path') as mock_path:
            mock_repo_path = MagicMock()
            mock_repo_path.exists.return_value = True
            mock_file_path = MagicMock()
            mock_file_path.exists.return_value = False
            mock_repo_path.__truediv__ = Mock(return_value=mock_file_path)
            mock_path.return_value.__truediv__ = Mock(return_value=mock_repo_path)
            
            # Mock file save failure
            mock_file_ops_service.save_yaml_file.return_value = False
            
            with pytest.raises(AppException) as exc_info:
                await prompt_service.create_prompt(
                    user_id=user_id,
                    repo_name=repo_name,
                    file_path=file_path,
                    prompt_data=sample_prompt_data
                )
            
            assert "Failed to save prompt" in str(exc_info.value.message)


class TestGetPrompt:
    """Tests for get_prompt method."""
    
    @pytest.mark.asyncio
    async def test_get_prompt_success(self, prompt_service, mock_file_ops_service):
        """Test successful retrieval of an existing prompt."""
        repo_name = "test-repo"
        file_path = "prompts/test.yaml"
        user_id = "test-user"
        
        yaml_data = {
            "id": "test-repo:prompts/test.yaml",
            "name": "Test Prompt",
            "description": "Test description",
            "provider": "openai",
            "model": "gpt-4",
            "prompt": "Test content",
            "created_at": datetime.utcnow().isoformat(),
            "updated_at": datetime.utcnow().isoformat()
        }
        
        with patch('services.prompt.prompt_service.Path') as mock_path:
            mock_file_path = MagicMock()
            mock_file_path.exists.return_value = True
            mock_path.return_value.__truediv__.return_value.__truediv__.return_value = mock_file_path
            
            mock_file_ops_service.load_yaml_file.return_value = yaml_data
            
            with patch.object(prompt_service, '_get_file_commit_history', return_value=[]):
                result = await prompt_service.get_prompt(user_id, repo_name, file_path)
        
        assert result is not None
        assert result.prompt.name == "Test Prompt"
        assert result.repo_name == repo_name
        assert result.file_path == file_path
    
    @pytest.mark.asyncio
    async def test_get_prompt_not_found(self, prompt_service):
        """Test get_prompt returns None when file doesn't exist."""
        repo_name = "test-repo"
        file_path = "prompts/nonexistent.yaml"
        user_id = "test-user"
        
        with patch('services.prompt.prompt_service.Path') as mock_path:
            mock_file_path = MagicMock()
            mock_file_path.exists.return_value = False
            mock_path.return_value.__truediv__.return_value.__truediv__.return_value = mock_file_path
            
            result = await prompt_service.get_prompt(user_id, repo_name, file_path)
        
        assert result is None


class TestUpdatePrompt:
    """Tests for update_prompt method."""
    
    @pytest.mark.asyncio
    async def test_update_prompt_success(self, prompt_service, mock_file_ops_service):
        """Test successful prompt update."""
        repo_name = "test-repo"
        file_path = "prompts/test.yaml"
        user_id = "test-user"
        
        existing_data = {
            "id": "test-repo:prompts/test.yaml",
            "name": "Old Name",
            "provider": "openai",
            "model": "gpt-4",
            "prompt": "Old content"
        }
        
        update_data = PromptDataUpdate(
            id="test-repo:prompts/test.yaml",
            name="New Name",
            prompt="New content",
            description=None,
            provider=None,
            model=None,
            failover_model=None,
            tool_choice=None,
            temperature=None,
            top_p=None,
            max_tokens=None,
            response_format=None,
            stream=None,
            n_completions=None,
            stop=None,
            presence_penalty=None,
            frequency_penalty=None,
            seed=None,
            api_key=None,
            api_base=None,
            user=None,
            parallel_tool_calls=None,
            logprobs=None,
            top_logprobs=None,
            logit_bias=None,
            stream_options=None,
            max_completion_tokens=None,
            reasoning_effort=None,
            extra_args=None,
            tags=None
        )
        
        with patch('services.prompt.prompt_service.Path') as mock_path:
            mock_file_path = MagicMock()
            mock_file_path.exists.return_value = True
            mock_path.return_value.__truediv__.return_value.__truediv__.return_value = mock_file_path
            
            mock_file_ops_service.load_yaml_file.return_value = existing_data
            mock_file_ops_service.save_yaml_file.return_value = True
            
            with patch.object(prompt_service, '_get_file_commit_history', return_value=[]):
                with patch.object(prompt_service, 'get_prompt') as mock_get:
                    # First call returns existing prompt, second call returns updated
                    mock_get.side_effect = [
                        PromptMeta(
                            prompt=PromptData(
                                id=existing_data["id"],
                                name=existing_data["name"],
                                provider=existing_data["provider"],
                                model=existing_data["model"],
                                prompt=existing_data["prompt"],
                                failover_model=None,
                                tool_choice=None,
                                temperature=0.7,
                                top_p=1.0,
                                max_tokens=1000,
                                response_format=None,
                                stream=False,
                                n_completions=1,
                                stop=None,
                                presence_penalty=0.0,
                                frequency_penalty=0.0,
                                seed=None,
                                api_key=None,
                                api_base=None,
                                user=None,
                                parallel_tool_calls=None,
                                logprobs=False,
                                top_logprobs=None,
                                logit_bias=None,
                                stream_options=None,
                                max_completion_tokens=None,
                                reasoning_effort=None,
                                extra_args=None,
                                tags=[]
                            ),
                            repo_name=repo_name,
                            file_path=file_path,
                            recent_commits=[],
                            pr_info=None
                        ),
                        PromptMeta(
                            prompt=PromptData(
                                id=existing_data["id"],
                                name="New Name",
                                provider="openai",
                                model="gpt-4",
                                prompt="New content",
                                failover_model=None,
                                tool_choice=None,
                                temperature=0.7,
                                top_p=1.0,
                                max_tokens=1000,
                                response_format=None,
                                stream=False,
                                n_completions=1,
                                stop=None,
                                presence_penalty=0.0,
                                frequency_penalty=0.0,
                                seed=None,
                                api_key=None,
                                api_base=None,
                                user=None,
                                parallel_tool_calls=None,
                                logprobs=False,
                                top_logprobs=None,
                                logit_bias=None,
                                stream_options=None,
                                max_completion_tokens=None,
                                reasoning_effort=None,
                                extra_args=None,
                                tags=[]
                            ),
                            repo_name=repo_name,
                            file_path=file_path,
                            recent_commits=[],
                            pr_info=None
                        )
                    ]
                    
                    # Mock the async method properly
                    with patch.object(prompt_service.local_repo_service, 'handle_git_workflow_after_save', new_callable=AsyncMock) as mock_workflow:
                        mock_workflow.return_value = None
                    
                        result = await prompt_service.update_prompt(
                            user_id=user_id,
                            repo_name=repo_name,
                            file_path=file_path,
                            prompt_data=update_data
                        )
        
        assert result is not None
        # update_prompt returns a tuple (PromptMeta, PRInfo)
        updated_prompt, _pr_info = result
        assert updated_prompt is not None
        assert updated_prompt.prompt.name == "New Name"


class TestDeletePrompt:
    """Tests for delete_prompt method."""
    
    @pytest.mark.asyncio
    async def test_delete_prompt_success(self, prompt_service, mock_file_ops_service):
        """Test successful prompt deletion."""
        repo_name = "test-repo"
        file_path = "prompts/test.yaml"
        user_id = "test-user"
        
        with patch.object(prompt_service, 'get_prompt') as mock_get:
            mock_get.return_value = PromptMeta(
                prompt=PromptData(
                    id="test-repo:prompts/test.yaml",
                    name="Test Prompt",
                    failover_model=None,
                    tool_choice=None,
                    temperature=0.7,
                    top_p=1.0,
                    max_tokens=1000,
                    response_format=None,
                    stream=False,
                    n_completions=1,
                    stop=None,
                    presence_penalty=0.0,
                    frequency_penalty=0.0,
                    seed=None,
                    api_key=None,
                    api_base=None,
                    user=None,
                    parallel_tool_calls=None,
                    logprobs=False,
                    top_logprobs=None,
                    logit_bias=None,
                    stream_options=None,
                    max_completion_tokens=None,
                    reasoning_effort=None,
                    extra_args=None,
                    tags=[]
                ),
                repo_name=repo_name,
                file_path=file_path,
                recent_commits=[],
                pr_info=None
            )
            
            mock_file_ops_service.delete_file.return_value = True
            
            with patch('services.prompt.prompt_service.Path'):
                result = await prompt_service.delete_prompt(user_id, repo_name, file_path)
        
        assert result is True
        mock_file_ops_service.delete_file.assert_called_once()
    
    @pytest.mark.asyncio
    async def test_delete_prompt_not_found(self, prompt_service):
        """Test delete_prompt returns False when prompt doesn't exist."""
        repo_name = "test-repo"
        file_path = "prompts/nonexistent.yaml"
        user_id = "test-user"
        
        with patch.object(prompt_service, 'get_prompt') as mock_get:
            mock_get.return_value = None
            
            result = await prompt_service.delete_prompt(user_id, repo_name, file_path)
        
        assert result is False