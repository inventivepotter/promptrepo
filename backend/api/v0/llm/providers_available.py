"""
Available LLM providers endpoint.
Returns predefined providers without requiring API keys.
"""
from fastapi import APIRouter
from typing import List
from pydantic import BaseModel
import logging

from services.provider_service import provider_service

logger = logging.getLogger(__name__)
router = APIRouter()

class BasicProviderInfo(BaseModel):
    """Basic provider info without models"""
    id: str
    name: str
    custom_api_base: bool = False

class BasicProvidersResponse(BaseModel):
    """Response for basic providers endpoint"""
    providers: List[BasicProviderInfo]

@router.get("/providers/available", response_model=BasicProvidersResponse)
async def get_available_providers() -> BasicProvidersResponse:
    """
    Get all available LLM providers without models.
    This endpoint returns predefined providers without requiring API keys.
    """
    try:
        providers_data = provider_service.get_available_providers()
        providers = [
            BasicProviderInfo(**provider_data)
            for provider_data in providers_data
        ]
        return BasicProvidersResponse(providers=providers)
        
    except Exception as e:
        logger.error(f"Error getting available providers: {e}")
        return BasicProvidersResponse(providers=[])