"""
Update configuration endpoint with standardized responses.
"""
import logging
from fastapi import APIRouter, Request, status, Body

from services.config.models import AppConfig
from api.deps import ConfigServiceDep, CurrentUserDep
from middlewares.rest import (
    StandardResponse,
    success_response,
    AppException,
    ValidationException
)

logger = logging.getLogger(__name__)

router = APIRouter()

@router.patch(
    "/",
    response_model=StandardResponse[AppConfig],
    status_code=status.HTTP_200_OK,
    responses={
        400: {
            "description": "Invalid configuration data",
            "content": {
                "application/json": {
                    "example": {
                        "status": "error",
                        "type": "/errors/bad-request",
                        "title": "Bad request",
                        "detail": "Invalid configuration parameters"
                    }
                }
            }
        },
        422: {
            "description": "Validation error",
            "content": {
                "application/json": {
                    "example": {
                        "status": "error",
                        "type": "/errors/validation-failed",
                        "title": "Validation Error",
                        "detail": "The request contains invalid data"
                    }
                }
            }
        },
        500: {
            "description": "Internal server error",
            "content": {
                "application/json": {
                    "example": {
                        "status": "error",
                        "type": "/errors/internal-server-error",
                        "title": "Internal Server Error",
                        "detail": "Failed to update configuration"
                    }
                }
            }
        }
    },
    summary="Update configuration",
    description="Update application configuration including LLM and repository configurations (partial update).",
)
async def update_config(
    request: Request,
    config_service: ConfigServiceDep,
    user_id: CurrentUserDep,
    request_body: AppConfig = Body(...)
) -> StandardResponse[AppConfig]:
    """
    Update application configuration including LLM and repository configurations (partial update).
    
    Returns:
        StandardResponse[AppConfig]: Standardized response containing updated configuration
    
    Raises:
        ValidationException: When configuration validation fails
        AppException: When configuration update fails
    """
    request_id = request.state.request_id
    
    try:
        logger.info(
            f"Configuration update request received for user {user_id}",
            extra={
                "request_id": request_id,
            }
        )

        llm_configs = getattr(request_body, 'llm_configs', None)
        repo_configs = getattr(request_body, 'repo_configs', None)

        if llm_configs:
            _validate_llm_configs_uniqueness(llm_configs)

        if repo_configs:
            _validate_repo_configs_uniqueness(repo_configs)

        # Update configuration using the service method
        config_service.save_configs_for_api(
            user_id=user_id,
            llm_configs=llm_configs,
            repo_configs=repo_configs
        )

        # Get and return the updated configuration
        updated_config = config_service.get_configs_for_api(user_id=user_id)
        
        logger.info(
            f"Configuration updated successfully for user {user_id}",
            extra={
                "request_id": request_id,
            }
        )
        
        return success_response(
            data=updated_config,
            message="Configuration updated successfully",
            meta={"request_id": request_id}
        )
        
    except (ValidationException, AppException):
        # These will be handled by the global exception handlers
        raise
    except Exception as e:
        logger.error(
            f"Failed to update configuration for user {user_id}: {str(e)}",
            exc_info=True,
            extra={"request_id": request_id}
        )
        raise AppException(
            message="Failed to update configuration",
            detail=str(e)
        )


def _validate_llm_configs_uniqueness(llm_configs):
    """
    Validates that LLM configurations with scope=user are unique based on the combination of
    provider, model, api_key, and api_base_url.
    
    Raises:
        ValidationException: When duplicate configurations are found
    """
    if not llm_configs:
        return
        
    seen_configs = set()
    
    for idx, config_item in enumerate(llm_configs):
        # Only validate uniqueness for user-scoped configs
        scope = getattr(config_item, 'scope', '') or ''
        if scope != 'user':
            continue
            
        # Safely handle potential None values
        provider = getattr(config_item, 'provider', '') or ''
        model = getattr(config_item, 'model', '') or ''
        
        # Create a tuple to represent the unique combination
        config_key = (provider, model)
        
        if config_key in seen_configs:
            raise ValidationException(
                message="Duplicate LLM configuration found",
                errors=[{
                    "code": "DUPLICATE_CONFIG",
                    "message": "The combination of provider, model must be unique for user-scoped configurations",
                    "field": f"llm_configs[{idx}]",
                    "context": {
                        "provider": provider,
                        "model": model,
                        "scope": scope
                    }
                }]
            )
        
        seen_configs.add(config_key)


def _validate_repo_configs_uniqueness(repo_configs):
    """
    Validates that repository configurations are unique based on the combination of
    provider, repository URL, and access token.
    
    Raises:
        ValidationException: When duplicate configurations are found
    """
    if not repo_configs:
        return
        
    seen_configs = set()
    
    for idx, config_item in enumerate(repo_configs):
        # Safely handle potential None values
        provider = getattr(config_item, 'provider', '') or ''
        repo_url = getattr(config_item, 'repo_url', '') or ''
        access_token = getattr(config_item, 'access_token', '') or ''
        
        # Create a tuple to represent the unique combination
        config_key = (provider, repo_url, access_token)
        
        if config_key in seen_configs:
            raise ValidationException(
                message="Duplicate repository configuration found",
                errors=[{
                    "code": "DUPLICATE_CONFIG",
                    "message": "The combination of provider, repository URL, and access token must be unique",
                    "field": f"repo_configs[{idx}]",
                    "context": {
                        "provider": provider,
                        "repo_url": repo_url
                    }
                }]
            )
        
        seen_configs.add(config_key)