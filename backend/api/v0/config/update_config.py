"""
Update configuration endpoint with standardized responses.
"""
import logging
from fastapi import APIRouter, Request, status

from schemas import AppConfig, HostingType
from services import ConfigStrategyFactory
from middlewares.rest import (
    StandardResponse,
    success_response,
    AuthorizationException,
    BadRequestException,
    AppException,
    ValidationException
)

logger = logging.getLogger(__name__)

router = APIRouter()

# TODO: Fix the hostingType to hostingConfig.type in front end
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
        403: {
            "description": "Configuration updates not allowed",
            "content": {
                "application/json": {
                    "example": {
                        "status": "error",
                        "type": "/errors/access-denied",
                        "title": "Access denied",
                        "detail": "Configuration updates are only allowed for individual hosting type"
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
    description="Update application configuration (partial update, only for individual hosting)",
)
async def update_config(
    configs_param: AppConfig,
    request: Request
) -> StandardResponse[AppConfig]:
    """
    Update application configuration (partial update).
    Only allowed for individual hosting type.
    
    Returns:
        StandardResponse[AppConfig]: Standardized response containing updated configuration
    
    Raises:
        AuthorizationException: When hosting type is not individual
        BadRequestException: When trying to set non-individual hosting type
        ValidationException: When configuration validation fails
        AppException: When configuration update fails
    """
    request_id = getattr(request.state, "request_id", None)
    
    try:
        config = ConfigStrategyFactory.get_strategy()
        current_hosting_type = config.get_hosting_config()

        # Check hosting types
        hosting_type = getattr(configs_param, 'hostingConfig', {}).get('type', '') or ''
        
        logger.info(
            f"Configuration update request received",
            extra={
                "request_id": request_id,
                "incoming_hosting_type": hosting_type,
                "current_hosting_type": str(current_hosting_type)
            }
        )
        
        # Validate hosting type - only allow saves for individual hosting
        if current_hosting_type != HostingType.INDIVIDUAL:
            logger.warning(
                f"Configuration update blocked - non-individual hosting type",
                extra={
                    "request_id": request_id,
                    "current_hosting_type": str(current_hosting_type)
                }
            )
            raise AuthorizationException(
                message=f"Configuration updates are only allowed for individual hosting type",
                context={"current_hosting_type": str(current_hosting_type)}
            )
        
        if hosting_type and hosting_type != HostingType.INDIVIDUAL:
            logger.warning(
                f"Configuration update blocked - attempting to set non-individual hosting",
                extra={
                    "request_id": request_id,
                    "requested_hosting_type": hosting_type
                }
            )
            raise BadRequestException(
                message="Configuration updates can only set hosting type to 'individual'",
                context={"requested_hosting_type": hosting_type}
            )
        
        # Validate individual hosting specific configuration
        _validate_individual_hosting_config(configs_param)
        
        # Update configuration
        config.set_llm_configs(getattr(configs_param, 'llmConfigs'))

        # Get and return the updated configuration
        updated_config = config.get_config()
        
        logger.info(
            "Configuration updated successfully",
            extra={
                "request_id": request_id,
                "hosting_type": str(current_hosting_type)
            }
        )
        
        return success_response(
            data=updated_config,
            message="Configuration updated successfully",
            meta={"request_id": request_id}
        )
        
    except (AuthorizationException, BadRequestException, ValidationException, AppException):
        # These will be handled by the global exception handlers
        raise
    except Exception as e:
        logger.error(
            f"Failed to update configuration: {str(e)}",
            exc_info=True,
            extra={"request_id": request_id}
        )
        raise AppException(
            message="Failed to update configuration",
            detail=str(e)
        )


def _validate_individual_hosting_config(configs_param: AppConfig):
    """
    Validates configuration for individual hosting type only.
    
    Raises:
        ValidationException: When validation fails
    """
    hosting_type = getattr(configs_param, 'hostingType', '') or ''
    
    if hosting_type != "individual":
        raise ValidationException(
            message="Only individual hosting type is supported for configuration updates",
            errors=[{
                "code": "INVALID_HOSTING_TYPE",
                "message": "Only individual hosting type is supported",
                "field": "hostingType",
                "context": {"provided_type": hosting_type}
            }]
        )
    
    # Individual hosting requires LLM configs
    llm_configs = getattr(configs_param, 'llmConfigs', []) or []
    if not llm_configs:
        raise ValidationException(
            message="Individual hosting requires at least one LLM configuration",
            errors=[{
                "code": "MISSING_LLM_CONFIG",
                "message": "At least one LLM configuration is required",
                "field": "llmConfigs"
            }]
        )
    
    # Validate uniqueness of LLM configurations
    _validate_llm_configs_uniqueness(llm_configs)


def _validate_llm_configs_uniqueness(llm_configs):
    """
    Validates that LLM configurations are unique based on the combination of
    provider, model, apiKey, and apiBaseUrl.
    
    Raises:
        ValidationException: When duplicate configurations are found
    """
    if not llm_configs:
        return
        
    seen_configs = set()
    
    for idx, config_item in enumerate(llm_configs):
        # Safely handle potential None values
        provider = getattr(config_item, 'provider', '') or ''
        model = getattr(config_item, 'model', '') or ''
        api_key = getattr(config_item, 'apiKey', '') or ''
        api_base_url = getattr(config_item, 'apiBaseUrl', '') or ''
        
        # Create a tuple to represent the unique combination
        config_key = (provider, model, api_key, api_base_url)
        
        if config_key in seen_configs:
            raise ValidationException(
                message="Duplicate LLM configuration found",
                errors=[{
                    "code": "DUPLICATE_CONFIG",
                    "message": "The combination of provider, model, API base URL, and API key must be unique",
                    "field": f"llmConfigs[{idx}]",
                    "context": {
                        "provider": provider,
                        "model": model
                    }
                }]
            )
        
        seen_configs.add(config_key)