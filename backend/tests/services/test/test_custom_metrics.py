"""
Unit tests for custom DeepEval metrics.

Tests the ProfessionalismMetric and ConcisenessMetric implementations
to ensure they work correctly with DeepEval's evaluation framework.
"""

import pytest
from unittest.mock import Mock, patch
from deepeval.test_case import LLMTestCase

from services.evals.models import MetricType, MetricConfig
from lib.deepeval.custom_metrics import (
    ProfessionalismMetric,
    ConcisenessMetric,
    FuzzyMatchMetric,
    SemanticSimilarityMetric
)


class TestProfessionalismMetric:
    """Test cases for ProfessionalismMetric."""
    
    def test_professionalism_metric_initialization(self):
        """Test that ProfessionalismMetric initializes correctly."""
        metric = ProfessionalismMetric(threshold=0.8, model="gpt-4o", strict_mode=True)
        
        assert metric.threshold == 0.8
        assert metric.__class__.__name__ == "ProfessionalismMetric"
    
    def test_professionalism_metric_default_values(self):
        """Test ProfessionalismMetric with default values."""
        metric = ProfessionalismMetric()
        
        assert metric.threshold == 0.7
        assert metric.strict_mode is False
    
    @patch('lib.deepeval.custom_metrics.professionalism_metric.GEval.measure')
    def test_professionalism_metric_measure(self, mock_measure):
        """Test that ProfessionalismMetric can measure a test case."""
        # Setup
        metric = ProfessionalismMetric()
        test_case = LLMTestCase(
            input="What is my account balance?",
            actual_output="Your current account balance is $5,432.10 as of today.",
            expected_output="Your account balance is $5,432.10"
        )
        
        # Mock the parent measure method
        mock_measure.return_value = None
        mock_measure.side_effect = lambda tc: setattr(metric, 'score', 0.9)
        
        # Execute
        metric.measure(test_case)
        
        # Verify
        mock_measure.assert_called_once_with(test_case)
        assert hasattr(metric, 'score')
    
    def test_professionalism_metric_evaluation_steps(self):
        """Test that professionalism metric has correct evaluation steps."""
        metric = ProfessionalismMetric()
        
        # Check that evaluation steps are properly set
        assert hasattr(metric, 'evaluation_steps')
        assert len(metric.evaluation_steps) == 4
        assert "professional tone" in metric.evaluation_steps[0].lower()
        assert "domain-appropriate formality" in metric.evaluation_steps[1].lower()
        assert "casual or ambiguous" in metric.evaluation_steps[2].lower()
        assert "slang" in metric.evaluation_steps[3].lower()


class TestConcisenessMetric:
    """Test cases for ConcisenessMetric."""
    
    def test_conciseness_metric_initialization(self):
        """Test that ConcisenessMetric initializes correctly."""
        metric = ConcisenessMetric(threshold=0.6, model="gpt-3.5-turbo", strict_mode=True)
        
        assert metric.threshold == 0.6
        assert metric.__class__.__name__ == "ConcisenessMetric"
    
    def test_conciseness_metric_default_values(self):
        """Test ConcisenessMetric with default values."""
        metric = ConcisenessMetric()
        
        assert metric.threshold == 0.7
        assert metric.strict_mode is False
    
    @patch('lib.deepeval.custom_metrics.conciseness_metric.GEval.measure')
    def test_conciseness_metric_measure(self, mock_measure):
        """Test that ConcisenessMetric can measure a test case."""
        # Setup
        metric = ConcisenessMetric()
        test_case = LLMTestCase(
            input="What time is it?",
            actual_output="3:45 PM",
            expected_output="3:45 PM"
        )
        
        # Mock the parent measure method
        mock_measure.return_value = None
        mock_measure.side_effect = lambda tc: setattr(metric, 'score', 0.95)
        
        # Execute
        metric.measure(test_case)
        
        # Verify
        mock_measure.assert_called_once_with(test_case)
        assert hasattr(metric, 'score')
    
    def test_conciseness_metric_criteria(self):
        """Test that conciseness metric has correct criteria."""
        metric = ConcisenessMetric()
        
        # Check that criteria is properly set
        assert hasattr(metric, 'criteria')
        assert metric.criteria is not None
        assert "concise" in metric.criteria.lower()
        assert "essential points" in metric.criteria.lower()
        assert "avoid repetition" in metric.criteria.lower()


