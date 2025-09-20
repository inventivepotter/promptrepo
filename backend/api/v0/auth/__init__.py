"""
Authentication endpoints module.
"""
from fastapi import APIRouter

# Import sub-routers
from .login_github import router as login_router
from .callback_github import router as callback_router
from .verify import router as verify_router
from .logout import router as logout_router
from .refresh import router as refresh_router
from .health import router as health_router

# Create main auth router
router = APIRouter()

# Include all sub-routers
router.include_router(login_router)
router.include_router(callback_router)
router.include_router(verify_router)
router.include_router(logout_router)
router.include_router(refresh_router)
router.include_router(health_router)