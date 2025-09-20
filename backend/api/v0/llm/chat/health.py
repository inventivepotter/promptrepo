"""
Health check endpoint for chat service.
"""
import logging
from fastapi import APIRouter, Request, status
from datetime import datetime

from middlewares.rest import StandardResponse, success_response

logger = logging.getLogger(__name__)
router = APIRouter()


@router.get(
    "/health",
    response_model=StandardResponse[dict],
    status_code=status.HTTP_200_OK,
    summary="Chat service health check",
    description="Health check for chat endpoints"
)
async def chat_health_check(request: Request) -> StandardResponse[dict]:
    """Health check for chat endpoints."""
    request_id = getattr(request.state, "request_id", None)
    
    health_data = {
        "status": "healthy",
        "service": "chat",
        "endpoints": [
            "POST /completions"
        ],
        "timestamp": datetime.utcnow().isoformat()
    }
    
    return success_response(
        data=health_data,
        message="Chat service is healthy",
        meta={"request_id": request_id}
    )