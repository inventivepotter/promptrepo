"""
Authentication Service Implementation

This module provides the main authentication service that orchestrates
authentication operations including OAuth login, logout, refresh, and verification.
"""

import logging
from datetime import datetime, timedelta, UTC
from sqlmodel import Session

from services.git_provider import GitProviderService
from .session_service import SessionService
from database.daos.user import UserDAO
from database.models.user import User
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

logger = logging.getLogger(__name__)


class AuthService:
    """
    Main authentication service handling all auth operations.
    
    This service orchestrates authentication flows, handling OAuth integration,
    session management, and user verification operations.
    """
    
    def __init__(self, db: Session, git_provider_service: GitProviderService, session_service: SessionService):
        """
        Initialize the authentication service.
        
        Args:
            db: Database session
            git_provider_service: OAuth service instance for OAuth operations
            session_service: Session service instance for session management
        """
        self.db = db
        self.git_provider_service = git_provider_service
        self.session_service = session_service
    
    async def initiate_oauth_login(
        self,
        request: LoginRequest,
    ) -> str:
        """
        Initiate OAuth login flow.
        
        Args:
            request: Login request containing provider and redirect URI
            
        Returns:
            Authorization URL for OAuth flow
            
        Raises:
            AuthenticationFailedError: If login initiation fails
        """
        try:
            # Validate provider availability
            available_providers = self.git_provider_service.get_available_providers()
            if request.provider not in [p.lower() for p in available_providers]:
                raise AuthenticationFailedError(
                    f"OAuth provider '{request.provider}' is not supported. Available providers: {', '.join(available_providers)}",
                    context={"provider": request.provider, "available_providers": available_providers}
                )
            
            # Clean up expired states
            self.git_provider_service.cleanup_expired_states()
            
            # Generate authorization URL
            auth_url_response = await self.git_provider_service.get_authorization_url(
                provider=request.provider,
                redirect_uri=request.redirect_uri
            )
            
            logger.info(
                f"Generated {request.provider} OAuth URL",
                extra={
                    "provider": request.provider,
                    "state": auth_url_response.state
                }
            )
            
            return auth_url_response.auth_url
            
        except Exception as e:
            logger.error(f"Failed to initiate OAuth login: {e}", exc_info=True)
            raise AuthenticationFailedError(f"Failed to generate authentication URL: {str(e)}")
    
    async def handle_oauth_callback(
        self,
        provider: str,
        code: str,
        state: str,
        redirect_uri: str,
    ) -> LoginResponse:
        """
        Handle OAuth callback and create user session.
        
        Args:
            provider: OAuth provider name
            code: Authorization code from callback
            state: State parameter for CSRF verification
            redirect_uri: Redirect URI used in initial request
            
        Returns:
            Login response with user and session information
            
        Raises:
            AuthenticationFailedError: If callback handling fails
        """
        try:
            # Exchange code for token
            token_response = await self.git_provider_service.exchange_code_for_token(
                provider=provider,
                code=code,
                redirect_uri=redirect_uri,
                state=state
            )
            
            # Get user information
            user_info = await self.git_provider_service.get_user_info(
                provider=provider,
                access_token=token_response.access_token
            )
            
            # Get user's primary email
            primary_email = None
            try:
                emails = await self.git_provider_service.get_user_emails(
                    provider=provider,
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
                logger.warning(f"Failed to get user emails from {provider}: {e}")
            
            # Create user object based on OAuth data
            user_data = {
                "username": user_info.username,
                "name": user_info.name or user_info.username,
                "email": primary_email or user_info.email or "",
                "avatar_url": user_info.avatar_url,
                "html_url": user_info.profile_url,
                "github_id": int(user_info.id) if provider == "github" and user_info.id else None
            }
            
            # Create or update user in database
            user_service = UserDAO(self.db)
            user = User(**user_data)
            user_db = user_service.save_user(user_data=user)
            
            # Create session in database
            user_session = self.session_service.create_session(
                user_id=user_db.id,
                oauth_token=token_response.access_token
            )
            
            # Calculate expiry time
            expires_at = datetime.now(UTC) + timedelta(hours=24)
            
            logger.info(
                f"Successfully authenticated user with {provider}",
                extra={
                    "username": user_info.username,
                    "provider": provider
                }
            )
            
            return LoginResponse(
                user=user_db,
                session_token=user_session.session_id,
                expires_at=expires_at.isoformat() + "Z"
            )
            
        except Exception as e:
            logger.error(f"Failed to handle OAuth callback: {e}", exc_info=True)
            raise AuthenticationFailedError(f"Authentication failed: {str(e)}")
    
    async def logout(
        self,
        request: LogoutRequest,
    ) -> LogoutResponse:
        """
        Logout user and invalidate session.
        
        Args:
            request: Logout request containing session token
            
        Returns:
            Logout response confirming operation
            
        Raises:
            SessionNotFoundError: If session is not found
        """
        try:
            user_session = self.session_service.get_session_by_id(request.session_token)
            
            # Optionally revoke the OAuth token
            if user_session:
                # Infer provider from user data if available, otherwise default to github
                provider = user_session.user.oauth_provider if user_session and user_session.user and user_session.user.oauth_provider else "github"
                try:
                    await self.git_provider_service.revoke_token(provider, user_session.oauth_token)
                except Exception as e:
                    logger.warning(
                        f"Could not revoke OAuth token: {e}",
                        extra={
                            "username": user_session.user.username if user_session else None,
                            "provider": provider
                        }
                    )
                    # Continue with logout even if revocation fails
            
            # Delete session from database
            success = self.session_service.delete_session(request.session_token)
            
            if success:
                logger.info(
                    "User successfully logged out",
                    extra={
                        "username": user_session.user.username if user_session else None
                    }
                )
            
            return LogoutResponse(
                status="success",
                message="Successfully logged out"
            )
            
        except Exception as e:
            logger.error(f"Failed to logout: {e}", exc_info=True)
            raise AuthError(f"Logout failed: {str(e)}")
    
    async def refresh_session(
        self,
        request: RefreshRequest,
    ) -> RefreshResponse:
        """
        Refresh session token to extend expiry.
        
        Args:
            request: Refresh request containing current session token
            
        Returns:
            Refresh response with new session information
            
        Raises:
            SessionNotFoundError: If session is not found
            TokenValidationError: If token validation fails
        """
        try:
            # Check if current session exists and is valid
            user_session = self.session_service.get_session_by_id(request.session_token)
            if not user_session:
                raise SessionNotFoundError("Invalid session token")
            
            # Infer provider from user data if available, otherwise default to github
            provider = user_session.user.oauth_provider if user_session and user_session.user and user_session.user.oauth_provider else "github"
            # Validate the OAuth token before creating a new session
            is_valid = await self.git_provider_service.validate_token(provider, user_session.oauth_token)
            
            if not is_valid:
                raise TokenValidationError("Invalid OAuth token")
            
            # Create new session for the same user
            new_session = self.session_service.create_session(
                user_id=user_session.user_id,
                oauth_token=user_session.oauth_token
            )
            
            # Delete old session
            self.session_service.delete_session(request.session_token)
            
            # Calculate new expiry
            new_expires_at = datetime.now(UTC) + timedelta(hours=24)
            
            logger.info(
                "Session refreshed successfully",
                extra={
                    "username": user_session.user.username,
                    "provider": provider
                }
            )
            
            return RefreshResponse(
                session_token=new_session.session_id,
                expires_at=new_expires_at.isoformat() + "Z"
            )
            
        except (SessionNotFoundError, TokenValidationError):
            raise
        except Exception as e:
            logger.error(f"Failed to refresh session: {e}", exc_info=True)
            raise AuthError(f"Failed to refresh session: {str(e)}")
    
    async def verify_session(
        self,
        request: VerifyRequest,
    ) -> VerifyResponse:
        """
        Verify session and return user information.
        
        Args:
            request: Verify request containing session token
            
        Returns:
            Verify response with user information
            
        Raises:
            SessionNotFoundError: If session is not found
            TokenValidationError: If token validation fails
        """
        try:
            # Check if session exists and is valid
            if not self.session_service.is_session_valid(request.session_token):
                raise SessionNotFoundError("Invalid or expired session token")
            
            user_session = self.session_service.get_session_by_id(request.session_token)
            if not user_session:
                raise SessionNotFoundError("Session not found")
            
            # Infer provider from user data if available, otherwise default to github
            provider = user_session.user.oauth_provider if user_session and user_session.user and user_session.user.oauth_provider else "github"
            
            try:
                # Validate OAuth token
                if not await self.git_provider_service.validate_token(provider, user_session.oauth_token):
                    # OAuth token is invalid, delete session
                    self.session_service.delete_session(request.session_token)
                    raise TokenValidationError("OAuth token has been revoked")
                
                # Get fresh user info from OAuth provider
                oauth_user_info = await self.git_provider_service.get_user_info(provider, user_session.oauth_token)
                
                # Get user's primary email
                primary_email = None
                try:
                    emails = await self.git_provider_service.get_user_emails(provider, user_session.oauth_token)
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
                    logger.warning(f"Failed to get user emails from OAuth provider: {e}")
                
                # Get or create/update user in database
                user_service = UserDAO(self.db)
                user_db = User(
                    name=oauth_user_info.name or oauth_user_info.username,
                    oauth_provider=provider,
                    username=oauth_user_info.username,
                    email=primary_email or oauth_user_info.email or "",
                    avatar_url=oauth_user_info.avatar_url,
                    oauth_user_id=int(oauth_user_info.id) if provider == "github" and oauth_user_info.id else None,
                    html_url=oauth_user_info.profile_url,
                )
                user_db = user_service.save_user(user_data=user_db)
                
                logger.info(
                    "Session verified successfully",
                    extra={
                        "username": oauth_user_info.username,
                        "provider": provider
                    }
                )
                
                return VerifyResponse(
                    user=user_db,
                    is_valid=True
                )
                
            except Exception as e:
                logger.warning(f"Could not validate OAuth token for session: {e}")
                
                # Try to get user from database if OAuth validation fails
                from database.models.user import User as UserModel
                user = self.db.query(UserModel).filter_by(username=user_session.user.username).first()
                
                if user:
                    # OAuth token validation failed but user exists in DB
                    # Delete the session and raise an error
                    self.session_service.delete_session(request.session_token)
                    raise TokenValidationError("OAuth token has been revoked")
                else:
                    # Create minimal user object if not found
                    user_db = User(
                        username=user_session.user.username,
                        oauth_provider=provider, # Use inferred provider
                        name=user_session.user.username,
                        email="",
                        avatar_url="",
                        oauth_user_id=None,
                        html_url=""
                    )
                    
                    return VerifyResponse(
                        user=user_db,
                        is_valid=True
                    )
                    
        except (SessionNotFoundError, TokenValidationError):
            raise
        except Exception as e:
            logger.error(f"Failed to verify session: {e}", exc_info=True)
            raise AuthError(f"Failed to verify session: {str(e)}")
    
    def get_available_providers(self) -> list[str]:
        """
        Get list of available OAuth providers.
        
        Returns:
            List of provider names
        """
        return self.git_provider_service.get_available_providers()
    
    def cleanup_expired_sessions(self) -> int:
        """
        Clean up expired sessions and OAuth states.
        
        Returns:
            Number of sessions cleaned up
        """
        try:
            # Clean up expired OAuth states
            oauth_cleanup_count = self.git_provider_service.cleanup_expired_states()
            
            # Note: SessionService doesn't have a cleanup method, but we could add one
            # For now, just return the OAuth cleanup count
            logger.info(f"Cleaned up {oauth_cleanup_count} expired OAuth states")
            
            return oauth_cleanup_count
            
        except Exception as e:
            logger.error(f"Failed to cleanup expired sessions: {e}", exc_info=True)
            return 0