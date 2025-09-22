from abc import ABC, abstractmethod
from pathlib import Path
from typing import List, Dict, Optional, Any, Union
import yaml
import json
from datetime import datetime
from services.git.git_service import GitService, CommitInfo as GitCommitInfo
from .models import PromptFile, CommitInfo, UserCredentials

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
        self.git_service = GitService(self.repo_path)
        
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
                            content=json.dumps(data) if data else None,
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
            # Initialize git service for this specific repo
            git_service = GitService(repo_path)
            
            # Add all changes
            git_service.add_files(["."])
            
            # Commit changes
            commit_result = git_service.commit_changes(
                commit_message=commit_message,
                author_name=username,
                author_email=f"{username}@example.com"
            )
            
            if not commit_result.success:
                raise ValueError(f"Failed to commit changes: {commit_result.message}")
            
            # Push changes if remote exists
            push_result = git_service.push_branch(oauth_token=user_credentials.token)
            
            if not push_result.success:
                raise ValueError(f"Failed to push changes: {push_result.message}")
                
            # Get commit info from result
            commit_hash = commit_result.data.get("commit_hash", "") if commit_result.data else ""
            
            return CommitInfo(
                commit_id=commit_hash,
                message=commit_message,
                author=username,
                timestamp=datetime.now()  # Use current time as fallback
            )
        except Exception as e:
            raise ValueError(f"Failed to commit and push changes: {str(e)}")