"""
Configured LLM providers endpoint.
Returns standardized provider information based on AppConfig.
"""
from fastapi import APIRouter
import logging

from services.provider_service import provider_service
from schemas.config import ProvidersResponse

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/providers/configured", response_model=ProvidersResponse)
async def get_configured_providers() -> ProvidersResponse:
    """
    Get configured LLM providers and their models.
    Returns standardized provider information based on AppConfig.
    """
    return provider_service.get_configured_providers()