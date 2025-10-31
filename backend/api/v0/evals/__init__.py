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

# Include evals endpoints
router.include_router(
    evals.router,
    prefix="/evals",
    tags=["Eval evals"]
)

# Include eval execution endpoints
router.include_router(
    execution.router,
    prefix="/evals",
    tags=["Eval Execution"]
)

# Include metrics metadata endpoints
router.include_router(
    metrics.router,
    prefix="/metrics",
    tags=["Metrics"]
)

__all__ = ["router"]