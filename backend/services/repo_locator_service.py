from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Dict, Optional, Any, Union
from pydantic import BaseModel, Field, validator
import httpx
import git
import yaml
import json
import asyncio
from enum import Enum
from datetime import datetime
from settings.base_settings import Settings

class RepoInfo(BaseModel):
    name: str
    full_name: str
    clone_url: str
    owner: str
    private: bool = False
    default_branch: str = "main"
    language: Optional[str] = None
    size: int = 0
    updated_at: Optional[str] = None




class IRepoLocator(ABC):
    @abstractmethod
    async def get_repositories(self) -> Dict[str]:
        """Get list of available repositories"""
        pass



class LocalRepoLocator(IRepoLocator):
    def __init__(self):
        self.base_path = Settings.app_config.repo_path
        if not self.base_path.exists():
            self.base_path.mkdir(parents=True, exist_ok=True)


    async def get_repositories(self) -> Dict[str]:
        repos = {}
        for item in self.base_path.iterdir():
            if item.is_dir() and (item / ".git").exists():
                repos[item.name] = str(item.resolve())
        return repos


class GitHubRepoLocator(IRepoLocator):
    def __init__(self, username:str, oauth_token: str):
        self.base_path = Settings.app_config.repo_path
        self.oauth_token = oauth_token
        self.username = username
        if not self.base_path.exists():
            self.base_path.mkdir(parents=True, exist_ok=True)

    def _get_headers(self) -> Dict[str, str]:
        return {
            "Authorization": f"Bearer {self.oauth_token}",
            "Accept": "application/vnd.github.v3+json"
        }

    async def get_repositories(self) -> Dict[str]:
        repos = {}
        url = f"https://api.github.com/users/repos"
        async with httpx.AsyncClient() as client:
            response = await client.get(url, headers=self._get_headers())
            if response.status_code == 200:
                data = response.json()
                for repo in data:
                    name = repo["name"]
                    git_url = repo["clone_url"]
                    repos[name] = git_url
            else:
                raise ValueError(f"GitHub API error: {response.status_code} - {response.text}")
        return repos