"""
Get configuration endpoint with standardized responses.
"""
import logging
from fastapi import APIRouter, Request, status

from services.config.models import AppConfig
from api.deps import ConfigServiceDep
from middlewares.rest import (
    StandardResponse,
    success_response,
    AppException
)

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get(
    "/",
    response_model=StandardResponse[AppConfig],
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
                        "detail": "Failed to retrieve configuration"
                    }
                }
            }
        }
    },
    summary="Get configuration",
    description="Retrieve current application configuration",
)
async def get_config(
    request: Request,
    config_service: ConfigServiceDep
) -> StandardResponse[AppConfig]:
    """
    Get current application configuration.
    
    Returns:
        StandardResponse[AppConfig]: Standardized response containing the configuration
    
    Raises:
        AppException: When configuration retrieval fails
    """
    request_id = request.state.request_id
    user_id = request.state.user_id
    
    try:
        logger.info(
            "Fetching configuration",
            extra={"request_id": request_id, "user_id": user_id}
        )
        
        config_data = config_service.get_configs_for_api(user_id=user_id)
        
        logger.info(
            "Configuration retrieved successfully",
            extra={"request_id": request_id, "user_id": user_id}
        )
        
        return success_response(
            data=config_data,
            message="Configuration retrieved successfully",
            meta={"request_id": request_id}
        )
        
    except AppException:
        # This will be handled by the global exception handler
        raise
    except Exception as e:
        logger.error(
            f"Failed to retrieve configuration: {str(e)}",
            exc_info=True,
            extra={"request_id": request_id, "user_id": user_id}
        )
        raise AppException(
            message="Failed to retrieve configuration",
            detail=str(e)
        )