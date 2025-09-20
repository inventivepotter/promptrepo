"""
Global authentication utilities for the 
"""
from fastapi import HTTPException, Depends, Header
from sqlmodel import Session
from typing import Annotated

from models.database import get_session
from services.session_service import SessionService


async def get_bearer_token(authorization: Annotated[str | None, Header()] = None) -> str:
    """Extract Bearer token from Authorization header."""
    if not authorization:
        raise HTTPException(
            status_code=401,
            detail="Authorization header required"
        )

    if not authorization.startswith("Bearer "):
        raise HTTPException(
            status_code=401,
            detail="Invalid authorization header format"
        )

    return authorization.replace("Bearer ", "")


async def verify_session(
    token: str = Depends(get_bearer_token), 
    db: Session = Depends(get_session)
) -> str:
    """Verify session token and return username."""
    if not SessionService.is_session_valid(db, token):
        raise HTTPException(
            status_code=401,
            detail="Invalid or expired session token"
        )
    
    user_session = SessionService.get_session_by_id(db, token)
    if not user_session:
        raise HTTPException(
            status_code=401,
            detail="Session not found"
        )
    
    return user_session.username