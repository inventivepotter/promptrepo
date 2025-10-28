"""
Test API endpoints for DeepEval test management and execution.

This module provides REST API endpoints for:
- Test suite CRUD operations
- Test execution and history
- Metrics metadata
"""

from fastapi import APIRouter
from . import suites, execution, metrics

router = APIRouter()

# Include test suite endpoints
router.include_router(
    suites.router,
    prefix="/suites",
    tags=["Test Suites"]
)

# Include test execution endpoints
router.include_router(
    execution.router,
    prefix="/suites",
    tags=["Test Execution"]
)

# Include metrics metadata endpoints
router.include_router(
    metrics.router,
    prefix="/metrics",
    tags=["Metrics"]
)

__all__ = ["router"]