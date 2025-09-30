"""
Remote Repository Providers

This package contains different provider implementations for remote repositories.
"""

from services.remote_repo.providers.github_provider import GitHubRepoLocator
from services.remote_repo.providers.gitlab_provider import GitLabRepoLocator
from services.remote_repo.providers.bitbucket_provider import BitbucketRepoLocator

__all__ = [
    "GitHubRepoLocator",
    "GitLabRepoLocator",
    "BitbucketRepoLocator",
]