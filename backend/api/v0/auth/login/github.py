"""
GitHub OAuth login initiation endpoint with standardized responses.
"""
import logging
from typing import Optional
from fastapi import APIRouter, Request, Query, status
from pydantic import BaseModel

from middlewares.rest import (
    StandardResponse,
    success_response,
    AppException,
    BadRequestException
)
from api.deps import AuthServiceDep
from services.auth.models import AuthError, AuthenticationFailedError, LoginRequest
from schemas.oauth_provider_enum import OAuthProvider

logger = logging.getLogger(__name__)
router = APIRouter()


class AuthUrlResponseData(BaseModel):
    authUrl: str


@router.get(
    "/github/",
    response_model=StandardResponse[AuthUrlResponseData],
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
    auth_service: AuthServiceDep,
    promptrepo_redirect_url: Optional[str] = Query(None, description="PromptRepo app URL to redirect after login")
) -> StandardResponse[AuthUrlResponseData]:
    """
    Start GitHub OAuth flow.
    Returns the GitHub OAuth authorization URL.
    
    Args:
        request: FastAPI request object
        auth_service: Auth service instance
        promptrepo_redirect_url: Optional PromptRepo app URL to redirect after login
        
    Returns:
        StandardResponse[AuthUrlResponseData]: Standardized response containing the auth URL
        
    Raises:
        AppException: When OAuth URL generation fails
    """
    request_id = getattr(request.state, "request_id", None)
    
    try:
        # Create login request with optional promptrepo redirect URL
        login_request = LoginRequest(
            provider=OAuthProvider.GITHUB,
            promptrepo_redirect_url=promptrepo_redirect_url
        )
        auth_url = await auth_service.initiate_oauth_login(request=login_request)

        return success_response(
            data=AuthUrlResponseData(authUrl=auth_url),
            message="GitHub authorization URL generated successfully",
            meta={"request_id": request_id, "provider": "github"}
        )
        
    except AuthenticationFailedError as e:
        logger.error(
            f"Authentication failed: {e}",
            extra={"request_id": request_id, "provider": "github"}
        )
        raise BadRequestException(str(e))
    except AuthError as e:
        logger.error(
            f"Auth error during login initiation: {e}",
            extra={"request_id": request_id, "provider": "github"}
        )
        raise AppException(message=str(e))
    except (BadRequestException, AppException):
        # Re-raise custom exceptions
        raise
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