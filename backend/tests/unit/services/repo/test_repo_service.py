"""
Unit tests for repo service

Tests the RepoService functionality including prompt file discovery,
data operations, and git commit operations.
"""

import pytest
import json
import yaml
from unittest.mock import Mock, patch, mock_open, MagicMock
from pathlib import Path
from datetime import datetime

from services.repo.repo_service import RepoService, IRepoService
from services.repo.models import PromptFile, CommitInfo, UserCredentials
from services.git.git_service import GitOperationResult


class TestRepoService:
    """Test the RepoService class"""
    
    def setup_method(self):
        """Set up test fixtures"""
        self.repo_path = Path("/test/repos")
        self.service = RepoService(self.repo_path)
    
    def test_init_with_string_path(self):
        """Test RepoService initialization with string path"""
        service = RepoService("/test/string/path")
        assert service.repo_path == Path("/test/string/path")
        assert isinstance(service.git_service, type(self.service.git_service))
    
    def test_init_with_path_object(self):
        """Test RepoService initialization with Path object"""
        path_obj = Path("/test/path/object")
        service = RepoService(path_obj)
        assert service.repo_path == path_obj
    
    @patch('pathlib.Path.exists')
    @patch('pathlib.Path.rglob')
    def test_find_prompts_repo_not_exists(self, mock_rglob, mock_exists):
        """Test find_prompts when repository doesn't exist"""
        mock_exists.return_value = False
        
        result = self.service.find_prompts("nonexistent-repo", "testuser")
        
        assert result == []
        mock_exists.assert_called_once()
        mock_rglob.assert_not_called()
    
    @patch('pathlib.Path.exists')
    @patch('pathlib.Path.rglob')
    @patch('builtins.open', new_callable=mock_open)
    @patch('yaml.safe_load')
    def test_find_prompts_with_valid_yaml(self, mock_yaml_load, mock_file_open, mock_rglob, mock_exists):
        """Test find_prompts with valid YAML files containing prompts"""
        mock_exists.return_value = True
        
        # Mock YAML files
        mock_file1 = Mock()
        mock_file1.name = "prompt1.yaml"
        mock_file1.__str__ = lambda: "/test/repos/test-repo/prompt1.yaml"
        
        mock_file2 = Mock()
        mock_file2.name = "prompt2.yaml"
        mock_file2.__str__ = lambda: "/test/repos/test-repo/prompt2.yaml"
        
        mock_rglob.return_value = [mock_file1, mock_file2]
        
        # Mock YAML content
        yaml_data1 = {
            "system_prompt": "You are a helpful assistant",
            "user_prompt": "What is the weather?",
            "other_field": "some value"
        }
        yaml_data2 = {
            "system_prompt": "You are a code reviewer",
            "description": "Code review prompt"
        }
        
        mock_yaml_load.side_effect = [yaml_data1, yaml_data2]
        
        result = self.service.find_prompts("test-repo", "testuser")
        
        assert len(result) == 2
        
        # Check first prompt file
        assert result[0].path == "/test/repos/test-repo/prompt1.yaml"
        assert result[0].name == "prompt1.yaml"
        assert result[0].system_prompt == "You are a helpful assistant"
        assert result[0].user_prompt == "What is the weather?"
        assert result[0].content is not None
        assert json.loads(result[0].content) == yaml_data1
        
        # Check second prompt file
        assert result[1].path == "/test/repos/test-repo/prompt2.yaml"
        assert result[1].name == "prompt2.yaml"
        assert result[1].system_prompt == "You are a code reviewer"
        assert result[1].user_prompt is None
        assert result[1].content is not None
        assert json.loads(result[1].content) == yaml_data2
    
    @patch('pathlib.Path.exists')
    @patch('pathlib.Path.rglob')
    @patch('builtins.open', new_callable=mock_open)
    @patch('yaml.safe_load')
    def test_find_prompts_ignores_invalid_yaml(self, mock_yaml_load, mock_file_open, mock_rglob, mock_exists):
        """Test find_prompts ignores files without prompt fields or invalid YAML"""
        mock_exists.return_value = True
        
        # Mock YAML files
        mock_file1 = Mock()
        mock_file1.name = "invalid.yaml"
        mock_file2 = Mock()
        mock_file2.name = "no_prompts.yaml"
        mock_file3 = Mock()
        mock_file3.name = "corrupted.yaml"
        
        mock_rglob.return_value = [mock_file1, mock_file2, mock_file3]
        
        # Mock YAML content - invalid data, no prompts, exception
        mock_yaml_load.side_effect = [
            {"other_field": "no prompts here"},  # No prompt fields
            None,  # Empty/null YAML
            Exception("YAML parse error")  # Exception during parsing
        ]
        
        result = self.service.find_prompts("test-repo", "testuser")
        
        assert result == []
    
    @patch('pathlib.Path.exists')
    @patch('builtins.open', new_callable=mock_open)
    @patch('yaml.safe_load')
    def test_get_data_yaml_file(self, mock_yaml_load, mock_file_open, mock_exists):
        """Test get_data with YAML file"""
        mock_exists.return_value = True
        yaml_data = {"key": "value", "nested": {"data": "test"}}
        mock_yaml_load.return_value = yaml_data
        
        result = self.service.get_data("/test/file.yaml")
        
        assert result == yaml_data
        mock_yaml_load.assert_called_once()
    
    @patch('pathlib.Path.exists')
    @patch('builtins.open', new_callable=mock_open)
    @patch('json.load')
    def test_get_data_json_file(self, mock_json_load, mock_file_open, mock_exists):
        """Test get_data with JSON file"""
        mock_exists.return_value = True
        json_data = {"key": "value", "list": [1, 2, 3]}
        mock_json_load.return_value = json_data
        
        result = self.service.get_data("/test/file.json")
        
        assert result == json_data
        mock_json_load.assert_called_once()
    
    @patch('pathlib.Path.exists')
    @patch('builtins.open', new_callable=mock_open, read_data="plain text content")
    def test_get_data_text_file(self, mock_file_open, mock_exists):
        """Test get_data with plain text file"""
        mock_exists.return_value = True
        
        result = self.service.get_data("/test/file.txt")
        
        expected = {"content": "plain text content"}
        assert result == expected
    
    @patch('pathlib.Path.exists')
    def test_get_data_file_not_exists(self, mock_exists):
        """Test get_data when file doesn't exist"""
        mock_exists.return_value = False
        
        result = self.service.get_data("/test/nonexistent.yaml")
        
        assert result is None
    
    @patch('pathlib.Path.exists')
    @patch('builtins.open', side_effect=Exception("Read error"))
    def test_get_data_read_exception(self, mock_file_open, mock_exists):
        """Test get_data when file read raises exception"""
        mock_exists.return_value = True
        
        result = self.service.get_data("/test/file.yaml")
        
        assert result is None
    
    @patch('pathlib.Path.mkdir')
    @patch('builtins.open', new_callable=mock_open)
    @patch('yaml.safe_dump')
    def test_save_data_yaml_file(self, mock_yaml_dump, mock_file_open, mock_mkdir):
        """Test save_data with YAML file"""
        data = {"key": "value", "nested": {"data": "test"}}
        
        result = self.service.save_data("/test/output.yaml", data)
        
        assert result is True
        mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)
        mock_yaml_dump.assert_called_once_with(data, mock_file_open.return_value.__enter__.return_value)
    
    @patch('pathlib.Path.mkdir')
    @patch('builtins.open', new_callable=mock_open)
    @patch('json.dump')
    def test_save_data_json_file(self, mock_json_dump, mock_file_open, mock_mkdir):
        """Test save_data with JSON file"""
        data = {"key": "value", "list": [1, 2, 3]}
        
        result = self.service.save_data("/test/output.json", data)
        
        assert result is True
        mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)
        mock_json_dump.assert_called_once_with(data, mock_file_open.return_value.__enter__.return_value, indent=2)
    
    @patch('pathlib.Path.mkdir')
    @patch('builtins.open', new_callable=mock_open)
    def test_save_data_text_file(self, mock_file_open, mock_mkdir):
        """Test save_data with plain text file"""
        data = "plain text content"
        
        result = self.service.save_data("/test/output.txt", data)
        
        assert result is True
        mock_mkdir.assert_called_once_with(parents=True, exist_ok=True)
        mock_file_open.return_value.__enter__.return_value.write.assert_called_once_with(data)
    
    @patch('pathlib.Path.mkdir', side_effect=Exception("Directory creation failed"))
    def test_save_data_exception(self, mock_mkdir):
        """Test save_data when operation raises exception"""
        data = {"key": "value"}
        
        result = self.service.save_data("/test/output.yaml", data)
        
        assert result is False
    
    @patch('services.repo.repo_service.GitService')
    def test_save_commit_success(self, mock_git_service_class):
        """Test save_commit with successful commit and push"""
        # Setup mock git service
        mock_git_service = Mock()
        mock_git_service_class.return_value = mock_git_service
        
        # Mock successful commit
        commit_result = GitOperationResult(
            success=True,
            message="Commit successful",
            data={"commit_hash": "abc123def456"}
        )
        mock_git_service.commit_changes.return_value = commit_result
        
        # Mock successful push
        push_result = GitOperationResult(success=True, message="Push successful")
        mock_git_service.push_branch.return_value = push_result
        
        # Setup user credentials
        user_creds = UserCredentials(username="testuser", token="test-token")
        
        # Call method
        result = self.service.save_commit("testuser", "test-repo", "Test commit", user_creds)
        
        # Verify result
        assert isinstance(result, CommitInfo)
        assert result.commit_id == "abc123def456"
        assert result.message == "Test commit"
        assert result.author == "testuser"
        assert isinstance(result.timestamp, datetime)
        
        # Verify git operations were called
        mock_git_service.add_files.assert_called_once_with(["."])
        mock_git_service.commit_changes.assert_called_once_with(
            commit_message="Test commit",
            author_name="testuser",
            author_email="testuser@example.com"
        )
        mock_git_service.push_branch.assert_called_once_with(oauth_token="test-token")
    
    @patch('services.repo.repo_service.GitService')
    def test_save_commit_commit_failure(self, mock_git_service_class):
        """Test save_commit when commit operation fails"""
        # Setup mock git service
        mock_git_service = Mock()
        mock_git_service_class.return_value = mock_git_service
        
        # Mock failed commit
        commit_result = GitOperationResult(
            success=False,
            message="Commit failed: no changes"
        )
        mock_git_service.commit_changes.return_value = commit_result
        
        # Setup user credentials
        user_creds = UserCredentials(username="testuser", token="test-token")
        
        # Call method and expect ValueError
        with pytest.raises(ValueError, match="Failed to commit changes"):
            self.service.save_commit("testuser", "test-repo", "Test commit", user_creds)
        
        # Verify commit was attempted but push was not
        mock_git_service.add_files.assert_called_once_with(["."])
        mock_git_service.commit_changes.assert_called_once()
        mock_git_service.push_branch.assert_not_called()
    
    @patch('services.repo.repo_service.GitService')
    def test_save_commit_push_failure(self, mock_git_service_class):
        """Test save_commit when push operation fails"""
        # Setup mock git service
        mock_git_service = Mock()
        mock_git_service_class.return_value = mock_git_service
        
        # Mock successful commit
        commit_result = GitOperationResult(
            success=True,
            message="Commit successful",
            data={"commit_hash": "abc123def456"}
        )
        mock_git_service.commit_changes.return_value = commit_result
        
        # Mock failed push
        push_result = GitOperationResult(
            success=False,
            message="Push failed: authentication error"
        )
        mock_git_service.push_branch.return_value = push_result
        
        # Setup user credentials
        user_creds = UserCredentials(username="testuser", token="invalid-token")
        
        # Call method and expect ValueError
        with pytest.raises(ValueError, match="Failed to push changes"):
            self.service.save_commit("testuser", "test-repo", "Test commit", user_creds)
        
        # Verify both operations were attempted
        mock_git_service.add_files.assert_called_once_with(["."])
        mock_git_service.commit_changes.assert_called_once()
        mock_git_service.push_branch.assert_called_once_with(oauth_token="invalid-token")
    
    @patch('services.repo.repo_service.GitService')
    def test_save_commit_exception_handling(self, mock_git_service_class):
        """Test save_commit when git operations raise exceptions"""
        # Setup mock git service that raises exception
        mock_git_service_class.side_effect = Exception("Git service initialization failed")
        
        # Setup user credentials
        user_creds = UserCredentials(username="testuser", token="test-token")
        
        # Call method and expect ValueError
        with pytest.raises(ValueError, match="Failed to commit and push changes"):
            self.service.save_commit("testuser", "test-repo", "Test commit", user_creds)
    
    @patch('services.repo.repo_service.GitService')
    def test_save_commit_no_commit_hash(self, mock_git_service_class):
        """Test save_commit when commit result has no commit hash"""
        # Setup mock git service
        mock_git_service = Mock()
        mock_git_service_class.return_value = mock_git_service
        
        # Mock successful commit without commit hash
        commit_result = GitOperationResult(
            success=True,
            message="Commit successful",
            data={}  # No commit_hash
        )
        mock_git_service.commit_changes.return_value = commit_result
        
        # Mock successful push
        push_result = GitOperationResult(success=True, message="Push successful")
        mock_git_service.push_branch.return_value = push_result
        
        # Setup user credentials
        user_creds = UserCredentials(username="testuser", token="test-token")
        
        # Call method
        result = self.service.save_commit("testuser", "test-repo", "Test commit", user_creds)
        
        # Verify result with empty commit_id
        assert isinstance(result, CommitInfo)
        assert result.commit_id == ""
        assert result.message == "Test commit"
        assert result.author == "testuser"


class TestIRepoService:
    """Test the IRepoService interface"""
    
    def test_interface_methods_exist(self):
        """Test that IRepoService defines all required abstract methods"""
        # This test ensures the interface is properly defined
        assert hasattr(IRepoService, 'find_prompts')
        assert hasattr(IRepoService, 'get_data')
        assert hasattr(IRepoService, 'save_data')
        assert hasattr(IRepoService, 'save_commit')
        
        # Verify methods are abstract
        assert getattr(IRepoService.find_prompts, '__isabstractmethod__', False)
        assert getattr(IRepoService.get_data, '__isabstractmethod__', False)
        assert getattr(IRepoService.save_data, '__isabstractmethod__', False)
        assert getattr(IRepoService.save_commit, '__isabstractmethod__', False)