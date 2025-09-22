"""
Get hosting type endpoint without authentication - with standardized responses.
"""
import logging
from fastapi import APIRouter, Request, status
from api.deps import ConfigServiceDep
from middlewares.rest import (
    StandardResponse,
    success_response,
    AppException
)
from services.config.models import HostingConfig

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get(
    "/hosting-type",
    response_model=StandardResponse[HostingConfig],
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
                        "detail": "Failed to retrieve hosting type"
                    }
                }
            }
        }
    },
    summary="Get hosting type",
    description="Get current hosting type without authentication (publicly accessible)",
)
async def get_hosting_type(
    request: Request,
    config_service: ConfigServiceDep
) -> StandardResponse[HostingConfig]:
    """
    Get current hosting type without authentication.
    This endpoint is publicly accessible to determine UI behavior.
    
    Returns:
        StandardResponse[HostingTypeResponse]: Standardized response containing hosting type
    
    Raises:
        AppException: When hosting type retrieval fails
    """
    request_id = request.state.request_id
    correlation_id = request.state.correlation_id

    try:
        hosting_type = config_service.get_hosting_config()
        
        logger.info(
            f"Hosting type retrieved: {hosting_type}",
            extra={
                "request_id": request_id,
                "hosting_type": hosting_type
            }
        )
        
        
        return success_response(
            data=hosting_type,
            message="Hosting type retrieved successfully",
            meta={"request_id": request_id, "correlation_id": correlation_id}
        )
        
    except AttributeError as e:
        logger.error(
            f"Hosting type not found in request state: {str(e)}",
            exc_info=True,
            extra={"request_id": request_id}
        )
        raise AppException(
            message="Hosting type not available",
            detail="Request state is missing hosting_type, check middleware configuration."
        )