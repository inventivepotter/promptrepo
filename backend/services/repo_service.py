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