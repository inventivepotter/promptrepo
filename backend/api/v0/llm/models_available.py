"""
LLM models endpoints.
Handles fetching models for specific providers.
"""
from fastapi import APIRouter
from openai import base_url
from pydantic import BaseModel
from typing import List
from any_llm import provider, list_models
import logging

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

        models = []

        any_llm_provider = provider.ProviderFactory.get_provider_class(provider_id)
        if not any_llm_provider:
            logger.error(f"Unsupported provider: {provider_id}")
            return ModelsResponse(models=[])

        raw_models = list_models(provider_id, request.api_key, api_base=request.api_base if request.api_base else None)
        models = [
            ModelInfo(id=model.id, name=model.id)
            for model in raw_models
            if model.id and model.object == 'model'
        ]
        logger.info(f"Returning {len(models)} models for provider {provider_id}")
        return ModelsResponse(models=models)
        
    except Exception as e:
        logger.error(f"Error fetching models for provider {provider_id}: {e}")
        return ModelsResponse(models=[])