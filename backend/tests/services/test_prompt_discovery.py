"""
Unit tests for the Prompt Discovery Service.

Tests the prompt discovery functionality for scanning repositories.
"""

import pytest
from pathlib import Path
import tempfile
import yaml

from services.prompt.prompt_discovery_service import PromptDiscoveryService


class TestPromptDiscoveryService:
    """Test suite for PromptDiscoveryService."""
    
    @pytest.fixture
    def discovery_service(self):
        """Create PromptDiscoveryService instance."""
        return PromptDiscoveryService()
    
    @pytest.fixture
    def temp_repo(self):
        """Create a temporary repository with prompt files."""
        with tempfile.TemporaryDirectory() as tmpdir:
            repo_path = Path(tmpdir)
            
            # Create a valid prompt file
            prompt1 = repo_path / "prompt1.yaml"
            prompt1.write_text(yaml.dump({
                "name": "Test Prompt 1",
                "system_prompt": "You are a helpful assistant",
                "user_prompt": "Help me with coding",
                "category": "coding",
                "tags": ["python", "test"]
            }))
            
            # Create another valid prompt file in subdirectory
            subdir = repo_path / "prompts"
            subdir.mkdir()
            prompt2 = subdir / "prompt2.yml"
            prompt2.write_text(yaml.dump({
                "system_prompt": "You are an expert",
                "user_prompt": "Explain this concept",
                "description": "Educational prompt"
            }))
            
            # Create an invalid YAML file (no prompts)
            invalid = repo_path / "config.yaml"
            invalid.write_text(yaml.dump({
                "setting": "value",
                "another": "config"
            }))
            
            # Create a non-YAML file
            other_file = repo_path / "readme.txt"
            other_file.write_text("This is not a prompt file")
            
            yield repo_path
    
    def test_scan_repository_finds_prompts(self, discovery_service, temp_repo):
        """Test that scan_repository finds valid prompt files."""
        # Act
        prompt_files = discovery_service.scan_repository(temp_repo)
        
        # Assert
        assert len(prompt_files) == 2
        
        # Check first prompt
        prompt_names = [pf.name for pf in prompt_files]
        assert "prompt1" in prompt_names
        assert "prompt2" in prompt_names
        
        # Verify content
        prompt1 = next(pf for pf in prompt_files if pf.name == "prompt1")
        assert prompt1.system_prompt == "You are a helpful assistant"
        assert prompt1.user_prompt == "Help me with coding"
        assert prompt1.metadata["category"] == "coding"
        assert prompt1.metadata["tags"] == ["python", "test"]
    
    def test_validate_prompt_structure_valid(self, discovery_service):
        """Test validating a valid prompt structure."""
        # Arrange
        valid_data = {
            "system_prompt": "System prompt",
            "user_prompt": "User prompt",
            "description": "Test"
        }
        
        # Act
        is_valid = discovery_service.validate_prompt_structure(valid_data)
        
        # Assert
        assert is_valid is True
    
    def test_validate_prompt_structure_invalid(self, discovery_service):
        """Test validating an invalid prompt structure."""
        # Arrange
        invalid_data = {
            "description": "No prompts here"
        }
        
        # Act
        is_valid = discovery_service.validate_prompt_structure(invalid_data)
        
        # Assert
        assert is_valid is False
    
    def test_extract_prompt_metadata(self, discovery_service):
        """Test extracting metadata from prompt data."""
        # Arrange
        prompt_data = {
            "system_prompt": "System",
            "user_prompt": "User",
            "name": "Test Prompt",
            "category": "testing",
            "tags": ["test", "example"],
            "custom_field": "custom_value"
        }
        
        # Act
        metadata = discovery_service.extract_prompt_metadata(prompt_data)
        
        # Assert
        assert metadata["name"] == "Test Prompt"
        assert metadata["category"] == "testing"
        assert metadata["tags"] == ["test", "example"]
        assert metadata["custom_field"] == "custom_value"
        assert "system_prompt" not in metadata
        assert "user_prompt" not in metadata
    
    def test_scan_empty_repository(self, discovery_service):
        """Test scanning an empty repository."""
        with tempfile.TemporaryDirectory() as tmpdir:
            # Act
            prompt_files = discovery_service.scan_repository(Path(tmpdir))
            
            # Assert
            assert len(prompt_files) == 0
            assert discovery_service.discovered_count == 0
            assert discovery_service.error_count == 0
    
    def test_scan_nonexistent_repository(self, discovery_service):
        """Test scanning a non-existent repository."""
        # Act
        prompt_files = discovery_service.scan_repository(Path("/nonexistent/path"))
        
        # Assert
        assert len(prompt_files) == 0
    
    def test_get_statistics(self, discovery_service, temp_repo):
        """Test getting scan statistics."""
        # Act
        discovery_service.scan_repository(temp_repo)
        stats = discovery_service.get_statistics()
        
        # Assert
        assert stats["discovered"] == 2.0
        assert stats["errors"] == 0.0
        assert stats["success_rate"] == 1.0