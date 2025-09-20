"""
Get configuration endpoint with standardized responses.
"""
import logging
from fastapi import APIRouter, Request, status

from schemas import AppConfig, HostingType
from services import ConfigStrategyFactory
from middlewares.rest import (
    StandardResponse,
    success_response,
    AuthorizationException,
    AppException
)

logger = logging.getLogger(__name__)

router = APIRouter()

@router.get(
    "/",
    response_model=StandardResponse[AppConfig],
    status_code=status.HTTP_200_OK,
    responses={
        403: {
            "description": "Configuration access not allowed for non-individual hosting",
            "content": {
                "application/json": {
                    "example": {
                        "status": "error",
                        "type": "/errors/access-denied",
                        "title": "Access denied",
                        "detail": "Configuration access is only allowed for individual hosting type"
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
                        "detail": "Failed to retrieve configuration"
                    }
                }
            }
        }
    },
    summary="Get configuration",
    description="Retrieve current application configuration (only for individual hosting type)",
)
async def get_config(request: Request) -> StandardResponse[AppConfig]:
    """
    Get current application configuration.
    Only allowed for individual hosting type.
    
    Returns:
        StandardResponse[AppConfig]: Standardized response containing the configuration
    
    Raises:
        AuthorizationException: When hosting type is not individual
        AppException: When configuration retrieval fails
    """
    request_id = getattr(request.state, "request_id", None)
    
    try:
        config = ConfigStrategyFactory.get_strategy()
        current_hosting_type = config.get_hosting_config()
        
        logger.info(
            f"Fetching configuration for hosting type: {current_hosting_type}",
            extra={
                "request_id": request_id,
                "hosting_type": current_hosting_type.type
            }
        )
        
        # Check authorization based on hosting type
        if current_hosting_type != HostingType.INDIVIDUAL:
            logger.warning(
                f"Configuration access denied for hosting type: {current_hosting_type}",
                extra={
                    "request_id": request_id,
                    "hosting_type": current_hosting_type.type
                }
            )
            raise AuthorizationException(
                message="Configuration access is only allowed for individual hosting type",
                context={"current_hosting_type": current_hosting_type.type}
            )
        
        config_data = config.get_config()
        
        logger.info(
            "Configuration retrieved successfully",
            extra={
                "request_id": request_id,
                "hosting_type": current_hosting_type.type
            }
        )
        
        return success_response(
            data=config_data,
            message="Configuration retrieved successfully",
            meta={"request_id": request_id}
        )
        
    except (AuthorizationException, AppException):
        # These will be handled by the global exception handlers
        raise
    except Exception as e:
        logger.error(
            f"Failed to retrieve configuration: {str(e)}",
            exc_info=True,
            extra={"request_id": request_id}
        )
        raise AppException(
            message="Failed to retrieve configuration",
            detail=str(e)
        )