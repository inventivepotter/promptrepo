"""
Git Provider Service

This module provides the main Git Provider service that orchestrates
OAuth flows, Git operations across multiple providers using the Strategy pattern.
"""

import logging
from typing import List, Optional, Dict, Any
from .git_provider_factory import OAuthProviderFactory, auto_register_providers
from .state_manager import StateManager
from .models import (
    OAuthToken, 
    UserInfo, 
    UserEmail, 
    AuthUrlResponse, 
    LoginResponse,
    OAuthError,
    ProviderNotFoundError,
    InvalidStateError,
    TokenExchangeError,
    ConfigurationError
)
from ..config.config_interface import IConfig

logger = logging.getLogger(__name__)


class GitProviderService:
    """
    Main Git Provider service handling all providers.
    
    This service orchestrates Git Provider flows across multiple providers,
    handling state management, provider instantiation, and common
    Git Provider operations.
    """
    
    def __init__(self, config_service: IConfig, auto_register: bool = True):
        """
        Initialize the Git Provider service.
        
        Args:
            config_service: Configuration service instance
            auto_register: Whether to auto-register known providers
        """
        self.config_service = config_service
        self.state_manager = StateManager()
        
        # Auto-register providers if requested
        if auto_register:
            auto_register_providers()
    
    def _get_git_provider(self, provider: str):
        """
        Private method to get Git provider instance.
        
        Args:
            provider: Git provider name
            
        Returns:
            Git provider instance
            
        Raises:
            ProviderNotFoundError: If provider is not supported
        """
        return OAuthProviderFactory.create_provider(provider, self.config_service)
    
    async def get_authorization_url(
        self,
        provider: str,
        redirect_uri: str,
        scopes: Optional[List[str]] = None,
        state: Optional[str] = None
    ) -> AuthUrlResponse:
        """
        Generate Git Provider authorization URL for specified provider.
        
        Args:
            provider: Git provider name
            redirect_uri: Callback URL after authorization
            scopes: List of Git Provider scopes to request
            state: Optional CSRF protection state
            
        Returns:
            AuthUrlResponse containing authorization URL and state
            
        Raises:
            ProviderNotFoundError: If provider is not supported
            ConfigurationError: If provider configuration is invalid
        """
        # Validate parameters
        if not provider or provider.strip() == "":
            raise ValueError("Provider name must be a non-empty string")
        if not redirect_uri or redirect_uri.strip() == "":
            raise ValueError("Redirect URI must be a non-empty string")
        
        try:
            # Create provider instance
            oauth_provider = self._get_git_provider(provider)
            
            # Generate state if not provided
            if state is None:
                state = self.state_manager.generate_state()
            
            # Generate authorization URL
            auth_url, provider_state = await oauth_provider.generate_auth_url(
                scopes=scopes or [],
                redirect_uri=redirect_uri,
                state=state
            )
            
            # Store state with provider info
            self.state_manager.store_state(
                state=state,
                provider=provider,
                redirect_uri=redirect_uri,
                scopes=scopes or []
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
        provider: str,
        code: str,
        redirect_uri: str,
        state: str
    ) -> OAuthToken:
        """
        Exchange authorization code for access token.
        
        Args:
            provider: Git provider name
            code: Authorization code from callback
            redirect_uri: Callback URL used in initial request
            state: State parameter for CSRF verification
            
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
            
            # Verify redirect URI matches
            if state_data.redirect_uri != redirect_uri:
                raise InvalidStateError("Redirect URI mismatch", provider)
            
            # Create provider instance
            oauth_provider = self._get_git_provider(provider)
            
            # Exchange code for token
            token = await oauth_provider.exchange_code_for_token(
                code=code,
                redirect_uri=redirect_uri,
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
    
    async def get_user_info(self, provider: str, access_token: str) -> UserInfo:
        """
        Get user information from Git provider.
        
        Args:
            provider: Git provider name
            access_token: Git Provider access token
            
        Returns:
            UserInfo object containing user details
            
        Raises:
            ProviderNotFoundError: If provider is not supported
            OAuthError: If user info retrieval fails
        """
        try:
            # Create provider instance
            oauth_provider = self._get_git_provider(provider)
            
            # Get user info
            user_info = await oauth_provider.get_user_info(access_token)
            
            return user_info
            
        except ProviderNotFoundError:
            raise
        except Exception as e:
            logger.error(f"Error getting user info from {provider}: {e}")
            raise OAuthError(f"Failed to get user info: {str(e)}", provider)
    
    async def get_user_emails(self, provider: str, access_token: str) -> List[UserEmail]:
        """
        Get user email addresses from Git provider.
        
        Args:
            provider: Git provider name
            access_token: Git Provider access token
            
        Returns:
            List of UserEmail objects
            
        Raises:
            ProviderNotFoundError: If provider is not supported
            OAuthError: If email retrieval fails
        """
        try:
            # Create provider instance
            oauth_provider = self._get_git_provider(provider)
            
            # Get user emails
            emails = await oauth_provider.get_user_emails(access_token)
            
            return emails
            
        except ProviderNotFoundError:
            raise
        except Exception as e:
            logger.error(f"Error getting user emails from {provider}: {e}")
            raise OAuthError(f"Failed to get user emails: {str(e)}", provider)
    
    async def refresh_token(self, provider: str, refresh_token: str) -> Optional[OAuthToken]:
        """
        Refresh an expired access token.
        
        Args:
            provider: Git provider name
            refresh_token: Refresh token from initial token exchange
            
        Returns:
            New OAuthToken if refresh is supported, None otherwise
            
        Raises:
            ProviderNotFoundError: If provider is not supported
            OAuthError: If token refresh fails
        """
        try:
            # Create provider instance
            oauth_provider = self._get_git_provider(provider)
            
            # Refresh token
            new_token = await oauth_provider.refresh_token(refresh_token)
            
            return new_token
            
        except ProviderNotFoundError:
            raise
        except Exception as e:
            logger.error(f"Error refreshing token with {provider}: {e}")
            raise OAuthError(f"Failed to refresh token: {str(e)}", provider)
    
    async def revoke_token(self, provider: str, access_token: str) -> bool:
        """
        Revoke an Git Provider access token.
        
        Args:
            provider: Git provider name
            access_token: OAuth access token to revoke
            
        Returns:
            True if revocation was successful, False otherwise
            
        Raises:
            ProviderNotFoundError: If provider is not supported
            OAuthError: If token revocation fails
        """
        try:
            # Create provider instance
            oauth_provider = self._get_git_provider(provider)
            
            # Revoke token
            result = await oauth_provider.revoke_token(access_token)
            
            return result
            
        except ProviderNotFoundError:
            raise
        except Exception as e:
            logger.error(f"Error revoking token with {provider}: {e}")
            raise OAuthError(f"Failed to revoke token: {str(e)}", provider)
    
    async def validate_token(self, provider: str, access_token: str) -> bool:
        """
        Validate if an OAuth access token is still valid.
        
        Args:
            provider: Git provider name
            access_token: Git Provider access token to validate
            
        Returns:
            True if token is valid, False otherwise
            
        Raises:
            ProviderNotFoundError: If provider is not supported
            OAuthError: If token validation fails
        """
        try:
            # Create provider instance
            oauth_provider = self._get_git_provider(provider)
            
            # Validate token
            is_valid = await oauth_provider.validate_token(access_token)
            
            return is_valid
            
        except ProviderNotFoundError:
            raise
        except Exception as e:
            logger.error(f"Error validating token with {provider}: {e}")
            raise OAuthError(f"Failed to validate token: {str(e)}", provider)
    
    def get_available_providers(self) -> List[str]:
        """
        Get list of available Git Provider providers.
        
        Returns:
            List of provider names
        """
        return OAuthProviderFactory.get_available_providers()
    
    def cleanup_expired_states(self) -> int:
        """
        Clean up expired Git Provider states.
        
        Returns:
            Number of expired states removed
        """
        return self.state_manager.cleanup_expired_states()
    
    def get_provider_config(self, provider: str) -> Optional[Dict[str, Any]]:
        """
        Get configuration for a specific provider.
        
        Args:
            provider: Provider name
            
        Returns:
            Provider configuration dictionary or None if not found
        """
        oauth_configs = self.config_service.get_oauth_configs()
        if not oauth_configs:
            return None
        
        for config in oauth_configs:
            if config.provider.lower() == provider.lower():
                return {
                    "provider": config.provider,
                    "client_id": config.client_id,
                    "scopes": []  # Default scopes would be provider-specific
                }
        
        return None
    
    async def get_user_repositories(self, provider: str, access_token: str) -> Dict[str, str]:
        """
        Get user repositories from Git provider.
        
        Args:
            provider: Git provider name
            access_token: Git Provider access token
            
        Returns:
            Dict[str, str]: Dictionary mapping repository names to their clone URLs
            
        Raises:
            ProviderNotFoundError: If provider is not supported
            OAuthError: If repository retrieval fails
        """
        try:
            # Create provider instance
            oauth_provider = self._get_git_provider(provider)
            
            # Get user repositories
            repos = await oauth_provider.get_user_repositories(access_token)
            
            return repos
            
        except ProviderNotFoundError:
            raise
        except Exception as e:
            logger.error(f"Error getting user repositories from {provider}: {e}")
            raise OAuthError(f"Failed to get user repositories: {str(e)}", provider)