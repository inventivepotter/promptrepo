"""
GitHub OAuth callback endpoint with standardized responses.
"""
import logging
from typing import Optional
from fastapi import APIRouter, Request, status, Query
from pydantic import BaseModel

from middlewares.rest import (
    StandardResponse,
    success_response,
    BadRequestException,
    AuthenticationException,
    AppException
)
from database.models.user import User
from api.deps import AuthServiceDep, DBSession
from services.auth import AuthError, AuthenticationFailedError
from services.oauth.enums import OAuthProvider

logger = logging.getLogger(__name__)
router = APIRouter()


class LoginResponseData(BaseModel):
    user: User
    sessionToken: str
    expiresAt: str
    promptrepoRedirectUrl: Optional[str] = None


@router.get(
    "/github/",
    response_model=StandardResponse[LoginResponseData],
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
                        "detail": "Invalid or expired state parameter"
                    }
                }
            }
        },
        401: {
            "description": "Authentication failed",
            "content": {
                "application/json": {
                    "example": {
                        "status": "error",
                        "type": "/errors/authentication-failed",
                        "title": "Authentication failed",
                        "detail": "Failed to exchange authorization code for token"
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
                        "detail": "Authentication failed due to server error"
                    }
                }
            }
        }
    },
    summary="GitHub OAuth callback",
    description="Handle GitHub OAuth callback and create user session"
)
async def github_oauth_callback(
    request: Request,
    auth_service: AuthServiceDep,
    code: str = Query(..., description="Authorization code from GitHub"),
    state: str = Query(..., description="State parameter for CSRF verification"),
) -> StandardResponse[LoginResponseData]:
    """
    Handle GitHub OAuth callback.
    Exchange the authorization code for an access token and create user session.
    
    Args:
        code: Authorization code from GitHub
        state: State parameter for CSRF verification
        request: FastAPI request object
        db: Database session
        auth_service: Auth service instance
        
    Returns:
        StandardResponse[LoginResponseData]: Standardized response containing login data
        
    Raises:
        BadRequestException: When state parameter is invalid
        AppException: When authentication fails
    """
    request_id = getattr(request.state, "request_id", None)
    
    try:
        # Validate parameters
        if not code or code.strip() == "":
            raise BadRequestException("Authorization code is required")
        
        if not state or state.strip() == "":
            raise BadRequestException("State parameter is required")
        
        # Handle OAuth callback using auth service
        login_response = await auth_service.handle_oauth_callback(
            provider=OAuthProvider.GITHUB,
            code=code,
            state=state
        )
        
        # Convert response to expected format
        response_data = LoginResponseData(
            user=login_response.user,
            sessionToken=login_response.session_token,
            expiresAt=login_response.expires_at,
            promptrepoRedirectUrl=login_response.promptrepo_redirect_url
        )
        
        return success_response(
            data=response_data,
            message="User authenticated successfully",
            meta={
                "request_id": request_id,
                "provider": OAuthProvider.GITHUB,
                "has_promptrepo_redirect": login_response.promptrepo_redirect_url is not None
            }
        )
        
    except AuthenticationFailedError as e:
        logger.error(
            f"GitHub authentication error: {e}",
            extra={"request_id": request_id, "provider": "github"}
        )
        raise AuthenticationException(message=str(e))
    except AuthError as e:
        logger.error(
            f"Auth error during callback: {e}",
            extra={"request_id": request_id, "provider": "github"}
        )
        raise BadRequestException(str(e))
    except (BadRequestException, AuthenticationException, AppException):
        # Re-raise custom exceptions
        raise
    except Exception as e:
        logger.error(
            f"Unexpected error during GitHub OAuth callback: {e}",
            exc_info=True,
            extra={"request_id": request_id, "provider": "github"}
        )
        raise AppException(
            message="Authentication failed due to server error",
            detail=str(e)
        )