"""
Logout endpoint with standardized responses.
"""
import logging
from fastapi import APIRouter, Request, Depends, status
from pydantic import BaseModel
from sqlmodel import Session

from middlewares.rest import (
    StandardResponse,
    success_response,
    AppException
)
from models.database import get_session
from services import create_github_service
from services.session_service import SessionService
from .verify import get_bearer_token

logger = logging.getLogger(__name__)
router = APIRouter()


class StatusResponse(BaseModel):
    status: str
    message: str


@router.post(
    "/logout",
    response_model=StandardResponse[StatusResponse],
    status_code=status.HTTP_200_OK,
    summary="Logout user",
    description="Logout user and invalidate session"
)
async def logout(
    request: Request,
    token: str = Depends(get_bearer_token),
    db: Session = Depends(get_session)
) -> StandardResponse[StatusResponse]:
    """
    Logout user and invalidate session.
    
    Returns:
        StandardResponse[StatusResponse]: Standardized response confirming logout
    """
    request_id = getattr(request.state, "request_id", None)
    user_session = SessionService.get_session_by_id(db, token)

    # Optionally revoke the GitHub token
    if user_session:
        try:
            github_service = create_github_service()
            async with github_service:
                await github_service.revoke_token(user_session.oauth_token)
        except Exception as e:
            logger.warning(
                f"Could not revoke GitHub token: {e}",
                extra={
                    "request_id": request_id,
                    "username": user_session.username if user_session else None
                }
            )
            # Continue with logout even if revocation fails

    # Delete session from database
    success = SessionService.delete_session(db, token)

    if success:
        logger.info(
            "User successfully logged out",
            extra={
                "request_id": request_id,
                "username": user_session.username if user_session else None
            }
        )

    return success_response(
        data=StatusResponse(
            status="success",
            message="Successfully logged out"
        ),
        message="User logged out successfully",
        meta={"request_id": request_id}
    )