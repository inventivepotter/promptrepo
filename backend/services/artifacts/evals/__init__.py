"""
Eval service package for DeepEval integration.

This package provides evals management and execution functionality
for evaluating LLM prompts using DeepEval metrics.
"""

from .models import (
    MetricType,
    MetricConfig,
    TestDefinition,
    EvalDefinition,
    EvalData,
    MetricResult,
    TestExecutionResult,
    EvalExecutionResult,
    EvalExecutionData,
    EvalSummary,
    # Conversational test models
    Turn,
    TurnRole,
    TestType,
    ConversationalTestConfig,
)
from .eval_meta_service import EvalMetaService
from .eval_execution_meta_service import EvalExecutionMetaService
from .eval_execution_service import EvalExecutionService

__all__ = [
    "MetricType",
    "MetricConfig",
    "TestDefinition",
    "EvalDefinition",
    "EvalData",
    "MetricResult",
    "TestExecutionResult",
    "EvalExecutionResult",
    "EvalExecutionData",
    "EvalSummary",
    "EvalMetaService",
    "EvalExecutionMetaService",
    "EvalExecutionService",
    # Conversational test models
    "Turn",
    "TurnRole",
    "TestType",
    "ConversationalTestConfig",
]