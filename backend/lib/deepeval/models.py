"""
Pydantic models for the Test service.

These models handle data validation and serialization for DeepEval test framework
across test definitions and execution results.
"""

from datetime import datetime
from enum import Enum
from typing import Dict, Any, List, Optional, Union
from pydantic import BaseModel, Field, model_validator

from lib.deepeval.metric_config import (
    MetricRegistry,
    MetricCategory,
    BaseMetricConfig
)

class MetricType(str, Enum):
    """
    Predefined DeepEval metrics supported in UI.
    
    This enum delegates to MetricRegistry for metadata, following DRY principle.
    """
    
    # Deterministic metrics (exact comparisons, no LLM involvement)
    EXACT_MATCH = "exact_match"
    TOOLS_CALLED = "tools_called"
    JSON_SCHEMA_VERIFICATION = "json_schema_verification"
    KEYWORD_PATTERN_PRESENCE = "keyword_pattern_presence"
    OUTPUT_LENGTH = "output_length"
    FUZZY_MATCH = "fuzzy_match"
    SEMANTIC_SIMILARITY = "semantic_similarity"
    
    # Non-deterministic metrics (LLM-based evaluation)
    ANSWER_RELEVANCY = "answer_relevancy"
    FAITHFULNESS = "faithfulness"
    CONTEXTUAL_RELEVANCY = "contextual_relevancy"
    CONTEXTUAL_PRECISION = "contextual_precision"
    CONTEXTUAL_RECALL = "contextual_recall"
    HALLUCINATION = "hallucination"
    BIAS = "bias"
    TOXICITY = "toxicity"
    SUMMARIZATION = "summarization"
    PROFESSIONALISM = "professionalism"
    CONCISENESS = "conciseness"
    
    @property
    def description(self) -> str:
        """Get human-readable description for the metric type"""
        config_class = MetricRegistry.get_config_class(self.value)
        return config_class.get_description()
    
    @property
    def category(self) -> MetricCategory:
        """Get the category (deterministic/non-deterministic) for this metric"""
        config_class = MetricRegistry.get_config_class(self.value)
        return config_class.get_category()
    
    @classmethod
    def is_deterministic(cls, metric_type: 'MetricType') -> bool:
        """Check if a metric type is deterministic (no LLM involvement)"""
        config_class = MetricRegistry.get_config_class(metric_type.value)
        return config_class.get_category() == MetricCategory.DETERMINISTIC
    
    @classmethod
    def is_non_deterministic(cls, metric_type: 'MetricType') -> bool:
        """Check if a metric type is non-deterministic (LLM-based evaluation)"""
        return not cls.is_deterministic(metric_type)
    
    @classmethod
    def get_required_expected_fields(cls, metric_type: 'MetricType') -> List[str]:
        """Get required expected fields for a metric type"""
        config_class = MetricRegistry.get_config_class(metric_type.value)
        return config_class.get_required_expected_field_names()
    
    @classmethod
    def get_required_actual_fields(cls, metric_type: 'MetricType') -> List[str]:
        """Get required actual fields for a metric type"""
        config_class = MetricRegistry.get_config_class(metric_type.value)
        return config_class.get_required_actual_fields()
    
    @classmethod
    def get_config_class(cls, metric_type: 'MetricType') -> type[BaseMetricConfig]:
        """Get the configuration class for a metric type"""
        return MetricRegistry.get_config_class(metric_type.value)

class MetricConfig(BaseModel):
    """Configuration for a single DeepEval metric"""
    type: MetricType = Field(description="Type of DeepEval metric")
    
    # Optional for deterministic metrics that use exact comparisons
    threshold: Optional[float] = Field(
        default=None,
        ge=0.0,
        le=1.0,
        description="Minimum passing score (optional for deterministic metrics)"
    )
    
    # LLM configuration - required for non-deterministic metrics
    provider: Optional[str] = Field(
        default=None,
        description="LLM provider for non-deterministic metrics (e.g., openai, anthropic)"
    )
    model: Optional[str] = Field(
        default=None,
        description="LLM model for non-deterministic metrics (e.g., gpt-4, claude-3-opus)"
    )
    
    include_reason: bool = Field(default=True, description="Include reasoning in results")
    strict_mode: Optional[bool] = Field(
        default=None,
        description="Enable strict evaluation mode (optional)"
    )
    
    @model_validator(mode='after')
    def validate_llm_config(self) -> 'MetricConfig':
        """Validate that LLM configuration is provided for non-deterministic metrics"""
        if MetricType.is_non_deterministic(self.type):
            if not self.provider or not self.model:
                raise ValueError(
                    f"Non-deterministic metric '{self.type.value}' requires both 'provider' and 'model' to be specified"
                )
        return self

class MetricResult(BaseModel):
    """Result from a single metric evaluation"""
    type: MetricType
    score: float = Field(description="Metric score (0.0 to 1.0)")
    passed: bool = Field(description="Whether metric passed threshold")
    threshold: float
    reason: Optional[str] = Field(default=None, description="Explanation from DeepEval")
    error: Optional[str] = Field(default=None, description="Error if metric failed to execute")

