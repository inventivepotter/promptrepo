"""
Main implementation of the Prompt Service.

Handles prompt operations across both individual and organization hosting types,
using constructor injection for all dependencies following SOLID principles.
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any, Union

from schemas.hosting_type_enum import HostingType
from services.config.config_interface import IConfig
from services.local_repo.git_service import GitService
from services.local_repo.local_repo_service import LocalRepoService
from services.file_operations import FileOperationsService
from settings import settings
from middlewares.rest.exceptions import NotFoundException, AppException, ConflictException

from .prompt_interface import IPromptService
from .models import (
    PromptMeta,
    PromptData,
    PromptDataUpdate
)
from services.local_repo.models import CommitInfo

logger = logging.getLogger(__name__)


class PromptService(IPromptService):
    """
    Main prompt service implementation using constructor injection.
    
    This service handles:
    - CRUD operations for prompts
    - Repository cloning and management
    - User-scoped operations in organization mode
    - Prompt discovery and synchronization
    """
    
    def __init__(
        self,
        config_service: IConfig,
        file_ops_service: FileOperationsService,
        local_repo_service: LocalRepoService
    ):
        """
        Initialize PromptService with injected dependencies.
        
        Args:
            config_service: Configuration service for hosting type
            file_ops_service: File operations service for file I/O
            local_repo_service: Local repository service for git operations
        """
        self.config_service = config_service
        self.file_ops = file_ops_service
        self.local_repo_service = local_repo_service
        
    def _get_repo_base_path(self, user_id: str) -> Path:
        """
        Get the base repository path based on hosting type.
        
        Args:
            user_id: ID of the user
            
        Returns:
            Path object for the repository base directory
        """
        hosting_config = self.config_service.get_hosting_config()
        
        if hosting_config.type == HostingType.INDIVIDUAL:
            # Use local_repo_path for individual hosting
            return Path(settings.local_repo_path)
        else:
            # Use multi_user_repo_path with user scoping for organization
            return Path(settings.multi_user_repo_path) / user_id
        
    def _save_prompt_file(self, file_path: Union[str, Path], data: Dict[str, Any]) -> bool:
        """Save prompt data to a YAML file using FileOperationsService."""
        return self.file_ops.save_yaml_file(file_path, data)
    
    def _load_prompt_file(self, file_path: Union[str, Path]) -> Optional[Dict[str, Any]]:
        """Load prompt data from a YAML file using FileOperationsService."""
        return self.file_ops.load_yaml_file(file_path)
    
    def _generate_prompt_id(self, repo_name: str, file_path: str) -> str:
        """Generate a deterministic prompt ID based on repo and file path."""
        # Use a deterministic ID based on repo and file path
        return f"{repo_name}:{file_path}"
    
    def _get_file_commit_history(self, repo_path: Path, file_path: str, limit: int = 5) -> list[CommitInfo]:
        """Get commit history for a specific file using GitService."""
        try:
            git_service = GitService(repo_path)
            return git_service.get_file_commit_history(file_path, limit)
        except Exception as e:
            logger.warning(f"Failed to get commit history for {file_path}: {e}")
            return []
    
    async def create_prompt(
        self,
        user_id: str,
        repo_name: str,
        file_path: str,
        prompt_data: PromptData
    ) -> PromptMeta:
        """Create a new prompt in the specified repository."""
        # Get repository base path
        repo_base_path = self._get_repo_base_path(user_id)
        repo_path = repo_base_path / repo_name
        
        if not repo_path.exists():
            raise NotFoundException(
                resource="Repository",
                identifier=repo_name
            )
        
        # Check if file already exists
        full_file_path = repo_path / file_path
        if full_file_path.exists():
            raise ConflictException(
                message=f"Prompt file already exists at {file_path}",
                context={"repo_name": repo_name, "file_path": file_path}
            )
        
        # Set user field in organization mode
        if self.config_service.get_hosting_config().type == HostingType.ORGANIZATION:
            prompt_data.user = user_id
        
        # Set timestamps
        prompt_data.created_at = datetime.utcnow()
        prompt_data.updated_at = datetime.utcnow()
        
        # Generate ID based on repo and file path
        prompt_data.id = self._generate_prompt_id(repo_name, file_path)
        
        # Convert PromptData to dict for YAML serialization
        prompt_content = prompt_data.model_dump(exclude_none=True, by_alias=False)
        
        # Convert datetime objects to ISO strings for YAML
        if isinstance(prompt_content.get("created_at"), datetime):
            prompt_content["created_at"] = prompt_content["created_at"].isoformat()
        if isinstance(prompt_content.get("updated_at"), datetime):
            prompt_content["updated_at"] = prompt_content["updated_at"].isoformat()
        
        # Save to file (full_file_path already defined above)
        success = self._save_prompt_file(full_file_path, prompt_content)
        
        if not success:
            raise AppException(
                message=f"Failed to save prompt to {file_path}"
            )
        
        recent_commits = self._get_file_commit_history(repo_path, file_path)

        # Create PromptMeta object
        prompt_meta = PromptMeta(
            prompt=prompt_data,
            repo_name=repo_name,
            file_path=file_path,
            recent_commits=recent_commits
        )
        
        logger.info(f"Created prompt {prompt_data.id} for user {user_id}")
        return prompt_meta
    
    async def get_prompt(
        self,
        user_id: str,
        repo_name: str,
        file_path: str
    ) -> Optional[PromptMeta]:
        """Get a single prompt by repo_name and file_path."""
        try:
            # Get repository base path
            repo_base_path = self._get_repo_base_path(user_id)
            repo_path = repo_base_path / repo_name
            full_file_path = repo_path / file_path
            
            if not full_file_path.exists():
                return None
            
            # Load the prompt file
            yaml_data = self._load_prompt_file(full_file_path)
            if not yaml_data:
                return None
            
            # Get commit history for this file
            recent_commits = self._get_file_commit_history(repo_path, file_path)
            
            # Parse datetime fields
            created_at = yaml_data.get("created_at")
            if isinstance(created_at, str):
                created_at = datetime.fromisoformat(created_at)
            elif created_at is None:
                created_at = datetime.utcnow()
                
            updated_at = yaml_data.get("updated_at")
            if isinstance(updated_at, str):
                updated_at = datetime.fromisoformat(updated_at)
            elif updated_at is None:
                updated_at = datetime.utcnow()
            
            # Create PromptData from YAML
            prompt_data = PromptData(
                id=self._generate_prompt_id(repo_name, file_path),
                name=yaml_data.get("name", file_path),
                description=yaml_data.get("description"),
                provider=yaml_data.get("provider", ""),
                model=yaml_data.get("model", ""),
                failover_model=yaml_data.get("failover_model"),
                prompt=yaml_data.get("prompt", ""),
                tool_choice=yaml_data.get("tool_choice"),
                temperature=yaml_data.get("temperature", 0.0),
                top_p=yaml_data.get("top_p"),
                max_tokens=yaml_data.get("max_tokens"),
                response_format=yaml_data.get("response_format"),
                stream=yaml_data.get("stream"),
                n_completions=yaml_data.get("n_completions"),
                stop=yaml_data.get("stop"),
                presence_penalty=yaml_data.get("presence_penalty"),
                frequency_penalty=yaml_data.get("frequency_penalty"),
                seed=yaml_data.get("seed"),
                api_key=yaml_data.get("api_key"),
                api_base=yaml_data.get("api_base"),
                user=yaml_data.get("user"),
                parallel_tool_calls=yaml_data.get("parallel_tool_calls"),
                logprobs=yaml_data.get("logprobs"),
                top_logprobs=yaml_data.get("top_logprobs"),
                logit_bias=yaml_data.get("logit_bias"),
                stream_options=yaml_data.get("stream_options"),
                max_completion_tokens=yaml_data.get("max_completion_tokens"),
                reasoning_effort=yaml_data.get("reasoning_effort", "auto"),
                extra_args=yaml_data.get("extra_args"),
                tags=yaml_data.get("tags", []) if isinstance(yaml_data.get("tags"), list) else [],
                created_at=created_at,
                updated_at=updated_at
            )
            
            # Create PromptMeta
            prompt_meta = PromptMeta(
                prompt=prompt_data,
                recent_commits=recent_commits,
                repo_name=repo_name,
                file_path=file_path
            )
            
            return prompt_meta
        except Exception as e:
            logger.error(f"Failed to get prompt {repo_name}:{file_path}: {e}")
            return None
    
    async def update_prompt(
        self,
        user_id: str,
        repo_name: str,
        file_path: str,
        prompt_data: PromptDataUpdate,
        oauth_token: Optional[str] = None,
        author_name: Optional[str] = None,
        author_email: Optional[str] = None,
        user_session = None
    ) -> Optional[PromptMeta]:
        """
        Update an existing prompt.
        
        Args:
            user_id: User ID
            repo_name: Repository name
            file_path: File path relative to repository root
            prompt_data: Prompt data to update
            oauth_token: Optional OAuth token for git operations
            author_name: Optional git commit author name
            author_email: Optional git commit author email
            user_session: Optional user session for PR creation
        """
        # Get existing prompt
        prompt_meta = await self.get_prompt(user_id, repo_name, file_path)
        
        if not prompt_meta:
            return None
        
        # Get repository base path
        repo_base_path = self._get_repo_base_path(user_id)
        repo_path = repo_base_path / repo_name
        full_file_path = repo_path / file_path
        
        # Load existing content
        existing_data = self._load_prompt_file(full_file_path)
        
        if not existing_data:
            logger.error(f"Could not load existing prompt file at {full_file_path}")
            return None
        
        # Update existing data with non-None values from prompt_data
        update_dict = prompt_data.model_dump(exclude_none=True, by_alias=False)
        existing_data.update(update_dict)
        
        # Update timestamp
        existing_data["updated_at"] = datetime.utcnow().isoformat()
        
        # Save updated content
        success = self._save_prompt_file(full_file_path, existing_data)
        
        if not success:
            logger.error(f"Failed to save updated prompt to {full_file_path}")
            return None
        
        # Handle git workflow (branch, commit, push, PR creation)
        await self.local_repo_service.handle_git_workflow_after_save(
            user_id=user_id,
            repo_name=repo_name,
            file_path=file_path,
            oauth_token=oauth_token,
            author_name=author_name,
            author_email=author_email,
            user_session=user_session
        )
        
        # Return updated prompt
        logger.info(f"Updated prompt {repo_name}:{file_path} for user {user_id}")
        return await self.get_prompt(user_id, repo_name, file_path)
    
    async def delete_prompt(
        self,
        user_id: str,
        repo_name: str,
        file_path: str
    ) -> bool:
        """Delete a prompt."""
        prompt_meta = await self.get_prompt(user_id, repo_name, file_path)
        
        if not prompt_meta:
            return False
        
        # Get repository base path
        repo_base_path = self._get_repo_base_path(user_id)
        repo_path = repo_base_path / repo_name
        full_file_path = repo_path / file_path
        
        # Delete the file using FileOperationsService
        success = self.file_ops.delete_file(full_file_path)
        
        if success:
            logger.info(f"Deleted prompt {repo_name}:{file_path} for user {user_id}")
        else:
            logger.error(f"Failed to delete prompt {repo_name}:{file_path}")
        
        return success
    
    async def discover_prompts(
        self,
        user_id: str,
        repo_name: str
    ) -> List[PromptMeta]:
        """Discover prompt files in a repository by scanning for YAML/YML files and converting them to PromptMeta."""
        # Get repository base path
        repo_base_path = self._get_repo_base_path(user_id)
        repo_path = repo_base_path / repo_name
        
        # Check if repository exists, if not return empty list instead of raising exception
        # This prevents infinite loops when repos haven't been cloned yet
        if not repo_path.exists():
            logger.warning(f"Repository {repo_name} not found at {repo_path}, returning empty list")
            return []
        
        # Scan for all YAML/YML files
        prompt_metas = []
        for ext in ['.yaml', '.yml']:
            pattern = f"**/*{ext}"
            for file_path in repo_path.glob(pattern):
                # Skip hidden files and directories
                if any(part.startswith('.') for part in file_path.parts):
                    continue
                
                try:
                    # Get relative path
                    relative_path = str(file_path.relative_to(repo_path))
                    
                    # Load YAML file to validate it has required prompt fields
                    yaml_data = self._load_prompt_file(file_path)
                    if not yaml_data:
                        continue
                    
                    # Check for mandatory prompt fields
                    required_fields = ['name', 'provider', 'model', 'prompt']
                    has_required_fields = all(yaml_data.get(field) for field in required_fields)
                    
                    if not has_required_fields:
                        logger.debug(f"Skipping {relative_path}: missing required prompt fields")
                        continue
                    
                    # Get the prompt using the existing get_prompt method
                    prompt_meta = await self.get_prompt(user_id, repo_name, relative_path)
                    if prompt_meta:
                        prompt_metas.append(prompt_meta)
                except Exception as e:
                    logger.warning(f"Failed to load prompt {file_path}: {e}")
                    continue
        
        logger.info(f"Discovered {len(prompt_metas)} prompts in {repo_name} for user {user_id}")
        return prompt_metas