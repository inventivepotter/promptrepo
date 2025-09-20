"""
Get hosting type endpoint without authentication - with standardized responses.
"""
import logging
from fastapi import APIRouter, Request, status
from pydantic import BaseModel
from services.config import ConfigStrategyFactory
from middlewares.rest import (
    StandardResponse,
    success_response,
    AppException
)

logger = logging.getLogger(__name__)
router = APIRouter()


class HostingTypeResponse(BaseModel):
    """Response for hosting type endpoint"""
    hosting_type: str


@router.get(
    "/hosting-type",
    response_model=StandardResponse[HostingTypeResponse],
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
async def get_hosting_type(request: Request) -> StandardResponse[HostingTypeResponse]:
    """
    Get current hosting type without authentication.
    This endpoint is publicly accessible to determine UI behavior.
    
    Returns:
        StandardResponse[HostingTypeResponse]: Standardized response containing hosting type
    
    Raises:
        AppException: When hosting type retrieval fails
    """
    request_id = getattr(request.state, "request_id", None)
    
    try:
        hosting_config = ConfigStrategyFactory.get_strategy().get_hosting_config()
        hosting_type = hosting_config.type.value
        
        logger.info(
            f"Hosting type retrieved: {hosting_type}",
            extra={
                "request_id": request_id,
                "hosting_type": hosting_type
            }
        )
        
        response_data = HostingTypeResponse(hosting_type=hosting_type)
        
        return success_response(
            data=response_data,
            message="Hosting type retrieved successfully",
            meta={"request_id": request_id}
        )
        
    except Exception as e:
        logger.error(
            f"Failed to retrieve hosting type: {str(e)}",
            exc_info=True,
            extra={"request_id": request_id}
        )
        raise AppException(
            message="Failed to retrieve hosting type",
            detail=str(e)
        )