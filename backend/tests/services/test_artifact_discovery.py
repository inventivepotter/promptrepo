"""
Unit tests for artifact discovery functionality.

Tests the generalized artifact discovery mechanism in LocalRepoService
and its integration with PromptService and ToolService.
"""

import pytest
from pathlib import Path
from unittest.mock import Mock, patch
import tempfile
import shutil

from schemas.artifact_type_enum import ArtifactType
from services.local_repo.local_repo_service import LocalRepoService
from services.local_repo.models import ArtifactDiscoveryResult
from services.config.config_service import ConfigService
from schemas.hosting_type_enum import HostingType


class TestArtifactDiscoveryResult:
    """Test ArtifactDiscoveryResult model."""
    
    def test_create_empty_result(self):
        """Test creating an empty discovery result."""
        result = ArtifactDiscoveryResult()
        assert result.prompts == []
        assert result.tools == []
    
    def test_add_prompt_file(self):
        """Test adding a prompt file."""
        result = ArtifactDiscoveryResult()
        result.add_file("prompts/test.prompt.yaml", ArtifactType.PROMPT)
        
        assert len(result.prompts) == 1
        assert "prompts/test.prompt.yaml" in result.prompts
        assert len(result.tools) == 0
    
    def test_add_tool_file(self):
        """Test adding a tool file."""
        result = ArtifactDiscoveryResult()
        result.add_file(".promptrepo/mock_tools/test.tool.yaml", ArtifactType.TOOL)
        
        assert len(result.tools) == 1
        assert ".promptrepo/mock_tools/test.tool.yaml" in result.tools
        assert len(result.prompts) == 0
    
    def test_get_files_by_type(self):
        """Test getting files by artifact type."""
        result = ArtifactDiscoveryResult()
        result.add_file("prompts/p1.prompt.yaml", ArtifactType.PROMPT)
        result.add_file("prompts/p2.prompt.yaml", ArtifactType.PROMPT)
        result.add_file("tools/t1.tool.yaml", ArtifactType.TOOL)
        
        prompts = result.get_files_by_type(ArtifactType.PROMPT)
        tools = result.get_files_by_type(ArtifactType.TOOL)
        
        assert len(prompts) == 2
        assert len(tools) == 1
        assert "prompts/p1.prompt.yaml" in prompts
        assert "prompts/p2.prompt.yaml" in prompts
        assert "tools/t1.tool.yaml" in tools


