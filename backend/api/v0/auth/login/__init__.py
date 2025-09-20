"""
Login endpoints for OAuth authentication.
"""
from fastapi import APIRouter
from .github import router as github_router

# Create main auth router
router = APIRouter()

router.include_router(github_router, prefix="/login", tags=["github"])