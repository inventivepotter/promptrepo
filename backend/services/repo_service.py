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


class PromptFile(BaseModel):
    """Represents a prompt file found in a repository."""
    path: str
    name: str
    content: Optional[str] = None
    system_prompt: Optional[str] = None
    user_prompt: Optional[str] = None


class UserCredentials(BaseModel):
    """Represents user credentials for repository operations."""
    username: str
    token: str


class CommitInfo(BaseModel):
    """Represents information about a commit."""
    commit_id: str
    message: str
    author: str
    timestamp: datetime


class IRepoService(ABC):

    @abstractmethod
    def find_prompts(self, repo_name: str, username: str) -> List[PromptFile]:
        """Find YAML files containing system_prompt and user_prompt keys"""
        pass

    @abstractmethod
    def get_data(self, file_path: Union[str, Path]) -> Optional[Dict[str, Any]]:
        """Get data from file"""
        pass

    @abstractmethod
    def save_data(self, file_path: Union[str, Path], data: Any) -> bool:
        """Save data to file"""
        pass

    @abstractmethod
    def save_commit(self, username: str, repo_name: str,
                    commit_message: str, user_credentials: UserCredentials) -> CommitInfo:
        """Add, commit and push all changes"""
        pass


class RepoService(IRepoService):
    """
    Implementation of the repository service for handling repository operations.
    """
    def __init__(self, repo_path: Union[str, Path]):
        self.repo_path = Path(repo_path) if isinstance(repo_path, str) else repo_path
        
    def find_prompts(self, repo_name: str, username: str) -> List[PromptFile]:
        """Find YAML files containing system_prompt and user_prompt keys"""
        prompt_files = []
        repo_path = self.repo_path / repo_name
        
        if not repo_path.exists():
            return prompt_files
            
        for yaml_file in repo_path.rglob("*.yaml"):
            try:
                with open(yaml_file, 'r') as f:
                    data = yaml.safe_load(f)
                    if data and isinstance(data, dict) and \
                       ('system_prompt' in data or 'user_prompt' in data):
                        prompt_file = PromptFile(
                            path=str(yaml_file),
                            name=yaml_file.name,
                            content=data,
                            system_prompt=data.get('system_prompt'),
                            user_prompt=data.get('user_prompt')
                        )
                        prompt_files.append(prompt_file)
            except Exception:
                continue
                
        return prompt_files
        
    def get_data(self, file_path: Union[str, Path]) -> Optional[Dict[str, Any]]:
        """Get data from file"""
        path = Path(file_path) if isinstance(file_path, str) else file_path
        
        if not path.exists():
            return None
            
        try:
            with open(path, 'r') as f:
                if path.suffix.lower() == '.yaml' or path.suffix.lower() == '.yml':
                    return yaml.safe_load(f)
                elif path.suffix.lower() == '.json':
                    return json.load(f)
                else:
                    return {"content": f.read()}
        except Exception:
            return None
            
    def save_data(self, file_path: Union[str, Path], data: Any) -> bool:
        """Save data to file"""
        path = Path(file_path) if isinstance(file_path, str) else file_path
        
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            with open(path, 'w') as f:
                if path.suffix.lower() == '.yaml' or path.suffix.lower() == '.yml':
                    yaml.safe_dump(data, f)
                elif path.suffix.lower() == '.json':
                    json.dump(data, f, indent=2)
                else:
                    f.write(str(data))
            return True
        except Exception:
            return False
            
    def save_commit(self, username: str, repo_name: str,
                    commit_message: str, user_credentials: UserCredentials) -> CommitInfo:
        """Add, commit and push all changes"""
        repo_path = self.repo_path / repo_name
        
        try:
            repo = git.Repo(repo_path)
            
            # Add all changes
            repo.git.add(all=True)
            
            # Commit changes
            commit = repo.index.commit(commit_message, author=git.Actor(username, f"{username}@example.com"))
            
            # Push changes if remote exists
            if 'origin' in repo.remotes:
                origin = repo.remote(name='origin')
                origin.push()
                
            return CommitInfo(
                commit_id=commit.hexsha,
                message=commit.message,
                author=commit.author.name,
                timestamp=commit.authored_datetime
            )
        except Exception as e:
            raise ValueError(f"Failed to commit and push changes: {str(e)}")