"""
Health check endpoint for config service.
"""
import logging
from datetime import datetime

from fastapi import APIRouter, Request, status

from middlewares.rest import StandardResponse, success_response

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get(
    "/health",
    response_model=StandardResponse[dict],
    status_code=status.HTTP_200_OK,
    summary="Config service health check",
    description="Health check for config endpoints"
)
async def config_health_check(request: Request) -> StandardResponse[dict]:
    """Health check for config endpoints."""
    request_id = getattr(request.state, "request_id", None)
    
    health_data = {
        "status": "healthy",
        "service": "config",
        "endpoints": [
            "GET /get_config",
            "POST /update_config",
            "GET /hosting_type"
        ],
        "timestamp": datetime.utcnow().isoformat()
    }
    
    return success_response(
        data=health_data,
        message="Config service is healthy",
        meta={"request_id": request_id}
    )