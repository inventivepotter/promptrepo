"""
LLM database.models endpoints with standardized responses.
Handles fetching database.models for specific providers.
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
from api.deps import ProviderServiceDep, CurrentUserDep
from services.llm.models import ModelInfo

logger = logging.getLogger(__name__)
router = APIRouter()

class FetchModelsRequest(BaseModel):
    """Request model for fetching models from a provider"""
    api_key: str
    api_base: str = ""

class ModelsResponse(BaseModel):
    """Response for database.models endpoint"""
    models: List[ModelInfo]


@router.post(
    "/provider/{provider_id}/models",
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
    summary="Fetch database.models by provider",
    description="Fetch available database.models for a specific provider using API key"
)
async def fetch_models_by_provider(
    provider_id: str,
    request: Request,
    req_body: FetchModelsRequest,
    user_id: CurrentUserDep,
    provider_service: ProviderServiceDep
) -> StandardResponse[ModelsResponse]:
    """
    Fetch available database.models for a specific provider using API key.
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
        if not provider_id:
            logger.error(
                f"Provider ID is required",
                extra={
                    "request_id": request_id,
                }
            )
            raise BadRequestException(
                message="Provider ID is required",
                context={
                    "provider_id": provider_id,
                }
            )

        logger.info(
            f"Fetching database.models for provider: {provider_id}",
            extra={
                "request_id": request_id,
                "provider": provider_id,
            }
        )

        models = provider_service.fetch_models_by_provider(
            provider_id=provider_id,
            api_key=req_body.api_key,
            api_base=req_body.api_base
        )
        
        logger.info(
            f"Retrieved {len(models)} database.models for provider: {provider_id}",
            extra={
                "request_id": request_id,
                "provider": provider_id,
                "model_count": len(models)
            }
        )
        
        return success_response(
            data=ModelsResponse(models=models),
            message=f"Retrieved {len(models)} database.models for provider {provider_id}",
            meta={"request_id": request_id}
        )
        
    except BadRequestException:
        raise
    except Exception as e:
        logger.error(
            f"Error fetching database.models for provider {provider_id}: {e}",
            exc_info=True,
            extra={
                "request_id": request_id,
                "provider": provider_id
            }
        )
        raise AppException(
            message=f"Failed to fetch database.models for provider {provider_id}",
            detail=str(e)
        )