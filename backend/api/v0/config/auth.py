"""
Shared authentication utilities for config endpoints.
"""
from fastapi import HTTPException, status, Header, Depends
from pydantic import BaseModel
from typing import Annotated
from sqlmodel import Session

from models.database import get_session
from services.session_service import SessionService


async def get_bearer_token(authorization: Annotated[str | None, Header()] = None) -> str | None:
    """Extract Bearer token from Authorization header, returns None if not present."""
    if not authorization:
        return None

    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authorization header format"
        )

    return authorization.replace("Bearer ", "")


async def get_current_user(
    token: str = Depends(get_bearer_token), 
    db: Session = Depends(get_session)
) -> dict:
    """Get current authenticated user from session token."""
    # Check if session exists and is valid
    if not SessionService.is_session_valid(db, token):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired session token"
        )

    user_session = SessionService.get_session_by_id(db, token)
    if not user_session:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Session not found"
        )

    return {
        "username": user_session.username,
        "session_id": user_session.session_id,
        "oauth_token": user_session.oauth_token
    }