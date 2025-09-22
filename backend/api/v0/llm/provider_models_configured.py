"""
Configured LLM providers endpoint with standardized responses.
Returns provider information based on AppConfig.
"""
from fastapi import APIRouter, Request, status
from pydantic import BaseModel
from typing import List
import logging

from middlewares.rest import (
    StandardResponse,
    success_response,
    AppException
)
from api.deps import ProviderServiceDep
from services.llm.models import ProviderInfo

logger = logging.getLogger(__name__)
router = APIRouter()


class ProvidersResponse(BaseModel):
    """Response for configured providers endpoint"""
    providers: List[ProviderInfo]


@router.get(
    "/providers/configured",
    response_model=StandardResponse[ProvidersResponse],
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
                        "detail": "Failed to retrieve configured providers"
                    }
                }
            }
        }
    },
    summary="Get configured providers",
    description="Get configured LLM providers and their database.models based on AppConfig"
)
async def get_configured_providers(
    request: Request,
    provider_service: ProviderServiceDep,
) -> StandardResponse[ProvidersResponse]:
    """
    Get configured LLM providers and their models.
    Returns standardized provider information based on AppConfig.
    
    Returns:
        StandardResponse[ProvidersResponse]: Standardized response containing providers
    
    Raises:
        AppException: When provider retrieval fails
    """
    request_id = getattr(request.state, "request_id", None)
    
    try:
        logger.info(
            "Fetching configured providers",
            extra={"request_id": request_id}
        )
        
        user_id = request.state.user_id
        providers_data = provider_service.get_configured_providers(user_id=user_id)
        
        # provider_service.get_configured_providers() always returns a ProvidersResponse
        response_data = providers_data
        provider_count = len(providers_data.providers) if providers_data.providers else 0
        
        logger.info(
            f"Retrieved {provider_count} configured providers for user {user_id}",
            extra={
                "request_id": request_id,
                "provider_count": provider_count,
                "user_id": user_id
            }
        )
        
        return success_response(
            data=response_data,
            message="Configured providers retrieved successfully",
            meta={"request_id": request_id}
        )
        
    except AppException:
        raise
    except Exception as e:
        logger.error(
            f"Failed to retrieve configured providers: {e}",
            exc_info=True,
            extra={"request_id": request_id}
        )
        raise AppException(
            message="Failed to retrieve configured providers",
            detail=str(e)
        )