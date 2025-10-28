"""
Unit tests for Test Service.

Tests cover:
- Test suite CRUD operations
- Execution history retrieval
- File operations and error handling
"""

import pytest
from datetime import datetime
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any

from services.test.test_service import TestService
from services.test.models import (
    TestSuiteData,
    TestSuiteDefinition,
    UnitTestDefinition,
    MetricConfig,
    MetricType,
    TestSuiteExecutionResult,
    UnitTestExecutionResult,
    TestSuiteSummary
)
from schemas.hosting_type_enum import HostingType
from middlewares.rest.exceptions import NotFoundException, AppException


@pytest.fixture
def mock_config_service():
    """Mock configuration service."""
    config_service = Mock()
    hosting_config = Mock()
    hosting_config.type = HostingType.INDIVIDUAL
    config_service.get_hosting_config.return_value = hosting_config
    return config_service


@pytest.fixture
def mock_file_ops_service():
    """Mock file operations service."""
    return Mock()


@pytest.fixture
def mock_local_repo_service():
    """Mock local repository service."""
    return Mock()


@pytest.fixture
def test_service(mock_config_service, mock_file_ops_service, mock_local_repo_service):
    """Create TestService instance with mocked dependencies."""
    return TestService(
        config_service=mock_config_service,
        file_ops_service=mock_file_ops_service,
        local_repo_service=mock_local_repo_service
    )


