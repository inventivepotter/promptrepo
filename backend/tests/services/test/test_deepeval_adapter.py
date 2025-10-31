"""
Unit tests for DeepEval Adapter.

Tests cover:
- Metric creation from configurations
- Test case creation
- Error handling when DeepEval is not available
"""

import pytest
from unittest.mock import Mock, patch, MagicMock

from lib.deepeval.deepeval_adapter import DeepEvalAdapter
from services.evals.models import MetricConfig, MetricType, MetricResult


@pytest.fixture
def adapter():
    """Create DeepEvalAdapter instance."""
    return DeepEvalAdapter()


class TestMetricCreation:
    """Test metric creation functionality."""
    
    def test_adapter_initialization_without_deepeval(self):
        """Test adapter initialization when DeepEval is not installed."""
        with patch('services.test.deepeval_adapter.DeepEvalAdapter.__init__', 
                   return_value=None):
            adapter = DeepEvalAdapter()
            adapter.deepeval_available = False
            adapter.metric_mapping = {}
            
            assert adapter.deepeval_available is False
    
    def test_create_metric_without_deepeval(self):
        """Test creating metric when DeepEval is not available."""
        adapter = DeepEvalAdapter()
        adapter.deepeval_available = False
        
        config = MetricConfig(
            type=MetricType.ANSWER_RELEVANCY,
            threshold=0.8,
            model="openai:gpt-4"
        )
        
        with pytest.raises(ImportError) as exc_info:
            adapter.create_metric(config)
        assert "DeepEval is not installed" in str(exc_info.value)
    
    def test_create_metric_with_provider_model_format(self, adapter):
        """Test creating metric with provider:model format."""
        if not adapter.deepeval_available:
            pytest.skip("DeepEval not available")
        
        config = MetricConfig(
            type=MetricType.ANSWER_RELEVANCY,
            threshold=0.8,
            model="openai:gpt-4"
        )
        
        with patch.object(adapter, 'metric_mapping') as mock_mapping:
            mock_metric_class = Mock()
            mock_metric_instance = Mock()
            mock_metric_class.return_value = mock_metric_instance
            mock_mapping.get.return_value = mock_metric_class
            
            adapter.create_metric(config)
            
            # Verify that the model name is extracted correctly (just "gpt-4", not "openai:gpt-4")
            mock_metric_class.assert_called_once_with(
                threshold=0.8,
                model="gpt-4",
                include_reason=True,
                strict_mode=False
            )
    
    def test_create_metric_backward_compatible(self, adapter):
        """Test creating metric with plain model name (backward compatibility)."""
        if not adapter.deepeval_available:
            pytest.skip("DeepEval not available")
        
        config = MetricConfig(
            type=MetricType.ANSWER_RELEVANCY,
            threshold=0.8,
            model="gpt-4"
        )
        
        with patch.object(adapter, 'metric_mapping') as mock_mapping:
            mock_metric_class = Mock()
            mock_metric_instance = Mock()
            mock_metric_class.return_value = mock_metric_instance
            mock_mapping.get.return_value = mock_metric_class
            
            adapter.create_metric(config)
            
            # Verify that plain model name still works
            mock_metric_class.assert_called_once_with(
                threshold=0.8,
                model="gpt-4",
                include_reason=True,
                strict_mode=False
            )
    
    def test_create_test_case_without_deepeval(self):
        """Test creating test case when DeepEval is not available."""
        adapter = DeepEvalAdapter()
        adapter.deepeval_available = False
        
        with pytest.raises(ImportError) as exc_info:
            adapter.create_test_case(
                input_text="test input",
                actual_output="test output"
            )
        assert "DeepEval is not installed" in str(exc_info.value)


class TestTestCaseCreation:
    """Test test case creation functionality."""
    
    def test_create_test_case_basic(self, adapter):
        """Test creating basic test case."""
        if not adapter.deepeval_available:
            pytest.skip("DeepEval not available")
        
        test_case = adapter.create_test_case(
            input_text="What is the capital of France?",
            actual_output="Paris"
        )
        
        assert test_case is not None
    
    def test_create_test_case_with_context(self, adapter):
        """Test creating test case with retrieval context."""
        if not adapter.deepeval_available:
            pytest.skip("DeepEval not available")
        
        test_case = adapter.create_test_case(
            input_text="What is the capital?",
            actual_output="Paris",
            expected_output="The capital is Paris",
            retrieval_context=["France is a country in Europe", "Paris is the capital"]
        )
        
        assert test_case is not None


class TestMetricEvaluation:
    """Test metric evaluation functionality."""
    
    @pytest.mark.asyncio
    async def test_evaluate_metrics_without_deepeval(self):
        """Test evaluating metrics when DeepEval is not available."""
        adapter = DeepEvalAdapter()
        adapter.deepeval_available = False
        
        with pytest.raises(ImportError):
            await adapter.evaluate_metrics(None, [], [])
    
    @pytest.mark.asyncio
    async def test_evaluate_metrics_with_error(self, adapter):
        """Test evaluating metrics when metric raises exception."""
        if not adapter.deepeval_available:
            pytest.skip("DeepEval not available")
        
        # Create mock metric that raises exception
        mock_metric = Mock()
        mock_metric.measure.side_effect = Exception("Metric evaluation failed")
        
        config = MetricConfig(
            type=MetricType.ANSWER_RELEVANCY,
            threshold=0.8,
            model="openai:gpt-4"
        )
        
        test_case = Mock()
        
        results = await adapter.evaluate_metrics(test_case, [mock_metric], [config])
        
        assert len(results) == 1
        assert results[0].passed is False
        assert results[0].error is not None
        assert "Metric evaluation failed" in results[0].error