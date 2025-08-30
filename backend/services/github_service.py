"""
GitHub OAuth Service for PromptRepo
Based on: https://docs.github.com/en/apps/oauth-apps/building-oauth-apps/authorizing-oauth-apps
"""
import httpx
import secrets
from typing import Dict, Optional, Any
from urllib.parse import urlencode
from pydantic import BaseModel, Field
from fastapi import HTTPException, status
import logging

logger = logging.getLogger(__name__)


class GitHubUserInfo(BaseModel):
    """GitHub user information model"""
    id: int
    login: str  # username
    name: Optional[str] = None
    email: Optional[str] = None
    avatar_url: str
    html_url: str
    type: str
    created_at: str
    updated_at: str


class GitHubUserEmail(BaseModel):
    """GitHub user email model"""
    email: str
    primary: bool
    verified: bool
    visibility: Optional[str] = None


class GitHubTokenResponse(BaseModel):
    """GitHub OAuth token response model"""
    access_token: str
    token_type: str = "bearer"
    scope: str = ""


class GitHubService:
    """
    GitHub OAuth service implementing the OAuth App flow.
    Reference: https://docs.github.com/en/apps/oauth-apps/building-oauth-apps/authorizing-oauth-apps
    """

    # GitHub OAuth endpoints
    AUTHORIZE_URL = "https://github.com/login/oauth/authorize"
    TOKEN_URL = "https://github.com/login/oauth/access_token"
    API_BASE_URL = "https://api.github.com"

    def __init__(self, client_id: str, client_secret: str):
        """
        Initialize GitHub service with OAuth credentials.

        Args:
            client_id: GitHub OAuth App Client ID
            client_secret: GitHub OAuth App Client Secret
            redirect_uri: Callback URL registered with GitHub OAuth App
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
                "X-GitHub-Api-Version": "2022-11-28"
            }
        )

    async def __aenter__(self):
        """Async context manager entry"""
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        await self.http_client.aclose()

    def generate_auth_url(self, scopes: Optional[list[str]] = None, state: Optional[str] = None) -> tuple[str, str]:
        """
        Generate GitHub OAuth authorization URL.

        Args:
            scopes: List of OAuth scopes (default: ["user:email", "read:user"])
            state: CSRF protection state (auto-generated if not provided)

        Returns:
            Tuple of (auth_url, state)
        """
        if scopes is None:
            scopes = ["repo", "user:email", "read:user"]

        if state is None:
            state = secrets.token_urlsafe(32)

        params = {
            "client_id": self.client_id,
            "scope": " ".join(scopes),
            "state": state,
            "allow_signup": "true"  # Allow users to sign up during OAuth flow
        }

        auth_url = f"{self.AUTHORIZE_URL}?{urlencode(params)}"
        return auth_url, state

    async def exchange_code_for_token(self, code: str, state: Optional[str] = None) -> GitHubTokenResponse:
        """
        Exchange authorization code for access token.

        Args:
            code: Authorization code from GitHub callback
            state: State parameter for CSRF verification

        Returns:
            GitHubTokenResponse with access token

        Raises:
            HTTPException: If token exchange fails
        """
        try:
            # Prepare token exchange request
            token_data = {
                "client_id": self.client_id,
                "client_secret": self.client_secret,
                "code": code
            }

            headers = {
                "Accept": "application/json",
                "User-Agent": "PromptRepo/1.0"
            }

            # Exchange code for token
            response = await self.http_client.post(
                self.TOKEN_URL,
                data=token_data,
                headers=headers
            )

            if response.status_code != 200:
                logger.error(f"GitHub token exchange failed: {response.status_code} {response.text}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail="Failed to exchange authorization code for access token"
                )

            token_data = response.json()

            # Check for errors in response
            if "error" in token_data:
                logger.error(f"GitHub OAuth error: {token_data}")
                raise HTTPException(
                    status_code=status.HTTP_400_BAD_REQUEST,
                    detail=f"GitHub OAuth error: {token_data.get('error_description', 'Unknown error')}"
                )

            return GitHubTokenResponse(**token_data)

        except httpx.HTTPError as e:
            logger.error(f"HTTP error during token exchange: {e}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Failed to communicate with GitHub"
            )

    async def get_user_info(self, access_token: str) -> GitHubUserInfo:
        """
        Get user information from GitHub API.

        Args:
            access_token: GitHub OAuth access token

        Returns:
            GitHubUserInfo with user details

        Raises:
            HTTPException: If user info retrieval fails
        """
        try:
            headers = {
                "Authorization": f"Bearer {access_token}",
                "User-Agent": "PromptRepo/1.0"
            }

            response = await self.http_client.get(
                f"{self.API_BASE_URL}/user",
                headers=headers
            )

            if response.status_code == 401:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid or expired GitHub access token"
                )
            elif response.status_code != 200:
                logger.error(f"GitHub user info failed: {response.status_code} {response.text}")
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="Failed to retrieve user information from GitHub"
                )

            user_data = response.json()
            return GitHubUserInfo(**user_data)

        except httpx.HTTPError as e:
            logger.error(f"HTTP error during user info retrieval: {e}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Failed to communicate with GitHub"
            )

    async def get_user_emails(self, access_token: str) -> list[GitHubUserEmail]:
        """
        Get user email addresses from GitHub API.
        Requires 'user:email' scope.

        Args:
            access_token: GitHub OAuth access token

        Returns:
            List of GitHubUserEmail objects

        Raises:
            HTTPException: If email retrieval fails
        """
        try:
            headers = {
                "Authorization": f"Bearer {access_token}",
                "User-Agent": "PromptRepo/1.0"
            }

            response = await self.http_client.get(
                f"{self.API_BASE_URL}/user/emails",
                headers=headers
            )

            if response.status_code == 401:
                raise HTTPException(
                    status_code=status.HTTP_401_UNAUTHORIZED,
                    detail="Invalid or expired GitHub access token"
                )
            elif response.status_code == 403:
                # Might be missing scope
                raise HTTPException(
                    status_code=status.HTTP_403_FORBIDDEN,
                    detail="Insufficient permissions to access user emails. Required scope: user:email"
                )
            elif response.status_code != 200:
                logger.error(f"GitHub user emails failed: {response.status_code} {response.text}")
                raise HTTPException(
                    status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                    detail="Failed to retrieve user emails from GitHub"
                )

            emails_data = response.json()
            return [GitHubUserEmail(**email) for email in emails_data]

        except httpx.HTTPError as e:
            logger.error(f"HTTP error during email retrieval: {e}")
            raise HTTPException(
                status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
                detail="Failed to communicate with GitHub"
            )

    async def get_primary_email(self, access_token: str) -> Optional[str]:
        """
        Get user's primary email address.

        Args:
            access_token: GitHub OAuth access token

        Returns:
            Primary email address or None if not found
        """
        try:
            emails = await self.get_user_emails(access_token)

            # Find primary email
            for email in emails:
                if email.primary and email.verified:
                    return email.email

            # Fallback to first verified email
            for email in emails:
                if email.verified:
                    return email.email

            return None

        except HTTPException:
            # If we can't get emails, try to get from user profile
            try:
                user_info = await self.get_user_info(access_token)
                return user_info.email
            except HTTPException:
                return None

    async def revoke_token(self, access_token: str) -> bool:
        """
        Revoke GitHub OAuth token.

        Args:
            access_token: GitHub OAuth access token to revoke

        Returns:
            True if revocation was successful
        """
        try:
            # GitHub Apps use a different endpoint for revocation
            # For OAuth Apps, we revoke by deleting the authorization
            auth_string = f"{self.client_id}:{self.client_secret}"
            import base64
            encoded_auth = base64.b64encode(auth_string.encode()).decode()

            headers = {
                "Authorization": f"Basic {encoded_auth}",
                "User-Agent": "PromptRepo/1.0"
            }

            # This endpoint revokes all tokens for the OAuth app
            response = await self.http_client.delete(
                f"{self.API_BASE_URL}/applications/{self.client_id}/token",
                headers=headers,
                json={"access_token": access_token}
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
            True if token is valid
        """
        try:
            headers = {
                "Authorization": f"Bearer {access_token}",
                "User-Agent": "PromptRepo/1.0"
            }

            response = await self.http_client.get(
                f"{self.API_BASE_URL}/user",
                headers=headers
            )

            return response.status_code == 200

        except Exception:
            return False