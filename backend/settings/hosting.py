# backend/settings/hosting.py
from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Literal


class HostingSettings(BaseSettings):
    """Hosting-specific configuration settings"""
    
    # Hosting Configuration
    hosting_type: Literal["individual", "organization", "multi-tenant"] = Field(
        default="individual", 
        description="Hosting type: individual, organization, or multi-tenant", 
        alias="HOSTING_TYPE"
    )
    
    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
        "extra": "ignore"
    }