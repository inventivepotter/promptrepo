"""
Chat API endpoints for PromptRepo.
Provides chat completion functionality using any-llm.
"""
from fastapi import APIRouter
from .completions import router as completions_router

router = APIRouter()

# Include all endpoint routers
router.include_router(completions_router)