"""
OAuth Enums

This module contains enumeration classes for OAuth-related functionality,
keeping them separate from models to avoid circular imports.
"""

from enum import Enum


class OAuthProvider(str, Enum):
    """Supported OAuth providers"""
    GITHUB = "github"
    GITLAB = "gitlab"
    BITBUCKET = "bitbucket"