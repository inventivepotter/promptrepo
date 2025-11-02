"""
File Operations Service

Provides centralized file and directory operations following SOLID principles.
Handles operations like:
- Deleting directories (e.g., repository folders)
- Saving/loading YAML files (e.g., prompts)
- Deleting files
"""

import logging
import shutil
import yaml
from pathlib import Path
from typing import Optional, Dict, Any, Union
from pydantic import BaseModel

from schemas.artifact_type_enum import ArtifactType
from settings import settings

logger = logging.getLogger(__name__)


class SavedFileData(BaseModel):
    """Result of saving an artifact with path information."""
    success: bool
    relative_path: str  # Full relative path including .yaml (e.g., "evals/strict-match/eval.yaml")
    directory_name: str  # Sanitized directory name (e.g., "strict-match")
    filename: str  # The filename used (e.g., "eval.yaml")

class FileOperationsService:
    """
    Service for handling file and directory operations.
    
    This service provides a centralized, testable interface for file operations,
    making it easier to mock in tests and maintain consistency across the codebase.
    """
    
    def delete_directory(self, path: Union[str, Path]) -> bool:
        """
        Delete a directory and all its contents.
        
        Args:
            path: Path to the directory to delete
            
        Returns:
            bool: True if deletion was successful, False otherwise
        """
        dir_path = Path(path) if isinstance(path, str) else path
        
        try:
            if dir_path.exists() and dir_path.is_dir():
                shutil.rmtree(dir_path)
                logger.info(f"Deleted directory: {dir_path}")
                return True
            else:
                logger.warning(f"Directory does not exist: {dir_path}")
                return False
        except Exception as e:
            logger.error(f"Failed to delete directory {dir_path}: {e}", exc_info=True)
            return False
    
    def delete_file(self, path: Union[str, Path]) -> bool:
        """
        Delete a file.
        
        Args:
            path: Path to the file to delete
            
        Returns:
            bool: True if deletion was successful, False otherwise
        """
        file_path = Path(path) if isinstance(path, str) else path
        
        try:
            if file_path.exists() and file_path.is_file():
                file_path.unlink()
                logger.info(f"Deleted file: {file_path}")
                return True
            else:
                logger.warning(f"File does not exist: {file_path}")
                return False
        except Exception as e:
            logger.error(f"Failed to delete file {file_path}: {e}", exc_info=True)
            return False
    
    def create_directory(self, path: Union[str, Path], parents: bool = True, exist_ok: bool = True) -> bool:
        """
        Create a directory.
        
        Args:
            path: Path to the directory to create
            parents: If True, create parent directories as needed
            exist_ok: If True, don't raise error if directory already exists
            
        Returns:
            bool: True if creation was successful, False otherwise
        """
        dir_path = Path(path) if isinstance(path, str) else path
        
        try:
            dir_path.mkdir(parents=parents, exist_ok=exist_ok)
            logger.info(f"Created directory: {dir_path}")
            return True
        except Exception as e:
            logger.error(f"Failed to create directory {dir_path}: {e}", exc_info=True)
            return False
    
    def load_yaml_file(self, path: Union[str, Path]) -> Optional[Dict[str, Any]]:
        """
        Load data from a YAML file.
        
        Args:
            path: Path to the YAML file
            
        Returns:
            Optional[Dict[str, Any]]: Loaded data or None if loading failed
        """
        file_path = Path(path) if isinstance(path, str) else path
        
        if not file_path.exists():
            logger.warning(f"YAML file does not exist: {file_path}")
            return None
        
        try:
            with open(file_path, 'r') as f:
                data = yaml.safe_load(f)
            return data
        except Exception as e:
            logger.error(f"Failed to load YAML file {file_path}: {e}", exc_info=True)
            return None
    
    def save_yaml_file(
        self,
        file_path: Path,
        data: Dict[str, Any],
        exclusive: bool = False
    ) -> SavedFileData:
        """
        Save YAML file to the specified path.
        
        Args:
            file_path: Full path to the file to save
            data: Data to save as YAML
            exclusive: If True, fail if file already exists
            
        Returns:
            SavedFileData with success status and path information
        """
        directory_path = file_path.parent
        filename = file_path.name

        try:
            # Create the directory
            directory_path.mkdir(parents=True, exist_ok=True)
            
            # Save the YAML file
            mode = 'x' if exclusive else 'w'
            with open(file_path, mode) as f:
                yaml.safe_dump(data, f)
            
            # Extract directory name from path
            dir_name = directory_path.name
            
            # Calculate relative path from repo root
            # The repo root is the directory containing the meta_directory (.promptrepo)
            relative_path = str(file_path)
            repo_root = None
            
            # Walk up the directory tree to find the repo root
            for parent in file_path.parents:
                if (parent / settings.meta_directory).exists():
                    # This parent directory contains .promptrepo, so it's the repo root
                    repo_root = parent
                    break
            
            if repo_root:
                relative_path = str(file_path.relative_to(repo_root))
            else:
                logger.warning(f"Could not find repo root for {file_path}, using absolute path")

            logger.info(f"Saved file '{filename}' to {file_path} (relative: {relative_path})")
            return SavedFileData(
                success=True,
                relative_path=relative_path,
                directory_name=dir_name,
                filename=filename
            )
            
        except FileExistsError:
            logger.warning(f"File already exists (exclusive mode): {file_path}")
            raise
        except Exception as e:
            logger.error(f"Failed to save file {file_path}: {e}", exc_info=True)
            return SavedFileData(
                success=False,
                relative_path=str(file_path),
                directory_name=directory_path.name,
                filename=filename
            )