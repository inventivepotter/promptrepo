"""
Main implementation of the Prompt Service.

Handles prompt operations across both individual and organization hosting types,
using constructor injection for all dependencies following SOLID principles.
"""

import logging
from datetime import datetime, timezone
from typing import List, Optional, Union, Tuple

from schemas.artifact_type_enum import ArtifactType
from services.artifacts.artifact_meta_interface import ArtifactMetaInterface
from services.config.config_interface import IConfig
from middlewares.rest.exceptions import ValidationException
from services.local_repo.local_repo_service import LocalRepoService
from middlewares.rest.exceptions import NotFoundException, AppException
from .models import (
    PromptMeta,
    PromptData,
    PromptDataUpdate
)
from services.local_repo.models import PRInfo

logger = logging.getLogger(__name__)

PROMPT_FILE_SUFFIX = f".{ArtifactType.PROMPT}.yaml"

class PromptMetaService(ArtifactMetaInterface[PromptData, PromptMeta]):
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
        local_repo_service: LocalRepoService
    ):
        """
        Initialize PromptService with injected dependencies.
        
        Args:
            local_repo_service: Local repository service for git operations
        """
        self.local_repo_service = local_repo_service

    
    async def save(
        self,
        user_id: str,
        repo_name: str,
        artifact_data: Union[PromptData, PromptDataUpdate],
        file_path: str | None = None,
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
            prompt_data: Prompt data (PromptData for creation, PromptDataUpdate for updates)
            oauth_token: Optional OAuth token for git operations
            author_name: Optional git commit author name
            author_email: Optional git commit author email
            user_session: Optional user session for PR creation
            
        Returns:
            Tuple[PromptMeta, Optional[PRInfo]]: Saved prompt and PR info if created
        """
        # Get repository path using local_repo service
        repo_path = self.local_repo_service.get_repo_path(user_id, repo_name)
        
        if not repo_path.exists():
            raise NotFoundException(
                resource="Repository",
                identifier=repo_name
            )
        
        if isinstance(artifact_data, PromptDataUpdate):
            # Convert PromptDataUpdate to PromptData by filling in required fields
            artifact_data = PromptData(
                name=artifact_data.name or "Untitled Prompt",
                description=artifact_data.description or "",
                provider=artifact_data.provider or "",
                model=artifact_data.model or "",
                prompt=artifact_data.prompt or "",
                temperature=artifact_data.temperature if artifact_data.temperature is not None else 1.0,
                top_p=artifact_data.top_p if artifact_data.top_p is not None else 1.0,
                **artifact_data.model_dump(exclude_none=True, exclude={"name", "description", "provider", "model", "prompt", "temperature", "top_p"})
            )
            artifact_data.user = author_name
        
        artifact_data.updated_at = datetime.now(timezone.utc)

        
        # Convert PromptData to dict for YAML serialization
        prompt_content = artifact_data.model_dump(exclude_none=True, by_alias=False)
        
        # Convert datetime objects to ISO strings for YAML
        if isinstance(prompt_content.get("created_at"), datetime):
            prompt_content["created_at"] = prompt_content["created_at"].isoformat()
        if isinstance(prompt_content.get("updated_at"), datetime):
            prompt_content["updated_at"] = prompt_content["updated_at"].isoformat()
        
        # Save the artifact using LocalRepoService (includes git workflow)
        save_result = await self.local_repo_service.save_artifact(
            user_id=user_id,
            repo_name=repo_name,
            artifact_type=ArtifactType.PROMPT,
            artifact_name=prompt_content.get("name", "Untitled Prompt"),
            artifact_data=prompt_content,
            file_path=file_path if file_path else None,
            oauth_token=oauth_token,
            author_name=author_name,
            author_email=author_email,
            user_session=user_session
        )
        
        logger.info(f"Saved prompt {artifact_data.name} in {repo_name}")
        
        # Reload the prompt to get the latest state using the actual file path
        updated_prompt = await self.get(user_id, repo_name, save_result.file_path)
        
        if not updated_prompt:
            raise AppException(
                message=f"Failed to load saved prompt from {save_result.file_path}"
            )
        
        # Attach PR info to the PromptMeta if available
        if save_result.pr_info:
            updated_prompt.pr_info = save_result.pr_info.model_dump(mode='json')
        return updated_prompt, save_result.pr_info
    
    async def get(
        self,
        user_id: str,
        repo_name: str,
        file_path: str
    ) -> Optional[PromptMeta]:
        """Get a single prompt by repo_name and file_path."""
        try:
            # Get repository path using local_repo service
            repo_path = self.local_repo_service.get_repo_path(user_id, repo_name)
            
            # Load the prompt file
            yaml_data = self.local_repo_service.load_artifact(
                user_id=user_id,
                repo_name=repo_name,
                artifact_type=ArtifactType.PROMPT,
                file_path=file_path
            )
            if not yaml_data:
                return None
            
            # Get commit history for this file
            recent_commits = self.local_repo_service.get_file_commit_history(repo_path, file_path)
            
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
    
    
    async def delete(
        self,
        user_id: str,
        repo_name: str,
        file_path: str
    ) -> bool:
        """Delete a prompt."""
        prompt_meta = await self.get(user_id, repo_name, file_path)
        
        if not prompt_meta:
            return False
        
        # Get repository path using local_repo service
        repo_path = self.local_repo_service.get_repo_path(user_id, repo_name)
        full_file_path = repo_path / file_path
        
        # Delete the file
        try:
            full_file_path.unlink()
            logger.info(f"Deleted prompt {repo_name}:{file_path} for user {user_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete prompt {repo_name}:{file_path}: {e}")
            return False
    
    async def discover(
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
                prompt_meta = await self.get(user_id, repo_name, file_path)
                if prompt_meta:
                    prompt_metas.append(prompt_meta)
            except Exception as e:
                logger.warning(f"Failed to load prompt {file_path}: {e}")
                continue
        
        logger.info(f"Discovered {len(prompt_metas)} prompts in {repo_name} for user {user_id}")
        return prompt_metas
    
    def validate(self, artifact_data: Union[PromptData, PromptDataUpdate]) -> PromptData:
        """
        Validate prompt data using Pydantic model.
        
        Args:
            artifact_data: The prompt data to validate
            
        Returns:
            The validated prompt data as PromptData
            
        Raises:
            ValidationException: If validation fails
        """
        
        try:
            # Validate using Pydantic model
            if isinstance(artifact_data, PromptData):
                validated = PromptData.model_validate(artifact_data.model_dump())
            elif isinstance(artifact_data, PromptDataUpdate):
                # Convert PromptDataUpdate to PromptData
                validated = PromptData.model_validate(artifact_data.model_dump(exclude_none=True))
            else:
                # Handle dict input
                validated = PromptData.model_validate(artifact_data)
            
            logger.debug(f"Prompt data validated successfully")
            return validated
        except Exception as e:
            logger.error(f"Prompt validation failed: {str(e)}")
            raise ValidationException(f"Invalid prompt data: {str(e)}")