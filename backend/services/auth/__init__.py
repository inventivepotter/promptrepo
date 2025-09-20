"""
Authentication Services

This module provides authentication services including login, logout,
refresh, and verification operations with OAuth integration.
"""

from .auth_service import AuthService
from .session_service import SessionService
from .models import (
    LoginRequest,
    LoginResponse,
    LogoutRequest,
    LogoutResponse,
    RefreshRequest,
    RefreshResponse,
    VerifyRequest,
    VerifyResponse,
    AuthError,
    AuthenticationFailedError,
    SessionNotFoundError,
    TokenValidationError
)

__all__ = [
    "AuthService",
    "LoginRequest",
    "LoginResponse",
    "LogoutRequest",
    "LogoutResponse",
    "RefreshRequest",
    "RefreshResponse",
    "VerifyRequest",
    "VerifyResponse",
    "AuthError",
    "AuthenticationFailedError",
    "SessionNotFoundError",
    "TokenValidationError"
]