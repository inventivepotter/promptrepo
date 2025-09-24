"""
OAuth Service

This module provides the main OAuth service that orchestrates
OAuth flows, authentication operations across multiple providers using the Strategy pattern.
"""

import logging
from typing import List, Optional, Dict, Any
from middlewares.rest.exceptions import AppException
from services.config.models import OAuthConfig
from services.oauth.enums import OAuthProvider
from services.oauth.oauth_factory import OAuthProviderFactory, auto_register_providers
from services.oauth.oauth_interface import IOAuthProvider
from services.oauth.state_manager_singleton import get_state_manager
from services.oauth.models import (
    OAuthToken, 
    OAuthUserInfo, 
    OAuthUserEmail, 
    AuthUrlResponse, 
    LoginResponse,
    OAuthError,
    ProviderNotFoundError,
    InvalidStateError,
    TokenExchangeError,
    ConfigurationError
)
from services.config.config_interface import IConfig

logger = logging.getLogger(__name__)


class OAuthService:
    """
    Main OAuth service handling all providers.
    
    This service orchestrates OAuth flows across multiple providers,
    handling state management, provider instantiation, and common
    OAuth operations.
    """
    
    def __init__(self, config_service: IConfig, auto_register: bool = True):
        """
        Initialize the OAuth service.
        
        Args:
            config_service: Configuration service instance
            auto_register: Whether to auto-register known providers
        """
        self.config_service = config_service
        # Use singleton state manager to persist states across requests
        self.state_manager = get_state_manager()
        
        # Auto-register providers if requested
        if auto_register:
            auto_register_providers()
    
    def _get_oauth_provider(self, provider: OAuthProvider) -> IOAuthProvider:
        """
        Private method to get OAuth provider instance.
        
        Args:
            provider: OAuth provider name
            
        Returns:
            OAuth provider instance
            
        Raises:
            ProviderNotFoundError: If provider is not supported
        """
        return OAuthProviderFactory.create_provider(provider, self.config_service)
    
    async def get_authorization_url(
        self,
        provider: OAuthProvider,
        scopes: Optional[List[str]] = None,
        state: Optional[str] = None,
        promptrepo_redirect_url: Optional[str] = None
    ) -> AuthUrlResponse:
        """
        Generate OAuth authorization URL for specified provider.
        
        Args:
            provider: OAuth provider name
            scopes: List of requested scopes
            state: Optional state parameter for CSRF protection
            promptrepo_redirect_url: Optional PromptRepo app URL to redirect after login
            
        Returns:
            AuthUrlResponse containing authorization URL and state
            
        Raises:
            ProviderNotFoundError: If provider is not supported
            ConfigurationError: If provider configuration is invalid
        """
        # Validate parameters
        if not provider or provider.strip() == "":
            raise ValueError("Provider name must be a non-empty string")

        oauth_redirect_uri = self.get_provider_config(provider).redirect_url
        if not oauth_redirect_uri or oauth_redirect_uri.strip() == "":
            raise ValueError("Redirect URI must be a non-empty string")
        
        try:
            # Create provider instance
            oauth_provider = self._get_oauth_provider(provider)
            
            state = self.state_manager.generate_state()
            
            # Generate authorization URL
            auth_url, provider_state = await oauth_provider.generate_auth_url(
                scopes=scopes or [],
                redirect_uri=oauth_redirect_uri,
                state=state
            )
            
            # Store state with provider info and promptrepo redirect URL
            self.state_manager.store_state(
                state=state,
                provider=provider,
                redirect_uri=oauth_redirect_uri,
                scopes=scopes or [],
                promptrepo_redirect_url=promptrepo_redirect_url
            )
            
            return AuthUrlResponse(
                auth_url=auth_url,
                provider=provider,
                state=state
            )
            
        except ProviderNotFoundError:
            raise
        except ConfigurationError:
            raise
        except Exception as e:
            logger.error(f"Error generating authorization URL for {provider}: {e}")
            raise OAuthError(f"Failed to generate authorization URL: {str(e)}", provider)
    
    async def exchange_code_for_token(
        self,
        provider: OAuthProvider,
        code: str,
        state: str,
        redirect_uri: Optional[str] = None
    ) -> OAuthToken:
        """
        Exchange authorization code for access token.
        
        Args:
            provider: OAuth provider name
            code: Authorization code from callback
            state: State parameter for CSRF verification
            redirect_uri: Optional redirect URI for validation (if provided, must match stored value)
            
        Returns:
            OAuthToken containing access token and related information
            
        Raises:
            InvalidStateError: If state is invalid or expired
            ProviderNotFoundError: If provider is not supported
            TokenExchangeError: If token exchange fails
        """
        try:
            # Validate state
            if not self.state_manager.validate_state(state, provider):
                raise InvalidStateError(state, provider)
            
            # Get state data
            state_data = self.state_manager.get_state_data(state)
            if not state_data:
                raise InvalidStateError(state, provider)
            
            # Get redirect URI from state
            stored_redirect_uri = state_data.redirect_uri
            if not stored_redirect_uri:
                raise InvalidStateError("Missing redirect URI in state", provider)
            
            # Create provider instance
            oauth_provider = self._get_oauth_provider(provider)
            
            # Exchange code for token using stored redirect URI
            token = await oauth_provider.exchange_code_for_token(
                code=code,
                redirect_uri=stored_redirect_uri,
                state=state
            )
            
            # Clean up state
            self.state_manager.remove_state(state)
            
            return token
            
        except (InvalidStateError, ProviderNotFoundError, TokenExchangeError):
            raise
        except Exception as e:
            logger.error(f"Error exchanging code for token with {provider}: {e}")
            raise TokenExchangeError(f"Failed to exchange code for token: {str(e)}", provider)
    
    async def get_user_info(self, provider: OAuthProvider, access_token: str) -> OAuthUserInfo:
        """
        Get user information from OAuth provider.
        
        Args:
            provider: OAuth provider name
            access_token: OAuth access token
            
        Returns:
            UserInfo object containing user details
            
        Raises:
            ProviderNotFoundError: If provider is not supported
            OAuthError: If user info retrieval fails
        """
        try:
            # Create provider instance
            oauth_provider = self._get_oauth_provider(provider)
            
            # Get user info
            user_info = await oauth_provider.get_user_info(access_token)
            
            return user_info
            
        except ProviderNotFoundError:
            raise
        except Exception as e:
            logger.error(f"Error getting user info from {provider}: {e}")
            raise OAuthError(f"Failed to get user info: {str(e)}", provider)
    
    async def get_user_emails(self, provider: OAuthProvider, access_token: str) -> List[OAuthUserEmail]:
        """
        Get user email addresses from OAuth provider.
        
        Args:
            provider: OAuth provider name
            access_token: OAuth access token
            
        Returns:
            List of UserEmail objects
            
        Raises:
            ProviderNotFoundError: If provider is not supported
            OAuthError: If email retrieval fails
        """
        try:
            # Create provider instance
            oauth_provider = self._get_oauth_provider(provider)
            
            # Get user emails
            emails = await oauth_provider.get_user_emails(access_token)
            
            return emails
            
        except ProviderNotFoundError:
            raise
        except Exception as e:
            logger.error(f"Error getting user emails from {provider}: {e}")
            raise OAuthError(f"Failed to get user emails: {str(e)}", provider)
    
    async def refresh_token(self, provider: OAuthProvider, refresh_token: str) -> Optional[OAuthToken]:
        """
        Refresh an expired access token.
        
        Args:
            provider: OAuth provider name
            refresh_token: Refresh token from initial token exchange
            
        Returns:
            New OAuthToken if refresh is supported, None otherwise
            
        Raises:
            ProviderNotFoundError: If provider is not supported
            OAuthError: If token refresh fails
        """
        try:
            # Create provider instance
            oauth_provider = self._get_oauth_provider(provider)
            
            # Refresh token
            new_token = await oauth_provider.refresh_token(refresh_token)
            
            return new_token
            
        except ProviderNotFoundError:
            raise
        except Exception as e:
            logger.error(f"Error refreshing token with {provider}: {e}")
            raise OAuthError(f"Failed to refresh token: {str(e)}", provider)
    
    async def revoke_token(self, provider: OAuthProvider, access_token: str) -> bool:
        """
        Revoke an OAuth access token.
        
        Args:
            provider: OAuth provider name
            access_token: OAuth access token to revoke
            
        Returns:
            True if revocation was successful, False otherwise
            
        Raises:
            ProviderNotFoundError: If provider is not supported
            OAuthError: If token revocation fails
        """
        try:
            # Create provider instance
            oauth_provider = self._get_oauth_provider(provider)
            
            # Revoke token
            result = await oauth_provider.revoke_token(access_token)
            
            return result
            
        except ProviderNotFoundError:
            raise
        except Exception as e:
            logger.error(f"Error revoking token with {provider}: {e}")
            raise OAuthError(f"Failed to revoke token: {str(e)}", provider)
    
    async def validate_token(self, provider: OAuthProvider, access_token: str) -> bool:
        """
        Validate if an OAuth access token is still valid.
        
        Args:
            provider: OAuth provider name
            access_token: OAuth access token to validate
            
        Returns:
            True if token is valid, False otherwise
            
        Raises:
            ProviderNotFoundError: If provider is not supported
            OAuthError: If token validation fails
        """
        try:
            # Create provider instance
            oauth_provider = self._get_oauth_provider(provider)
            
            # Validate token
            is_valid = await oauth_provider.validate_token(access_token)
            
            return is_valid
            
        except ProviderNotFoundError:
            raise
        except Exception as e:
            logger.error(f"Error validating token with {provider}: {e}")
            raise OAuthError(f"Failed to validate token: {str(e)}", provider)

    def get_available_providers(self) -> List[OAuthProvider]:
        """
        Get list of available OAuth providers.
        
        Returns:
            List of provider names
        """
        return OAuthProviderFactory.get_available_providers()
    
    def cleanup_expired_states(self) -> int:
        """
        Clean up expired OAuth states.
        
        Returns:
            Number of expired states removed
        """
        return self.state_manager.cleanup_expired_states()

    def get_provider_config(self, provider: OAuthProvider) -> OAuthConfig:
        """
        Get configuration for a specific provider.
        
        Args:
            provider: Provider name
            
        Returns:
            Provider configuration dictionary or None if not found
        """
        oauth_configs = self.config_service.get_oauth_configs()
        if not oauth_configs:
            raise AppException(
                status_code=400,
                error_code="BAD_REQUEST",
                message="No OAuth configurations found",
                detail="Please configure OAuth providers in the ENV."
            )
        
        for config in oauth_configs:
            if config.provider == provider:
                return config
        
        raise AppException(
            status_code=400,
            error_code="BAD_REQUEST",
            message="No OAuth configurations found",
            detail="Please configure OAuth providers in the ENV."
        )
    