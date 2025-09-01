"""
LLM models endpoints.
Handles fetching models for specific providers.
"""
from fastapi import APIRouter
from pydantic import BaseModel
from typing import List
import logging

from services import provider_service
from schemas.config import ModelInfo

logger = logging.getLogger(__name__)
router = APIRouter()

# New endpoint for fetching models by provider and API key
class FetchModelsRequest(BaseModel):
    """Request for fetching models by provider and API key"""
    provider: str
    api_key: str
    api_base: str = ''

class ModelsResponse(BaseModel):
    """Response for models endpoint"""
    models: List[ModelInfo]

@router.post("/providers/{provider_id}/models", response_model=ModelsResponse)
async def fetch_models_by_provider(provider_id: str, request: FetchModelsRequest) -> ModelsResponse:
    """
    Fetch available models for a specific provider using API key.
    This endpoint would connect to the actual provider APIs to get real-time model information.
    """
    try:
        # Validate provider
        if provider_id != request.provider:
            logger.error(f"Provider ID mismatch: {provider_id} != {request.provider}")
            return ModelsResponse(models=[])

        models = provider_service.fetch_models_by_provider(
            provider_id,
            request.api_key,
            request.api_base
        )
        return ModelsResponse(models=models)
        
    except Exception as e:
        logger.error(f"Error fetching models for provider {provider_id}: {e}")
        return ModelsResponse(models=[])