"""
Eval API endpoints for DeepEval eval management and execution.

This module provides REST API endpoints for:
- Eval evals CRUD operations
- Eval execution and history
- Metrics metadata
"""

from fastapi import APIRouter
from . import evals, execution, metrics

router = APIRouter()

# Include metrics metadata endpoints FIRST (more specific routes should come before generic ones)
router.include_router(
    metrics.router,
    prefix="/metrics",
    tags=["Metrics"]
)

# Include eval execution endpoints
router.include_router(
    execution.router,
    prefix="/executions",
    tags=["Eval Execution"]
)

# Include evals endpoints (generic parameterized routes should be last)
router.include_router(
    evals.router,
    tags=["Eval evals"]
)

__all__ = ["router"]