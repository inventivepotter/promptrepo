from typing import Optional
import reflex as rx
import httpx
from httpx import AsyncClient
import os
from dotenv import load_dotenv
import json

from promptrepo.schemas.user import User

load_dotenv()

CLIENT_ID = os.getenv("GITHUB_CLIENT_ID")
CLIENT_SECRET = os.getenv("GITHUB_CLIENT_SECRET")
SCOPE = "user,user:email,repo"
REDIRECT_URI = "http://localhost:3000/callback"

async def get_access_token(auth_code) -> str:
    token_url = "https://github.com/login/oauth/access_token"
    headers = {"Accept": "application/json"}
    data = {
        "client_id": CLIENT_ID,
        "client_secret": CLIENT_SECRET,
        "code": auth_code,
    }

    async with httpx.AsyncClient() as client:
        response = await client.post(token_url, headers=headers, json=data)
        response.raise_for_status()
        token_data = response.json()
        return token_data.get("access_token", "")

class AuthState(rx.State):
    """State for GitHub OAuth."""
    access_token: str = rx.LocalStorage()

    @rx.event
    def login(self):
        return rx.redirect(
            f"https://github.com/login/oauth/authorize?client_id={CLIENT_ID}&scope={SCOPE}&redirect_uri={REDIRECT_URI}"
        )

    @rx.event
    async def callback(self):
        oauth_code: str = str(self.router_data.get("query", {}).get("code", ""))
        print(f"DEBUG: Extracted OAuth code: {oauth_code}")
        if oauth_code:
            self.access_token = await get_access_token(oauth_code)
            print(f"DEBUG: Obtained access token: {self.access_token}")
            data = await self.user
            print(f"DEBUG: Fetched user info: {data}")
        return rx.redirect("/")

    @rx.event
    async def logout(self):
        self.access_token = ""
        await self.user
        return rx.redirect("/")

    @rx.var(cache=True)
    async def user(self) -> Optional[User]:
        if self.access_token:
            user_url = "https://api.github.com/user"
            headers = {
                "Authorization": f"Bearer {self.access_token}",
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28"
            }

            async with httpx.AsyncClient() as client:
                response = await client.get(user_url, headers=headers)
                response.raise_for_status()
                user_data = response.json()
                return User(
                    login=user_data.get("login"),
                    name=user_data.get("name"),
                    avatar_url=user_data.get("avatar_url"),
                    url=user_data.get("html_url"),
                    email=user_data.get("email"),
                )
        return None