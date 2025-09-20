"""
GitHub OAuth callback endpoint with standardized responses.
"""
import logging
from datetime import datetime, timedelta, UTC
from fastapi import APIRouter, Request, Depends, status
from pydantic import BaseModel
from sqlmodel import Session

from middlewares.rest import (
    StandardResponse,
    success_response,
    BadRequestException,
    AuthenticationException,
    AppException
)
from models.database import get_session
from models.user_sessions import User
from services import create_github_service
from services.session_service import SessionService
from services.user_service import UserService
from .login_github import oauth_states, cleanup_expired_states

logger = logging.getLogger(__name__)
router = APIRouter()


class LoginResponse(BaseModel):
    user: User
    sessionToken: str
    expiresAt: str


@router.get(
    "/callback/github",
    response_model=StandardResponse[LoginResponse],
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
        code: str,
        state: str,
        request: Request,
        db: Session = Depends(get_session)
) -> StandardResponse[LoginResponse]:
    """
    Handle GitHub OAuth callback.
    Exchange the authorization code for an access token and create user session.
    
    Returns:
        StandardResponse[LoginResponse]: Standardized response containing login data
    
    Raises:
        BadRequestException: When state parameter is invalid
        AppException: When authentication fails
    """
    request_id = getattr(request.state, "request_id", None)
    cleanup_expired_states()

    # Verify state parameter for CSRF protection
    if state not in oauth_states:
        logger.warning(
            f"Invalid or expired state parameter",
            extra={
                "request_id": request_id,
                "state": state
            }
        )
        raise BadRequestException(
            message="Invalid or expired state parameter",
            context={"state": state}
        )

    # Remove used state
    oauth_states.pop(state)

    try:
        # Create GitHub service
        github_service = create_github_service()

        async with github_service:
            # Exchange code for access token
            token_response = await github_service.exchange_code_for_token(
                code=code,
                state=state
            )

            # Get user information
            github_user = await github_service.get_user_info(token_response.access_token)

            # Get user's primary email
            primary_email = await github_service.get_primary_email(token_response.access_token)

            # Create or update user in database
            user_db = User(
                username=github_user.login,
                name=github_user.name or github_user.login,
                email=primary_email or "",
                avatar_url=github_user.avatar_url,
                github_id=github_user.id,
                html_url=github_user.html_url,
            )
            user_db = UserService.create_user(db=db, user=user_db)
            
            # Create session in database
            user_session = SessionService.create_session(
                db=db,
                username=github_user.login,
                oauth_token=token_response.access_token
            )

            # Calculate expiry time
            expires_at = datetime.now(UTC) + timedelta(hours=24)

            logger.info(
                f"Successfully authenticated user",
                extra={
                    "request_id": request_id,
                    "username": github_user.login
                }
            )

            return success_response(
                data=LoginResponse(
                    user=user_db,
                    sessionToken=user_session.session_id,
                    expiresAt=expires_at.isoformat() + "Z"
                ),
                message="User authenticated successfully",
                meta={"request_id": request_id}
            )

    except (BadRequestException, AuthenticationException, AppException):
        # Re-raise custom exceptions
        raise
    except Exception as e:
        logger.error(
            f"Unexpected error during OAuth callback: {e}",
            exc_info=True,
            extra={"request_id": request_id}
        )
        raise AppException(
            message="Authentication failed due to server error",
            detail=str(e)
        )