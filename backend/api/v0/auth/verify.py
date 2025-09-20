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
from api.deps import get_auth_service
from services.auth.auth_service import AuthService
from services.auth.models import VerifyRequest, AuthError, SessionNotFoundError, TokenValidationError

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
    auth_service: AuthService = Depends(get_auth_service)
) -> StandardResponse[User]:
    """
    Verify current session and return user information.
    
    Returns:
        StandardResponse[User]: Standardized response containing user data
    
    Raises:
        AuthenticationException: When session is invalid or expired
    """
    request_id = getattr(request.state, "request_id", None)
    
    try:
        # Create verify request using auth service models
        verify_request = VerifyRequest(session_token=token)
        verify_response = await auth_service.verify_session(verify_request, db)
        
        return success_response(
            data=verify_response.user,
            message="Session verified successfully",
            meta={"request_id": request_id}
        )
        
    except SessionNotFoundError:
        raise AuthenticationException(message="Invalid or expired session token")
    except TokenValidationError:
        raise AuthenticationException(message="OAuth token has been revoked")
    except AuthError as e:
        logger.error(
            f"Auth error during verification: {e}",
            extra={"request_id": request_id}
        )
        raise AppException(message=str(e))
    except Exception as e:
        logger.error(
            f"Unexpected error during verification: {e}",
            exc_info=True,
            extra={"request_id": request_id}
        )
        raise AppException(message="Failed to verify session")