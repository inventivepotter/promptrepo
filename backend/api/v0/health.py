"""
Health check endpoints.
"""
from fastapi import APIRouter, status
from pydantic import BaseModel
import os

from middlewares.rest.responses import StandardResponse, success_response

router = APIRouter()

class HealthResponse(BaseModel):
    """Health check response model."""
    status: str
    message: str
    version: str
    environment: str


@router.get(
    "/health",
    response_model=StandardResponse[HealthResponse],
    status_code=status.HTTP_200_OK,
    tags=["monitoring"],
    summary="Health check",
    description="Check if the API is running and healthy",
)
async def health_check() -> StandardResponse[HealthResponse]:
    """
    Health check endpoint to verify the API is running.
    """
    health_data = HealthResponse(
        status="healthy",
        message="PromptRepo API is running successfully",
        version="0.1.0",  # Consider fetching this from a central config
        environment=os.getenv("ENVIRONMENT", "development")
    )
    
    return success_response(
        data=health_data,
        message="Service is healthy"
    )