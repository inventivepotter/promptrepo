"""
Chat API utilities and endpoints.
"""
from fastapi import APIRouter
from .completions import router as completions_router
from .health import router as health_router

router = APIRouter()
router.include_router(completions_router)
router.include_router(health_router)