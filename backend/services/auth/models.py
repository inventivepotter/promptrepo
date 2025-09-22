"""
Authentication Data Models

This module contains Pydantic database.models for authentication-related data structures,
ensuring type safety and consistent data validation across the auth service.
"""

from typing import Optional
from pydantic import BaseModel, Field
from datetime import datetime
from database.models.user import User


class LoginRequest(BaseModel):
    """Request model for OAuth login initiation"""
    provider: str = Field(..., description="OAuth provider name (e.g., 'github')")
    redirect_uri: str = Field(..., description="Callback URL after authorization")


class LoginResponse(BaseModel):
    """Response model for successful OAuth callback"""
    user: User = Field(..., description="User information")
    session_token: str = Field(..., description="Session token")
    expires_at: str = Field(..., description="Session expiration time (ISO format)")


class LogoutRequest(BaseModel):
    """Request model for logout operation"""
    session_token: str = Field(..., description="Session token to invalidate")


class LogoutResponse(BaseModel):
    """Response model for logout operation"""
    status: str = Field(..., description="Operation status")
    message: str = Field(..., description="Status message")


class RefreshRequest(BaseModel):
    """Request model for session refresh"""
    session_token: str = Field(..., description="Current session token")


class RefreshResponse(BaseModel):
    """Response model for session refresh"""
    session_token: str = Field(..., description="New session token")
    expires_at: str = Field(..., description="New expiration time (ISO format)")


class VerifyRequest(BaseModel):
    """Request model for session verification"""
    session_token: str = Field(..., description="Session token to verify")


class VerifyResponse(BaseModel):
    """Response model for session verification"""
    user: User = Field(..., description="User information")
    is_valid: bool = Field(..., description="Whether session is valid")


class AuthError(Exception):
    """Base authentication error"""
    def __init__(self, message: str, context: Optional[dict] = None):
        self.message = message
        self.context = context or {}
        super().__init__(self.message)


class AuthenticationFailedError(AuthError):
    """Raised when authentication fails"""
    def __init__(self, message: str = "Authentication failed", context: Optional[dict] = None):
        super().__init__(message, context)


class SessionNotFoundError(AuthError):
    """Raised when session is not found or invalid"""
    def __init__(self, message: str = "Session not found", context: Optional[dict] = None):
        super().__init__(message, context)


class TokenValidationError(AuthError):
    """Raised when token validation fails"""
    def __init__(self, message: str = "Token validation failed", context: Optional[dict] = None):
        super().__init__(message, context)


class OAuthTokenUserInfo(BaseModel):
    """Response model for OAuth token and user info"""
    oauth_token: str = Field(..., description="OAuth access token")
    oauth_provider: str = Field(..., description="OAuth provider name")
    user_id: str = Field(..., description="User ID")
    username: str = Field(..., description="Username")
    name: Optional[str] = Field(None, description="User's display name")