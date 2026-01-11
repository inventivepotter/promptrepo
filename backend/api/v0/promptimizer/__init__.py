"""
Promptimizer API endpoints.

This module provides API endpoints for AI-powered prompt optimization.
"""
from fastapi import APIRouter
from api.v0.promptimizer.optimize import router as optimize_router

router = APIRouter()

# Include all endpoint routers
router.include_router(optimize_router)
