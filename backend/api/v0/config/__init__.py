"""
Configuration management endpoints.
Handles getting and updating application configuration through environment variables.
"""
from fastapi import APIRouter
from .get_config import router as get_router
from .update_config import router as update_router
from .export_config import router as export_router

router = APIRouter()

# Include all endpoint routers
router.include_router(get_router)
router.include_router(update_router)
router.include_router(export_router)