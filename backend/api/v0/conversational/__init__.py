"""
Conversational API endpoints.

Provides endpoints for generating and simulating multi-turn conversations.
"""

from fastapi import APIRouter
from .turns import router as turns_router

router = APIRouter(tags=["conversational"])

router.include_router(turns_router)
