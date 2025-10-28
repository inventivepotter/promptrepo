"""
Unit tests for test service models.
"""

import pytest
from datetime import datetime
from typing import Dict, Any, List

from services.test.models import (
    MetricType,
    ExpectedEvaluationFieldsModel,
    ActualEvaluationFieldsModel,
    MetricConfig,
    UnitTestDefinition,
    TestSuiteDefinition,
    MetricResult,
    UnitTestExecutionResult,
    TestSuiteExecutionResult,
    TestSuiteSummary
)


class TestMetricType:
    """Test MetricType enum"""
    
    def test_metric_type_values(self):
        """Test that all expected metric types are defined"""
        expected_metrics = {
            "exact_match",
            "tools_called",
            "json_schema_verification",
            "keyword_pattern_presence",
            "output_length",
            "answer_relevancy",
            "faithfulness",
            "contextual_relevancy",
            "contextual_precision",
            "contextual_recall",
            "hallucination",
            "bias",
            "toxicity"
        }
        
        actual_metrics = {metric.value for metric in MetricType}
        assert actual_metrics == expected_metrics
    
    def test_deterministic_classification(self):
        """Test deterministic vs non-deterministic classification"""
        # Test deterministic metrics
        assert MetricType.is_deterministic(MetricType.EXACT_MATCH) is True
        assert MetricType.is_deterministic(MetricType.TOOLS_CALLED) is True
        assert MetricType.is_deterministic(MetricType.JSON_SCHEMA_VERIFICATION) is True
        assert MetricType.is_deterministic(MetricType.KEYWORD_PATTERN_PRESENCE) is True
        assert MetricType.is_deterministic(MetricType.OUTPUT_LENGTH) is True
        
        # Test non-deterministic metrics
        assert MetricType.is_deterministic(MetricType.ANSWER_RELEVANCY) is False
        assert MetricType.is_deterministic(MetricType.FAITHFULNESS) is False
        assert MetricType.is_deterministic(MetricType.BIAS) is False
        
        # Test convenience method
        assert MetricType.is_non_deterministic(MetricType.EXACT_MATCH) is False
        assert MetricType.is_non_deterministic(MetricType.ANSWER_RELEVANCY) is True


class TestExpectedEvaluationFieldsModel:
    """Test ExpectedEvaluationFieldsModel"""
    
    def test_default_values(self):
        """Test that default values are set correctly"""
        fields = ExpectedEvaluationFieldsModel()
        
        assert fields.expected_output is None
        assert fields.retrieval_context is None
        assert fields.evaluation_steps is None
        assert fields.criteria is None
        assert fields.expected_tools is None
        assert fields.expected_schema is None
        assert fields.expected_keywords is None
        assert fields.expected_patterns is None
        assert fields.forbidden_keywords is None
        assert fields.min_length is None
        assert fields.max_length is None
        assert fields.length_unit == "characters"
        assert fields.domain is None
        assert fields.chatbot_role is None
        assert fields.assessment_questions is None
    
    def test_with_values(self):
        """Test model with values"""
        expected_output = "Expected response"
        retrieval_context = ["Context 1", "Context 2"]
        evaluation_steps = ["Step 1", "Step 2"]
        
        fields = ExpectedEvaluationFieldsModel(
            expected_output=expected_output,
            retrieval_context=retrieval_context,
            evaluation_steps=evaluation_steps
        )
        
        assert fields.expected_output == expected_output
        assert fields.retrieval_context == retrieval_context
        assert fields.evaluation_steps == evaluation_steps
    
    def test_get_context_for_metric(self):
        """Test get_context_for_metric method"""
        fields = ExpectedEvaluationFieldsModel(
            retrieval_context=["test context"]
        )
        
        # Test RAG metrics
        assert fields.get_context_for_metric(MetricType.FAITHFULNESS) == ["test context"]
        assert fields.get_context_for_metric(MetricType.CONTEXTUAL_RELEVANCY) == ["test context"]
        assert fields.get_context_for_metric(MetricType.CONTEXTUAL_PRECISION) == ["test context"]
        assert fields.get_context_for_metric(MetricType.CONTEXTUAL_RECALL) == ["test context"]
        
        # Test hallucination metric (should use retrieval_context since context field was removed)
        assert fields.get_context_for_metric(MetricType.HALLUCINATION) == ["test context"]
        
        # Test metrics that don't need context
        assert fields.get_context_for_metric(MetricType.ANSWER_RELEVANCY) is None
        assert fields.get_context_for_metric(MetricType.BIAS) is None
        assert fields.get_context_for_metric(MetricType.TOXICITY) is None
        
        # Test deterministic metrics
        assert fields.get_context_for_metric(MetricType.EXACT_MATCH) is None
        assert fields.get_context_for_metric(MetricType.TOOLS_CALLED) is None
    
    def test_get_required_fields_for_metric(self):
        """Test get_required_fields_for_metric method"""
        fields = ExpectedEvaluationFieldsModel()
        
        # Test deterministic metrics
        assert fields.get_required_fields_for_metric(MetricType.EXACT_MATCH) == ["expected_output"]
        assert fields.get_required_fields_for_metric(MetricType.TOOLS_CALLED) == ["expected_tools"]
        assert fields.get_required_fields_for_metric(MetricType.JSON_SCHEMA_VERIFICATION) == ["expected_schema"]
        assert fields.get_required_fields_for_metric(MetricType.KEYWORD_PATTERN_PRESENCE) == ["expected_keywords", "expected_patterns"]
        assert fields.get_required_fields_for_metric(MetricType.OUTPUT_LENGTH) == ["min_length", "max_length"]
        
        # Test non-deterministic metrics
        assert fields.get_required_fields_for_metric(MetricType.ANSWER_RELEVANCY) == []
        assert fields.get_required_fields_for_metric(MetricType.FAITHFULNESS) == ["retrieval_context"]
        assert fields.get_required_fields_for_metric(MetricType.CONTEXTUAL_RELEVANCY) == ["retrieval_context"]
        assert fields.get_required_fields_for_metric(MetricType.CONTEXTUAL_PRECISION) == ["retrieval_context"]
        assert fields.get_required_fields_for_metric(MetricType.CONTEXTUAL_RECALL) == ["retrieval_context"]
        assert fields.get_required_fields_for_metric(MetricType.HALLUCINATION) == ["context"]
        assert fields.get_required_fields_for_metric(MetricType.BIAS) == []
        assert fields.get_required_fields_for_metric(MetricType.TOXICITY) == []


