"""
LLM-related API endpoints for PromptRepo.
Provides information about configured LLM providers and models.
"""
from fastapi import APIRouter
from .provider_models_configured import router as providers_configured_router
from .providers_available import router as providers_available_router
from .models_available import router as models_router
from .chat import router as chat_router

router = APIRouter()

# Include all endpoint routers
router.include_router(providers_configured_router)
router.include_router(providers_available_router)
router.include_router(models_router)
router.include_router(chat_router)