class TestCustomMetricsIntegration:
    """Integration tests for custom metrics with the test framework."""
    
    def test_metric_type_descriptions(self):
        """Test that new metric types have proper descriptions."""
        assert MetricType.SUMMARIZATION.description is not None
        assert "summarizes" in MetricType.SUMMARIZATION.description.lower()
        
        assert MetricType.PROFESSIONALISM.description is not None
        assert "professional" in MetricType.PROFESSIONALISM.description.lower()
        
        assert MetricType.CONCISENESS.description is not None
        assert "brief" in MetricType.CONCISENESS.description.lower()
    
    def test_metric_config_compatibility(self):
        """Test that custom metrics work with MetricConfig."""
        # Test ProfessionalismMetric
        prof_config = MetricConfig(
            type=MetricType.PROFESSIONALISM,
            threshold=0.8,
            model="gpt-4o",
            include_reason=True,
            strict_mode=False
        )
        
        prof_metric = ProfessionalismMetric(
            threshold=prof_config.threshold,
            model=prof_config.model,
            strict_mode=prof_config.strict_mode
        )
        
        assert prof_metric.threshold == prof_config.threshold
        assert prof_metric.strict_mode == prof_config.strict_mode
        
        # Test ConcisenessMetric
        conc_config = MetricConfig(
            type=MetricType.CONCISENESS,
            threshold=0.9,
            model="gpt-3.5-turbo",
            include_reason=False,
            strict_mode=True
        )
        
        conc_metric = ConcisenessMetric(
            threshold=conc_config.threshold,
            model=conc_config.model,
            strict_mode=conc_config.strict_mode
        )
        
        assert conc_metric.threshold == conc_config.threshold
        assert conc_metric.model == conc_config.model
        assert conc_metric.strict_mode == conc_config.strict_mode


class TestFuzzyMatchMetric:
    """Test cases for FuzzyMatchMetric."""
    
    def test_fuzzy_match_metric_initialization(self):
        """Test that FuzzyMatchMetric initializes correctly."""
        metric = FuzzyMatchMetric(threshold=0.8)
        
        assert metric.threshold == 0.8
        assert metric.__class__.__name__ == "FuzzyMatchMetric"
    
    def test_fuzzy_match_metric_default_values(self):
        """Test FuzzyMatchMetric with default values."""
        metric = FuzzyMatchMetric()
        
        assert metric.threshold == 0.8  # Default is 0.8 based on implementation
    
    def test_fuzzy_match_perfect_match(self):
        """Test fuzzy match with identical strings."""
        metric = FuzzyMatchMetric()
        test_case = LLMTestCase(
            input="Test input",
            actual_output="Hello world",
            expected_output="Hello world"
        )
        
        metric.measure(test_case)
        
        assert metric.score == 1.0
        assert metric.reason is not None
        assert "essentially identical" in metric.reason.lower()
    
    def test_fuzzy_match_no_match(self):
        """Test fuzzy match with completely different strings."""
        metric = FuzzyMatchMetric()
        test_case = LLMTestCase(
            input="Test input",
            actual_output="Hello world",
            expected_output="Goodbye moon"
        )
        
        metric.measure(test_case)
        
        assert metric.score is not None
        assert metric.score < 0.5  # Should be low similarity
        assert metric.reason is not None
    
    def test_fuzzy_match_partial_match(self):
        """Test fuzzy match with partially similar strings."""
        metric = FuzzyMatchMetric()
        test_case = LLMTestCase(
            input="Test input",
            actual_output="Hello world",
            expected_output="Hello there world"
        )
        
        metric.measure(test_case)
        
        assert metric.score is not None
        assert 0.5 < metric.score < 1.0  # Should be partial similarity
        assert metric.reason is not None


