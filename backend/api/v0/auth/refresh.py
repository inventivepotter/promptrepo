"""
Session refresh endpoint with standardized responses.
"""
import logging
from datetime import datetime, timedelta, UTC
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
from services.session_service import SessionService
from .verify import get_bearer_token
from api.deps import get_oauth_service
from services.oauth.oauth_service import OAuthService

logger = logging.getLogger(__name__)
router = APIRouter()


class RefreshResponse(BaseModel):
    sessionToken: str
    expiresAt: str


@router.post(
    "/refresh",
    response_model=StandardResponse[RefreshResponse],
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
    oauth_service: OAuthService = Depends(get_oauth_service)
) -> StandardResponse[RefreshResponse]:
    """
    Refresh session token to extend expiry.
    
    Returns:
        StandardResponse[RefreshResponse]: Standardized response containing new session info
    
    Raises:
        AuthenticationException: When session is invalid
        AppException: When refresh fails
    """
    request_id = getattr(request.state, "request_id", None)
    
    # Check if current session exists and is valid
    user_session = SessionService.get_session_by_id(db, token)
    if not user_session:
        logger.warning(
            "Invalid session token for refresh",
            extra={
                "request_id": request_id,
                "session_token": token[:10] + "..."
            }
        )
        raise AuthenticationException(
            message="Invalid session token"
        )

    # Validate the OAuth token before creating a new session
    try:
        # Default to GitHub provider for backward compatibility
        provider = "github"
        is_valid = await oauth_service.validate_token(provider, user_session.oauth_token)
        
        if not is_valid:
            logger.warning(
                "Invalid OAuth token for refresh",
                extra={
                    "request_id": request_id,
                    "session_token": token[:10] + "...",
                    "provider": provider
                }
            )
            raise AuthenticationException(
                message="Invalid OAuth token"
            )
            
        # Create new session for the same user
        new_session = SessionService.create_session(
            db=db,
            username=user_session.username,
            oauth_token=user_session.oauth_token
        )

        # Delete old session
        SessionService.delete_session(db, token)

        # Calculate new expiry
        new_expires_at = datetime.now(UTC) + timedelta(hours=24)

        logger.info(
            "Session refreshed successfully",
            extra={
                "request_id": request_id,
                "username": user_session.username,
                "provider": provider
            }
        )

        return success_response(
            data=RefreshResponse(
                sessionToken=new_session.session_id,
                expiresAt=new_expires_at.isoformat() + "Z"
            ),
            message="Session refreshed successfully",
            meta={"request_id": request_id}
        )

    except AuthenticationException:
        raise
    except Exception as e:
        logger.error(
            f"Failed to refresh session: {e}",
            exc_info=True,
            extra={
                "request_id": request_id,
                "username": user_session.username
            }
        )
        raise AppException(
            message="Failed to refresh session",
            detail=str(e)
        )