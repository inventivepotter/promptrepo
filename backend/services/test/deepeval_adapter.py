"""
DeepEval Adapter

Wraps DeepEval library interactions to provide a clean interface for:
- Converting metric configs to DeepEval metric instances
- Creating DeepEval test cases
- Evaluating metrics and handling errors
"""

import logging
from typing import List, Optional, Any, Type, Dict

from .models import MetricConfig, MetricResult, MetricType

logger = logging.getLogger(__name__)


class DeepEvalAdapter:
    """
    Adapter for DeepEval library integration.
    
    This adapter wraps DeepEval functionality to:
    - Create metric instances from configurations
    - Create test cases from our data models
    - Evaluate metrics and convert results
    - Handle DeepEval exceptions gracefully
    """
    
    def __init__(self):
        """Initialize DeepEval adapter."""
        # Import DeepEval modules here to avoid import errors if not installed
        try:
            from deepeval.metrics import (
                AnswerRelevancyMetric,
                FaithfulnessMetric,
                ContextualRelevancyMetric,
                ContextualPrecisionMetric,
                ContextualRecallMetric,
                HallucinationMetric,
                BiasMetric,
                ToxicityMetric
            )
            from deepeval.test_case import LLMTestCase
            
            self.metric_mapping: Dict[MetricType, Type[Any]] = {
                MetricType.ANSWER_RELEVANCY: AnswerRelevancyMetric,
                MetricType.FAITHFULNESS: FaithfulnessMetric,
                MetricType.CONTEXTUAL_RELEVANCY: ContextualRelevancyMetric,
                MetricType.CONTEXTUAL_PRECISION: ContextualPrecisionMetric,
                MetricType.CONTEXTUAL_RECALL: ContextualRecallMetric,
                MetricType.HALLUCINATION: HallucinationMetric,
                MetricType.BIAS: BiasMetric,
                MetricType.TOXICITY: ToxicityMetric,
            }
            
            self.LLMTestCase: Optional[Type[Any]] = LLMTestCase
            self.deepeval_available = True
            
        except ImportError as e:
            logger.warning(f"DeepEval not available: {e}")
            self.deepeval_available = False
            self.metric_mapping: Dict[MetricType, Type[Any]] = {}
            self.LLMTestCase: Optional[Type[Any]] = None
    
    def create_metric(self, config: MetricConfig) -> Any:
        """
        Create DeepEval metric instance from configuration.
        
        Args:
            config: Metric configuration
            
        Returns:
            DeepEval metric instance
            
        Raises:
            ImportError: If DeepEval is not available
            ValueError: If metric type is not supported
        """
        if not self.deepeval_available:
            raise ImportError("DeepEval is not installed. Install with: pip install deepeval")
        
        metric_class = self.metric_mapping.get(config.type)
        if not metric_class:
            raise ValueError(f"Unsupported metric type: {config.type}")
        
        try:
            # Create metric with configuration
            metric = metric_class(
                threshold=config.threshold,
                model=config.model,
                include_reason=config.include_reason,
                strict_mode=config.strict_mode
            )
            return metric
        except Exception as e:
            logger.error(f"Failed to create metric {config.type}: {e}")
            raise
    
    def create_test_case(
        self,
        input_text: str,
        actual_output: str,
        expected_output: Optional[str] = None,
        retrieval_context: Optional[List[str]] = None
    ) -> Any:
        """
        Create DeepEval LLMTestCase from test data.
        
        Args:
            input_text: Input text for the test
            actual_output: Actual output from LLM
            expected_output: Expected output (optional)
            retrieval_context: Retrieval context for RAG metrics (optional)
            
        Returns:
            DeepEval LLMTestCase instance
            
        Raises:
            ImportError: If DeepEval is not available
        """
        if not self.deepeval_available or self.LLMTestCase is None:
            raise ImportError("DeepEval is not installed. Install with: pip install deepeval")
        
        try:
            test_case = self.LLMTestCase(
                input=input_text,
                actual_output=actual_output,
                expected_output=expected_output,
                retrieval_context=retrieval_context
            )
            return test_case
        except Exception as e:
            logger.error(f"Failed to create test case: {e}")
            raise
    
    async def evaluate_metrics(
        self,
        test_case: Any,
        metrics: List[Any],
        metric_configs: List[MetricConfig]
    ) -> List[MetricResult]:
        """
        Evaluate DeepEval metrics and return results.
        
        Args:
            test_case: DeepEval LLMTestCase
            metrics: List of DeepEval metric instances
            metric_configs: List of metric configurations (for metadata)
            
        Returns:
            List of MetricResult objects
        """
        if not self.deepeval_available:
            raise ImportError("DeepEval is not installed. Install with: pip install deepeval")
        
        results = []
        
        for metric, config in zip(metrics, metric_configs):
            try:
                # Measure the metric
                metric.measure(test_case)
                
                # Extract results
                score = metric.score if hasattr(metric, 'score') else 0.0
                reason = metric.reason if hasattr(metric, 'reason') and config.include_reason else None
                
                # Determine if passed based on threshold
                passed = score >= config.threshold
                
                result = MetricResult(
                    type=config.type,
                    score=score,
                    passed=passed,
                    threshold=config.threshold,
                    reason=reason,
                    error=None
                )
                
                results.append(result)
                
            except Exception as e:
                logger.error(f"Failed to evaluate metric {config.type}: {e}")
                
                # Create error result
                error_result = MetricResult(
                    type=config.type,
                    score=0.0,
                    passed=False,
                    threshold=config.threshold,
                    reason=None,
                    error=str(e)
                )
                
                results.append(error_result)
        
        return results