class TestSemanticSimilarityMetric:
    """Test cases for SemanticSimilarityMetric."""
    
    def test_semantic_similarity_metric_initialization(self):
        """Test that SemanticSimilarityMetric initializes correctly."""
        metric = SemanticSimilarityMetric(threshold=0.8)
        
        assert metric.threshold == 0.8
        assert metric.__class__.__name__ == "SemanticSimilarityMetric"
    
    def test_semantic_similarity_metric_default_values(self):
        """Test SemanticSimilarityMetric with default values."""
        metric = SemanticSimilarityMetric()
        
        assert metric.threshold == 0.7
        # SemanticSimilarityMetric doesn't have a model attribute in the same way
        # It uses the default DeepEval model system
        assert metric.threshold == 0.7
    
    @patch('deepeval.metrics.utils.initialize_model')
    def test_semantic_similarity_measure(self, mock_initialize_model):
        """Test that SemanticSimilarityMetric can measure a test case."""
        # Setup mock model
        mock_model = Mock()
        mock_initialize_model.return_value = (mock_model, True)
        
        metric = SemanticSimilarityMetric()
        test_case = LLMTestCase(
            input="Test input",
            actual_output="The cat is sleeping",
            expected_output="A feline is resting"
        )
        
        # Execute
        metric.measure(test_case)
        
        # Verify
        assert mock_initialize_model.call_count == 1  # Called once during initialization
        assert hasattr(metric, 'score')
        assert metric.score is not None
        assert 0.0 <= metric.score <= 1.0
        assert metric.reason is not None
    
    def test_semantic_similarity_identical_meaning(self):
        """Test semantic similarity with identical meaning."""
        metric = SemanticSimilarityMetric()
        test_case = LLMTestCase(
            input="Test input",
            actual_output="The weather is sunny today",
            expected_output="It's a bright sunny day"
        )
        
        # Mock the embedding calculation by patching the measure method directly
        with patch.object(metric, 'measure') as mock_measure:
            mock_measure.return_value = 1.0
            metric.measure(test_case)
            
            assert metric.score == 1.0
            assert metric.reason is not None
            assert "identical" in metric.reason.lower()
    
    def test_semantic_similarity_different_meaning(self):
        """Test semantic similarity with different meaning."""
        metric = SemanticSimilarityMetric()
        test_case = LLMTestCase(
            input="Test input",
            actual_output="The weather is sunny today",
            expected_output="I like to eat pizza"
        )
        
        # Mock the embedding calculation to return orthogonal vectors
        with patch.object(metric, 'measure') as mock_measure:
            mock_measure.return_value = 0.0
            metric.measure(test_case)
            
            assert metric.score == 0.0
            assert metric.reason is not None
            assert "different" in metric.reason.lower()


class TestNewMetricsIntegration:
    """Integration tests for new metrics with the test framework."""
    
    def test_new_metric_type_descriptions(self):
        """Test that new metric types have proper descriptions."""
        assert MetricType.FUZZY_MATCH.description is not None
        assert "fuzzy" in MetricType.FUZZY_MATCH.description.lower()
        assert "similarity" in MetricType.FUZZY_MATCH.description.lower()
        
        assert MetricType.SEMANTIC_SIMILARITY.description is not None
        assert "semantic" in MetricType.SEMANTIC_SIMILARITY.description.lower()
        assert "similarity" in MetricType.SEMANTIC_SIMILARITY.description.lower()
    
    def test_new_metric_config_compatibility(self):
        """Test that new metrics work with MetricConfig."""
        # Test FuzzyMatchMetric
        fuzzy_config = MetricConfig(
            type=MetricType.FUZZY_MATCH,
            threshold=0.8,
            include_reason=True
        )
        
        fuzzy_metric = FuzzyMatchMetric(threshold=fuzzy_config.threshold)
        assert fuzzy_metric.threshold == fuzzy_config.threshold
        
        # Test SemanticSimilarityMetric
        semantic_config = MetricConfig(
            type=MetricType.SEMANTIC_SIMILARITY,
            threshold=0.9,
            model="text-embedding-ada-002",
            include_reason=False
        )
        
        semantic_metric = SemanticSimilarityMetric(
            threshold=semantic_config.threshold
        )
        assert semantic_metric.threshold == semantic_config.threshold
    
    def test_deterministic_metric_classification(self):
        """Test that new metrics are correctly classified as deterministic."""
        assert MetricType.is_deterministic(MetricType.FUZZY_MATCH) is True
        assert MetricType.is_deterministic(MetricType.SEMANTIC_SIMILARITY) is True
        assert MetricType.is_non_deterministic(MetricType.FUZZY_MATCH) is False
        assert MetricType.is_non_deterministic(MetricType.SEMANTIC_SIMILARITY) is False
    
    def test_required_fields_for_new_metrics(self):
        """Test that new metrics have correct required fields."""
        
        # Test FUZZY_MATCH
        fuzzy_fields = MetricType.get_required_expected_fields(MetricType.FUZZY_MATCH)
        assert "expected_output" in fuzzy_fields
        
        # Test SEMANTIC_SIMILARITY
        semantic_fields = MetricType.get_required_expected_fields(MetricType.SEMANTIC_SIMILARITY)
        assert "expected_output" in semantic_fields