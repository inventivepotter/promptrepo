"""
Unit tests for Test API endpoints.

Tests the test suite CRUD operations and execution endpoints.
"""
import pytest
from fastapi.testclient import TestClient
from unittest.mock import Mock, AsyncMock
from datetime import datetime

from main import app
from services.test.models import (
    TestSuiteData,
    TestSuiteDefinition,
    TestSuiteSummary,
    UnitTestDefinition,
    MetricConfig,
    MetricType,
    TestSuiteExecutionResult,
    UnitTestExecutionResult,
    MetricResult
)
from api.deps import get_test_service, get_test_execution_service, get_current_user


@pytest.fixture
def client():
    """Create test client"""
    return TestClient(app)


@pytest.fixture
def mock_test_service():
    """Create mock test service"""
    service = Mock()
    service.list_test_suites = AsyncMock()
    service.get_test_suite = AsyncMock()
    service.save_test_suite = AsyncMock()
    service.delete_test_suite = AsyncMock()
    service.list_executions = AsyncMock()
    service.get_latest_execution = AsyncMock()
    return service


@pytest.fixture
def mock_test_execution_service():
    """Create mock test execution service"""
    service = Mock()
    service.execute_test_suite = AsyncMock()
    service.execute_single_test = AsyncMock()
    service.test_service = Mock()
    service.test_service.list_executions = AsyncMock()
    service.test_service.get_latest_execution = AsyncMock()
    return service


