"""
Prompts API endpoints module.

Aggregates all prompt-related endpoints.
"""
from fastapi import APIRouter

# Import sub-routers
from .crud import router as crud_router
from .discover import router as discover_router

# Create main prompts router
router = APIRouter()

# Include all sub-routers
router.include_router(crud_router)
router.include_router(discover_router)