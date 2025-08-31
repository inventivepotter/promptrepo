# backend/settings/llm.py
from pydantic_settings import BaseSettings
from pydantic import Field
import json
from typing import List, Dict, Any


class LLMSettings(BaseSettings):
    """LLM Provider configuration settings"""
    
    # LLM Configuration (only for individual and organization hosting)
    llm_configs_json: str = Field(
        default="[]", 
        description="LLM configurations as JSON string", 
        alias="LLM_CONFIGS"
    )
    
    @property
    def llm_configs(self) -> List[Dict[str, Any]]:
        """Get parsed LLM configurations"""
        try:
            return json.loads(self.llm_configs_json) if self.llm_configs_json else []
        except json.JSONDecodeError:
            return []
    
    model_config = {
        "env_file": ".env",
        "env_file_encoding": "utf-8",
        "case_sensitive": False,
        "extra": "ignore"
    }