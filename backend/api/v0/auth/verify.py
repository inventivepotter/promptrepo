"""
Session verification endpoint with standardized responses.
"""
import logging
from typing import Annotated
from fastapi import APIRouter, Request, Depends, status, Header
from sqlmodel import Session

from middlewares.rest import (
    StandardResponse,
    success_response,
    AuthenticationException,
    AppException
)
from models.database import get_session
from models.user import User
from services.session_service import SessionService
from services.user_service import UserService
from api.deps import get_oauth_service
from services.oauth.oauth_service import OAuthService
from services.oauth.models import UserInfo, UserEmail

logger = logging.getLogger(__name__)
router = APIRouter()


# Dependency to extract Bearer token
async def get_bearer_token(authorization: Annotated[str | None, Header()] = None) -> str:
    """Extract Bearer token from Authorization header."""
    if not authorization:
        raise AuthenticationException(
            message="Authorization header required",
            context={"header": "Authorization"}
        )

    if not authorization.startswith("Bearer "):
        raise AuthenticationException(
            message="Invalid authorization header format",
            context={"expected_format": "Bearer <token>"}
        )

    return authorization.replace("Bearer ", "")


@router.get(
    "/verify",
    response_model=StandardResponse[User],
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
                        "detail": "Invalid or expired session token"
                    }
                }
            }
        }
    },
    summary="Verify session",
    description="Verify current session and return user information"
)
async def verify_session(
    request: Request,
    token: str = Depends(get_bearer_token),
    db: Session = Depends(get_session),
    oauth_service: OAuthService = Depends(get_oauth_service)
) -> StandardResponse[User]:
    """
    Verify current session and return user information.
    
    Returns:
        StandardResponse[User]: Standardized response containing user data
    
    Raises:
        AuthenticationException: When session is invalid or expired
    """
    request_id = getattr(request.state, "request_id", None)
    
    # Default to GitHub provider for backward compatibility
    provider = "github"
    
    # Check if session exists and is valid
    if not SessionService.is_session_valid(db, token):
        logger.warning(
            "Invalid or expired session token",
            extra={
                "request_id": request_id,
                "session_token": token[:10] + "..."
            }
        )
        raise AuthenticationException(
            message="Invalid or expired session token"
        )

    user_session = SessionService.get_session_by_id(db, token)
    if not user_session:
        logger.warning(
            "Session not found",
            extra={
                "request_id": request_id,
                "session_token": token[:10] + "..."
            }
        )
        raise AuthenticationException(
            message="Session not found"
        )

    # Try to validate OAuth token and get fresh user info
    try:
        # Validate OAuth token
        if not await oauth_service.validate_token(provider, user_session.oauth_token):
            # OAuth token is invalid, delete session
            SessionService.delete_session(db, token)
            logger.warning(
                "OAuth token has been revoked",
                extra={
                    "request_id": request_id,
                    "username": user_session.username,
                    "provider": provider
                }
            )
            raise AuthenticationException(
                message="OAuth token has been revoked"
            )

        # Get fresh user info from OAuth provider
        oauth_user_info = await oauth_service.get_user_info(provider, user_session.oauth_token)
        
        # Get user's primary email
        primary_email = None
        try:
            emails = await oauth_service.get_user_emails(provider, user_session.oauth_token)
            # Find primary email
            primary_email = next(
                (email.email for email in emails if email.primary and email.verified),
                None
            )
            # If no primary verified email, use the first verified one
            if not primary_email:
                primary_email = next(
                    (email.email for email in emails if email.verified),
                    None
                )
        except Exception as e:
            logger.warning(
                f"Failed to get user emails from OAuth provider: {e}",
                extra={
                    "request_id": request_id,
                    "username": user_session.username,
                    "provider": provider
                }
            )

        # Get or create/update user in database
        user_db = User(
            username=oauth_user_info.username,
            name=oauth_user_info.name or oauth_user_info.username,
            email=primary_email or oauth_user_info.email or "",
            avatar_url=oauth_user_info.avatar_url,
            github_id=int(oauth_user_info.id) if provider == "github" and oauth_user_info.id else None,
            html_url=oauth_user_info.profile_url,
        )
        user_db = UserService.create_user(db=db, user=user_db)
        
        logger.info(
            "Session verified successfully",
            extra={
                "request_id": request_id,
                "username": oauth_user_info.username,
                "provider": provider
            }
        )
        
        return success_response(
            data=user_db,
            message="Session verified successfully",
            meta={"request_id": request_id}
        )
    except AuthenticationException:
        raise
    except Exception as e:
        logger.warning(
            f"Could not validate OAuth token for session: {e}",
            extra={
                "request_id": request_id,
                "session_token": token[:10] + "...",
                "provider": provider
            }
        )
        
        # Try to get user from database if OAuth validation fails
        from models.user import User as UserModel
        user = db.query(UserModel).filter_by(username=user_session.username).first()
        
        if user:
            return success_response(
                data=user,
                message="Session verified (offline mode)",
                meta={"request_id": request_id}
            )
        else:
            # Create minimal user object if not found
            user_db = User(
                username=user_session.username,
                name=user_session.username,
                email="",
                avatar_url="",
                github_id=None,
                html_url=""
            )
            
            return success_response(
                data=user_db,
                message="Session verified (minimal info)",
                meta={"request_id": request_id}
            )