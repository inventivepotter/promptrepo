"""
Available LLM providers endpoint with standardized responses.
Returns predefined providers without requiring API keys.
"""
from fastapi import APIRouter, Request, status
from typing import List
from pydantic import BaseModel
import logging

from middlewares.rest import (
    StandardResponse,
    success_response,
    AppException
)
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


@router.get(
    "/providers/available",
    response_model=StandardResponse[BasicProvidersResponse],
    status_code=status.HTTP_200_OK,
    responses={
        500: {
            "description": "Internal server error",
            "content": {
                "application/json": {
                    "example": {
                        "status": "error",
                        "type": "/errors/internal-server-error",
                        "title": "Internal Server Error",
                        "detail": "Failed to retrieve available providers"
                    }
                }
            }
        }
    },
    summary="Get available providers",
    description="Get all available LLM providers without requiring API keys"
)
async def get_available_providers(request: Request) -> StandardResponse[BasicProvidersResponse]:
    """
    Get all available LLM providers without models.
    This endpoint returns predefined providers without requiring API keys.
    
    Returns:
        StandardResponse[BasicProvidersResponse]: Standardized response containing providers
    
    Raises:
        AppException: When provider retrieval fails
    """
    request_id = getattr(request.state, "request_id", None)
    
    try:
        logger.info(
            "Fetching available providers",
            extra={"request_id": request_id}
        )
        
        providers_data = provider_service.get_available_providers()
        providers = [
            BasicProviderInfo(**provider_data)
            for provider_data in providers_data
        ]
        
        logger.info(
            f"Retrieved {len(providers)} available providers",
            extra={
                "request_id": request_id,
                "provider_count": len(providers)
            }
        )
        
        return success_response(
            data=BasicProvidersResponse(providers=providers),
            message=f"Retrieved {len(providers)} available providers",
            meta={"request_id": request_id}
        )
        
    except Exception as e:
        logger.error(
            f"Error getting available providers: {e}",
            exc_info=True,
            extra={"request_id": request_id}
        )
        raise AppException(
            message="Failed to retrieve available providers",
            detail=str(e)
        )