"""
Repository management endpoints module.
"""
from fastapi import APIRouter

# Import sub-routers
from .get_repos_available import router as available_router
from .get_configured import router as configured_router
from .get_branches import router as branches_router

# Create main repos router
router = APIRouter()

# Include all sub-routers
router.include_router(available_router)
router.include_router(configured_router)
router.include_router(branches_router)