class TestActualEvaluationFieldsModel:
    """Test ActualEvaluationFieldsModel"""
    
    def test_default_values(self):
        """Test that default values are set correctly"""
        fields = ActualEvaluationFieldsModel(actual_output="test output")
        
        assert fields.actual_output == "test output"
        assert fields.tools_called is None
        assert fields.execution_time_ms is None
        assert fields.error is None
    
    def test_with_values(self):
        """Test model with values"""
        actual_output = "Actual response"
        tools_called = [{"tool": "search", "params": {}}]
        execution_time_ms = 1500
        
        fields = ActualEvaluationFieldsModel(
            actual_output=actual_output,
            tools_called=tools_called,
            execution_time_ms=execution_time_ms
        )
        
        assert fields.actual_output == actual_output
        assert fields.tools_called == tools_called
        assert fields.execution_time_ms == execution_time_ms


class TestMetricConfig:
    """Test MetricConfig model"""
    
    def test_default_values(self):
        """Test default values"""
        config = MetricConfig(type=MetricType.ANSWER_RELEVANCY)
        
        assert config.type == MetricType.ANSWER_RELEVANCY
        assert config.threshold == 0.7
        assert config.model == ""
        assert config.include_reason is True
        assert config.strict_mode is False
    
    def test_with_values(self):
        """Test config with custom values"""
        config = MetricConfig(
            type=MetricType.FAITHFULNESS,
            threshold=0.8,
            model="gpt-4",
            include_reason=False,
            strict_mode=True
        )
        
        assert config.type == MetricType.FAITHFULNESS
        assert config.threshold == 0.8
        assert config.model == "gpt-4"
        assert config.include_reason is False
        assert config.strict_mode is True
    
    def test_threshold_validation(self):
        """Test threshold validation"""
        # Valid thresholds
        config = MetricConfig(type=MetricType.ANSWER_RELEVANCY, threshold=0.5)
        assert config.threshold == 0.5
        
        config = MetricConfig(type=MetricType.ANSWER_RELEVANCY, threshold=1.0)
        assert config.threshold == 1.0
        
        # Invalid thresholds should raise validation error
        with pytest.raises(ValueError):
            MetricConfig(type=MetricType.ANSWER_RELEVANCY, threshold=-0.1)
        
        with pytest.raises(ValueError):
            MetricConfig(type=MetricType.ANSWER_RELEVANCY, threshold=1.1)


class TestUnitTestDefinition:
    """Test UnitTestDefinition model"""
    
    def test_default_values(self):
        """Test default values"""
        test_def = UnitTestDefinition(
            name="test",
            prompt_reference="test_prompt.txt"
        )
        
        assert test_def.name == "test"
        assert test_def.prompt_reference == "test_prompt.txt"
        assert test_def.description == ""
        assert test_def.template_variables == {}
        assert isinstance(test_def.evaluation_fields, ExpectedEvaluationFieldsModel)
        assert test_def.enabled is True
    
    def test_with_values(self):
        """Test test definition with values"""
        evaluation_fields = ExpectedEvaluationFieldsModel(
            expected_output="Expected result",
            retrieval_context=["Context"]
        )
        
        test_def = UnitTestDefinition(
            name="test_with_values",
            description="Test description",
            prompt_reference="test_prompt.txt",
            template_variables={"var1": "value1"},
            evaluation_fields=evaluation_fields,
            enabled=False
        )
        
        assert test_def.name == "test_with_values"
        assert test_def.description == "Test description"
        assert test_def.prompt_reference == "test_prompt.txt"
        assert test_def.template_variables == {"var1": "value1"}
        assert test_def.evaluation_fields == evaluation_fields
        assert test_def.enabled is False


