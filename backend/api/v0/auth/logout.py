"""
Logout endpoint with standardized responses.
"""
import logging
from fastapi import APIRouter, Request, Response, Depends, status

from middlewares.rest import (
    StandardResponse,
    success_response,
    AppException,
    AuthenticationException
)
from api.deps import AuthServiceDep, SessionCookieDep
from services.auth.models import LogoutRequest, AuthError, SessionNotFoundError

logger = logging.getLogger(__name__)
router = APIRouter()


@router.post(
    "/logout",
    response_model=StandardResponse[dict],
    status_code=status.HTTP_200_OK,
    summary="Logout user",
    description="Logout user and invalidate session"
)
async def logout(
    request: Request,
    response: Response,
    auth_service: AuthServiceDep,
    token: SessionCookieDep,
) -> StandardResponse[dict]:
    """
    Logout user and invalidate session.
    
    Returns:
        StandardResponse[dict]: Standardized response confirming logout
    """
    request_id = getattr(request.state, "request_id", None)
    
    try:
        # Create logout request using auth service models
        logout_request = LogoutRequest(session_token=token)
        logout_response = await auth_service.logout(logout_request)
        
        # Clear the session cookie
        response.delete_cookie(
            key="sessionId",
            httponly=True,
            secure=True,
            samesite='lax'
        )
        
        return success_response(
            data={
                "status": logout_response.status,
                "message": logout_response.message
            },
            message="User logged out successfully",
            meta={"request_id": request_id}
        )
        
    except SessionNotFoundError:
        raise AuthenticationException(message="Session not found")
    except AuthError as e:
        logger.error(
            f"Auth error during logout: {e}",
            extra={"request_id": request_id}
        )
        raise AppException(message=str(e))
    except Exception as e:
        logger.error(
            f"Unexpected error during logout: {e}",
            exc_info=True,
            extra={"request_id": request_id}
        )
        raise AppException(message="Failed to logout")