"""
GitHub OAuth Provider

This module implements the IOAuthProvider interface for GitHub,
providing OAuth authentication functionality specific to GitHub.
"""

import httpx
import secrets
from typing import List, Tuple, Optional, Dict, Any
from urllib.parse import urlencode
from ..oauth_interface import IOAuthProvider
from ..models import (
    OAuthToken, 
    UserInfo, 
    UserEmail, 
    OAuthProvider,
    TokenExchangeError,
    OAuthError
)
import logging

logger = logging.getLogger(__name__)


class GitHubOAuthProvider(IOAuthProvider):
    """
    GitHub OAuth provider implementation.
    
    This class implements the IOAuthProvider interface for GitHub,
    handling all GitHub-specific OAuth operations.
    """
    
    # GitHub OAuth endpoints
    AUTHORIZE_URL = "https://github.com/login/oauth/authorize"
    TOKEN_URL = "https://github.com/login/oauth/access_token"
    API_BASE_URL = "https://api.github.com"
    
    # Default scopes for GitHub
    DEFAULT_SCOPES = ["user:email", "read:user"]
    
    def __init__(self, client_id: str, client_secret: str):
        """
        Initialize GitHub OAuth provider.
        
        Args:
            client_id: GitHub OAuth App Client ID
            client_secret: GitHub OAuth App Client Secret
        """
        if not client_id or not client_secret:
            raise ValueError("GitHub client_id and client_secret are required")
        
        self.client_id = client_id
        self.client_secret = client_secret
        
        # HTTP client for API requests
        self.http_client = httpx.AsyncClient(
            timeout=30.0,
            headers={
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28",
                "User-Agent": "PromptRepo/1.0"
            }
        )
    
    async def __aenter__(self):
        """Async context manager entry"""
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.http_client.aclose()
    
    async def generate_auth_url(
        self, 
        scopes: List[str], 
        redirect_uri: str, 
        state: Optional[str] = None
    ) -> Tuple[str, str]:
        """
        Generate GitHub OAuth authorization URL.
        
        Args:
            scopes: List of OAuth scopes
            redirect_uri: Callback URL after authorization
            state: Optional CSRF protection state
            
        Returns:
            Tuple of (authorization_url, state)
        """
        if not scopes:
            scopes = self.DEFAULT_SCOPES
        
        if state is None:
            state = secrets.token_urlsafe(32)
        
        params = {
            "client_id": self.client_id,
            "redirect_uri": redirect_uri,
            "scope": " ".join(scopes),
            "state": state,
            "allow_signup": "true"
        }
        
        auth_url = f"{self.AUTHORIZE_URL}?{urlencode(params)}"
        return auth_url, state
    
    async def exchange_code_for_token(
        self, 
        code: str, 
        redirect_uri: str, 
        state: Optional[str] = None
    ) -> OAuthToken:
        """
        Exchange authorization code for access token.
        
        Args:
            code: Authorization code from GitHub callback
            redirect_uri: Callback URL used in the initial request
            state: State parameter for CSRF verification
            
        Returns:
            OAuthToken containing access token and related information
            
        Raises:
            TokenExchangeError: If token exchange fails
        """
        try:
            # Prepare token exchange request
            token_data = {
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "code": code,
                "redirect_uri": redirect_uri
            }
            
            headers = {
                "Accept": "application/json"
            }
            
            # Exchange code for token
            response = await self.http_client.post(
                self.TOKEN_URL,
                data=token_data,
                headers=headers
            )
            
            if response.status_code != 200:
                logger.error(f"GitHub token exchange failed: {response.status_code} {response.text}")
                raise TokenExchangeError(
                    "Failed to exchange authorization code for access token",
                    "github",
                    str(response.status_code)
                )
            
            token_data = response.json()
            
            # Check for errors in response
            if "error" in token_data:
                logger.error(f"GitHub OAuth error: {token_data}")
                raise TokenExchangeError(
                    f"GitHub OAuth error: {token_data.get('error_description', 'Unknown error')}",
                    "github",
                    token_data.get("error")
                )
            
            # Create OAuth token
            oauth_token = OAuthToken(
                access_token=token_data["access_token"],
                token_type=token_data.get("token_type", "bearer"),
                scope=token_data.get("scope", "")
            )
            
            # GitHub doesn't provide expires_in or refresh_token by default
            if "expires_in" in token_data:
                oauth_token.expires_in = token_data["expires_in"]
            
            if "refresh_token" in token_data:
                oauth_token.refresh_token = token_data["refresh_token"]
            
            return oauth_token
            
        except httpx.HTTPError as e:
            logger.error(f"HTTP error during token exchange: {e}")
            raise TokenExchangeError(
                "Failed to communicate with GitHub",
                "github"
            )
        except Exception as e:
            if isinstance(e, TokenExchangeError):
                raise
            logger.error(f"Unexpected error during token exchange: {e}")
            raise TokenExchangeError(
                f"Unexpected error: {str(e)}",
                "github"
            )
    
    async def get_user_info(self, access_token: str) -> UserInfo:
        """
        Get user information from GitHub API.
        
        Args:
            access_token: GitHub OAuth access token
            
        Returns:
            UserInfo object containing user details
            
        Raises:
            OAuthError: If user info retrieval fails
        """
        try:
            headers = {
                "Authorization": f"Bearer {access_token}"
            }
            
            response = await self.http_client.get(
                f"{self.API_BASE_URL}/user",
                headers=headers
            )
            
            if response.status_code == 401:
                raise OAuthError("Invalid or expired GitHub access token", "github")
            elif response.status_code != 200:
                logger.error(f"GitHub user info failed: {response.status_code} {response.text}")
                raise OAuthError("Failed to retrieve user information from GitHub", "github")
            
            user_data = response.json()
            
            # Create UserInfo object
            user_info = UserInfo(
                id=str(user_data["id"]),
                username=user_data["login"],
                name=user_data.get("name"),
                email=user_data.get("email"),
                avatar_url=user_data.get("avatar_url"),
                profile_url=user_data.get("html_url"),
                provider=OAuthProvider.GITHUB,
                raw_data=user_data
            )
            
            return user_info
            
        except httpx.HTTPError as e:
            logger.error(f"HTTP error during user info retrieval: {e}")
            raise OAuthError("Failed to communicate with GitHub", "github")
        except Exception as e:
            if isinstance(e, OAuthError):
                raise
            logger.error(f"Unexpected error during user info retrieval: {e}")
            raise OAuthError(f"Unexpected error: {str(e)}", "github")
    
    async def get_user_emails(self, access_token: str) -> List[UserEmail]:
        """
        Get user email addresses from GitHub API.
        
        Args:
            access_token: GitHub OAuth access token
            
        Returns:
            List of UserEmail objects
            
        Raises:
            OAuthError: If email retrieval fails
        """
        try:
            headers = {
                "Authorization": f"Bearer {access_token}"
            }
            
            response = await self.http_client.get(
                f"{self.API_BASE_URL}/user/emails",
                headers=headers
            )
            
            if response.status_code == 401:
                raise OAuthError("Invalid or expired GitHub access token", "github")
            elif response.status_code == 403:
                raise OAuthError(
                    "Insufficient permissions to access user emails. Required scope: user:email",
                    "github"
                )
            elif response.status_code != 200:
                logger.error(f"GitHub user emails failed: {response.status_code} {response.text}")
                raise OAuthError("Failed to retrieve user emails from GitHub", "github")
            
            emails_data = response.json()
            
            # Create UserEmail objects
            user_emails = []
            for email_data in emails_data:
                user_email = UserEmail(
                    email=email_data["email"],
                    primary=email_data.get("primary", False),
                    verified=email_data.get("verified", False),
                    visibility=email_data.get("visibility")
                )
                user_emails.append(user_email)
            
            return user_emails
            
        except httpx.HTTPError as e:
            logger.error(f"HTTP error during email retrieval: {e}")
            raise OAuthError("Failed to communicate with GitHub", "github")
        except Exception as e:
            if isinstance(e, OAuthError):
                raise
            logger.error(f"Unexpected error during email retrieval: {e}")
            raise OAuthError(f"Unexpected error: {str(e)}", "github")
    
    async def refresh_token(self, refresh_token: str) -> Optional[OAuthToken]:
        """
        Refresh an expired access token.
        
        Note: GitHub OAuth Apps don't support token refresh by default.
        This method returns None for GitHub.
        
        Args:
            refresh_token: Refresh token from initial token exchange
            
        Returns:
            None (GitHub doesn't support token refresh)
        """
        # GitHub OAuth Apps don't support token refresh
        return None
    
    async def revoke_token(self, access_token: str) -> bool:
        """
        Revoke GitHub OAuth token.
        
        Args:
            access_token: GitHub OAuth access token to revoke
            
        Returns:
            True if revocation was successful, False otherwise
        """
        try:
            # GitHub Apps use a different endpoint for revocation
            # For OAuth Apps, we revoke by deleting the authorization
            import base64
            auth_string = f"{self.client_id}:{self.client_secret}"
            encoded_auth = base64.b64encode(auth_string.encode()).decode()
            
            headers = {
                "Authorization": f"Basic {encoded_auth}"
            }
            
            # This endpoint revokes all tokens for the OAuth app
            response = await self.http_client.delete(
                f"{self.API_BASE_URL}/applications/{self.client_id}/token",
                headers=headers,
                params={"access_token": access_token}
            )
            
            return response.status_code == 204
            
        except Exception as e:
            logger.error(f"Token revocation failed: {e}")
            return False
    
    async def validate_token(self, access_token: str) -> bool:
        """
        Validate if GitHub OAuth token is still valid.
        
        Args:
            access_token: GitHub OAuth access token
            
        Returns:
            True if token is valid, False otherwise
        """
        try:
            headers = {
                "Authorization": f"Bearer {access_token}"
            }
            
            response = await self.http_client.get(
                f"{self.API_BASE_URL}/user",
                headers=headers
            )
            
            return response.status_code == 200
            
        except Exception:
            return False