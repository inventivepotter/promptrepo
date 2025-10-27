"""
Pydantic models for the Test service.

These models handle data validation and serialization for DeepEval test framework
across test definitions and execution results.
"""

from datetime import datetime
from enum import Enum
from typing import Dict, Any, List, Optional
from pydantic import BaseModel, Field


class MetricType(str, Enum):
    """Predefined DeepEval metrics supported in UI"""
    ANSWER_RELEVANCY = "answer_relevancy"
    FAITHFULNESS = "faithfulness"
    CONTEXTUAL_RELEVANCY = "contextual_relevancy"
    CONTEXTUAL_PRECISION = "contextual_precision"
    CONTEXTUAL_RECALL = "contextual_recall"
    HALLUCINATION = "hallucination"
    BIAS = "bias"
    TOXICITY = "toxicity"


class MetricConfig(BaseModel):
    """Configuration for a single DeepEval metric"""
    type: MetricType = Field(description="Type of DeepEval metric")
    threshold: float = Field(default=0.7, ge=0.0, le=1.0, description="Minimum passing score")
    model: str = Field(default="gpt-4", description="LLM model for metric evaluation")
    include_reason: bool = Field(default=True, description="Include reasoning in results")
    strict_mode: bool = Field(default=False, description="Enable strict evaluation mode")


class UnitTestDefinition(BaseModel):
    """Individual test case definition"""
    name: str = Field(description="Unique test name within suite")
    description: Optional[str] = Field(default="", description="Test description")
    prompt_reference: str = Field(description="Reference to prompt file path")
    template_variables: Dict[str, Any] = Field(
        default_factory=dict,
        description="Template variables for prompt execution"
    )
    expected_output: Optional[str] = Field(default=None, description="Expected output for comparison")
    retrieval_context: Optional[List[str]] = Field(
        default=None,
        description="Context for RAG evaluation metrics"
    )
    metrics: List[MetricConfig] = Field(description="DeepEval metrics to evaluate")
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
    test_name: str
    prompt_reference: str
    template_variables: Dict[str, Any]
    actual_output: str = Field(description="Output from prompt execution")
    expected_output: Optional[str] = None
    retrieval_context: Optional[List[str]] = None
    metric_results: List[MetricResult] = Field(description="Results from all metrics")
    overall_passed: bool = Field(description="Whether all metrics passed")
    execution_time_ms: int = Field(description="Execution duration in milliseconds")
    executed_at: datetime = Field(default_factory=datetime.utcnow)
    error: Optional[str] = Field(default=None, description="Error if test failed to execute")

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