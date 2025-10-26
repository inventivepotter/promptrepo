"""
Interface for Prompt Service following Interface Segregation Principle (ISP).

This interface defines the contract that all prompt service implementations
must follow, supporting both individual and organization hosting types.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Tuple, Union
from pathlib import Path

from .models import (
    PromptMeta,
    PromptData,
    PromptDataUpdate
)
from services.local_repo.models import PRInfo


class IPromptService(ABC):
    """
    Abstract base class defining the interface for prompt service operations.
    
    This interface supports:
    - CRUD operations for prompts
    - Repository scanning and discovery
    - User-scoped operations in organization mode
    - Both individual and organization hosting types
    """
    
    @abstractmethod
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
            user_id: ID of the user saving the prompt
            repo_name: Repository name where prompt will be stored
            file_path: File path within the repository
            prompt_data: Prompt data (PromptData for creation, PromptDataUpdate for updates)
            oauth_token: Optional OAuth token for git operations
            author_name: Optional git commit author name
            author_email: Optional git commit author email
            user_session: Optional user session for PR creation
            
        Returns:
            Tuple[PromptMeta, Optional[PRInfo]]: Saved prompt and PR info if created
            
        Raises:
            NotFoundException: If repository doesn't exist
            AppException: If save operation fails
        """
        pass
    
    @abstractmethod
    async def get_prompt(
        self,
        user_id: str,
        repo_name: str,
        file_path: str,
    ) -> Optional[PromptMeta]:
        """
        Get a single prompt by repo_name and file_path.
        
        Args:
            user_id: ID of the user requesting the prompt
            repo_name: Repository name
            file_path: File path within the repository
            
        Returns:
            Prompt object if found and user has access, None otherwise
        """
        pass
    
    @abstractmethod
    async def delete_prompt(
        self,
        user_id: str,
        repo_name: str,
        file_path: str,
    ) -> bool:
        """
        Delete a prompt.
        
        Args:
            user_id: ID of the user deleting the prompt
            prompt_id: ID of the prompt to delete
            
        Returns:
            True if deleted successfully, False otherwise
            
        Raises:
            ValueError: If user lacks permission to delete
        """
        pass

    @abstractmethod
    async def discover_prompts(
        self,
        user_id: str,
        repo_name: str
    ) -> List[PromptMeta]:
        """
        Discover prompt files in a repository by scanning for YAML/YML files.
        
        Args:
            user_id: ID of the user performing discovery
            repo_name: Name of the repository to scan
            
        Returns:
            List of PromptMeta objects found in the repository
            
        Raises:
            NotFoundException: If repository doesn't exist or user lacks access
        """
        pass
    