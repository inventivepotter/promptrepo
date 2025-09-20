"""
GitHub OAuth login initiation endpoint with standardized responses.
"""
import logging
from fastapi import APIRouter, Request, status, Depends, Query
from pydantic import BaseModel, Field

from middlewares.rest import (
    StandardResponse,
    success_response,
    AppException,
    BadRequestException
)
from api.deps import get_oauth_service
from services.oauth.oauth_service import OAuthService
from services.oauth.models import ProviderNotFoundError, ConfigurationError

logger = logging.getLogger(__name__)
router = APIRouter()


class AuthUrlResponse(BaseModel):
    authUrl: str


@router.get(
    "/github/",
    response_model=StandardResponse[AuthUrlResponse],
    status_code=status.HTTP_200_OK,
    responses={
        400: {
            "description": "Bad request",
            "content": {
                "application/json": {
                    "example": {
                        "status": "error",
                        "type": "/errors/bad-request",
                        "title": "Bad request",
                        "detail": "Redirect URI parameter is required"
                    }
                }
            }
        },
        404: {
            "description": "Provider not found",
            "content": {
                "application/json": {
                    "example": {
                        "status": "error",
                        "type": "/errors/not-found",
                        "title": "Provider not found",
                        "detail": "OAuth provider 'github' is not supported"
                    }
                }
            }
        },
        503: {
            "description": "Service unavailable",
            "content": {
                "application/json": {
                    "example": {
                        "status": "error",
                        "type": "/errors/service-unavailable",
                        "title": "Service unavailable",
                        "detail": "OAuth provider is not properly configured"
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
                        "detail": "Failed to generate authentication URL"
                    }
                }
            }
        }
    },
    summary="Initiate GitHub OAuth login",
    description="Start GitHub OAuth flow and get authorization URL"
)
async def initiate_github_login(
    request: Request,
    redirect_uri: str = Query(..., description="Callback URL after authorization"),
    oauth_service: OAuthService = Depends(get_oauth_service)
) -> StandardResponse[AuthUrlResponse]:
    """
    Start GitHub OAuth flow.
    Returns the GitHub OAuth authorization URL.
    
    Args:
        request: FastAPI request object
        redirect_uri: Callback URL after authorization
        oauth_service: OAuth service instance
        
    Returns:
        StandardResponse[AuthUrlResponse]: Standardized response containing the auth URL
        
    Raises:
        BadRequestException: When redirect_uri is missing
        AppException: When OAuth URL generation fails
    """
    request_id = getattr(request.state, "request_id", None)
    
    # Clean up expired states
    oauth_service.cleanup_expired_states()
    
    try:
        # Validate redirect_uri
        if not redirect_uri or redirect_uri.strip() == "":
            raise BadRequestException("Redirect URI parameter is required")
        
        # Check if GitHub provider is available
        available_providers = oauth_service.get_available_providers()
        if "github" not in [p.lower() for p in available_providers]:
            raise BadRequestException(f"GitHub OAuth provider is not supported. Available providers: {', '.join(available_providers)}")
        
        # Generate authorization URL with default scopes
        auth_url_response = await oauth_service.get_authorization_url(
            provider="github",
            redirect_uri=redirect_uri
        )
        
        logger.info(
            "Generated GitHub OAuth URL",
            extra={
                "request_id": request_id,
                "provider": "github",
                "state": auth_url_response.state
            }
        )
        
        return success_response(
            data=AuthUrlResponse(authUrl=auth_url_response.auth_url),
            message="GitHub authorization URL generated successfully",
            meta={"request_id": request_id, "provider": "github"}
        )
        
    except (BadRequestException, ProviderNotFoundError, ConfigurationError):
        # Re-raise custom exceptions
        raise
    except ValueError as e:
        logger.error(
            f"OAuth service validation error: {e}",
            exc_info=True,
            extra={"request_id": request_id, "provider": "github"}
        )
        raise BadRequestException(str(e))
    except Exception as e:
        logger.error(
            f"Unexpected error generating GitHub auth URL: {e}",
            exc_info=True,
            extra={"request_id": request_id, "provider": "github"}
        )
        raise AppException(
            message="Failed to generate authentication URL",
            detail=str(e)
        )