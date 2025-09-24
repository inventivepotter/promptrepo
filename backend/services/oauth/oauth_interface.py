"""
OAuth Provider Interface

This module defines the abstract base class for OAuth providers,
ensuring all provider implementations follow a consistent interface.
"""

from abc import ABC, abstractmethod
from typing import List, Tuple, Optional, Dict
from services.oauth.models import OAuthToken, OAuthUserInfo, OAuthUserEmail


class IOAuthProvider(ABC):
    """
    Abstract base class for OAuth providers.
    
    This interface defines the contract that all OAuth provider
    implementations must follow, ensuring consistency across
    different providers (GitHub, GitLab, Bitbucket, etc.).
    """
    
    @abstractmethod
    def __init__(self, client_id: str, client_secret: str):
        """
        Initialize the OAuth provider with credentials.
        
        Args:
            client_id: OAuth client ID for the provider
            client_secret: OAuth client secret for the provider
        """
        pass
    
    @abstractmethod
    async def generate_auth_url(
        self, 
        scopes: List[str], 
        redirect_uri: str, 
        state: Optional[str] = None
    ) -> Tuple[str, str]:
        """
        Generate OAuth authorization URL.
        
        Args:
            scopes: List of OAuth scopes to request
            redirect_uri: Callback URL after authorization
            state: Optional CSRF protection state (generated if not provided)
            
        Returns:
            Tuple of (authorization_url, state)
        """
        pass
    
    @abstractmethod
    async def exchange_code_for_token(
        self, 
        code: str, 
        redirect_uri: str, 
        state: Optional[str] = None
    ) -> OAuthToken:
        """
        Exchange authorization code for access token.
        
        Args:
            code: Authorization code from OAuth callback
            redirect_uri: Callback URL used in the initial request
            state: State parameter for CSRF verification
            
        Returns:
            OAuthToken containing access token and related information
            
        Raises:
            TokenExchangeError: If token exchange fails
        """
        pass
    
    @abstractmethod
    async def get_user_info(self, access_token: str) -> OAuthUserInfo:
        """
        Get user information from the provider.
        
        Args:
            access_token: OAuth access token
            
        Returns:
            UserInfo object containing user details
            
        Raises:
            OAuthError: If user info retrieval fails
        """
        pass
    
    @abstractmethod
    async def get_user_emails(self, access_token: str) -> List[OAuthUserEmail]:
        """
        Get user email addresses from the provider.
        
        Args:
            access_token: OAuth access token
            
        Returns:
            List of UserEmail objects
            
        Raises:
            OAuthError: If email retrieval fails
        """
        pass
    
    @abstractmethod
    async def get_user_repositories(self, access_token: str) -> Dict[str, str]:
        """
        Get user repositories from the provider.
        
        Args:
            access_token: OAuth access token
            
        Returns:
            Dict[str, str]: Dictionary mapping repository names to their clone URLs
            
        Raises:
            OAuthError: If repository retrieval fails
        """
        pass
    
    @abstractmethod
    async def refresh_token(self, refresh_token: str) -> Optional[OAuthToken]:
        """
        Refresh an expired access token.
        
        Args:
            refresh_token: Refresh token from initial token exchange
            
        Returns:
            New OAuthToken if refresh is supported, None otherwise
            
        Raises:
            OAuthError: If token refresh fails
        """
        pass
    
    @abstractmethod
    async def revoke_token(self, access_token: str) -> bool:
        """
        Revoke an access token.
        
        Args:
            access_token: OAuth access token to revoke
            
        Returns:
            True if revocation was successful, False otherwise
        """
        pass
    
    @abstractmethod
    async def validate_token(self, access_token: str) -> bool:
        """
        Validate if an access token is still valid.
        
        Args:
            access_token: OAuth access token to validate
            
        Returns:
            True if token is valid, False otherwise
        """
        pass