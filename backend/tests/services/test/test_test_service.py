"""
Unit tests for Eval Service.

Tests cover:
- Eval suite CRUD operations
- Execution history retrieval
- File operations and error handling
"""

import pytest
from datetime import datetime
from pathlib import Path
from unittest.mock import Mock, patch, MagicMock
from typing import Dict, Any

from services.evals.eval_meta_service import EvalMetaService
from services.evals.models import (
    EvalSuiteData,
    EvalSuiteDefinition,
    EvalDefinition,
    MetricConfig,
    MetricType,
    EvalSuiteExecutionResult,
    EvalExecutionResult,
    EvalSuiteSummary,
    ExpectedEvaluationFieldsModel
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
    """Create EvalMetaService instance with mocked dependencies."""
    return EvalMetaService(
        config_service=mock_config_service,
        file_ops_service=mock_file_ops_service,
        local_repo_service=mock_local_repo_service
    )


@pytest.fixture
def sample_eval_suite():
    """Create sample eval suite for testing."""
    metric_config = MetricConfig(
        type=MetricType.ANSWER_RELEVANCY,
        threshold=0.8,
        model="gpt-4",
        include_reason=True,
        strict_mode=False
    )
    
    unit_test = EvalDefinition(
        name="test-login-prompt",
        description="Test login prompt",
        prompt_reference="file:///.promptrepo/prompts/auth/login.yaml",
        template_variables={"user_question": "How do I reset my password?"},
        evaluation_fields=ExpectedEvaluationFieldsModel(
            metric_type=MetricType.ANSWER_RELEVANCY,
            config={"expected_output": "Click 'Forgot Password' link"}
        ),
        enabled=True
    )
    
    suite_def = EvalSuiteDefinition(
        name="auth-suite",
        description="Authentication eval suite",
        evals=[unit_test],
        tags=["auth", "security"],
        created_at=datetime.utcnow(),
        updated_at=datetime.utcnow()
    )
    
    return EvalSuiteData(eval_suite=suite_def)


class TestEvalServiceCRUD:
    """Test CRUD operations for eval suites."""
    
    @pytest.mark.asyncio
    async def test_list_eval_suites_empty_directory(
        self, test_service, mock_file_ops_service
    ):
        """Test listing eval suites when directory doesn't exist."""
        with patch('pathlib.Path.exists', return_value=True):
            with patch('pathlib.Path.iterdir', return_value=[]):
                with patch.object(Path, '__truediv__', return_value=Path('/tmp/test')):
                    suites = await test_service.list_eval_suites("user1", "repo1")
                    assert suites == []
    
    @pytest.mark.asyncio
    async def test_list_eval_suites_repository_not_found(self, test_service):
        """Test listing eval suites when repository doesn't exist."""
        with patch('pathlib.Path.exists', return_value=False):
            with pytest.raises(NotFoundException) as exc_info:
                await test_service.list_eval_suites("user1", "nonexistent-repo")
            assert "Repository" in str(exc_info.value.message)
    
    @pytest.mark.asyncio
    async def test_get_eval_suite_success(
        self, test_service, mock_file_ops_service, sample_eval_suite
    ):
        """Test getting an eval suite successfully."""
        suite_dict = sample_eval_suite.model_dump(mode='json')
        mock_file_ops_service.load_yaml_file.return_value = suite_dict
        
        with patch('pathlib.Path.exists', return_value=True):
            result = await test_service.get_eval_suite("user1", "repo1", "auth-suite")
            
            assert result is not None
            assert result.eval_suite.name == "auth-suite"
            assert len(result.eval_suite.evals) == 1
    
    @pytest.mark.asyncio
    async def test_get_eval_suite_not_found(self, test_service):
        """Test getting non-existent eval suite."""
        with patch('pathlib.Path.exists', return_value=False):
            with pytest.raises(NotFoundException) as exc_info:
                await test_service.get_eval_suite("user1", "repo1", "nonexistent")
            assert "Eval suite" in str(exc_info.value.message)
    
    @pytest.mark.asyncio
    async def test_save_eval_suite_create(
        self, test_service, mock_file_ops_service, sample_eval_suite
    ):
        """Test creating a new eval suite."""
        mock_file_ops_service.save_yaml_file.return_value = True
        
        with patch('pathlib.Path.exists', side_effect=[True, False]):
            result = await test_service.save_eval_suite(
                "user1", "repo1", sample_eval_suite
            )
            
            assert result is not None
            assert result.eval_suite.name == "auth-suite"
            assert mock_file_ops_service.save_yaml_file.called
    
    @pytest.mark.asyncio
    async def test_save_eval_suite_update(
        self, test_service, mock_file_ops_service, sample_eval_suite
    ):
        """Test updating an existing eval suite."""
        existing_data = sample_eval_suite.model_dump(mode='json')
        mock_file_ops_service.load_yaml_file.return_value = existing_data
        mock_file_ops_service.save_yaml_file.return_value = True
        
        with patch('pathlib.Path.exists', return_value=True):
            result = await test_service.save_eval_suite(
                "user1", "repo1", sample_eval_suite
            )
            
            assert result is not None
            assert mock_file_ops_service.save_yaml_file.called
    
    @pytest.mark.asyncio
    async def test_delete_eval_suite_success(
        self, test_service, mock_file_ops_service
    ):
        """Test deleting an eval suite successfully."""
        mock_file_ops_service.delete_directory.return_value = True
        
        with patch('pathlib.Path.exists', return_value=True):
            result = await test_service.delete_eval_suite("user1", "repo1", "auth-suite")
            
            assert result is True
            assert mock_file_ops_service.delete_directory.called
    
    @pytest.mark.asyncio
    async def test_delete_eval_suite_not_found(self, test_service):
        """Test deleting non-existent eval suite."""
        with patch('pathlib.Path.exists', side_effect=[True, False]):
            with pytest.raises(NotFoundException):
                await test_service.delete_eval_suite("user1", "repo1", "nonexistent")


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
        
        execution_result = EvalSuiteExecutionResult(
            suite_name="auth-suite",
            eval_results=[],
            total_evals=0,
            passed_evals=0,
            failed_evals=0,
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