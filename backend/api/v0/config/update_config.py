"""
Update configuration endpoint.
"""
import logging
from fastapi import APIRouter, HTTPException, status

from schemas.config import AppConfig
from services.config import config_service

logger = logging.getLogger(__name__)

router = APIRouter()


@router.patch("/", response_model=AppConfig)
async def update_config(config: AppConfig):
    """
    Update application configuration (partial update)
    Only allowed for individual hosting type
    """
    try:
        # Check hosting types
        hosting_type = getattr(config, 'hostingType', '') or ''
        current_hosting_type = config_service.get_hosting_type()
        logger.info(f"update_config: Incoming config hosting type = '{hosting_type}'")
        logger.info(f"update_config: Current system hosting type = '{current_hosting_type}'")
        
        # Validate hosting type - only allow saves for individual hosting
        if current_hosting_type != "individual":
            logger.warning(f"update_config: Blocking update - system hosting type is not individual: {current_hosting_type}")
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Configuration updates are only allowed for individual hosting type. Current hosting type: {current_hosting_type}"
            )
        
        if hosting_type and hosting_type != "individual":
            logger.warning(f"update_config: Blocking update - incoming config tries to set non-individual hosting: {hosting_type}")
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Configuration updates can only set hosting type to 'individual'"
            )
        
        # Validate individual hosting specific configuration
        _validate_individual_hosting_config(config)
        
        # Update .env file for individual hosting
        config_service.update_env_vars_from_config(config)

        # Return the updated config
        updated_config = config_service.get_current_config()
        return updated_config
        
    except HTTPException:
        # Re-raise HTTP exceptions (like 400)
        raise
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Failed to update config: {str(e)}"
        )


def _validate_individual_hosting_config(config: AppConfig):
    """
    Validates configuration for individual hosting type only
    """
    hosting_type = getattr(config, 'hostingType', '') or ''
    
    if hosting_type != "individual":
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Only individual hosting type is supported for config updates."
        )
    
    # Individual hosting requires LLM configs
    llm_configs = getattr(config, 'llmConfigs', []) or []
    if not llm_configs:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Individual hosting requires at least one LLM configuration."
        )
    
    # Validate uniqueness of LLM configurations
    _validate_llm_configs_uniqueness(llm_configs)


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