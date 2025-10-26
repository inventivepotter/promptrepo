"""
Tools API endpoints module.

Manages CRUD operations for mock tool definitions.
"""
from fastapi import APIRouter

# Import sub-routers
from .tools import router as tools_router

# Create main tools router
router = APIRouter()

# Include all sub-routers
router.include_router(tools_router)