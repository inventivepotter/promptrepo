"""
Service for discovering prompts in repositories.

This service scans repositories for YAML/YML files containing prompts,
following the Single Responsibility Principle (SRP).
"""

import json
import logging
import yaml
from pathlib import Path
from typing import List, Dict, Any, Optional

from .models import PromptFile

logger = logging.getLogger(__name__)


class PromptDiscoveryService:
    """
    Service responsible for discovering and parsing prompt files in repositories.
    
    This service:
    - Scans directories for YAML/YML files
    - Parses prompt content and metadata
    - Validates prompt structure
    - Extracts system and user prompts
    """
    
    # File extensions to scan
    PROMPT_EXTENSIONS = {'.yaml', '.yml'}
    
    # Required keys for a file to be considered a prompt
    PROMPT_KEYS = {'system_prompt', 'user_prompt'}
    
    def __init__(self):
        """Initialize the PromptDiscoveryService."""
        self.discovered_count = 0
        self.error_count = 0
    
    def scan_repository(self, repo_path: Path) -> List[PromptFile]:
        """
        Scan a repository for prompt files.
        
        Args:
            repo_path: Path to the repository to scan
            
        Returns:
            List of PromptFile objects discovered in the repository
        """
        if not repo_path.exists():
            logger.warning(f"Repository path does not exist: {repo_path}")
            return []
        
        prompt_files = []
        self.discovered_count = 0
        self.error_count = 0
        
        # Scan for YAML/YML files
        for ext in self.PROMPT_EXTENSIONS:
            pattern = f"**/*{ext}"
            for file_path in repo_path.glob(pattern):
                # Skip hidden files and directories
                if any(part.startswith('.') for part in file_path.parts):
                    continue
                
                # Try to parse the file
                prompt_file = self._parse_prompt_file(file_path, repo_path)
                if prompt_file:
                    prompt_files.append(prompt_file)
                    self.discovered_count += 1
        
        logger.info(
            f"Scanned {repo_path.name}: found {self.discovered_count} prompts, "
            f"{self.error_count} errors"
        )
        
        return prompt_files
    
    def _parse_prompt_file(
        self,
        file_path: Path,
        repo_path: Path
    ) -> Optional[PromptFile]:
        """
        Parse a single YAML/YML file to extract prompt data.
        
        Args:
            file_path: Path to the file to parse
            repo_path: Base repository path for relative path calculation
            
        Returns:
            PromptFile object if valid prompt file, None otherwise
        """
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                data = yaml.safe_load(f)
            
            if not isinstance(data, dict):
                return None
            
            # Check if file contains prompt keys
            has_prompt_keys = any(key in data for key in self.PROMPT_KEYS)
            if not has_prompt_keys:
                return None
            
            # Calculate relative path
            relative_path = str(file_path.relative_to(repo_path))
            
            # Extract prompt content
            system_prompt = data.get('system_prompt')
            user_prompt = data.get('user_prompt')
            
            # Extract metadata (all other keys)
            metadata = {
                k: v for k, v in data.items()
                if k not in {'system_prompt', 'user_prompt'}
            }
            
            # Create PromptFile object
            prompt_file = PromptFile(
                path=relative_path,
                name=file_path.stem,  # File name without extension
                content=json.dumps(data),
                system_prompt=system_prompt,
                user_prompt=user_prompt,
                metadata=metadata
            )
            
            logger.debug(f"Discovered prompt: {relative_path}")
            return prompt_file
            
        except yaml.YAMLError as e:
            logger.warning(f"Failed to parse YAML file {file_path}: {e}")
            self.error_count += 1
            return None
        except Exception as e:
            logger.error(f"Unexpected error parsing {file_path}: {e}")
            self.error_count += 1
            return None
    
    def validate_prompt_structure(self, prompt_data: Dict[str, Any]) -> bool:
        """
        Validate that prompt data has the required structure.
        
        Args:
            prompt_data: Dictionary containing prompt data
            
        Returns:
            True if valid prompt structure, False otherwise
        """
        # Must be a dictionary
        if not isinstance(prompt_data, dict):
            return False
        
        # Must have at least one prompt key
        has_prompt = any(key in prompt_data for key in self.PROMPT_KEYS)
        if not has_prompt:
            return False
        
        # Validate prompt values are strings if present
        for key in self.PROMPT_KEYS:
            if key in prompt_data:
                value = prompt_data[key]
                if value is not None and not isinstance(value, str):
                    return False
        
        return True
    
    def extract_prompt_metadata(self, prompt_data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Extract metadata from prompt data.
        
        Metadata includes all fields except system_prompt and user_prompt.
        
        Args:
            prompt_data: Dictionary containing prompt data
            
        Returns:
            Dictionary of metadata fields
        """
        metadata = {}
        
        # Common metadata fields to extract
        metadata_fields = [
            'name',
            'description',
            'category',
            'tags',
            'author',
            'version',
            'model',
            'temperature',
            'max_tokens',
            'examples',
            'variables',
            'instructions'
        ]
        
        for field in metadata_fields:
            if field in prompt_data:
                metadata[field] = prompt_data[field]
        
        # Also include any other non-prompt fields
        for key, value in prompt_data.items():
            if key not in self.PROMPT_KEYS and key not in metadata:
                metadata[key] = value
        
        return metadata
    
    def scan_directory_recursive(
        self,
        directory: Path,
        max_depth: int = 10
    ) -> List[PromptFile]:
        """
        Recursively scan a directory for prompt files with depth limit.
        
        Args:
            directory: Directory to scan
            max_depth: Maximum depth to recurse (default 10)
            
        Returns:
            List of PromptFile objects found
        """
        prompt_files = []
        
        def _scan(path: Path, current_depth: int = 0):
            if current_depth >= max_depth:
                return
            
            if not path.is_dir():
                return
            
            for item in path.iterdir():
                # Skip hidden files and directories
                if item.name.startswith('.'):
                    continue
                
                if item.is_file() and item.suffix in self.PROMPT_EXTENSIONS:
                    # Parse the file
                    prompt_file = self._parse_prompt_file(item, directory)
                    if prompt_file:
                        prompt_files.append(prompt_file)
                elif item.is_dir():
                    # Recurse into subdirectory
                    _scan(item, current_depth + 1)
        
        _scan(directory)
        return prompt_files
    
    def find_prompts_by_pattern(
        self,
        repo_path: Path,
        pattern: str = "*.prompt.yaml"
    ) -> List[PromptFile]:
        """
        Find prompts matching a specific naming pattern.
        
        Args:
            repo_path: Repository path to search
            pattern: Glob pattern to match (default "*.prompt.yaml")
            
        Returns:
            List of PromptFile objects matching the pattern
        """
        prompt_files = []
        
        for file_path in repo_path.glob(f"**/{pattern}"):
            # Skip hidden files
            if any(part.startswith('.') for part in file_path.parts):
                continue
            
            prompt_file = self._parse_prompt_file(file_path, repo_path)
            if prompt_file:
                prompt_files.append(prompt_file)
        
        return prompt_files
    
    def get_statistics(self) -> Dict[str, float]:
        """
        Get statistics from the last scan operation.
        
        Returns:
            Dictionary with scan statistics
        """
        return {
            "discovered": float(self.discovered_count),
            "errors": float(self.error_count),
            "success_rate": (
                self.discovered_count / (self.discovered_count + self.error_count)
                if (self.discovered_count + self.error_count) > 0
                else 0.0
            )
        }