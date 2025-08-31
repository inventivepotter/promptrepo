"""
Update configuration endpoint.
"""
from fastapi import APIRouter, HTTPException, status, Depends
from typing import Optional
from sqlmodel import Session

from schemas.config import AppConfig
from .utils import update_env_vars_from_config, get_current_config, is_config_empty, validate_hosting_authorization
from .auth import get_bearer_token
from models.database import get_session
from settings.base_settings import settings

router = APIRouter()


@router.patch("/", response_model=AppConfig)
async def update_config(
    config: AppConfig,
    token: Optional[str] = Depends(get_bearer_token),
    db: Session = Depends(get_session)
):
    """
    Update application configuration (partial update)
    Requires admin privileges if configs are already available
    """
    try:
        current_config = get_current_config()
        
        # Validate hosting type - reject saves for non-individual hosting types
        hosting_type = getattr(config, 'hostingType', '') or ''
        
        if hosting_type != "individual":
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Configuration saves are only allowed for individual hosting. Please update your ENV restart the service for updating configs."
            )
        
        # If config is not empty, check authorization based on hosting type
        if not is_config_empty(current_config):
            # Use hosting-aware authorization validation
            await validate_hosting_authorization(current_config, token, db)
            
            # Validate hosting-type specific configurations
            _validate_hosting_specific_config(config)
            
            # Validate uniqueness of LLM configurations (only if they exist)
            if hasattr(config, 'llmConfigs') and config.llmConfigs:
                _validate_llm_configs_uniqueness(config.llmConfigs)
            
            # For individual hosting types, update .env file instead of os.environ
            update_env_vars_from_config(config)
        
        # Reload settings to reflect the changes
        # Note: In production, you might want to restart the application
        # or use a more sophisticated config reload mechanism
        
        # Return the updated config
        updated_config = get_current_config()
        return updated_config
        
    except HTTPException:
        # Re-raise HTTP exceptions (like 401)
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update config: {str(e)}"
        )


def _validate_hosting_specific_config(config: AppConfig):
    """
    Validates configuration based on hosting type requirements
    """
    hosting_type = getattr(config, 'hostingType', '') or ''
    
    if hosting_type == "individual":
        # Individual hosting requires LLM configs
        llm_configs = getattr(config, 'llmConfigs', []) or []
        if not llm_configs:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Individual hosting requires at least one LLM configuration."
            )
    elif hosting_type == "organization":
        # Organization hosting requires GitHub OAuth and LLM configs
        github_client_id = getattr(config, 'githubClientId', '') or ''
        github_client_secret = getattr(config, 'githubClientSecret', '') or ''
        llm_configs = getattr(config, 'llmConfigs', []) or []
        
        if not github_client_id or not github_client_secret:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Organization hosting requires GitHub OAuth credentials."
            )
        
        if not llm_configs:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Organization hosting requires at least one LLM configuration."
            )
    elif hosting_type == "multi-tenant":
        # Multi-tenant hosting doesn't require LLM configs globally
        pass
    else:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid hosting type. Must be 'individual', 'organization', or 'multi-tenant'."
        )


def _validate_llm_configs_uniqueness(llm_configs):
    """
    Validates that LLM configurations are unique based on the combination of
    provider, model, apiKey, and apiBaseUrl.
    """
    if not llm_configs:
        return
        
    seen_configs = set()
    
    for config in llm_configs:
        # Safely handle potential None values
        provider = getattr(config, 'provider', '') or ''
        model = getattr(config, 'model', '') or ''
        api_key = getattr(config, 'apiKey', '') or ''
        api_base_url = getattr(config, 'apiBaseUrl', '') or ''
        
        # Create a tuple to represent the unique combination
        config_key = (provider, model, api_key, api_base_url)
        
        if config_key in seen_configs:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Duplicate LLM configuration found. The combination of provider, model, API base URL, and API key must be unique."
            )
        
        seen_configs.add(config_key)