@pytest.fixture
def sample_test_suite():
    """Create sample test suite for testing."""
    metric_config = MetricConfig(
        type=MetricType.ANSWER_RELEVANCY,
        threshold=0.8,
        model="gpt-4",
        include_reason=True,
        strict_mode=False
    )
    
    unit_test = UnitTestDefinition(
        name="test-login-prompt",
        description="Test login prompt",
        prompt_reference="file:///.promptrepo/prompts/auth/login.yaml",
        template_variables={"user_question": "How do I reset my password?"},
        expected_output="Click 'Forgot Password' link",
        metrics=[metric_config],
        enabled=True
    )
    
    suite_def = TestSuiteDefinition(
        name="auth-suite",
        description="Authentication test suite",
        tests=[unit_test],
        tags=["auth", "security"],
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    
    return TestSuiteData(test_suite=suite_def)


class TestTestServiceCRUD:
    """Test CRUD operations for test suites."""
    
    @pytest.mark.asyncio
    async def test_list_test_suites_empty_directory(
        self, test_service, mock_file_ops_service
    ):
        """Test listing test suites when directory doesn't exist."""
        with patch('pathlib.Path.exists', return_value=True):
            with patch('pathlib.Path.iterdir', return_value=[]):
                with patch.object(Path, '__truediv__', return_value=Path('/tmp/test')):
                    suites = await test_service.list_test_suites("user1", "repo1")
                    assert suites == []
    
    @pytest.mark.asyncio
    async def test_list_test_suites_repository_not_found(self, test_service):
        """Test listing test suites when repository doesn't exist."""
        with patch('pathlib.Path.exists', return_value=False):
            with pytest.raises(NotFoundException) as exc_info:
                await test_service.list_test_suites("user1", "nonexistent-repo")
            assert "Repository" in str(exc_info.value.message)
    
    @pytest.mark.asyncio
    async def test_get_test_suite_success(
        self, test_service, mock_file_ops_service, sample_test_suite
    ):
        """Test getting a test suite successfully."""
        suite_dict = sample_test_suite.model_dump(mode='json')
        mock_file_ops_service.load_yaml_file.return_value = suite_dict
        
        with patch('pathlib.Path.exists', return_value=True):
            result = await test_service.get_test_suite("user1", "repo1", "auth-suite")
            
            assert result is not None
            assert result.test_suite.name == "auth-suite"
            assert len(result.test_suite.tests) == 1
    
    @pytest.mark.asyncio
    async def test_get_test_suite_not_found(self, test_service):
        """Test getting non-existent test suite."""
        with patch('pathlib.Path.exists', return_value=False):
            with pytest.raises(NotFoundException) as exc_info:
                await test_service.get_test_suite("user1", "repo1", "nonexistent")
            assert "Test suite" in str(exc_info.value.message)
    
    @pytest.mark.asyncio
    async def test_save_test_suite_create(
        self, test_service, mock_file_ops_service, sample_test_suite
    ):
        """Test creating a new test suite."""
        mock_file_ops_service.save_yaml_file.return_value = True
        
        with patch('pathlib.Path.exists', side_effect=[True, False]):
            result = await test_service.save_test_suite(
                "user1", "repo1", sample_test_suite
            )
            
            assert result is not None
            assert result.test_suite.name == "auth-suite"
            assert mock_file_ops_service.save_yaml_file.called
    
    @pytest.mark.asyncio
    async def test_save_test_suite_update(
        self, test_service, mock_file_ops_service, sample_test_suite
    ):
        """Test updating an existing test suite."""
        existing_data = sample_test_suite.model_dump(mode='json')
        mock_file_ops_service.load_yaml_file.return_value = existing_data
        mock_file_ops_service.save_yaml_file.return_value = True
        
        with patch('pathlib.Path.exists', return_value=True):
            result = await test_service.save_test_suite(
                "user1", "repo1", sample_test_suite
            )
            
            assert result is not None
            assert mock_file_ops_service.save_yaml_file.called
    
    @pytest.mark.asyncio
    async def test_delete_test_suite_success(
        self, test_service, mock_file_ops_service
    ):
        """Test deleting a test suite successfully."""
        mock_file_ops_service.delete_directory.return_value = True
        
        with patch('pathlib.Path.exists', return_value=True):
            result = await test_service.delete_test_suite("user1", "repo1", "auth-suite")
            
            assert result is True
            assert mock_file_ops_service.delete_directory.called
    
    @pytest.mark.asyncio
    async def test_delete_test_suite_not_found(self, test_service):
        """Test deleting non-existent test suite."""
        with patch('pathlib.Path.exists', side_effect=[True, False]):
            with pytest.raises(NotFoundException):
                await test_service.delete_test_suite("user1", "repo1", "nonexistent")


class TestExecutionHistory:
    """Test execution history operations."""
    
    @pytest.mark.asyncio
    async def test_list_executions_empty(self, test_service):
        """Test listing executions when directory doesn't exist."""
        with patch('pathlib.Path.exists', side_effect=[True, False]):
            executions = await test_service.list_executions(
                "user1", "repo1", "auth-suite"
            )
            assert executions == []
    
    @pytest.mark.asyncio
    async def test_get_latest_execution_none(self, test_service):
        """Test getting latest execution when none exist."""
        with patch('pathlib.Path.exists', side_effect=[True, False]):
            latest = await test_service.get_latest_execution(
                "user1", "repo1", "auth-suite"
            )
            assert latest is None
    
    @pytest.mark.asyncio
    async def test_save_execution_result(
        self, test_service, mock_file_ops_service
    ):
        """Test saving execution result."""
        mock_file_ops_service.create_directory.return_value = True
        mock_file_ops_service.save_yaml_file.return_value = True
        
        execution_result = TestSuiteExecutionResult(
            suite_name="auth-suite",
            test_results=[],
            total_tests=0,
            passed_tests=0,
            failed_tests=0,
            total_execution_time_ms=100,
            executed_at=datetime.utcnow()
        )
        
        with patch('pathlib.Path.exists', return_value=True):
            result = await test_service.save_execution_result(
                "user1", "repo1", "auth-suite", execution_result
            )
            
            assert result is True
            assert mock_file_ops_service.save_yaml_file.called


class TestPathOperations:
    """Test path-related operations."""
    
    def test_get_repo_base_path_individual(self, test_service):
        """Test getting repo base path for individual hosting."""
        with patch('settings.settings.local_repo_path', '/tmp/repos'):
            path = test_service._get_repo_base_path("user1")
            assert str(path) == '/tmp/repos'
    
    def test_get_repo_base_path_organization(
        self, test_service, mock_config_service
    ):
        """Test getting repo base path for organization hosting."""
        hosting_config = Mock()
        hosting_config.type = HostingType.ORGANIZATION
        mock_config_service.get_hosting_config.return_value = hosting_config
        
        with patch('settings.settings.multi_user_repo_path', '/tmp/multi'):
            path = test_service._get_repo_base_path("user1")
            assert "user1" in str(path)