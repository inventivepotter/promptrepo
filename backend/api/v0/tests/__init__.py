"""
Test API endpoints for DeepEval test management and execution.

This module provides REST API endpoints for:
- Test suite CRUD operations
- Test execution and history
"""

from fastapi import APIRouter
from . import suites, execution

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

__all__ = ["router"]