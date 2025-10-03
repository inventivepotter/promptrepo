"""
Session verification endpoint with standardized responses.
"""
import logging
from fastapi import APIRouter, Request, Depends, status

from middlewares.rest import (
    StandardResponse,
    success_response,
    AuthenticationException,
    AppException
)
from database.models.user import User
from api.deps import AuthServiceDep, SessionCookieDep
from services.auth.models import VerifyRequest, AuthError, SessionNotFoundError, TokenValidationError

logger = logging.getLogger(__name__)
router = APIRouter()

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
    token: SessionCookieDep,
    auth_service: AuthServiceDep
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
        verify_response = await auth_service.verify_session(verify_request)
        
        return success_response(
            data=verify_response.user,
            message="Session verified successfully",
            meta={"request_id": request_id}
        )
        
    except SessionNotFoundError:
        raise AuthenticationException(message="Authentication required")
    except TokenValidationError:
        raise AuthenticationException(message="Authentication failed")
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