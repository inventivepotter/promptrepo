"""
Comprehensive unit tests for PromptDiscoveryService.

Tests prompt discovery, YAML parsing, validation, and repository scanning.
"""

import pytest
import yaml
from pathlib import Path
from unittest.mock import Mock, patch, mock_open

from services.prompt.prompt_discovery_service import PromptDiscoveryService
from services.prompt.models import PromptFile


class TestPromptDiscoveryService:
    """Comprehensive test suite for PromptDiscoveryService."""
    
    @pytest.fixture
    def discovery_service(self):
        """Create PromptDiscoveryService instance."""
        return PromptDiscoveryService()
    
    @pytest.fixture
    def temp_repo(self, tmp_path):
        """Create a temporary repository with various prompt files."""
        repo_path = tmp_path / "test-repo"
        repo_path.mkdir()
        
        # Create valid prompt file with all fields
        prompt1 = repo_path / "prompt1.yaml"
        prompt1.write_text(yaml.dump({
            "name": "Code Review Assistant",
            "description": "Helps with code reviews",
            "system_prompt": "You are a code review expert",
            "user_prompt": "Review this code for best practices",
            "category": "development",
            "tags": ["code", "review", "python"],
            "author": "test-user",
            "version": "1.0"
        }))
        
        # Create prompt file with only system_prompt
        prompt2 = repo_path / "prompt2.yml"
        prompt2.write_text(yaml.dump({
            "system_prompt": "You are a helpful assistant",
            "category": "general"
        }))
        
        # Create prompt file with only user_prompt
        prompt3 = repo_path / "prompt3.yaml"
        prompt3.write_text(yaml.dump({
            "user_prompt": "Explain quantum computing",
            "tags": ["education", "science"]
        }))
        
        # Create nested directory with prompt
        nested_dir = repo_path / "prompts" / "coding"
        nested_dir.mkdir(parents=True)
        nested_prompt = nested_dir / "nested.yaml"
        nested_prompt.write_text(yaml.dump({
            "system_prompt": "You are a Python expert",
            "user_prompt": "Help with Python code"
        }))
        
        # Create invalid YAML file (no prompt keys)
        invalid = repo_path / "config.yaml"
        invalid.write_text(yaml.dump({
            "setting": "value",
            "another": "config"
        }))
        
        # Create corrupted YAML file
        corrupted = repo_path / "corrupted.yaml"
        corrupted.write_text("{ invalid: yaml: syntax [")
        
        # Create hidden directory (should be skipped)
        hidden_dir = repo_path / ".hidden"
        hidden_dir.mkdir()
        hidden_prompt = hidden_dir / "hidden.yaml"
        hidden_prompt.write_text(yaml.dump({
            "system_prompt": "Should be ignored"
        }))
        
        # Create non-YAML file
        text_file = repo_path / "readme.txt"
        text_file.write_text("This is not a prompt file")
        
        return repo_path
    
    # Test: scan_repository with valid prompts
    def test_scan_repository_finds_all_valid_prompts(self, discovery_service, temp_repo):
        """Test that scan_repository finds all valid prompt files."""
        prompt_files = discovery_service.scan_repository(temp_repo)
        
        # Should find 4 valid prompts (prompt1, prompt2, prompt3, nested)
        assert len(prompt_files) == 4
        assert discovery_service.discovered_count == 4
        
        # Verify prompt names
        prompt_names = {pf.name for pf in prompt_files}
        assert "prompt1" in prompt_names
        assert "prompt2" in prompt_names
        assert "prompt3" in prompt_names
        assert "nested" in prompt_names
    
    def test_scan_repository_parses_content_correctly(self, discovery_service, temp_repo):
        """Test that prompts are parsed with correct content."""
        prompt_files = discovery_service.scan_repository(temp_repo)
        
        # Find and verify prompt1 content
        prompt1 = next(pf for pf in prompt_files if pf.name == "prompt1")
        assert prompt1.system_prompt == "You are a code review expert"
        assert prompt1.user_prompt == "Review this code for best practices"
        assert prompt1.metadata["name"] == "Code Review Assistant"
        assert prompt1.metadata["category"] == "development"
        assert prompt1.metadata["tags"] == ["code", "review", "python"]
        assert prompt1.metadata["author"] == "test-user"
        assert prompt1.metadata["version"] == "1.0"
    
    def test_scan_repository_handles_optional_fields(self, discovery_service, temp_repo):
        """Test handling of optional system_prompt and user_prompt fields."""
        prompt_files = discovery_service.scan_repository(temp_repo)
        
        # Check prompt with only system_prompt
        prompt2 = next(pf for pf in prompt_files if pf.name == "prompt2")
        assert prompt2.system_prompt == "You are a helpful assistant"
        assert prompt2.user_prompt is None
        
        # Check prompt with only user_prompt
        prompt3 = next(pf for pf in prompt_files if pf.name == "prompt3")
        assert prompt3.system_prompt is None
        assert prompt3.user_prompt == "Explain quantum computing"
    
    def test_scan_repository_ignores_hidden_files(self, discovery_service, temp_repo):
        """Test that hidden files and directories are skipped."""
        prompt_files = discovery_service.scan_repository(temp_repo)
        
        # Should not include hidden directory content
        for pf in prompt_files:
            assert ".hidden" not in pf.path
    
    def test_scan_repository_handles_nested_directories(self, discovery_service, temp_repo):
        """Test that nested directories are scanned recursively."""
        prompt_files = discovery_service.scan_repository(temp_repo)
        
        # Find nested prompt
        nested = next((pf for pf in prompt_files if pf.name == "nested"), None)
        assert nested is not None
        assert "prompts/coding" in nested.path or "prompts\\coding" in nested.path
    
    def test_scan_repository_skips_invalid_yaml(self, discovery_service, temp_repo):
        """Test that invalid YAML files are skipped."""
        prompt_files = discovery_service.scan_repository(temp_repo)
        
        # Should not include config.yaml or corrupted.yaml
        prompt_names = [pf.name for pf in prompt_files]
        assert "config" not in prompt_names
        assert "corrupted" not in prompt_names
        
        # Error count should reflect corrupted file
        assert discovery_service.error_count > 0
    
    def test_scan_empty_repository(self, discovery_service, tmp_path):
        """Test scanning an empty repository returns empty list."""
        empty_repo = tmp_path / "empty"
        empty_repo.mkdir()
        
        prompt_files = discovery_service.scan_repository(empty_repo)
        
        assert len(prompt_files) == 0
        assert discovery_service.discovered_count == 0
        assert discovery_service.error_count == 0
    
    def test_scan_nonexistent_repository(self, discovery_service):
        """Test scanning non-existent path returns empty list."""
        prompt_files = discovery_service.scan_repository(Path("/nonexistent/path"))
        
        assert len(prompt_files) == 0
    
    # Test: _parse_prompt_file
    def test_parse_prompt_file_with_valid_content(self, discovery_service, tmp_path):
        """Test parsing a valid prompt file."""
        repo_path = tmp_path / "repo"
        repo_path.mkdir()
        
        file_path = repo_path / "test.yaml"
        file_path.write_text(yaml.dump({
            "system_prompt": "Test system",
            "user_prompt": "Test user",
            "custom_field": "custom_value"
        }))
        
        result = discovery_service._parse_prompt_file(file_path, repo_path)
        
        assert result is not None
        assert isinstance(result, PromptFile)
        assert result.name == "test"
        assert result.system_prompt == "Test system"
        assert result.user_prompt == "Test user"
        assert result.metadata["custom_field"] == "custom_value"
    
    def test_parse_prompt_file_with_missing_prompts(self, discovery_service, tmp_path):
        """Test parsing file without prompt keys returns None."""
        repo_path = tmp_path / "repo"
        repo_path.mkdir()
        
        file_path = repo_path / "invalid.yaml"
        file_path.write_text(yaml.dump({"other": "data"}))
        
        result = discovery_service._parse_prompt_file(file_path, repo_path)
        
        assert result is None
    
    def test_parse_prompt_file_with_invalid_yaml(self, discovery_service, tmp_path):
        """Test parsing corrupted YAML file returns None."""
        repo_path = tmp_path / "repo"
        repo_path.mkdir()
        
        file_path = repo_path / "corrupted.yaml"
        file_path.write_text("{ invalid yaml [")
        
        result = discovery_service._parse_prompt_file(file_path, repo_path)
        
        assert result is None
        assert discovery_service.error_count > 0
    
    def test_parse_prompt_file_with_non_dict_content(self, discovery_service, tmp_path):
        """Test parsing YAML that's not a dict returns None."""
        repo_path = tmp_path / "repo"
        repo_path.mkdir()
        
        file_path = repo_path / "list.yaml"
        file_path.write_text(yaml.dump(["item1", "item2"]))
        
        result = discovery_service._parse_prompt_file(file_path, repo_path)
        
        assert result is None
    
    # Test: validate_prompt_structure
    def test_validate_prompt_structure_with_system_prompt(self, discovery_service):
        """Test validation with system_prompt is valid."""
        data = {
            "system_prompt": "Test system",
            "other": "field"
        }
        
        assert discovery_service.validate_prompt_structure(data) is True
    
    def test_validate_prompt_structure_with_user_prompt(self, discovery_service):
        """Test validation with user_prompt is valid."""
        data = {
            "user_prompt": "Test user",
            "other": "field"
        }
        
        assert discovery_service.validate_prompt_structure(data) is True
    
    def test_validate_prompt_structure_with_both_prompts(self, discovery_service):
        """Test validation with both prompts is valid."""
        data = {
            "system_prompt": "System",
            "user_prompt": "User"
        }
        
        assert discovery_service.validate_prompt_structure(data) is True
    
    def test_validate_prompt_structure_without_prompts(self, discovery_service):
        """Test validation without prompt keys is invalid."""
        data = {
            "other": "field",
            "another": "value"
        }
        
        assert discovery_service.validate_prompt_structure(data) is False
    
    def test_validate_prompt_structure_with_non_dict(self, discovery_service):
        """Test validation with non-dict is invalid."""
        assert discovery_service.validate_prompt_structure("string") is False
        assert discovery_service.validate_prompt_structure([1, 2, 3]) is False
        assert discovery_service.validate_prompt_structure(None) is False
    
    def test_validate_prompt_structure_with_non_string_prompts(self, discovery_service):
        """Test validation with non-string prompt values is invalid."""
        data = {
            "system_prompt": 123,  # Not a string
            "user_prompt": "Valid"
        }
        
        assert discovery_service.validate_prompt_structure(data) is False
    
    def test_validate_prompt_structure_allows_none_prompts(self, discovery_service):
        """Test validation allows None for prompt values."""
        data = {
            "system_prompt": None,
            "user_prompt": "Valid"
        }
        
        assert discovery_service.validate_prompt_structure(data) is True
    
    # Test: extract_prompt_metadata
    def test_extract_prompt_metadata_standard_fields(self, discovery_service):
        """Test extracting standard metadata fields."""
        data = {
            "system_prompt": "System",
            "user_prompt": "User",
            "name": "Test Prompt",
            "description": "A test",
            "category": "test",
            "tags": ["tag1", "tag2"],
            "author": "tester",
            "version": "1.0"
        }
        
        metadata = discovery_service.extract_prompt_metadata(data)
        
        assert metadata["name"] == "Test Prompt"
        assert metadata["description"] == "A test"
        assert metadata["category"] == "test"
        assert metadata["tags"] == ["tag1", "tag2"]
        assert metadata["author"] == "tester"
        assert metadata["version"] == "1.0"
        assert "system_prompt" not in metadata
        assert "user_prompt" not in metadata
    
    def test_extract_prompt_metadata_custom_fields(self, discovery_service):
        """Test extracting custom metadata fields."""
        data = {
            "system_prompt": "System",
            "custom_field": "custom_value",
            "another_field": 123
        }
        
        metadata = discovery_service.extract_prompt_metadata(data)
        
        assert metadata["custom_field"] == "custom_value"
        assert metadata["another_field"] == 123
        assert "system_prompt" not in metadata
    
    def test_extract_prompt_metadata_empty_data(self, discovery_service):
        """Test extracting metadata from minimal prompt data."""
        data = {
            "system_prompt": "System"
        }
        
        metadata = discovery_service.extract_prompt_metadata(data)
        
        assert len(metadata) == 0
    
    # Test: scan_directory_recursive
    def test_scan_directory_recursive_with_depth_limit(self, discovery_service, tmp_path):
        """Test recursive scanning respects max depth."""
        # Create deeply nested structure
        base = tmp_path / "base"
        base.mkdir()
        
        current = base
        for i in range(15):
            current = current / f"level{i}"
            current.mkdir()
            if i < 10:  # Within default depth
                prompt = current / f"prompt{i}.yaml"
                prompt.write_text(yaml.dump({"system_prompt": f"Level {i}"}))
        
        prompt_files = discovery_service.scan_directory_recursive(base, max_depth=10)
        
        # Should only find prompts within depth 10
        assert len(prompt_files) <= 10
    
    def test_scan_directory_recursive_skips_hidden(self, discovery_service, tmp_path):
        """Test recursive scan skips hidden directories."""
        base = tmp_path / "base"
        base.mkdir()
        
        # Create visible directory with prompt
        visible = base / "visible"
        visible.mkdir()
        visible_prompt = visible / "prompt.yaml"
        visible_prompt.write_text(yaml.dump({"system_prompt": "Visible"}))
        
        # Create hidden directory with prompt
        hidden = base / ".hidden"
        hidden.mkdir()
        hidden_prompt = hidden / "prompt.yaml"
        hidden_prompt.write_text(yaml.dump({"system_prompt": "Hidden"}))
        
        prompt_files = discovery_service.scan_directory_recursive(base)
        
        assert len(prompt_files) == 1
        assert prompt_files[0].name == "prompt"
    
    # Test: find_prompts_by_pattern
    def test_find_prompts_by_pattern_default(self, discovery_service, tmp_path):
        """Test finding prompts by default pattern."""
        repo_path = tmp_path / "repo"
        repo_path.mkdir()
        
        # Create files matching default pattern
        prompt1 = repo_path / "test.prompt.yaml"
        prompt1.write_text(yaml.dump({"system_prompt": "Test"}))
        
        # Create file not matching pattern
        prompt2 = repo_path / "other.yaml"
        prompt2.write_text(yaml.dump({"system_prompt": "Other"}))
        
        prompt_files = discovery_service.find_prompts_by_pattern(repo_path)
        
        assert len(prompt_files) == 1
        assert prompt_files[0].name == "test.prompt"
    
    def test_find_prompts_by_pattern_custom(self, discovery_service, tmp_path):
        """Test finding prompts by custom pattern."""
        repo_path = tmp_path / "repo"
        repo_path.mkdir()
        
        # Create files
        prompt1 = repo_path / "agent.yaml"
        prompt1.write_text(yaml.dump({"system_prompt": "Agent"}))
        
        prompt2 = repo_path / "template.yaml"
        prompt2.write_text(yaml.dump({"system_prompt": "Template"}))
        
        prompt_files = discovery_service.find_prompts_by_pattern(repo_path, "agent.yaml")
        
        assert len(prompt_files) == 1
        assert prompt_files[0].name == "agent"
    
    # Test: get_statistics
    def test_get_statistics_after_successful_scan(self, discovery_service, temp_repo):
        """Test statistics after successful scan."""
        discovery_service.scan_repository(temp_repo)
        stats = discovery_service.get_statistics()
        
        assert stats["discovered"] == 4.0
        assert stats["errors"] >= 1.0  # At least corrupted file
        assert 0.0 < stats["success_rate"] <= 1.0
    
    def test_get_statistics_with_no_scans(self, discovery_service):
        """Test statistics before any scans."""
        stats = discovery_service.get_statistics()
        
        assert stats["discovered"] == 0.0
        assert stats["errors"] == 0.0
        assert stats["success_rate"] == 0.0
    
    def test_get_statistics_resets_between_scans(self, discovery_service, tmp_path):
        """Test that statistics reset between scans."""
        # First scan
        repo1 = tmp_path / "repo1"
        repo1.mkdir()
        (repo1 / "prompt.yaml").write_text(yaml.dump({"system_prompt": "Test"}))
        discovery_service.scan_repository(repo1)
        
        assert discovery_service.discovered_count == 1
        
        # Second scan should reset
        repo2 = tmp_path / "repo2"
        repo2.mkdir()
        (repo2 / "prompt1.yaml").write_text(yaml.dump({"system_prompt": "Test 1"}))
        (repo2 / "prompt2.yaml").write_text(yaml.dump({"system_prompt": "Test 2"}))
        discovery_service.scan_repository(repo2)
        
        assert discovery_service.discovered_count == 2