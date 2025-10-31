"""
Pydantic models for the Eval service.

These models handle data validation and serialization for DeepEval eval framework
across eval definitions and execution results.
"""

from datetime import datetime
from enum import Enum
from typing import Dict, Any, List, Optional, TypeAlias
from pydantic import BaseModel, Field, model_validator
from lib.deepeval import MetricType, BaseMetricConfig, MetricConfig, MetricResult

class ExpectedEvaluationFieldsModel(BaseModel):
    """
    Expected evaluation fields for eval definition.
    
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
    """Actual evaluation fields from eval execution"""
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


class EvalDefinition(BaseModel):
    """Individual eval case definition"""
    name: str = Field(description="Unique eval name within suite")
    description: Optional[str] = Field(default="", description="Eval description")
    prompt_reference: str = Field(description="Reference to prompt file path")
    user_message: Optional[str] = Field(
        default=None,
        description="User message input for the prompt"
    )
    template_variables: Dict[str, Any] = Field(
        default_factory=dict,
        description="Template variables for prompt execution"
    )
    evaluation_fields: ExpectedEvaluationFieldsModel = Field(
        default_factory=ExpectedEvaluationFieldsModel,
        description="Expected evaluation fields for different metric types"
    )
    enabled: bool = Field(default=True, description="Whether eval is enabled")


class EvalSuiteDefinition(BaseModel):
    """Eval suite containing multiple unit evals"""
    name: str = Field(description="Eval suite name")
    description: Optional[str] = Field(default="", description="Suite description")
    evals: List[EvalDefinition] = Field(
        default_factory=list,
        description="Unit evals in this suite"
    )
    tags: List[str] = Field(default_factory=list, description="Tags for organization")
    metrics: List[MetricConfig] = Field(default_factory=list, description="DeepEval metrics to evaluate for all evals in suite")
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = {
        "json_encoders": {
            datetime: lambda v: v.isoformat()
        }
    }


class EvalSuiteData(BaseModel):
    """Wrapper for YAML serialization"""
    eval_suite: EvalSuiteDefinition


class EvalExecutionResult(BaseModel):
    """Execution result for a single eval"""
    eval_name: str = Field(description="Name of the eval")
    prompt_reference: str = Field(description="Reference to prompt file path")
    template_variables: Dict[str, Any] = Field(description="Template variables used in execution")
    actual_evaluation_fields: ActualEvaluationFieldsModel = Field(description="Actual evaluation fields from execution")
    expected_evaluation_fields: ExpectedEvaluationFieldsModel = Field(description="Expected evaluation fields from eval definition")
    metric_results: List[MetricResult] = Field(description="Results from all metrics")
    overall_passed: bool = Field(description="Whether all metrics passed")
    executed_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = {
        "json_encoders": {
            datetime: lambda v: v.isoformat()
        }
    }


class EvalSuiteExecutionResult(BaseModel):
    """Execution result for entire eval suite"""
    suite_name: str
    eval_results: List[EvalExecutionResult]
    total_evals: int
    passed_evals: int
    failed_evals: int
    total_execution_time_ms: int
    executed_at: datetime = Field(default_factory=datetime.utcnow)

    model_config = {
        "json_encoders": {
            datetime: lambda v: v.isoformat()
        }
    }


class EvalSuiteExecutionData(BaseModel):
    """Wrapper for execution YAML serialization"""
    execution: EvalSuiteExecutionResult


class EvalSuiteSummary(BaseModel):
    """Summary of eval suite for listing"""
    name: str
    description: str
    eval_count: int
    tags: List[str]
    file_path: str
    last_execution: Optional[datetime] = None
    last_execution_passed: Optional[bool] = None

    model_config = {
        "json_encoders": {
            datetime: lambda v: v.isoformat()
        }
    }


class MetricMetadataModel(BaseModel):
    """
    Metadata for a single metric type.

    This model describes all information needed by the frontend to:
    - Display metric information to users
    - Dynamically generate configuration forms
    - Validate user input
    """

    type: str = Field(
        description="Metric type identifier (e.g., 'exact_match', 'professionalism')"
    )
    category: str = Field(
        description="Metric category: 'deterministic' or 'non_deterministic'"
    )
    description: str = Field(
        description="Human-readable description of what this metric evaluates"
    )
    required_expected_fields: List[str] = Field(
        description="List of field names the user must provide in eval definition"
    )
    required_actual_fields: List[str] = Field(
        description="List of field names that must be present from eval execution"
    )
    field_schema: Dict[str, Any] = Field(
        description="JSON schema for expected fields configuration (for dynamic form generation)"
    )

    class Config:
        json_schema_extra = {
            "example": {
                "type": "exact_match",
                "category": "deterministic",
                "description": "Compares the actual output exactly against the expected output",
                "required_expected_fields": ["expected_output"],
                "required_actual_fields": ["actual_output"],
                "field_schema": {
                    "type": "object",
                    "properties": {
                        "expected_output": {
                            "type": "string",
                            "description": "Expected output for exact comparison"
                        }
                    },
                    "required": ["expected_output"]
                }
            }
        }


MetricsMetadataResponse: TypeAlias = Dict[str, MetricMetadataModel]