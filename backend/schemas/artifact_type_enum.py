"""
Artifact Type Enum

Defines the types of artifacts that can be managed through the git workflow in PromptRepo.
"""
from enum import Enum


class ArtifactType(str, Enum):
    """Artifact types for git workflow operations in PromptRepo."""
    
    PROMPT = "prompt"
    TOOL = "tool"
    
    def __str__(self) -> str:
        """Return the string value of the enum."""
        return self.value