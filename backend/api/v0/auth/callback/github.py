"""
GitHub OAuth callback endpoint with standardized responses.
"""
import logging
from datetime import datetime, timedelta, UTC
from fastapi import APIRouter, Request, Depends, status, Query
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
from models.user import User
from api.deps import get_oauth_service
from services.oauth.oauth_service import OAuthService
from services.oauth.models import (
    OAuthToken, 
    UserInfo, 
    UserEmail, 
    InvalidStateError,
    TokenExchangeError,
    ProviderNotFoundError
)
from services.session_service import SessionService
from services.user_service import UserService

logger = logging.getLogger(__name__)
router = APIRouter()


class LoginResponse(BaseModel):
    user: User
    sessionToken: str
    expiresAt: str


@router.get(
    "/github/",
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
    code: str = Query(..., description="Authorization code from GitHub"),
    state: str = Query(..., description="State parameter for CSRF verification"),
    redirect_uri: str = Query(..., description="Redirect URI used in initial request"),
    db: Session = Depends(get_session),
    oauth_service: OAuthService = Depends(get_oauth_service)
) -> StandardResponse[LoginResponse]:
    """
    Handle GitHub OAuth callback.
    Exchange the authorization code for an access token and create user session.
    
    Args:
        code: Authorization code from GitHub
        state: State parameter for CSRF verification
        redirect_uri: Redirect URI used in initial request
        request: FastAPI request object
        db: Database session
        oauth_service: OAuth service instance
        
    Returns:
        StandardResponse[LoginResponse]: Standardized response containing login data
        
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
        
        if not redirect_uri or redirect_uri.strip() == "":
            raise BadRequestException("Redirect URI parameter is required")
        
        # Exchange code for token
        token_response = await oauth_service.exchange_code_for_token(
            provider="github",
            code=code,
            redirect_uri=redirect_uri,
            state=state
        )
        
        # Get user information
        user_info = await oauth_service.get_user_info(
            provider="github",
            access_token=token_response.access_token
        )
        
        # Get user's primary email
        primary_email = None
        try:
            emails = await oauth_service.get_user_emails(
                provider="github",
                access_token=token_response.access_token
            )
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
                f"Failed to get user emails from GitHub: {e}",
                extra={"request_id": request_id, "provider": "github"}
            )
        
        # Create user object based on GitHub data
        user_data = {
            "username": user_info.username,
            "name": user_info.name or user_info.username,
            "email": primary_email or user_info.email or "",
            "avatar_url": user_info.avatar_url,
            "html_url": user_info.profile_url,
            "github_id": int(user_info.id)
        }
        
        # Create or update user in database
        user_db = User(**user_data)
        user_db = UserService.create_user(db=db, user=user_db)
        
        # Create session in database
        user_session = SessionService.create_session(
            db=db,
            username=user_info.username,
            oauth_token=token_response.access_token
        )
        
        # Calculate expiry time
        expires_at = datetime.now(UTC) + timedelta(hours=24)
        
        logger.info(
            "Successfully authenticated user with GitHub",
            extra={
                "request_id": request_id,
                "username": user_info.username,
                "provider": "github"
            }
        )
        
        # Manually create user dict to ensure all fields are included
        user_dict = {
            "id": user_db.id,
            "username": user_db.username,
            "name": user_db.name,
            "email": user_db.email,
            "avatar_url": user_db.avatar_url,
            "github_id": user_db.github_id,
            "html_url": user_db.html_url,
            "created_at": user_db.created_at.isoformat() + "Z" if user_db.created_at else None,
            "modified_at": user_db.modified_at.isoformat() + "Z" if user_db.modified_at else None
        }
        
        response_data = {
            "user": user_dict,
            "sessionToken": user_session.session_id,
            "expiresAt": expires_at.isoformat() + "Z"
        }
        
        return success_response(
            data=response_data,
            message="User authenticated successfully",
            meta={"request_id": request_id, "provider": "github"}
        )
        
    except (InvalidStateError, TokenExchangeError, ProviderNotFoundError) as e:
        logger.error(
            f"GitHub authentication error: {e}",
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