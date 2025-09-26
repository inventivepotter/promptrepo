"""
Session refresh endpoint with standardized responses.
"""
import logging
from fastapi import APIRouter, Request, Response, Depends, status
from pydantic import BaseModel

from middlewares.rest import (
    StandardResponse,
    success_response,
    AuthenticationException,
    AppException
)
from api.deps import AuthServiceDep, SessionCookieDep
from services.auth.models import RefreshRequest, AuthError, SessionNotFoundError, TokenValidationError
from utils.cookie import set_session_cookie

logger = logging.getLogger(__name__)
router = APIRouter()



@router.post(
    "/refresh",
    response_model=StandardResponse[None],
    status_code=status.HTTP_200_OK,
    responses={
        401: {
            "description": "Authentication required",
            "content": {
                "application/json": {
                    "example": {
                        "status": "error",
                        "type": "/errors/authentication-required",
                        "title": "Authentication required",
                        "detail": "Invalid session token"
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
                        "detail": "Failed to refresh session"
                    }
                }
            }
        }
    },
    summary="Refresh session",
    description="Refresh session token to extend expiry"
)
async def refresh_session(
    request: Request,
    response: Response,
    token: SessionCookieDep,
    auth_service: AuthServiceDep
) -> StandardResponse[None]:
    """
    Refresh session token to extend expiry.
    
    Returns:
        StandardResponse[None]: Standardized response indicating success
    
    Raises:
        AuthenticationException: When session is invalid
        AppException: When refresh fails
    """
    request_id = getattr(request.state, "request_id", None)
    
    try:
        # Create refresh request using auth service models
        refresh_request = RefreshRequest(session_token=token)
        refresh_response = await auth_service.refresh_session(refresh_request)
        
        # Set the new encrypted session token in an HttpOnly, Secure cookie
        await set_session_cookie(response, refresh_response.session_token, refresh_response.expires_at)
        
        return success_response(
            data=None,
            message="Session refreshed successfully",
            meta={"request_id": request_id}
        )
        
    except SessionNotFoundError:
        raise AuthenticationException(message="Authentication required")
    except TokenValidationError:
        raise AuthenticationException(message="Authentication failed")
    except AuthError as e:
        logger.error(
            f"Auth error during refresh: {e}",
            extra={"request_id": request_id}
        )
        raise AppException(message=str(e))
    except Exception as e:
        logger.error(
            f"Unexpected error during refresh: {e}",
            exc_info=True,
            extra={"request_id": request_id}
        )
        raise AppException(message="Failed to refresh session")