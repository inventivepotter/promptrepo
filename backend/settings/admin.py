# backend/settings/admin.py
from pydantic_settings import BaseSettings
from pydantic import Field
import json
from typing import List


class AdminSettings(BaseSettings):
    """Admin configuration settings"""
    
    # Admin Configuration  
    admin_emails: str = Field(
        default="[]", 
        description="Admin user emails as JSON string", 
        alias="ADMIN_EMAILS"
    )
    
    @property
    def admin_emails_list(self) -> List[str]:
        """Get parsed admin emails list"""
        try:
            return json.loads(self.admin_emails) if self.admin_emails else []
        except json.JSONDecodeError:
            return []
    
    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
        "extra": "ignore"
    }