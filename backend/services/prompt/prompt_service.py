"""
Main implementation of the Prompt Service.

Handles prompt operations across both individual and organization hosting types,
using constructor injection for all dependencies following SOLID principles.
"""

import json
import uuid
import yaml
import logging
from datetime import datetime
from pathlib import Path
from typing import List, Optional, Dict, Any, Union

from schemas.hosting_type_enum import HostingType
from services.config.config_interface import IConfig
from services.auth.session_service import SessionService
from services.git.git_service import GitService
from settings import settings

from .prompt_interface import IPromptService
from .prompt_discovery_service import PromptDiscoveryService
from .models import (
    Prompt,
    PromptCreate,
    PromptUpdate,
    PromptList,
    PromptSearchParams,
    PromptFile
)

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
        session_service: SessionService
    ):
        """
        Initialize PromptService with injected dependencies.
        
        Args:
            config_service: Configuration service for hosting type
            remote_repo_service: Service for discovering repositories
            session_service: Session service for user context
        """
        self.config_service = config_service
        self.session_service = session_service
        self.discovery_service = PromptDiscoveryService()
        
        # In-memory storage for prompts (would be database in production)
        self._prompts: Dict[str, Prompt] = {}
        
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
        """Save prompt data to a YAML file."""
        path = Path(file_path) if isinstance(file_path, str) else file_path
        
        try:
            path.parent.mkdir(parents=True, exist_ok=True)
            with open(path, 'w') as f:
                yaml.safe_dump(data, f)
            return True
        except Exception as e:
            logger.error(f"Failed to save prompt file {file_path}: {e}")
            return False
    
    def _load_prompt_file(self, file_path: Union[str, Path]) -> Optional[Dict[str, Any]]:
        """Load prompt data from a YAML file."""
        path = Path(file_path) if isinstance(file_path, str) else file_path
        
        if not path.exists():
            return None
            
        try:
            with open(path, 'r') as f:
                return yaml.safe_load(f)
        except Exception as e:
            logger.error(f"Failed to load prompt file {file_path}: {e}")
            return None
    
    def _generate_prompt_id(self, repo_name: str, file_path: str) -> str:
        """Generate a unique prompt ID based on repo and file path."""
        return f"{repo_name}:{file_path}:{uuid.uuid4().hex[:8]}"
    
    def _user_has_access(self, user_id: str, prompt: Prompt) -> bool:
        """
        Check if user has access to a prompt.
        
        In individual mode: all users have access
        In organization mode: only the owner has access
        """
        hosting_config = self.config_service.get_hosting_config()
        
        if hosting_config.type == HostingType.INDIVIDUAL:
            return True
        
        return prompt.owner == user_id
    
    async def create_prompt(
        self,
        user_id: str,
        prompt_data: PromptCreate
    ) -> Prompt:
        """Create a new prompt in the specified repository."""
        # Get repository base path
        repo_base_path = self._get_repo_base_path(user_id)
        repo_path = repo_base_path / prompt_data.repo_name
        
        if not repo_path.exists():
            raise ValueError(f"Repository {prompt_data.repo_name} not found")
        
        # Create prompt file content
        prompt_content = {
            "name": prompt_data.name,
            "description": prompt_data.description,
            "category": prompt_data.category,
            "tags": prompt_data.tags,
            "system_prompt": prompt_data.system_prompt,
            "user_prompt": prompt_data.user_prompt
        }
        
        # Add metadata if present
        if prompt_data.metadata:
            prompt_content.update(prompt_data.metadata)
        
        # Save to file
        file_path = repo_path / prompt_data.file_path
        
        # Save prompt file
        success = self._save_prompt_file(file_path, prompt_content)
        
        if not success:
            raise ValueError(f"Failed to save prompt to {prompt_data.file_path}")
        
        # Create Prompt object
        prompt = Prompt(
            id=self._generate_prompt_id(prompt_data.repo_name, prompt_data.file_path),
            name=prompt_data.name,
            description=prompt_data.description,
            content=json.dumps(prompt_content),
            repo_name=prompt_data.repo_name,
            file_path=prompt_data.file_path,
            category=prompt_data.category,
            tags=prompt_data.tags,
            system_prompt=prompt_data.system_prompt,
            user_prompt=prompt_data.user_prompt,
            owner=user_id if self.config_service.get_hosting_config().type == HostingType.ORGANIZATION else None,
            created_at=datetime.utcnow(),
            updated_at=datetime.utcnow()
        )
        
        # Store in memory
        self._prompts[prompt.id] = prompt
        
        logger.info(f"Created prompt {prompt.id} for user {user_id}")
        return prompt
    
    async def get_prompt(
        self,
        user_id: str,
        prompt_id: str
    ) -> Optional[Prompt]:
        """Get a single prompt by ID."""
        prompt = self._prompts.get(prompt_id)
        
        if not prompt:
            return None
        
        if not self._user_has_access(user_id, prompt):
            logger.warning(f"User {user_id} attempted to access prompt {prompt_id} without permission")
            return None
        
        return prompt
    
    async def update_prompt(
        self,
        user_id: str,
        prompt_id: str,
        prompt_data: PromptUpdate
    ) -> Optional[Prompt]:
        """Update an existing prompt."""
        prompt = await self.get_prompt(user_id, prompt_id)
        
        if not prompt:
            return None
        
        # Get repository base path
        repo_base_path = self._get_repo_base_path(user_id)
        repo_path = repo_base_path / prompt.repo_name
        file_path = repo_path / prompt.file_path
        
        # Load existing content
        existing_data = self._load_prompt_file(file_path)
        
        if not existing_data:
            logger.error(f"Could not load existing prompt file at {file_path}")
            return None
        
        # Update fields
        if prompt_data.name is not None:
            prompt.name = prompt_data.name
            existing_data["name"] = prompt_data.name
        
        if prompt_data.description is not None:
            prompt.description = prompt_data.description
            existing_data["description"] = prompt_data.description
        
        if prompt_data.category is not None:
            prompt.category = prompt_data.category
            existing_data["category"] = prompt_data.category
        
        if prompt_data.tags is not None:
            prompt.tags = prompt_data.tags
            existing_data["tags"] = prompt_data.tags
        
        if prompt_data.system_prompt is not None:
            prompt.system_prompt = prompt_data.system_prompt
            existing_data["system_prompt"] = prompt_data.system_prompt
        
        if prompt_data.user_prompt is not None:
            prompt.user_prompt = prompt_data.user_prompt
            existing_data["user_prompt"] = prompt_data.user_prompt
        
        if prompt_data.metadata:
            existing_data.update(prompt_data.metadata)
        
        # Save updated content
        success = self._save_prompt_file(file_path, existing_data)
        
        if not success:
            logger.error(f"Failed to save updated prompt to {file_path}")
            return None
        
        # Update prompt object
        prompt.content = json.dumps(existing_data)
        prompt.updated_at = datetime.utcnow()
        
        logger.info(f"Updated prompt {prompt_id} for user {user_id}")
        return prompt
    
    async def delete_prompt(
        self,
        user_id: str,
        prompt_id: str
    ) -> bool:
        """Delete a prompt."""
        prompt = await self.get_prompt(user_id, prompt_id)
        
        if not prompt:
            return False
        
        # Get repository base path
        repo_base_path = self._get_repo_base_path(user_id)
        repo_path = repo_base_path / prompt.repo_name
        file_path = repo_path / prompt.file_path
        
        # Delete the file
        try:
            if file_path.exists():
                file_path.unlink()
            
            # Remove from memory
            del self._prompts[prompt_id]
            
            logger.info(f"Deleted prompt {prompt_id} for user {user_id}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete prompt {prompt_id}: {e}")
            return False
    
    async def list_prompts(
        self,
        user_id: str,
        search_params: Optional[PromptSearchParams] = None
    ) -> PromptList:
        """List prompts accessible to the user with optional filtering."""
        if not search_params:
            # Use default values from the model
            search_params = PromptSearchParams()
        
        # Filter prompts based on access
        accessible_prompts = [
            prompt for prompt in self._prompts.values()
            if self._user_has_access(user_id, prompt)
        ]
        
        # Apply filters
        filtered_prompts = accessible_prompts
        
        if search_params.repo_name:
            filtered_prompts = [
                p for p in filtered_prompts
                if p.repo_name == search_params.repo_name
            ]
        
        if search_params.category:
            filtered_prompts = [
                p for p in filtered_prompts
                if p.category == search_params.category
            ]
        
        if search_params.tags:
            filtered_prompts = [
                p for p in filtered_prompts
                if any(tag in p.tags for tag in search_params.tags)
            ]
        
        if search_params.owner:
            filtered_prompts = [
                p for p in filtered_prompts
                if p.owner == search_params.owner
            ]
        
        if search_params.query:
            query = search_params.query.lower()
            filtered_prompts = [
                p for p in filtered_prompts
                if query in p.name.lower() or
                (p.description and query in p.description.lower())
            ]
        
        # Pagination
        total = len(filtered_prompts)
        start_idx = (search_params.page - 1) * search_params.page_size
        end_idx = start_idx + search_params.page_size
        paginated_prompts = filtered_prompts[start_idx:end_idx]
        
        return PromptList(
            prompts=paginated_prompts,
            total=total,
            page=search_params.page,
            page_size=search_params.page_size
        )
    
    async def list_repository_prompts(
        self,
        user_id: str,
        repo_name: str
    ) -> List[Prompt]:
        """List all prompts in a specific repository."""
        # Get repository base path
        repo_base_path = self._get_repo_base_path(user_id)
        repo_path = repo_base_path / repo_name
        
        if not repo_path.exists():
            raise ValueError(f"Repository {repo_name} not found")
        
        # Filter prompts by repository
        repo_prompts = [
            prompt for prompt in self._prompts.values()
            if prompt.repo_name == repo_name and self._user_has_access(user_id, prompt)
        ]
        
        return repo_prompts
    
    async def discover_prompts(
        self,
        user_id: str,
        repo_name: str
    ) -> List[PromptFile]:
        """Discover prompt files in a repository by scanning for YAML/YML files."""
        # Get repository base path
        repo_base_path = self._get_repo_base_path(user_id)
        repo_path = repo_base_path / repo_name
        
        if not repo_path.exists():
            raise ValueError(f"Repository {repo_name} not found")
        
        # Use discovery service to scan for prompts
        prompt_files = self.discovery_service.scan_repository(repo_path)
        
        logger.info(f"Discovered {len(prompt_files)} prompts in {repo_name} for user {user_id}")
        return prompt_files
    
    async def clone_repository_for_user(
        self,
        user_id: str,
        repo_name: str,
        clone_url: str,
        branch: Optional[str] = None
    ) -> Path:
        """Clone a repository to the appropriate path based on hosting type."""
        # Get repository base path
        repo_base_path = self._get_repo_base_path(user_id)
        
        # Ensure base path exists
        repo_base_path.mkdir(parents=True, exist_ok=True)
        
        # Target repository path
        repo_path = repo_base_path / repo_name
        
        # If repository already exists, pull latest changes
        if repo_path.exists():
            try:
                git_service = GitService(repo_path)
                # Get OAuth token from session if in organization mode
                oauth_token = None
                if self.config_service.get_hosting_config().type == HostingType.ORGANIZATION:
                    session = self.session_service.get_active_session(user_id)
                    if session:
                        oauth_token = session.oauth_token
                
                pull_result = git_service.pull_latest(oauth_token=oauth_token)
                if pull_result.success:
                    logger.info(f"Updated existing repository {repo_name} for user {user_id}")
                    return repo_path
            except Exception as e:
                logger.warning(f"Failed to pull latest changes for {repo_name}: {e}")
        
        # For now, if repo doesn't exist, raise an error (cloning not implemented in GitService)
        # In production, you would use gitpython or subprocess to clone the repository
        if not repo_path.exists():
            logger.error(f"Repository {repo_name} does not exist at {repo_path}")
            raise ValueError(f"Repository {repo_name} does not exist. Manual cloning required.")
        
        logger.info(f"Using existing repository {repo_name} for user {user_id} at {repo_path}")
        return repo_path
    
    async def sync_repository_prompts(
        self,
        user_id: str,
        repo_name: str
    ) -> int:
        """Sync prompts from a repository by discovering and storing them."""
        # Discover prompts in the repository
        prompt_files = await self.discover_prompts(user_id, repo_name)
        
        # Track synchronized prompts
        synced_count = 0
        existing_prompt_ids = set()
        
        for prompt_file in prompt_files:
            # Create a unique ID for the prompt
            prompt_id = self._generate_prompt_id(repo_name, prompt_file.path)
            
            # Check if prompt already exists
            existing_prompt = None
            for pid, prompt in self._prompts.items():
                if prompt.repo_name == repo_name and prompt.file_path == prompt_file.path:
                    existing_prompt = prompt
                    existing_prompt_ids.add(pid)
                    break
            
            # Parse metadata from content if available
            metadata = prompt_file.metadata or {}
            
            # Create or update prompt
            if existing_prompt:
                # Update existing prompt
                existing_prompt.name = prompt_file.name
                existing_prompt.content = prompt_file.content or json.dumps({
                    "system_prompt": prompt_file.system_prompt,
                    "user_prompt": prompt_file.user_prompt
                })
                existing_prompt.system_prompt = prompt_file.system_prompt
                existing_prompt.user_prompt = prompt_file.user_prompt
                existing_prompt.updated_at = datetime.utcnow()
                
                if "category" in metadata:
                    existing_prompt.category = metadata["category"]
                if "tags" in metadata:
                    existing_prompt.tags = metadata["tags"] if isinstance(metadata["tags"], list) else []
                
            else:
                # Create new prompt
                prompt = Prompt(
                    id=prompt_id,
                    name=prompt_file.name,
                    description=metadata.get("description"),
                    content=prompt_file.content or json.dumps({
                        "system_prompt": prompt_file.system_prompt,
                        "user_prompt": prompt_file.user_prompt
                    }),
                    repo_name=repo_name,
                    file_path=prompt_file.path,
                    category=metadata.get("category"),
                    tags=metadata.get("tags", []) if isinstance(metadata.get("tags"), list) else [],
                    system_prompt=prompt_file.system_prompt,
                    user_prompt=prompt_file.user_prompt,
                    owner=user_id if self.config_service.get_hosting_config().type == HostingType.ORGANIZATION else None,
                    created_at=datetime.utcnow(),
                    updated_at=datetime.utcnow()
                )
                
                self._prompts[prompt.id] = prompt
                existing_prompt_ids.add(prompt.id)
            
            synced_count += 1
        
        # Remove prompts that no longer exist in the repository
        prompts_to_remove = []
        for prompt_id, prompt in self._prompts.items():
            if prompt.repo_name == repo_name and prompt_id not in existing_prompt_ids:
                if self._user_has_access(user_id, prompt):
                    prompts_to_remove.append(prompt_id)
        
        for prompt_id in prompts_to_remove:
            del self._prompts[prompt_id]
            logger.info(f"Removed prompt {prompt_id} (no longer in repository)")
        
        logger.info(f"Synchronized {synced_count} prompts from {repo_name} for user {user_id}")
        return synced_count