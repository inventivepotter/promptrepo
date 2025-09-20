"""
API information endpoints.
"""
from fastapi import APIRouter, status
from pydantic import BaseModel

from middlewares.rest import.responses import StandardResponse, success_response

router = APIRouter()

class APIInfo(BaseModel):
    """API information model."""
    name: str
    version: str
    description: str
    documentation: dict
    endpoints: dict


@router.get(
    "/info",
    response_model=StandardResponse[APIInfo],
    status_code=status.HTTP_200_OK,
    tags=["info"],
    summary="API information",
    description="Get basic information about the API",
)
async def get_api_info() -> StandardResponse[APIInfo]:
    """
    Root endpoint with basic API information.
    """
    api_info = APIInfo(
        name="PromptRepo API",
        version="0.1.0",  # Consider fetching this from a central config
        description="Backend API for PromptRepo application with GitHub OAuth",
        documentation={
            "openapi": "/openapi.json",
            "swagger": "/docs",
            "redoc": "/redoc"
        },
        endpoints={
            "auth": "/api/v0/auth",
            "config": "/api/v0/config",
            "llm": "/api/v0/llm",
            "health": "/api/v0/health"
        }
    )
    
    return success_response(
        data=api_info,
        message="Welcome to PromptRepo API"
    )