class TestTestSuiteDefinition:
    """Test TestSuiteDefinition model"""
    
    def test_default_values(self):
        """Test default values"""
        suite = TestSuiteDefinition(name="test_suite")
        
        assert suite.name == "test_suite"
        assert suite.description == ""
        assert suite.tests == []
        assert suite.tags == []
        assert suite.metrics == []
        assert isinstance(suite.created_at, datetime)
        assert isinstance(suite.updated_at, datetime)
    
    def test_with_values(self):
        """Test suite with values"""
        test_def = UnitTestDefinition(
            name="test1",
            prompt_reference="prompt1.txt"
        )
        metric_config = MetricConfig(type=MetricType.ANSWER_RELEVANCY)
        
        suite = TestSuiteDefinition(
            name="suite_with_values",
            description="Suite description",
            tests=[test_def],
            tags=["test", "example"],
            metrics=[metric_config]
        )
        
        assert suite.name == "suite_with_values"
        assert suite.description == "Suite description"
        assert suite.tests == [test_def]
        assert suite.tags == ["test", "example"]
        assert suite.metrics == [metric_config]


class TestMetricResult:
    """Test MetricResult model"""
    
    def test_with_values(self):
        """Test metric result with values"""
        result = MetricResult(
            type=MetricType.ANSWER_RELEVANCY,
            score=0.8,
            passed=True,
            threshold=0.7,
            reason="Good answer"
        )
        
        assert result.type == MetricType.ANSWER_RELEVANCY
        assert result.score == 0.8
        assert result.passed is True
        assert result.threshold == 0.7
        assert result.reason == "Good answer"
        assert result.error is None


class TestUnitTestExecutionResult:
    """Test UnitTestExecutionResult model"""
    
    def test_with_values(self):
        """Test execution result with values"""
        actual_fields = ActualEvaluationFieldsModel(
            actual_output="Test output",
            execution_time_ms=1000
        )
        expected_fields = ExpectedEvaluationFieldsModel(
            expected_output="Expected output"
        )
        metric_result = MetricResult(
            type=MetricType.ANSWER_RELEVANCY,
            score=0.9,
            passed=True,
            threshold=0.7
        )
        
        execution_result = UnitTestExecutionResult(
            test_name="test_execution",
            prompt_reference="test_prompt.txt",
            template_variables={"var": "value"},
            actual_evaluation_fields=actual_fields,
            expected_evaluation_fields=expected_fields,
            metric_results=[metric_result],
            overall_passed=True
        )
        
        assert execution_result.test_name == "test_execution"
        assert execution_result.prompt_reference == "test_prompt.txt"
        assert execution_result.template_variables == {"var": "value"}
        assert execution_result.actual_evaluation_fields == actual_fields
        assert execution_result.expected_evaluation_fields == expected_fields
        assert execution_result.metric_results == [metric_result]
        assert execution_result.overall_passed is True
        assert isinstance(execution_result.executed_at, datetime)


class TestTestSuiteExecutionResult:
    """Test TestSuiteExecutionResult model"""
    
    def test_with_values(self):
        """Test suite execution result with values"""
        execution_result = UnitTestExecutionResult(
            test_name="test",
            prompt_reference="prompt.txt",
            template_variables={},
            actual_evaluation_fields=ActualEvaluationFieldsModel(actual_output="output"),
            expected_evaluation_fields=ExpectedEvaluationFieldsModel(),
            metric_results=[],
            overall_passed=True
        )
        
        suite_result = TestSuiteExecutionResult(
            suite_name="test_suite",
            test_results=[execution_result],
            total_tests=1,
            passed_tests=1,
            failed_tests=0,
            total_execution_time_ms=1500
        )
        
        assert suite_result.suite_name == "test_suite"
        assert suite_result.test_results == [execution_result]
        assert suite_result.total_tests == 1
        assert suite_result.passed_tests == 1
        assert suite_result.failed_tests == 0
        assert suite_result.total_execution_time_ms == 1500
        assert isinstance(suite_result.executed_at, datetime)


class TestTestSuiteSummary:
    """Test TestSuiteSummary model"""
    
    def test_with_values(self):
        """Test suite summary with values"""
        now = datetime.now()
        
        summary = TestSuiteSummary(
            name="test_suite",
            description="Test suite description",
            test_count=5,
            tags=["test", "example"],
            file_path="/path/to/suite.yaml",
            last_execution=now,
            last_execution_passed=True
        )
        
        assert summary.name == "test_suite"
        assert summary.description == "Test suite description"
        assert summary.test_count == 5
        assert summary.tags == ["test", "example"]
        assert summary.file_path == "/path/to/suite.yaml"
        assert summary.last_execution == now
        assert summary.last_execution_passed is True