"""
OAuth Data Models

This module contains Pydantic database.models for all OAuth-related data structures,
ensuring type safety and consistent data validation across the OAuth service.
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel, Field, field_validator, ConfigDict
from datetime import datetime, timedelta, UTC
from enum import Enum


class OAuthProvider(str, Enum):
    """Supported OAuth providers"""
    GITHUB = "github"
    GITLAB = "gitlab"
    BITBUCKET = "bitbucket"


class OAuthToken(BaseModel):
    """OAuth token response model"""
    access_token: str = Field(..., description="OAuth access token")
    token_type: str = Field(default="bearer", description="Token type")
    scope: Optional[str] = Field(default=None, description="Granted scopes")
    refresh_token: Optional[str] = Field(default=None, description="Refresh token")
    expires_in: Optional[int] = Field(default=None, description="Token expiration in seconds")
    created_at: Optional[datetime] = Field(default_factory=lambda: datetime.now(UTC), description="Token creation timestamp")
    
    @property
    def expires_at(self) -> Optional[datetime]:
        """Calculate token expiration datetime"""
        if self.expires_in and self.created_at:
            return self.created_at + timedelta(seconds=self.expires_in)
        return None
    
    @property
    def is_expired(self) -> bool:
        """Check if token is expired"""
        if not self.expires_at:
            return False
        return datetime.now(UTC) > self.expires_at
    
    model_config = ConfigDict(
        json_encoders={
            datetime: lambda v: v.isoformat()
        }
    )


class UserInfo(BaseModel):
    """User information from OAuth provider"""
    id: str = Field(..., description="Unique user identifier")
    username: str = Field(..., description="Username/handle")
    name: Optional[str] = Field(default=None, description="Full name")
    email: Optional[str] = Field(default=None, description="Primary email")
    avatar_url: Optional[str] = Field(default=None, description="Profile picture URL")
    profile_url: Optional[str] = Field(default=None, description="Profile URL")
    provider: OAuthProvider = Field(..., description="OAuth provider")
    raw_data: Optional[Dict[str, Any]] = Field(default=None, description="Raw provider response")
    
    model_config = ConfigDict(
        use_enum_values=True
    )


class UserEmail(BaseModel):
    """User email address model"""
    email: str = Field(..., description="Email address")
    primary: bool = Field(default=False, description="Is this the primary email?")
    verified: bool = Field(default=False, description="Is this email verified?")
    visibility: Optional[str] = Field(default=None, description="Email visibility setting")
    
    @field_validator('email')
    @classmethod
    def validate_email(cls, v):
        """Validate email format"""
        if '@' not in v:
            raise ValueError('Invalid email format')
        return v.lower()


class AuthUrlResponse(BaseModel):
    """Authorization URL response"""
    auth_url: str = Field(..., description="OAuth authorization URL")
    provider: str = Field(..., description="OAuth provider name")
    state: str = Field(..., description="CSRF protection state")


class LoginResponse(BaseModel):
    """Login response after successful OAuth"""
    user: UserInfo = Field(..., description="User information")
    access_token: str = Field(..., description="Session access token")
    refresh_token: Optional[str] = Field(default=None, description="Session refresh token")
    expires_at: Optional[datetime] = Field(default=None, description="Session expiration")
    provider: str = Field(..., description="OAuth provider used for login")
    
    model_config = ConfigDict(
        json_encoders={
            datetime: lambda v: v.isoformat()
        }
    )


class OAuthError(Exception):
    """Base OAuth error"""
    def __init__(self, message: str, provider: Optional[str] = None):
        self.message = message
        self.provider = provider
        super().__init__(self.message)


class ProviderNotFoundError(OAuthError):
    """Raised when OAuth provider is not found"""
    def __init__(self, provider: str):
        super().__init__(f"OAuth provider not found: {provider}", provider)


class InvalidStateError(OAuthError):
    """Raised when OAuth state is invalid or expired"""
    def __init__(self, state: str, provider: Optional[str] = None):
        super().__init__(f"Invalid or expired OAuth state: {state}", provider)


class TokenExchangeError(OAuthError):
    """Raised when token exchange fails"""
    def __init__(self, message: str, provider: Optional[str] = None, error_code: Optional[str] = None):
        self.error_code = error_code
        super().__init__(message, provider)


class ConfigurationError(OAuthError):
    """Raised when OAuth configuration is invalid"""
    def __init__(self, message: str, provider: Optional[str] = None):
        super().__init__(message, provider)


class OAuthState(BaseModel):
    """OAuth state for CSRF protection"""
    state: str = Field(..., description="State token")
    provider: str = Field(..., description="OAuth provider")
    redirect_uri: str = Field(..., description="Redirect URI")
    scopes: List[str] = Field(default_factory=list, description="Requested scopes")
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC), description="Creation timestamp")
    metadata: Optional[Dict[str, Any]] = Field(default=None, description="Additional metadata")
    
    @property
    def is_expired(self) -> bool:
        """Check if state is expired (10 minutes)"""
        return datetime.now(UTC) - self.created_at > timedelta(minutes=10)
    
    model_config = ConfigDict(
        json_encoders={
            datetime: lambda v: v.isoformat()
        }
    )


class ProviderConfig(BaseModel):
    """OAuth provider configuration"""
    provider: str = Field(..., description="Provider name")
    client_id: str = Field(..., description="OAuth client ID")
    client_secret: str = Field(..., description="OAuth client secret")
    scopes: List[str] = Field(default_factory=list, description="Default scopes")
    auth_url: Optional[str] = Field(default=None, description="Authorization endpoint")
    token_url: Optional[str] = Field(default=None, description="Token endpoint")
    user_info_url: Optional[str] = Field(default=None, description="User info endpoint")
    emails_url: Optional[str] = Field(default=None, description="Emails endpoint")
    
    @field_validator('client_id', 'client_secret')
    @classmethod
    def validate_credentials(cls, v):
        """Validate that credentials are not empty"""
        if not v or v.strip() == "":
            raise ValueError("Credential cannot be empty")
        return v