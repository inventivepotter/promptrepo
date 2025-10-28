"""
Pydantic models for the Test service.

These models handle data validation and serialization for DeepEval test framework
across test definitions and execution results.
"""

from datetime import datetime
from enum import Enum
from typing import Dict, Any, List, Optional, Union
from pydantic import BaseModel, Field, model_validator

from services.test.metric_config import (
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


class ExpectedEvaluationFieldsModel(BaseModel):
    """
    Expected evaluation fields for test definition.
    
    This model uses composition to store metric-specific configurations
    in a type-safe manner while maintaining backward compatibility.
    """
    
    # Store the actual metric-specific configuration
    metric_type: Optional[MetricType] = Field(
        default=None,
        description="The metric type this configuration is for"
    )
    
    # Dynamic storage for metric-specific config
    config: Optional[Dict[str, Any]] = Field(
        default=None,
        description="Metric-specific configuration fields"
    )
    
    @classmethod
    def from_metric_config(cls, metric_type: MetricType, config: BaseMetricConfig) -> "ExpectedEvaluationFieldsModel":
        """
        Create ExpectedEvaluationFieldsModel from a metric-specific config.
        
        Args:
            metric_type: The metric type
            config: The metric-specific configuration
            
        Returns:
            ExpectedEvaluationFieldsModel instance
        """
        return cls(
            metric_type=metric_type,
            config=config.model_dump(exclude_none=True)
        )
    
    def to_metric_config(self) -> Optional[BaseMetricConfig]:
        """
        Convert to metric-specific configuration object.
        
        Returns:
            The metric-specific configuration instance
        """
        if not self.metric_type or not self.config:
            return None
        
        config_class = MetricType.get_config_class(self.metric_type)
        return config_class(**self.config)
    
    def get_config_value(self, field_name: str) -> Any:
        """
        Get a specific configuration value.
        
        Args:
            field_name: The field name to retrieve
            
        Returns:
            The field value or None if not found
        """
        if not self.config:
            return None
        return self.config.get(field_name)
    
    @model_validator(mode='after')
    def validate_metric_config(self) -> 'ExpectedEvaluationFieldsModel':
        """Validate that config matches the metric type requirements"""
        if self.metric_type and self.config:
            # Validate that the config has all required fields
            config_class = MetricType.get_config_class(self.metric_type)
            try:
                # This will raise validation error if config is invalid
                config_class(**self.config)
            except Exception as e:
                raise ValueError(f"Invalid configuration for {self.metric_type.value}: {str(e)}")
        return self


class ActualEvaluationFieldsModel(BaseModel):
    """Actual evaluation fields from test execution"""
    # Common fields
    actual_output: str = Field(description="Actual output from LLM execution")
    
    # Tool-related fields for agent evaluation
    tools_called: Optional[List[Dict[str, Any]]] = Field(
        default=None,
        description="List of tools actually called during execution for agent metrics"
    )
    
    # Additional execution data
    execution_time_ms: Optional[int] = Field(
        default=None,
        description="Execution time in milliseconds"
    )
    
    error: Optional[str] = Field(
        default=None,
        description="Error that occurred during execution"
    )


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


class UnitTestDefinition(BaseModel):
    """Individual test case definition"""
    name: str = Field(description="Unique test name within suite")
    description: Optional[str] = Field(default="", description="Test description")
    prompt_reference: str = Field(description="Reference to prompt file path")
    template_variables: Dict[str, Any] = Field(
        default_factory=dict,
        description="Template variables for prompt execution"
    )
    evaluation_fields: ExpectedEvaluationFieldsModel = Field(
        default_factory=ExpectedEvaluationFieldsModel,
        description="Expected evaluation fields for different metric types"
    )
    enabled: bool = Field(default=True, description="Whether test is enabled")


class TestSuiteDefinition(BaseModel):
    """Test suite containing multiple unit tests"""
    name: str = Field(description="Test suite name")
    description: Optional[str] = Field(default="", description="Suite description")
    tests: List[UnitTestDefinition] = Field(
        default_factory=list,
        description="Unit tests in this suite"
    )
    tags: List[str] = Field(default_factory=list, description="Tags for organization")
    metrics: List[MetricConfig] = Field(default_factory=list, description="DeepEval metrics to evaluate for all tests in suite")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = {
        "json_encoders": {
            datetime: lambda v: v.isoformat()
        }
    }


class TestSuiteData(BaseModel):
    """Wrapper for YAML serialization"""
    test_suite: TestSuiteDefinition


class MetricResult(BaseModel):
    """Result from a single metric evaluation"""
    type: MetricType
    score: float = Field(description="Metric score (0.0 to 1.0)")
    passed: bool = Field(description="Whether metric passed threshold")
    threshold: float
    reason: Optional[str] = Field(default=None, description="Explanation from DeepEval")
    error: Optional[str] = Field(default=None, description="Error if metric failed to execute")


class UnitTestExecutionResult(BaseModel):
    """Execution result for a single unit test"""
    test_name: str = Field(description="Name of the test")
    prompt_reference: str = Field(description="Reference to prompt file path")
    template_variables: Dict[str, Any] = Field(description="Template variables used in execution")
    actual_evaluation_fields: ActualEvaluationFieldsModel = Field(description="Actual evaluation fields from execution")
    expected_evaluation_fields: ExpectedEvaluationFieldsModel = Field(description="Expected evaluation fields from test definition")
    metric_results: List[MetricResult] = Field(description="Results from all metrics")
    overall_passed: bool = Field(description="Whether all metrics passed")
    executed_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = {
        "json_encoders": {
            datetime: lambda v: v.isoformat()
        }
    }


class TestSuiteExecutionResult(BaseModel):
    """Execution result for entire test suite"""
    suite_name: str
    test_results: List[UnitTestExecutionResult]
    total_tests: int
    passed_tests: int
    failed_tests: int
    total_execution_time_ms: int
    executed_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = {
        "json_encoders": {
            datetime: lambda v: v.isoformat()
        }
    }


class TestSuiteExecutionData(BaseModel):
    """Wrapper for execution YAML serialization"""
    execution: TestSuiteExecutionResult


class TestSuiteSummary(BaseModel):
    """Summary of test suite for listing"""
    name: str
    description: str
    test_count: int
    tags: List[str]
    file_path: str
    last_execution: Optional[datetime] = None
    last_execution_passed: Optional[bool] = None

    model_config = {
        "json_encoders": {
            datetime: lambda v: v.isoformat()
        }
    }