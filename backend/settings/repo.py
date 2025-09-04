from pydantic import Field, validator, root_validator
from pydantic_settings import BaseSettings
from pathlib import Path
from typing import Optional, Dict, Any, List
from enum import Enum
import os


class HostingType(str, Enum):
    INDIVIDUAL = "individual"
    ORGANIZATION = "organization"


class RepoSettings(BaseSettings):
    """Repository management settings with Pydantic Settings"""

    # Core Repository Paths
    local_repo_path: Path = Field(
        default="",
        description="Path for individual local repositories"
    )

    multi_user_repo_path: Path = Field(
        default="",
        description="Path for multi-user repository workspaces"
    )