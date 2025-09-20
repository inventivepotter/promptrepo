"""
Health check endpoint for llm service.
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
    summary="LLM service health check",
    description="Health check for llm endpoints"
)
async def llm_health_check(request: Request) -> StandardResponse[dict]:
    """Health check for llm endpoints."""
    request_id = getattr(request.state, "request_id", None)
    
    health_data = {
        "status": "healthy",
        "service": "llm",
        "endpoints": [
            "GET /models_available",
            "GET /providers_available",
            "GET /provider_models_configured"
        ],
        "timestamp": datetime.utcnow().isoformat()
    }
    
    return success_response(
        data=health_data,
        message="LLM service is healthy",
        meta={"request_id": request_id}
    )