@pytest.fixture
def sample_test_suite():
    """Create sample test suite"""
    return TestSuiteData(
        test_suite=TestSuiteDefinition(
            name="sample-suite",
            description="Sample test suite",
            tests=[
                UnitTestDefinition(
                    name="test1",
                    description="Test 1",
                    prompt_reference="file:///.promptrepo/prompts/test.yaml",
                    template_variables={"user_question": "What is AI?"},
                    metrics=[
                        MetricConfig(
                            type=MetricType.ANSWER_RELEVANCY,
                            threshold=0.7
                        )
                    ]
                )
            ],
            tags=["sample"],
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
    )


class TestSuitesAPI:
    """Test suite CRUD endpoint tests"""
    
    def test_list_test_suites_success(self, client, mock_test_service):
        """Test listing test suites successfully"""
        # Setup
        mock_test_service.list_test_suites.return_value = [
            TestSuiteSummary(
                name="suite1",
                description="Suite 1",
                test_count=2,
                tags=["tag1"],
                file_path=".promptrepo/tests/suite1/suite.yaml",
                last_execution=None,
                last_execution_passed=None
            )
        ]
        
        # Override dependencies
        app.dependency_overrides[get_test_service] = lambda: mock_test_service
        app.dependency_overrides[get_current_user] = lambda: "test-user"
        
        try:
            # Execute
            response = client.get(
                "/api/v0/tests/suites?repo_name=test-repo"
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
    
    def test_get_test_suite_success(self, client, mock_test_service, sample_test_suite):
        """Test getting specific test suite"""
        # Setup
        mock_test_service.get_test_suite.return_value = sample_test_suite
        
        # Override dependencies
        app.dependency_overrides[get_test_service] = lambda: mock_test_service
        app.dependency_overrides[get_current_user] = lambda: "test-user"
        
        try:
            # Execute
            response = client.get(
                "/api/v0/tests/suites/sample-suite?repo_name=test-repo"
            )
            
            # Assert
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "success"
            assert data["data"]["test_suite"]["name"] == "sample-suite"
        finally:
            # Cleanup
            app.dependency_overrides.clear()
    
    def test_save_test_suite_success(self, client, mock_test_service, sample_test_suite):
        """Test creating/updating test suite"""
        # Setup
        mock_test_service.save_test_suite.return_value = sample_test_suite
        
        # Override dependencies
        app.dependency_overrides[get_test_service] = lambda: mock_test_service
        app.dependency_overrides[get_current_user] = lambda: "test-user"
        
        try:
            # Execute
            response = client.post(
                "/api/v0/tests/suites?repo_name=test-repo",
                json=sample_test_suite.model_dump(mode='json')
            )
            
            # Assert
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "success"
            assert data["data"]["test_suite"]["name"] == "sample-suite"
        finally:
            # Cleanup
            app.dependency_overrides.clear()
    
    def test_delete_test_suite_success(self, client, mock_test_service):
        """Test deleting test suite"""
        # Setup
        mock_test_service.delete_test_suite.return_value = True
        
        # Override dependencies
        app.dependency_overrides[get_test_service] = lambda: mock_test_service
        app.dependency_overrides[get_current_user] = lambda: "test-user"
        
        try:
            # Execute
            response = client.delete(
                "/api/v0/tests/suites/sample-suite?repo_name=test-repo"
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
    """Test execution endpoint tests"""
    
    def test_execute_test_suite_success(self, client, mock_test_execution_service):
        """Test executing test suite"""
        # Setup
        mock_test_execution_service.execute_test_suite.return_value = TestSuiteExecutionResult(
            suite_name="sample-suite",
            test_results=[],
            total_tests=1,
            passed_tests=1,
            failed_tests=0,
            total_execution_time_ms=100,
            executed_at=datetime.utcnow()
        )
        
        # Override dependencies
        app.dependency_overrides[get_test_execution_service] = lambda: mock_test_execution_service
        app.dependency_overrides[get_current_user] = lambda: "test-user"
        
        try:
            # Execute
            response = client.post(
                "/api/v0/tests/suites/sample-suite/execute?repo_name=test-repo",
                json={}
            )
            
            # Assert
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "success"
            assert data["data"]["suite_name"] == "sample-suite"
            assert data["data"]["passed_tests"] == 1
        finally:
            # Cleanup
            app.dependency_overrides.clear()
    
    def test_execute_single_test_success(self, client, mock_test_execution_service):
        """Test executing single test"""
        # Setup
        mock_test_execution_service.execute_single_test.return_value = UnitTestExecutionResult(
            test_name="test1",
            prompt_reference="file:///.promptrepo/prompts/test.yaml",
            template_variables={"user_question": "What is AI?"},
            actual_output="Test output",
            expected_output=None,
            retrieval_context=None,
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
            execution_time_ms=50,
            executed_at=datetime.utcnow()
        )
        
        # Override dependencies
        app.dependency_overrides[get_test_execution_service] = lambda: mock_test_execution_service
        app.dependency_overrides[get_current_user] = lambda: "test-user"
        
        try:
            # Execute
            response = client.post(
                "/api/v0/tests/suites/sample-suite/tests/test1/execute?repo_name=test-repo"
            )
            
            # Assert
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "success"
            assert data["data"]["test_name"] == "test1"
            assert data["data"]["overall_passed"] is True
        finally:
            # Cleanup
            app.dependency_overrides.clear()
    
    def test_get_execution_history_success(self, client, mock_test_execution_service):
        """Test getting execution history"""
        # Setup
        mock_test_execution_service.test_service.list_executions.return_value = [
            TestSuiteExecutionResult(
                suite_name="sample-suite",
                test_results=[],
                total_tests=1,
                passed_tests=1,
                failed_tests=0,
                total_execution_time_ms=100,
                executed_at=datetime.utcnow()
            )
        ]
        
        # Override dependencies
        app.dependency_overrides[get_test_execution_service] = lambda: mock_test_execution_service
        app.dependency_overrides[get_current_user] = lambda: "test-user"
        
        try:
            # Execute
            response = client.get(
                "/api/v0/tests/suites/sample-suite/executions?repo_name=test-repo"
            )
            
            # Assert
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "success"
            assert len(data["data"]) == 1
        finally:
            # Cleanup
            app.dependency_overrides.clear()
    
    def test_get_latest_execution_success(self, client, mock_test_execution_service):
        """Test getting latest execution"""
        # Setup
        mock_test_execution_service.test_service.get_latest_execution.return_value = TestSuiteExecutionResult(
            suite_name="sample-suite",
            test_results=[],
            total_tests=1,
            passed_tests=1,
            failed_tests=0,
            total_execution_time_ms=100,
            executed_at=datetime.utcnow()
        )
        
        # Override dependencies
        app.dependency_overrides[get_test_execution_service] = lambda: mock_test_execution_service
        app.dependency_overrides[get_current_user] = lambda: "test-user"
        
        try:
            # Execute
            response = client.get(
                "/api/v0/tests/suites/sample-suite/executions/latest?repo_name=test-repo"
            )
            
            # Assert
            assert response.status_code == 200
            data = response.json()
            assert data["status"] == "success"
            assert data["data"]["suite_name"] == "sample-suite"
        finally:
            # Cleanup
            app.dependency_overrides.clear()