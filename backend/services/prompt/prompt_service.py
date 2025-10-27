"""
Main implementation of the Prompt Service.

Handles prompt operations across both individual and organization hosting types,
using constructor injection for all dependencies following SOLID principles.
"""

import logging
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any, Union, Tuple

from schemas.artifact_type_enum import ArtifactType
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
from services.local_repo.models import PRInfo
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
        
    def _save_prompt_file(self, file_path: Union[str, Path], data: Dict[str, Any], exclusive: bool = False) -> bool:
        """Save prompt data to a YAML file using FileOperationsService.
        
        Args:
            file_path: Path to the YAML file
            data: Data to save as YAML
            exclusive: If True, fail atomically if file already exists
            
        Returns:
            bool: True if save was successful, False otherwise
            
        Raises:
            FileExistsError: If exclusive=True and file already exists
        """
        return self.file_ops.save_yaml_file(file_path, data, exclusive=exclusive)
    
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
    
    async def save_prompt(
        self,
        user_id: str,
        repo_name: str,
        file_path: str,
        prompt_data: Union[PromptData, PromptDataUpdate],
        oauth_token: Optional[str] = None,
        author_name: Optional[str] = None,
        author_email: Optional[str] = None,
        user_session = None
    ) -> Tuple[PromptMeta, Optional[PRInfo]]:
        """
        Save a prompt (create or update).
        
        If the file doesn't exist, creates a new prompt.
        If the file exists, updates the existing prompt.
        
        Args:
            user_id: User ID
            repo_name: Repository name
            file_path: File path relative to repository root
            prompt_data: Prompt data (PromptData for creation, PromptDataUpdate for updates)
            oauth_token: Optional OAuth token for git operations
            author_name: Optional git commit author name
            author_email: Optional git commit author email
            user_session: Optional user session for PR creation
            
        Returns:
            Tuple[PromptMeta, Optional[PRInfo]]: Saved prompt and PR info if created
        """
        # Get repository base path
        repo_base_path = self._get_repo_base_path(user_id)
        repo_path = repo_base_path / repo_name
        full_file_path = repo_path / file_path
        
        if not repo_path.exists():
            raise NotFoundException(
                resource="Repository",
                identifier=repo_name
            )
        
        # Check if file exists to determine create vs update
        is_update = full_file_path.exists()
        
        if is_update:
            # Update existing prompt
            existing_data = self._load_prompt_file(full_file_path)
            
            if not existing_data:
                logger.error(f"Could not load existing prompt file at {full_file_path}")
                raise AppException(
                    message=f"Failed to load existing prompt file at {file_path}"
                )
            
            # Update existing data with non-None values from prompt_data
            update_dict = prompt_data.model_dump(exclude_none=True, by_alias=False)
            existing_data.update(update_dict)
            
            # Update timestamp
            existing_data["updated_at"] = datetime.utcnow().isoformat()
            
            # Save updated content
            success = self._save_prompt_file(full_file_path, existing_data)
            
            if not success:
                logger.error(f"Failed to save updated prompt to {full_file_path}")
                raise AppException(
                    message=f"Failed to save updated prompt to {file_path}"
                )
        else:
            # Create new prompt
            # Ensure we have PromptData (not PromptDataUpdate) for creation
            if isinstance(prompt_data, PromptDataUpdate):
                # Convert PromptDataUpdate to PromptData by filling in required fields
                prompt_data = PromptData(
                    id="",  # Will be generated
                    name=prompt_data.name or "Untitled Prompt",
                    description=prompt_data.description or "",
                    provider=prompt_data.provider or "",
                    model=prompt_data.model or "",
                    prompt=prompt_data.prompt or "",
                    temperature=prompt_data.temperature if prompt_data.temperature is not None else 1.0,
                    top_p=prompt_data.top_p if prompt_data.top_p is not None else 1.0,
                    **prompt_data.model_dump(exclude_none=True, exclude={"name", "description", "provider", "model", "prompt", "temperature", "top_p"})
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
            
            # Save the file
            success = self._save_prompt_file(full_file_path, prompt_content)
            
            if not success:
                raise AppException(
                    message=f"Failed to save prompt to {file_path}"
                )
        
        # Handle git workflow (branch, commit, push, PR creation)
        pr_info = await self.local_repo_service.handle_git_workflow_after_save(
            user_id=user_id,
            repo_name=repo_name,
            file_path=file_path,
            artifact_type=ArtifactType.PROMPT,
            oauth_token=oauth_token,
            author_name=author_name,
            author_email=author_email,
            user_session=user_session
        )
        
        # Reload the prompt to get the latest state
        updated_prompt = await self.get_prompt(user_id, repo_name, file_path)
        
        if not updated_prompt:
            raise AppException(
                message=f"Failed to load saved prompt from {file_path}"
            )
        
        # Attach PR info to the PromptMeta if available
        if pr_info:
            updated_prompt.pr_info = pr_info.model_dump(mode='json')
        
        action = "Updated" if is_update else "Created"
        logger.info(f"{action} prompt {repo_name}:{file_path} for user {user_id}")
        
        return updated_prompt, pr_info
    
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
                temperature=yaml_data.get("temperature", 1.0),
                top_p=yaml_data.get("top_p", 1.0),
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
                tools=yaml_data.get("tools", []) if isinstance(yaml_data.get("tools"), list) else [],
                created_at=created_at,
                updated_at=updated_at
            )
            
            # Create PromptMeta
            prompt_meta = PromptMeta(
                prompt=prompt_data,
                recent_commits=recent_commits,
                repo_name=repo_name,
                file_path=file_path,
                pr_info=None
            )
            
            return prompt_meta
        except Exception as e:
            logger.error(f"Failed to get prompt {repo_name}:{file_path}: {e}")
            return None
    
    
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
        """
        Discover prompt files in a repository using the generalized artifact discovery.
        
        Uses LocalRepoService.discover_artifacts() to find all .prompt.yaml files
        in a single efficient scan.
        """
        # Use the generalized discovery from LocalRepoService
        discovery_result = self.local_repo_service.discover_artifacts(user_id, repo_name)
        
        # Get prompt file paths
        prompt_files = discovery_result.get_files_by_type(ArtifactType.PROMPT)
        
        # Convert file paths to PromptMeta objects
        prompt_metas = []
        for file_path in prompt_files:
            try:
                # Get the prompt using the existing get_prompt method
                prompt_meta = await self.get_prompt(user_id, repo_name, file_path)
                if prompt_meta:
                    prompt_metas.append(prompt_meta)
            except Exception as e:
                logger.warning(f"Failed to load prompt {file_path}: {e}")
                continue
        
        logger.info(f"Discovered {len(prompt_metas)} prompts in {repo_name} for user {user_id}")
        return prompt_metas