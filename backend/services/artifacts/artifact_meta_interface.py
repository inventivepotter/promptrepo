"""
Artifact Meta Service Interface

This module defines the interface that all artifact meta services (PromptMetaService,
ToolMetaService, EvalMetaService) should implement to ensure consistency and adherence
to SOLID principles.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Tuple, TypeVar, Generic
from pydantic import BaseModel

from services.local_repo.models import PRInfo

# Generic type for artifact data models
ArtifactDataType = TypeVar('ArtifactDataType', bound=BaseModel)
ArtifactMetaType = TypeVar('ArtifactMetaType', bound=BaseModel)


class ArtifactMetaInterface(ABC, Generic[ArtifactDataType, ArtifactMetaType]):
    """
    Interface for artifact meta services.
    
    All artifact meta services (Prompt, Tool, Eval) should implement this interface
    to provide consistent CRUD operations and discovery functionality.
    """
    
    @abstractmethod
    async def save(
        self,
        user_id: str,
        repo_name: str,
        artifact_data: ArtifactDataType,
        file_path: Optional[str] = None,
        oauth_token: Optional[str] = None,
        author_name: Optional[str] = None,
        author_email: Optional[str] = None,
        user_session = None
    ) -> Tuple[ArtifactMetaType, Optional[PRInfo]]:
        """
        Save an artifact (create or update).
        
        Args:
            user_id: User ID
            repo_name: Repository name
            artifact_data: Artifact data to save
            file_path: Optional file path for updates
            oauth_token: Optional OAuth token for git operations
            author_name: Optional git commit author name
            author_email: Optional git commit author email
            user_session: Optional user session for PR creation
            
        Returns:
            Tuple[ArtifactMetaType, Optional[PRInfo]]: Saved artifact metadata and PR info if created
        """
        pass
    
    @abstractmethod
    async def get(
        self,
        user_id: str,
        repo_name: str,
        file_path: str
    ) -> Optional[ArtifactMetaType]:
        """
        Get a single artifact by file path.
        
        Args:
            user_id: User ID
            repo_name: Repository name
            file_path: Relative path to artifact file from repo root
            
        Returns:
            Optional[ArtifactMetaType]: Artifact metadata if found, None otherwise
        """
        pass
    
    @abstractmethod
    async def delete(
        self,
        user_id: str,
        repo_name: str,
        file_path: str
    ) -> bool:
        """
        Delete an artifact.
        
        Args:
            user_id: User ID
            repo_name: Repository name
            file_path: Relative path to artifact file from repo root
            
        Returns:
            bool: True if deletion was successful, False otherwise
        """
        pass
    
    @abstractmethod
    async def discover(
        self,
        user_id: str,
        repo_name: str
    ) -> List[ArtifactMetaType]:
        """
        Discover all artifacts of this type in a repository.
        
        Args:
            user_id: User ID
            repo_name: Repository name
            
        Returns:
            List[ArtifactMetaType]: List of artifact metadata
        """
        pass
    
    @abstractmethod
    def validate(self, artifact_data: ArtifactDataType) -> ArtifactDataType:
        """
        Validate artifact data using Pydantic model.
        
        Args:
            artifact_data: The artifact data to validate
            
        Returns:
            ArtifactDataType: The validated artifact data
            
        Raises:
            ValidationException: If validation fails
        """
        pass