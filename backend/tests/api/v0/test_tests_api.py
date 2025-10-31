"""
Unit tests for Test API endpoints.

Tests the test suite CRUD operations and execution endpoints.
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, AsyncMock
from datetime import datetime

import sys
import os
sys.path.append(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from main import app
from services.evals.models import (
    EvalSuiteData,
    EvalSuiteDefinition,
    EvalSuiteSummary,
    EvalDefinition,
    MetricConfig,
    MetricType,
    EvalSuiteExecutionResult,
    EvalExecutionResult,
    MetricResult,
    ExpectedEvaluationFieldsModel
)
from api.deps import get_eval_service, get_eval_execution_service, get_current_user


@pytest.fixture
def client():
    """Create test client"""
    return TestClient(app)


@pytest.fixture
def mock_eval_service():
    """Create mock eval service"""
    service = Mock()
    service.list_eval_suites = AsyncMock()
    service.get_eval_suite = AsyncMock()
    service.save_eval_suite = AsyncMock()
    service.delete_eval_suite = AsyncMock()
    service.list_executions = AsyncMock()
    service.get_latest_execution = AsyncMock()
    return service


@pytest.fixture
def mock_eval_execution_service():
    """Create mock eval execution service"""
    service = Mock()
    service.execute_eval_suite = AsyncMock()
    service.execute_single_eval = AsyncMock()
    service.eval_service = Mock()
    service.eval_service.list_executions = AsyncMock()
    service.eval_service.get_latest_execution = AsyncMock()
    return service


@pytest.fixture
def sample_eval_suite():
    """Create sample eval suite"""
    return EvalSuiteData(
        eval_suite=EvalSuiteDefinition(
            name="sample-suite",
            description="Sample eval suite",
            evals=[
                EvalDefinition(
                    name="test1",
                    description="Test 1",
                    prompt_reference="file:///.promptrepo/prompts/test.yaml",
                    template_variables={"user_question": "What is AI?"},
                    evaluation_fields=ExpectedEvaluationFieldsModel(
                        metric_type=MetricType.ANSWER_RELEVANCY,
                        config={}
                    )
                )
            ],
            tags=["sample"],
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
    )


class TestSuitesAPI:
    """Eval suite CRUD endpoint tests"""
    
    def test_list_eval_suites_success(self, client, mock_eval_service):
        """Test listing eval suites successfully"""
        # Setup
        mock_eval_service.list_eval_suites.return_value = [
            EvalSuiteSummary(
                name="suite1",
                description="Suite 1",
                eval_count=2,
                tags=["tag1"],
                file_path=".promptrepo/evals/suite1/suite.yaml",
                last_execution=None,
                last_execution_passed=None
            )
        ]
        
        # Override dependencies
        app.dependency_overrides[get_eval_service] = lambda: mock_eval_service
        app.dependency_overrides[get_current_user] = lambda: "test-user"
        
        try:
            # Execute
            response = client.get(
                "/api/v0/evals/suites?repo_name=test-repo"
            )
            
            # Assert
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "success"
            assert len(data["data"]) == 1
            assert data["data"][0]["name"] == "suite1"
        finally:
            # Cleanup
            app.dependency_overrides.clear()
    
    def test_get_eval_suite_success(self, client, mock_eval_service, sample_eval_suite):
        """Test getting specific eval suite"""
        # Setup
        mock_eval_service.get_eval_suite.return_value = sample_eval_suite
        
        # Override dependencies
        app.dependency_overrides[get_eval_service] = lambda: mock_eval_service
        app.dependency_overrides[get_current_user] = lambda: "test-user"
        
        try:
            # Execute
            response = client.get(
                "/api/v0/evals/suites/sample-suite?repo_name=test-repo"
            )
            
            # Assert
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "success"
            assert data["data"]["eval_suite"]["name"] == "sample-suite"
        finally:
            # Cleanup
            app.dependency_overrides.clear()
    
    def test_save_eval_suite_success(self, client, mock_eval_service, sample_eval_suite):
        """Test creating/updating eval suite"""
        # Setup
        mock_eval_service.save_eval_suite.return_value = sample_eval_suite
        
        # Override dependencies
        app.dependency_overrides[get_eval_service] = lambda: mock_eval_service
        app.dependency_overrides[get_current_user] = lambda: "test-user"
        
        try:
            # Execute
            response = client.post(
                "/api/v0/evals/suites?repo_name=test-repo",
                json=sample_eval_suite.model_dump(mode='json')
            )
            
            # Assert
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "success"
            assert data["data"]["eval_suite"]["name"] == "sample-suite"
        finally:
            # Cleanup
            app.dependency_overrides.clear()
    
    def test_delete_eval_suite_success(self, client, mock_eval_service):
        """Test deleting eval suite"""
        # Setup
        mock_eval_service.delete_eval_suite.return_value = True
        
        # Override dependencies
        app.dependency_overrides[get_eval_service] = lambda: mock_eval_service
        app.dependency_overrides[get_current_user] = lambda: "test-user"
        
        try:
            # Execute
            response = client.delete(
                "/api/v0/evals/suites/sample-suite?repo_name=test-repo"
            )
            
            # Assert
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "success"
            assert data["data"]["deleted"] is True
        finally:
            # Cleanup
            app.dependency_overrides.clear()


class TestExecutionAPI:
    """Eval execution endpoint tests"""
    
    def test_execute_eval_suite_success(self, client, mock_eval_execution_service):
        """Test executing eval suite"""
        # Setup
        mock_eval_execution_service.execute_eval_suite.return_value = EvalSuiteExecutionResult(
            suite_name="sample-suite",
            eval_results=[],
            total_evals=1,
            passed_evals=1,
            failed_evals=0,
            total_execution_time_ms=100,
            executed_at=datetime.utcnow()
        )
        
        # Override dependencies
        app.dependency_overrides[get_eval_execution_service] = lambda: mock_eval_execution_service
        app.dependency_overrides[get_current_user] = lambda: "test-user"
        
        try:
            # Execute
            response = client.post(
                "/api/v0/evals/suites/sample-suite/execute?repo_name=test-repo",
                json={}
            )
            
            # Assert
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "success"
            assert data["data"]["suite_name"] == "sample-suite"
            assert data["data"]["passed_evals"] == 1
        finally:
            # Cleanup
            app.dependency_overrides.clear()
    
    def test_execute_single_eval_success(self, client, mock_eval_execution_service):
        """Test executing single eval"""
        from services.evals.models import ActualEvaluationFieldsModel, ExpectedEvaluationFieldsModel
        
        # Setup
        mock_eval_execution_service.execute_single_eval.return_value = EvalExecutionResult(
            eval_name="test1",
            prompt_reference="file:///.promptrepo/prompts/test.yaml",
            template_variables={"user_question": "What is AI?"},
            actual_evaluation_fields=ActualEvaluationFieldsModel(actual_output="Test output"),
            expected_evaluation_fields=ExpectedEvaluationFieldsModel(),
            metric_results=[
                MetricResult(
                    type=MetricType.ANSWER_RELEVANCY,
                    score=0.8,
                    passed=True,
                    threshold=0.7,
                    reason="Good relevancy"
                )
            ],
            overall_passed=True,
            executed_at=datetime.utcnow()
        )
        
        # Override dependencies
        app.dependency_overrides[get_eval_execution_service] = lambda: mock_eval_execution_service
        app.dependency_overrides[get_current_user] = lambda: "test-user"
        
        try:
            # Execute
            response = client.post(
                "/api/v0/evals/suites/sample-suite/evals/test1/execute?repo_name=test-repo"
            )
            
            # Assert
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "success"
            assert data["data"]["eval_name"] == "test1"
            assert data["data"]["overall_passed"] is True
        finally:
            # Cleanup
            app.dependency_overrides.clear()
    
    def test_get_execution_history_success(self, client, mock_eval_execution_service):
        """Test getting execution history"""
        # Setup
        mock_eval_execution_service.eval_service.list_executions.return_value = [
            EvalSuiteExecutionResult(
                suite_name="sample-suite",
                eval_results=[],
                total_evals=1,
                passed_evals=1,
                failed_evals=0,
                total_execution_time_ms=100,
                executed_at=datetime.utcnow()
            )
        ]
        
        # Override dependencies
        app.dependency_overrides[get_eval_execution_service] = lambda: mock_eval_execution_service
        app.dependency_overrides[get_current_user] = lambda: "test-user"
        
        try:
            # Execute
            response = client.get(
                "/api/v0/evals/suites/sample-suite/executions?repo_name=test-repo"
            )
            
            # Assert
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "success"
            assert len(data["data"]) == 1
        finally:
            # Cleanup
            app.dependency_overrides.clear()
    
    def test_get_latest_execution_success(self, client, mock_eval_execution_service):
        """Test getting latest execution"""
        # Setup
        mock_eval_execution_service.eval_service.get_latest_execution.return_value = EvalSuiteExecutionResult(
            suite_name="sample-suite",
            eval_results=[],
            total_evals=1,
            passed_evals=1,
            failed_evals=0,
            total_execution_time_ms=100,
            executed_at=datetime.utcnow()
        )
        
        # Override dependencies
        app.dependency_overrides[get_eval_execution_service] = lambda: mock_eval_execution_service
        app.dependency_overrides[get_current_user] = lambda: "test-user"
        
        try:
            # Execute
            response = client.get(
                "/api/v0/evals/suites/sample-suite/executions/latest?repo_name=test-repo"
            )
            
            # Assert
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "success"
            assert data["data"]["suite_name"] == "sample-suite"
        finally:
            # Cleanup
            app.dependency_overrides.clear()