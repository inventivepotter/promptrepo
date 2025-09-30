"""
Prompts API endpoints module.

Aggregates all prompt-related endpoints.
"""
from fastapi import APIRouter

# Import sub-routers
from .list import router as list_router
from .crud import router as crud_router
from .sync import router as sync_router
from .repositories import router as repositories_router

# Create main prompts router
router = APIRouter()

# Include all sub-routers
router.include_router(list_router)
router.include_router(crud_router)
router.include_router(sync_router)
router.include_router(repositories_router)