class TestLocalRepoServiceDiscovery:
    """Test LocalRepoService artifact discovery."""
    
    @pytest.fixture
    def temp_repo(self):
        """Create a temporary repository for testing."""
        temp_dir = tempfile.mkdtemp()
        repo_path = Path(temp_dir) / "test-repo"
        repo_path.mkdir(parents=True)
        
        # Create directory structure
        (repo_path / "prompts").mkdir()
        (repo_path / ".promptrepo" / "mock_tools").mkdir(parents=True)
        
        yield repo_path
        
        # Cleanup
        shutil.rmtree(temp_dir)
    
    @pytest.fixture
    def mock_config_service(self, temp_repo):
        """Create a mock config service."""
        config_service = Mock(spec=ConfigService)
        
        # Mock hosting config
        hosting_config = Mock()
        hosting_config.type = HostingType.INDIVIDUAL
        config_service.get_hosting_config.return_value = hosting_config
        
        return config_service
    
    @pytest.fixture
    def local_repo_service(self, mock_config_service, temp_repo):
        """Create LocalRepoService instance for testing."""
        service = LocalRepoService(
            config_service=mock_config_service,
            db=None,
            remote_repo_service=None
        )
        
        # Mock the _get_repo_base_path to return our temp directory
        service._get_repo_base_path = Mock(return_value=temp_repo.parent)
        
        return service
    
    def test_discover_artifacts_empty_repo(self, local_repo_service):
        """Test discovery in an empty repository."""
        result = local_repo_service.discover_artifacts("test-user", "test-repo")
        
        assert isinstance(result, ArtifactDiscoveryResult)
        assert len(result.prompts) == 0
        assert len(result.tools) == 0
    
    def test_discover_artifacts_with_prompts(self, local_repo_service, temp_repo):
        """Test discovery with prompt files."""
        # Create prompt files
        (temp_repo / "prompts" / "example.prompt.yaml").write_text("name: Example")
        (temp_repo / "prompts" / "another.prompt.yaml").write_text("name: Another")
        
        result = local_repo_service.discover_artifacts("test-user", "test-repo")
        
        assert len(result.prompts) == 2
        assert len(result.tools) == 0
        assert any("example.prompt.yaml" in p for p in result.prompts)
        assert any("another.prompt.yaml" in p for p in result.prompts)
    
    def test_discover_artifacts_with_tools(self, local_repo_service, temp_repo):
        """Test discovery with tool files."""
        # Create tool files
        (temp_repo / ".promptrepo" / "mock_tools" / "get_weather.tool.yaml").write_text("tool: {}")
        (temp_repo / ".promptrepo" / "mock_tools" / "send_email.tool.yaml").write_text("tool: {}")
        
        result = local_repo_service.discover_artifacts("test-user", "test-repo")
        
        assert len(result.prompts) == 0
        assert len(result.tools) == 2
        assert any("get_weather.tool.yaml" in t for t in result.tools)
        assert any("send_email.tool.yaml" in t for t in result.tools)
    
    def test_discover_artifacts_mixed(self, local_repo_service, temp_repo):
        """Test discovery with both prompts and tools."""
        # Create prompt files
        (temp_repo / "prompts" / "p1.prompt.yaml").write_text("name: P1")
        (temp_repo / "prompts" / "p2.prompt.yaml").write_text("name: P2")
        
        # Create tool files
        (temp_repo / ".promptrepo" / "mock_tools" / "t1.tool.yaml").write_text("tool: {}")
        
        result = local_repo_service.discover_artifacts("test-user", "test-repo")
        
        assert len(result.prompts) == 2
        assert len(result.tools) == 1
    
    def test_discover_artifacts_ignores_hidden_files(self, local_repo_service, temp_repo):
        """Test that discovery ignores hidden files and directories."""
        # Create hidden files and directories
        (temp_repo / ".git").mkdir()
        (temp_repo / ".git" / "config.prompt.yaml").write_text("name: Hidden")
        (temp_repo / "prompts" / ".hidden.prompt.yaml").write_text("name: Hidden")
        
        # Create valid files
        (temp_repo / "prompts" / "valid.prompt.yaml").write_text("name: Valid")
        
        result = local_repo_service.discover_artifacts("test-user", "test-repo")
        
        assert len(result.prompts) == 1
        assert "valid.prompt.yaml" in result.prompts[0]
    
    def test_discover_artifacts_ignores_non_matching_extensions(self, local_repo_service, temp_repo):
        """Test that discovery ignores files that don't match patterns."""
        # Create files with wrong extensions
        (temp_repo / "prompts" / "config.yaml").write_text("name: Config")
        (temp_repo / "prompts" / "data.yml").write_text("name: Data")
        (temp_repo / "prompts" / "readme.md").write_text("# Readme")
        
        # Create valid prompt file
        (temp_repo / "prompts" / "valid.prompt.yaml").write_text("name: Valid")
        
        result = local_repo_service.discover_artifacts("test-user", "test-repo")
        
        assert len(result.prompts) == 1
        assert "valid.prompt.yaml" in result.prompts[0]
    
    def test_discover_artifacts_non_existent_repo(self, local_repo_service):
        """Test discovery for non-existent repository."""
        result = local_repo_service.discover_artifacts("test-user", "non-existent")
        
        assert isinstance(result, ArtifactDiscoveryResult)
        assert len(result.prompts) == 0
        assert len(result.tools) == 0
    
    def test_discover_artifacts_nested_structure(self, local_repo_service, temp_repo):
        """Test discovery in nested directory structure."""
        # Create nested directories
        (temp_repo / "prompts" / "category1").mkdir()
        (temp_repo / "prompts" / "category2").mkdir()
        
        # Create prompt files in nested directories
        (temp_repo / "prompts" / "category1" / "p1.prompt.yaml").write_text("name: P1")
        (temp_repo / "prompts" / "category2" / "p2.prompt.yaml").write_text("name: P2")
        (temp_repo / "prompts" / "root.prompt.yaml").write_text("name: Root")
        
        result = local_repo_service.discover_artifacts("test-user", "test-repo")
        
        assert len(result.prompts) == 3
    
    def test_artifact_extension_patterns(self):
        """Test that extension patterns are correctly defined."""
        patterns = LocalRepoService.ARTIFACT_EXTENSION_PATTERNS
        
        assert ArtifactType.PROMPT in patterns
        assert ArtifactType.TOOL in patterns
        assert patterns[ArtifactType.PROMPT] == ".prompt.yaml"
        assert patterns[ArtifactType.TOOL] == ".tool.yaml"


class TestArtifactTypeEnum:
    """Test ArtifactType enum usage."""
    
    def test_artifact_types_exist(self):
        """Test that required artifact types exist."""
        assert hasattr(ArtifactType, 'PROMPT')
        assert hasattr(ArtifactType, 'TOOL')
    
    def test_artifact_type_values(self):
        """Test artifact type string values."""
        assert ArtifactType.PROMPT.value == "prompt"
        assert ArtifactType.TOOL.value == "tool"
    
    def test_artifact_type_string_representation(self):
        """Test string representation of artifact types."""
        assert str(ArtifactType.PROMPT) == "prompt"
        assert str(ArtifactType.TOOL) == "tool"