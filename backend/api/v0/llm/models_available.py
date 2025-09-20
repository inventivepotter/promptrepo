"""
LLM models endpoints with standardized responses.
Handles fetching models for specific providers.
"""
from fastapi import APIRouter, Request, status
from pydantic import BaseModel
from typing import List
import logging

from middlewares.rest import (
    StandardResponse,
    success_response,
    BadRequestException,
    AppException
)
from services.llm.provider_service import ProviderService
from services.llm.models import ModelInfo

logger = logging.getLogger(__name__)
router = APIRouter()


class FetchModelsRequest(BaseModel):
    """Request for fetching models by provider and API key"""
    provider: str
    api_key: str
    api_base: str = ''


class ModelsResponse(BaseModel):
    """Response for models endpoint"""
    models: List[ModelInfo]


@router.post(
    "/providers/models/{provider_id}",
    response_model=StandardResponse[ModelsResponse],
    status_code=status.HTTP_200_OK,
    responses={
        400: {
            "description": "Bad request",
            "content": {
                "application/json": {
                    "example": {
                        "status": "error",
                        "type": "/errors/bad-request",
                        "title": "Bad request",
                        "detail": "Provider ID mismatch"
                    }
                }
            }
        },
        500: {
            "description": "Internal server error",
            "content": {
                "application/json": {
                    "example": {
                        "status": "error",
                        "type": "/errors/internal-server-error",
                        "title": "Internal Server Error",
                        "detail": "Failed to fetch models"
                    }
                }
            }
        }
    },
    summary="Fetch models by provider",
    description="Fetch available models for a specific provider using API key"
)
async def fetch_models_by_provider(
    provider_id: str,
    request_body: FetchModelsRequest,
    request: Request
) -> StandardResponse[ModelsResponse]:
    """
    Fetch available models for a specific provider using API key.
    This endpoint connects to the actual provider APIs to get real-time model information.
    
    Returns:
        StandardResponse[ModelsResponse]: Standardized response containing models
    
    Raises:
        BadRequestException: When provider ID mismatch occurs
        AppException: When model fetching fails
    """
    request_id = getattr(request.state, "request_id", None)
    
    try:
        # Validate provider
        if provider_id != request_body.provider:
            logger.error(
                f"Provider ID mismatch",
                extra={
                    "request_id": request_id,
                    "url_provider": provider_id,
                    "body_provider": request_body.provider
                }
            )
            raise BadRequestException(
                message="Provider ID mismatch",
                context={
                    "url_provider": provider_id,
                    "body_provider": request_body.provider
                }
            )

        logger.info(
            f"Fetching models for provider: {provider_id}",
            extra={
                "request_id": request_id,
                "provider": provider_id,
                "has_api_base": bool(request_body.api_base)
            }
        )

        models = ProviderService.fetch_models_by_provider(
            provider_id,
            request_body.api_key,
            request_body.api_base
        )
        
        logger.info(
            f"Retrieved {len(models)} models for provider: {provider_id}",
            extra={
                "request_id": request_id,
                "provider": provider_id,
                "model_count": len(models)
            }
        )
        
        return success_response(
            data=ModelsResponse(models=models),
            message=f"Retrieved {len(models)} models for provider {provider_id}",
            meta={"request_id": request_id}
        )
        
    except BadRequestException:
        raise
    except Exception as e:
        logger.error(
            f"Error fetching models for provider {provider_id}: {e}",
            exc_info=True,
            extra={
                "request_id": request_id,
                "provider": provider_id
            }
        )
        raise AppException(
            message=f"Failed to fetch models for provider {provider_id}",
            detail=str(e)
        )