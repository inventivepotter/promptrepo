"""
Session refresh endpoint with standardized responses.
"""
import logging
from fastapi import APIRouter, Request, Depends, status
from pydantic import BaseModel
from sqlmodel import Session

from middlewares.rest import (
    StandardResponse,
    success_response,
    AuthenticationException,
    AppException
)
from models.database import get_session
from .verify import get_bearer_token
from api.deps import get_auth_service
from services.auth.auth_service import AuthService
from services.auth.models import RefreshRequest, AuthError, SessionNotFoundError, TokenValidationError

logger = logging.getLogger(__name__)
router = APIRouter()


class RefreshResponseData(BaseModel):
    sessionToken: str
    expiresAt: str


@router.post(
    "/refresh",
    response_model=StandardResponse[RefreshResponseData],
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
    token: str = Depends(get_bearer_token),
    db: Session = Depends(get_session),
    auth_service: AuthService = Depends(get_auth_service)
) -> StandardResponse[RefreshResponseData]:
    """
    Refresh session token to extend expiry.
    
    Returns:
        StandardResponse[RefreshResponseData]: Standardized response containing new session info
    
    Raises:
        AuthenticationException: When session is invalid
        AppException: When refresh fails
    """
    request_id = getattr(request.state, "request_id", None)
    
    try:
        # Create refresh request using auth service models
        refresh_request = RefreshRequest(session_token=token)
        refresh_response = await auth_service.refresh_session(refresh_request, db)
        
        return success_response(
            data=RefreshResponseData(
                sessionToken=refresh_response.session_token,
                expiresAt=refresh_response.expires_at
            ),
            message="Session refreshed successfully",
            meta={"request_id": request_id}
        )
        
    except SessionNotFoundError:
        raise AuthenticationException(message="Invalid session token")
    except TokenValidationError:
        raise AuthenticationException(message="Invalid OAuth token")
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