"""
Metric configuration system using Strategy Pattern.

This module provides a scalable, SOLID-compliant way to define metric-specific
configurations that can be easily extended and validated.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional, Type, Set, Union
from pydantic import BaseModel, Field
from enum import Enum


class MetricCategory(str, Enum):
    """Categories of metrics for organization."""
    DETERMINISTIC = "deterministic"
    NON_DETERMINISTIC = "non_deterministic"


class BaseMetricConfig(BaseModel, ABC):
    """
    Base configuration for all metrics - defines EXPECTED fields.
    
    Each metric type should extend this to define its specific required fields.
    This follows the Open/Closed Principle - open for extension, closed for modification.
    """
    
    @classmethod
    @abstractmethod
    def get_metric_type_name(cls) -> str:
        """Return the metric type name this config is for."""
        pass
    
    @classmethod
    @abstractmethod
    def get_category(cls) -> MetricCategory:
        """Return whether this metric is deterministic or non-deterministic."""
        pass
    
    @classmethod
    @abstractmethod
    def get_description(cls) -> str:
        """Return human-readable description of what this metric evaluates."""
        pass
    
    @classmethod
    @abstractmethod
    def get_required_actual_fields(cls) -> List[str]:
        """
        Return list of required ACTUAL fields from test execution.
        
        These are fields that must be present in ActualEvaluationFieldsModel
        for this metric to evaluate (e.g., 'actual_output', 'tools_called').
        
        Returns:
            List of required actual field names
        """
        pass
    
    @classmethod
    def get_required_expected_field_names(cls) -> List[str]:
        """
        Get list of required EXPECTED field names for this metric.
        
        These are fields the user must provide in test definition.
        
        Returns:
            List of field names that must be provided by the user
        """
        required_fields = []
        for field_name, field_info in cls.model_fields.items():
            if field_info.is_required():
                required_fields.append(field_name)
        return required_fields
    
    @classmethod
    def get_field_schema(cls) -> Dict[str, Any]:
        """
        Get JSON schema for all fields in this configuration.
        
        Useful for frontend to dynamically build forms.
        """
        return cls.model_json_schema()


# ============================================================================
# DETERMINISTIC METRIC CONFIGURATIONS
# ============================================================================

class ExactMatchConfig(BaseMetricConfig):
    """Configuration for exact match metric."""
    
    expected_output: str = Field(
        description="Expected output for exact comparison"
    )
    
    @classmethod
    def get_metric_type_name(cls) -> str:
        return "exact_match"
    
    @classmethod
    def get_category(cls) -> MetricCategory:
        return MetricCategory.DETERMINISTIC
    
    @classmethod
    def get_description(cls) -> str:
        return "Compares the actual output exactly against the expected output"
    
    @classmethod
    def get_required_actual_fields(cls) -> List[str]:
        return ["actual_output"]


class FuzzyMatchConfig(BaseMetricConfig):
    """Configuration for fuzzy match metric."""
    
    expected_output: str = Field(
        description="Expected output for fuzzy comparison"
    )
    json_field: Optional[str] = Field(
        default=None,
        description="JSON field path to extract text from for fuzzy matching. Supports nested paths with dot notation (e.g., 'data.result.text')"
    )
    
    @classmethod
    def get_metric_type_name(cls) -> str:
        return "fuzzy_match"
    
    @classmethod
    def get_category(cls) -> MetricCategory:
        return MetricCategory.DETERMINISTIC
    
    @classmethod
    def get_description(cls) -> str:
        return "Deterministic metric that measures similarity between text strings using fuzzy matching algorithms"
    
    @classmethod
    def get_required_actual_fields(cls) -> List[str]:
        return ["actual_output"]


class SemanticSimilarityConfig(BaseMetricConfig):
    """Configuration for semantic similarity metric."""
    
    expected_output: str = Field(
        description="Expected output for semantic comparison"
    )
    
    @classmethod
    def get_metric_type_name(cls) -> str:
        return "semantic_similarity"
    
    @classmethod
    def get_category(cls) -> MetricCategory:
        return MetricCategory.DETERMINISTIC
    
    @classmethod
    def get_description(cls) -> str:
        return "Deterministic metric that measures semantic similarity between text using embedding comparisons"
    
    @classmethod
    def get_required_actual_fields(cls) -> List[str]:
        return ["actual_output"]


class KeywordPatternPresenceConfig(BaseMetricConfig):
    """Configuration for keyword/pattern presence metric."""
    
    expected_keywords: Optional[List[str]] = Field(
        default=None,
        description="Expected keywords that must be present in output"
    )
    expected_patterns: Optional[List[str]] = Field(
        default=None,
        description="Expected regex patterns that must be present in output"
    )
    forbidden_keywords: Optional[List[str]] = Field(
        default=None,
        description="Keywords that must NOT be present in output"
    )
    
    @classmethod
    def get_metric_type_name(cls) -> str:
        return "keyword_pattern_presence"
    
    @classmethod
    def get_category(cls) -> MetricCategory:
        return MetricCategory.DETERMINISTIC
    
    @classmethod
    def get_description(cls) -> str:
        return "Checks for the presence of required keywords or patterns"
    
    @classmethod
    def get_required_actual_fields(cls) -> List[str]:
        return ["actual_output"]


class OutputLengthConfig(BaseMetricConfig):
    """Configuration for output length metric."""
    
    min_length: Optional[int] = Field(
        default=None,
        description="Minimum expected output length (characters or words)"
    )
    max_length: Optional[int] = Field(
        default=None,
        description="Maximum expected output length (characters or words)"
    )
    length_unit: str = Field(
        default="characters",
        description="Unit for length measurement: 'characters' or 'words'"
    )
    
    @classmethod
    def get_metric_type_name(cls) -> str:
        return "output_length"
    
    @classmethod
    def get_category(cls) -> MetricCategory:
        return MetricCategory.DETERMINISTIC
    
    @classmethod
    def get_description(cls) -> str:
        return "Validates that output length is within specified bounds"
    
    @classmethod
    def get_required_actual_fields(cls) -> List[str]:
        return ["actual_output"]


class ToolsCalledConfig(BaseMetricConfig):
    """Configuration for tools called metric."""
    
    expected_tools: List[Dict[str, Any]] = Field(
        description="Expected tools to be called for agent evaluation"
    )
    
    @classmethod
    def get_metric_type_name(cls) -> str:
        return "tools_called"
    
    @classmethod
    def get_category(cls) -> MetricCategory:
        return MetricCategory.DETERMINISTIC
    
    @classmethod
    def get_description(cls) -> str:
        return "Verifies that the correct tools were called during execution"
    
    @classmethod
    def get_required_actual_fields(cls) -> List[str]:
        return ["actual_output", "tools_called"]


class JsonSchemaVerificationConfig(BaseMetricConfig):
    """Configuration for JSON schema verification metric."""
    
    expected_schema: Dict[str, Any] = Field(
        description="Expected JSON schema for JSON correctness evaluation"
    )
    
    @classmethod
    def get_metric_type_name(cls) -> str:
        return "json_schema_verification"
    
    @classmethod
    def get_category(cls) -> MetricCategory:
        return MetricCategory.DETERMINISTIC
    
    @classmethod
    def get_description(cls) -> str:
        return "Validates that the output conforms to the expected JSON schema"
    
    @classmethod
    def get_required_actual_fields(cls) -> List[str]:
        return ["actual_output"]


# ============================================================================
# NON-DETERMINISTIC METRIC CONFIGURATIONS
# ============================================================================

class AnswerRelevancyConfig(BaseMetricConfig):
    """Configuration for answer relevancy metric."""
    
    # No additional fields required - uses input and actual_output
    
    @classmethod
    def get_metric_type_name(cls) -> str:
        return "answer_relevancy"
    
    @classmethod
    def get_category(cls) -> MetricCategory:
        return MetricCategory.NON_DETERMINISTIC
    
    @classmethod
    def get_description(cls) -> str:
        return "Measures how relevant the answer is to the input question"
    
    @classmethod
    def get_required_actual_fields(cls) -> List[str]:
        return ["actual_output"]


class FaithfulnessConfig(BaseMetricConfig):
    """Configuration for faithfulness metric."""
    
    retrieval_context: List[str] = Field(
        description="Context for RAG evaluation metrics"
    )
    
    @classmethod
    def get_metric_type_name(cls) -> str:
        return "faithfulness"
    
    @classmethod
    def get_category(cls) -> MetricCategory:
        return MetricCategory.NON_DETERMINISTIC
    
    @classmethod
    def get_description(cls) -> str:
        return "Evaluates whether the answer is factually consistent with the context"
    
    @classmethod
    def get_required_actual_fields(cls) -> List[str]:
        return ["actual_output"]


class ContextualRelevancyConfig(BaseMetricConfig):
    """Configuration for contextual relevancy metric."""
    
    retrieval_context: List[str] = Field(
        description="Context for RAG evaluation metrics"
    )
    
    @classmethod
    def get_metric_type_name(cls) -> str:
        return "contextual_relevancy"
    
    @classmethod
    def get_category(cls) -> MetricCategory:
        return MetricCategory.NON_DETERMINISTIC
    
    @classmethod
    def get_description(cls) -> str:
        return "Assesses if the retrieved context is relevant to the input"
    
    @classmethod
    def get_required_actual_fields(cls) -> List[str]:
        return ["actual_output"]


class ContextualPrecisionConfig(BaseMetricConfig):
    """Configuration for contextual precision metric."""
    
    retrieval_context: List[str] = Field(
        description="Context for RAG evaluation metrics"
    )
    
    @classmethod
    def get_metric_type_name(cls) -> str:
        return "contextual_precision"
    
    @classmethod
    def get_category(cls) -> MetricCategory:
        return MetricCategory.NON_DETERMINISTIC
    
    @classmethod
    def get_description(cls) -> str:
        return "Measures the signal-to-noise ratio in the retrieved context"
    
    @classmethod
    def get_required_actual_fields(cls) -> List[str]:
        return ["actual_output"]


class ContextualRecallConfig(BaseMetricConfig):
    """Configuration for contextual recall metric."""
    
    retrieval_context: List[str] = Field(
        description="Context for RAG evaluation metrics"
    )
    
    @classmethod
    def get_metric_type_name(cls) -> str:
        return "contextual_recall"
    
    @classmethod
    def get_category(cls) -> MetricCategory:
        return MetricCategory.NON_DETERMINISTIC
    
    @classmethod
    def get_description(cls) -> str:
        return "Evaluates if all relevant information was retrieved"
    
    @classmethod
    def get_required_actual_fields(cls) -> List[str]:
        return ["actual_output"]


class HallucinationConfig(BaseMetricConfig):
    """Configuration for hallucination metric."""
    
    retrieval_context: List[str] = Field(
        description="Context for hallucination detection"
    )
    
    @classmethod
    def get_metric_type_name(cls) -> str:
        return "hallucination"
    
    @classmethod
    def get_category(cls) -> MetricCategory:
        return MetricCategory.NON_DETERMINISTIC
    
    @classmethod
    def get_description(cls) -> str:
        return "Detects when the model generates factually incorrect information"
    
    @classmethod
    def get_required_actual_fields(cls) -> List[str]:
        return ["actual_output"]


class BiasConfig(BaseMetricConfig):
    """Configuration for bias metric."""
    
    # No additional fields required - uses input and actual_output
    
    @classmethod
    def get_metric_type_name(cls) -> str:
        return "bias"
    
    @classmethod
    def get_category(cls) -> MetricCategory:
        return MetricCategory.NON_DETERMINISTIC
    
    @classmethod
    def get_description(cls) -> str:
        return "Identifies biased content in the response"
    
    @classmethod
    def get_required_actual_fields(cls) -> List[str]:
        return ["actual_output"]


class ToxicityConfig(BaseMetricConfig):
    """Configuration for toxicity metric."""
    
    # No additional fields required - uses input and actual_output
    
    @classmethod
    def get_metric_type_name(cls) -> str:
        return "toxicity"
    
    @classmethod
    def get_category(cls) -> MetricCategory:
        return MetricCategory.NON_DETERMINISTIC
    
    @classmethod
    def get_description(cls) -> str:
        return "Detects toxic or harmful content in the response"
    
    @classmethod
    def get_required_actual_fields(cls) -> List[str]:
        return ["actual_output"]


class SummarizationConfig(BaseMetricConfig):
    """Configuration for summarization metric."""
    
    assessment_questions: List[str] = Field(
        description="Assessment questions for summarization evaluation"
    )
    
    @classmethod
    def get_metric_type_name(cls) -> str:
        return "summarization"
    
    @classmethod
    def get_category(cls) -> MetricCategory:
        return MetricCategory.NON_DETERMINISTIC
    
    @classmethod
    def get_description(cls) -> str:
        return "Evaluates how effectively an LLM summarizes a piece of text, capturing main points accurately and concisely"
    
    @classmethod
    def get_required_actual_fields(cls) -> List[str]:
        return ["actual_output"]


class ProfessionalismConfig(BaseMetricConfig):
    """Configuration for professionalism metric."""
    
    # No additional fields required - uses input and actual_output
    
    @classmethod
    def get_metric_type_name(cls) -> str:
        return "professionalism"
    
    @classmethod
    def get_category(cls) -> MetricCategory:
        return MetricCategory.NON_DETERMINISTIC
    
    @classmethod
    def get_description(cls) -> str:
        return "Ensures the chatbot maintains a formal and professional tone appropriate for the context"
    
    @classmethod
    def get_required_actual_fields(cls) -> List[str]:
        return ["actual_output"]


class ConcisenessConfig(BaseMetricConfig):
    """Configuration for conciseness metric."""
    
    # No additional fields required - uses input and actual_output
    
    @classmethod
    def get_metric_type_name(cls) -> str:
        return "conciseness"
    
    @classmethod
    def get_category(cls) -> MetricCategory:
        return MetricCategory.NON_DETERMINISTIC
    
    @classmethod
    def get_description(cls) -> str:
        return "Measures if the LLM's response is brief and to the point, without unnecessary filler"
    
    @classmethod
    def get_required_actual_fields(cls) -> List[str]:
        return ["actual_output"]


# ============================================================================
# METRIC REGISTRY
# ============================================================================

class MetricRegistry:
    """
    Registry for all metric configurations.
    
    This follows the Dependency Inversion Principle - high-level code depends on
    this abstraction rather than concrete metric implementations.
    """
    
    _registry: Dict[str, Type[BaseMetricConfig]] = {
        # Deterministic
        "exact_match": ExactMatchConfig,
        "fuzzy_match": FuzzyMatchConfig,
        "semantic_similarity": SemanticSimilarityConfig,
        "keyword_pattern_presence": KeywordPatternPresenceConfig,
        "output_length": OutputLengthConfig,
        "tools_called": ToolsCalledConfig,
        "json_schema_verification": JsonSchemaVerificationConfig,
        
        # Non-deterministic
        "answer_relevancy": AnswerRelevancyConfig,
        "faithfulness": FaithfulnessConfig,
        "contextual_relevancy": ContextualRelevancyConfig,
        "contextual_precision": ContextualPrecisionConfig,
        "contextual_recall": ContextualRecallConfig,
        "hallucination": HallucinationConfig,
        "bias": BiasConfig,
        "toxicity": ToxicityConfig,
        "summarization": SummarizationConfig,
        "professionalism": ProfessionalismConfig,
        "conciseness": ConcisenessConfig,
    }
    
    @classmethod
    def get_config_class(cls, metric_type: str) -> Type[BaseMetricConfig]:
        """
        Get the configuration class for a metric type.
        
        Args:
            metric_type: The metric type name
            
        Returns:
            The configuration class for that metric
            
        Raises:
            ValueError: If metric type is not registered
        """
        if metric_type not in cls._registry:
            raise ValueError(f"Unknown metric type: {metric_type}")
        return cls._registry[metric_type]
    
    @classmethod
    def get_all_metric_types(cls) -> List[str]:
        """Get list of all registered metric types."""
        return list(cls._registry.keys())
    
    @classmethod
    def get_metric_metadata(cls, metric_type: str) -> Dict[str, Any]:
        """
        Get metadata about a metric type for frontend consumption.
        
        Args:
            metric_type: The metric type name
            
        Returns:
            Dictionary containing metric metadata
        """
        config_class = cls.get_config_class(metric_type)
        return {
            "type": metric_type,
            "category": config_class.get_category().value,
            "description": config_class.get_description(),
            "required_expected_fields": config_class.get_required_expected_field_names(),
            "required_actual_fields": config_class.get_required_actual_fields(),
            "field_schema": config_class.get_field_schema()
        }
    
    @classmethod
    def get_all_metrics_metadata(cls) -> Dict[str, Dict[str, Any]]:
        """
        Get metadata for all registered metrics.
        
        Useful for frontend to display available metrics and their requirements.
        """
        return {
            metric_type: cls.get_metric_metadata(metric_type)
            for metric_type in cls.get_all_metric_types()
        }
    
    @classmethod
    def register_metric(cls, metric_type: str, config_class: Type[BaseMetricConfig]) -> None:
        """
        Register a new metric configuration.
        
        This allows for runtime extension of supported metrics.
        
        Args:
            metric_type: The metric type name
            config_class: The configuration class
        """
        cls._registry[metric_type] = config_class