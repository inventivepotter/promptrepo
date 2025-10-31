"""
Eval API endpoints for DeepEval eval management and execution.

This module provides REST API endpoints for:
- Eval suite CRUD operations
- Eval execution and history
- Metrics metadata
"""

from fastapi import APIRouter
from . import suites, execution, metrics

router = APIRouter()

# Include eval suite endpoints
router.include_router(
    suites.router,
    prefix="/suites",
    tags=["Eval Suites"]
)

# Include eval execution endpoints
router.include_router(
    execution.router,
    prefix="/suites",
    tags=["Eval Execution"]
)

# Include metrics metadata endpoints
router.include_router(
    metrics.router,
    prefix="/metrics",
    tags=["Metrics"]
)

__all__ = ["router"]