"""
Available LLM providers endpoint.
Returns predefined providers without requiring API keys.
"""
from fastapi import APIRouter
from typing import List
from fastapi.background import P
from pydantic import BaseModel
from any_llm.provider import ProviderName
from utils.constants import PROVIDER_NAMES_MAP
import logging

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
        providers = []
        for provider in ProviderName:
            provider_info = PROVIDER_NAMES_MAP.get(provider)
            provider_default_name = provider.replace("_", " ").title()
            display_name = provider_info.get("name", provider_default_name) if provider_info else provider_default_name
            providers.append(BasicProviderInfo(id=provider, name=display_name, custom_api_base=provider_info.get("custom_api_base", False) if provider_info else False))
        return BasicProvidersResponse(providers=providers)
        
    except Exception as e:
        logger.error(f"Error getting available providers: {e}")
        return BasicProvidersResponse(providers=[])