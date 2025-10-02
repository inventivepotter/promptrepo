"""
Prompt Service Package

This package provides services for discovering, managing, and handling prompts
in repositories across both individual and organization hosting types.
"""

from .models import (
    PromptMeta,
)
from .prompt_interface import IPromptService
from .prompt_service import PromptService

__all__ = [
    "PromptMeta",
    "IPromptService",
    "PromptService"
]