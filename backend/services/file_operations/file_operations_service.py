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

logger = logging.getLogger(__name__)


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
    
    def save_yaml_file(self, path: Union[str, Path], data: Dict[str, Any], exclusive: bool = False) -> bool:
        """
        Save data to a YAML file.
        
        Args:
            path: Path to the YAML file
            data: Data to save as YAML
            exclusive: If True, fail if file already exists (atomic creation)
            
        Returns:
            bool: True if save was successful, False otherwise
            
        Raises:
            FileExistsError: If exclusive=True and file already exists
        """
        file_path = Path(path) if isinstance(path, str) else path
        
        try:
            # Create parent directories if they don't exist
            file_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Write YAML file with exclusive mode if requested
            mode = 'x' if exclusive else 'w'
            with open(file_path, mode) as f:
                yaml.safe_dump(data, f)
            
            logger.info(f"Saved YAML file: {file_path}")
            return True
        except FileExistsError:
            logger.warning(f"File already exists (exclusive mode): {file_path}")
            raise
        except Exception as e:
            logger.error(f"Failed to save YAML file {file_path}: {e}", exc_info=True)
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
            logger.info(f"Loaded YAML file: {file_path}")
            return data
        except Exception as e:
            logger.error(f"Failed to load YAML file {file_path}: {e}", exc_info=True)
            return None