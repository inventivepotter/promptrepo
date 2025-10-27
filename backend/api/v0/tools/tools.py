"""
Tools API endpoints for CRUD operations on mock tools.
Follows standardized response patterns with proper exception handling.
"""
import logging
from typing import List
from fastapi import APIRouter, Request, Query, status

from api.deps import ToolServiceDep, CurrentUserDep, CurrentSessionDep
from middlewares.rest import (
    StandardResponse,
    success_response,
    AppException,
    NotFoundException,
    ValidationException,
    BadRequestException
)
from services.tool.models import (
    ToolDefinition,
    ToolSummary
)
from .models import (
    CreateToolRequest,
    MockExecutionRequest,
    MockExecutionResponse,
    ToolSaveResponse
)

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get(
    "/",
    response_model=StandardResponse[List[ToolSummary]],
    status_code=status.HTTP_200_OK,
    responses={
        500: {
            "description": "Internal server error",
            "content": {
                "application/json": {
                    "example": {
                        "status": "error",
                        "type": "/errors/internal-server-error",
                        "title": "Internal Server Error",
                        "detail": "Failed to retrieve tools"
                    }
                }
            }
        }
    },
    summary="List all tools",
    description="Retrieve a list of all tools in a repository.",
)
async def list_tools(
    request: Request,
    tool_service: ToolServiceDep,
    user_id: CurrentUserDep,
    repo_name: str = Query("default", description="Repository name")
) -> StandardResponse[List[ToolSummary]]:
    """
    List all tools in a repository.
    
    Returns:
        StandardResponse[List[ToolSummary]]: List of tool summaries
    
    Raises:
        AppException: When tool listing fails
    """
    request_id = request.state.request_id
    
    try:
        logger.info(
            f"Listing tools in repository: {repo_name}",
            extra={"request_id": request_id, "user_id": user_id, "repo_name": repo_name}
        )
        
        tools = tool_service.list_tools(repo_name=repo_name, user_id=user_id)
        
        logger.info(
            f"Successfully retrieved {len(tools)} tools",
            extra={"request_id": request_id, "user_id": user_id, "tool_count": len(tools)}
        )
        
        return success_response(
            data=tools,
            message=f"Retrieved {len(tools)} tools from repository '{repo_name}'",
            meta={"request_id": request_id, "repo_name": repo_name}
        )
        
    except Exception as e:
        logger.error(
            f"Failed to list tools: {str(e)}",
            exc_info=True,
            extra={"request_id": request_id, "user_id": user_id, "repo_name": repo_name}
        )
        raise AppException(
            message="Failed to retrieve tools",
            detail=str(e)
        )


@router.get(
    "/{tool_name}",
    response_model=StandardResponse[ToolDefinition],
    status_code=status.HTTP_200_OK,
    responses={
        404: {
            "description": "Tool not found",
            "content": {
                "application/json": {
                    "example": {
                        "status": "error",
                        "type": "/errors/not-found",
                        "title": "Not Found",
                        "detail": "Tool not found"
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
                        "detail": "Failed to retrieve tool"
                    }
                }
            }
        }
    },
    summary="Get tool definition",
    description="Retrieve a specific tool definition by name.",
)
async def get_tool(
    request: Request,
    tool_name: str,
    tool_service: ToolServiceDep,
    user_id: CurrentUserDep,
    repo_name: str = Query("default", description="Repository name")
) -> StandardResponse[ToolDefinition]:
    """
    Get a specific tool definition.
    
    Returns:
        StandardResponse[ToolDefinition]: Tool definition
    
    Raises:
        NotFoundException: When tool is not found
        AppException: When retrieval fails
    """
    request_id = request.state.request_id
    
    try:
        logger.info(
            f"Retrieving tool: {tool_name}",
            extra={"request_id": request_id, "user_id": user_id, "tool_name": tool_name, "repo_name": repo_name}
        )
        
        tool = tool_service.load_tool(tool_name=tool_name, repo_name=repo_name, user_id=user_id)
        
        logger.info(
            f"Successfully retrieved tool: {tool_name}",
            extra={"request_id": request_id, "user_id": user_id, "tool_name": tool_name}
        )
        
        return success_response(
            data=tool,
            message=f"Tool '{tool_name}' retrieved successfully",
            meta={"request_id": request_id, "repo_name": repo_name}
        )
        
    except NotFoundException:
        logger.warning(
            f"Tool not found: {tool_name}",
            extra={"request_id": request_id, "user_id": user_id, "tool_name": tool_name, "repo_name": repo_name}
        )
        raise
    except Exception as e:
        logger.error(
            f"Failed to retrieve tool {tool_name}: {str(e)}",
            exc_info=True,
            extra={"request_id": request_id, "user_id": user_id, "tool_name": tool_name}
        )
        raise AppException(
            message="Failed to retrieve tool",
            detail=str(e)
        )


@router.post(
    "/",
    response_model=StandardResponse[ToolSaveResponse],
    status_code=status.HTTP_201_CREATED,
    responses={
        422: {
            "description": "Validation error",
            "content": {
                "application/json": {
                    "example": {
                        "status": "error",
                        "type": "/errors/validation-error",
                        "title": "Validation Error",
                        "detail": "Tool validation failed"
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
                        "detail": "Failed to create tool"
                    }
                }
            }
        }
    },
    summary="Create or update tool",
    description="Create a new tool or update an existing tool definition.",
)
async def create_tool(
    request: Request,
    tool_request: CreateToolRequest,
    tool_service: ToolServiceDep,
    user_id: CurrentUserDep,
    user_session: CurrentSessionDep
) -> StandardResponse[ToolSaveResponse]:
    """
    Create or update a tool definition.
    
    Returns:
        StandardResponse[ToolSaveResponse]: Created/updated tool definition with PR info
    
    Raises:
        ValidationException: When tool validation fails
        AppException: When creation/update fails
    """
    request_id = request.state.request_id
    repo_name = tool_request.repo_name or "default"
    
    try:
        logger.info(
            f"Creating/updating tool: {tool_request.name}",
            extra={
                "request_id": request_id,
                "user_id": user_id,
                "tool_name": tool_request.name,
                "repo_name": repo_name
            }
        )
        
        # Create ToolDefinition from request
        tool = ToolDefinition(
            name=tool_request.name,
            description=tool_request.description,
            parameters=tool_request.parameters,
            mock=tool_request.mock
        )
        
        # Get OAuth token and user info from session
        oauth_token = getattr(user_session, 'oauth_token', None)
        
        # Get user information for git commit author
        user = getattr(user_session, 'user', None)
        author_name = (getattr(user, 'oauth_name', None)
                       or getattr(user, 'oauth_username', None))
        author_email = getattr(user, 'oauth_email', None)
        
        # Save the tool with git workflow
        saved_tool, pr_info = await tool_service.save_tool(
            tool=tool,
            repo_name=repo_name,
            user_id=user_id,
            oauth_token=oauth_token,
            author_name=author_name,
            author_email=author_email,
            user_session=user_session
        )
        
        logger.info(
            f"Successfully created/updated tool: {saved_tool.name}",
            extra={"request_id": request_id, "user_id": user_id, "tool_name": saved_tool.name}
        )
        
        # Create response with tool and PR info
        response_data = ToolSaveResponse(
            tool=saved_tool,
            pr_info=pr_info.model_dump(mode='json') if pr_info else None
        )
        
        return success_response(
            data=response_data,
            message=f"Tool '{saved_tool.name}' created/updated successfully",
            meta={"request_id": request_id, "repo_name": repo_name}
        )
        
    except ValidationException:
        logger.warning(
            f"Tool validation failed: {tool_request.name}",
            extra={"request_id": request_id, "user_id": user_id, "tool_name": tool_request.name}
        )
        raise
    except Exception as e:
        logger.error(
            f"Failed to create/update tool {tool_request.name}: {str(e)}",
            exc_info=True,
            extra={"request_id": request_id, "user_id": user_id, "tool_name": tool_request.name}
        )
        raise AppException(
            message="Failed to create/update tool",
            detail=str(e)
        )


@router.delete(
    "/{tool_name}",
    response_model=StandardResponse[dict],
    status_code=status.HTTP_200_OK,
    responses={
        404: {
            "description": "Tool not found",
            "content": {
                "application/json": {
                    "example": {
                        "status": "error",
                        "type": "/errors/not-found",
                        "title": "Not Found",
                        "detail": "Tool not found"
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
                        "detail": "Failed to delete tool"
                    }
                }
            }
        }
    },
    summary="Delete tool",
    description="Delete a tool definition from the repository.",
)
async def delete_tool(
    request: Request,
    tool_name: str,
    tool_service: ToolServiceDep,
    user_id: CurrentUserDep,
    repo_name: str = Query("default", description="Repository name")
) -> StandardResponse[dict]:
    """
    Delete a tool definition.
    
    Returns:
        StandardResponse[dict]: Deletion confirmation
    
    Raises:
        NotFoundException: When tool is not found
        AppException: When deletion fails
    """
    request_id = request.state.request_id
    
    try:
        logger.info(
            f"Deleting tool: {tool_name}",
            extra={"request_id": request_id, "user_id": user_id, "tool_name": tool_name, "repo_name": repo_name}
        )
        
        tool_service.delete_tool(tool_name=tool_name, repo_name=repo_name, user_id=user_id)
        
        logger.info(
            f"Successfully deleted tool: {tool_name}",
            extra={"request_id": request_id, "user_id": user_id, "tool_name": tool_name}
        )
        
        return success_response(
            data={"deleted": True, "tool_name": tool_name},
            message=f"Tool '{tool_name}' deleted successfully",
            meta={"request_id": request_id, "repo_name": repo_name}
        )
        
    except NotFoundException:
        logger.warning(
            f"Tool not found for deletion: {tool_name}",
            extra={"request_id": request_id, "user_id": user_id, "tool_name": tool_name}
        )
        raise
    except Exception as e:
        logger.error(
            f"Failed to delete tool {tool_name}: {str(e)}",
            exc_info=True,
            extra={"request_id": request_id, "user_id": user_id, "tool_name": tool_name}
        )
        raise AppException(
            message="Failed to delete tool",
            detail=str(e)
        )


@router.post(
    "/{tool_name}/validate",
    response_model=StandardResponse[dict],
    status_code=status.HTTP_200_OK,
    responses={
        422: {
            "description": "Validation error",
            "content": {
                "application/json": {
                    "example": {
                        "status": "error",
                        "type": "/errors/validation-error",
                        "title": "Validation Error",
                        "detail": "Tool validation failed"
                    }
                }
            }
        },
        404: {
            "description": "Tool not found",
            "content": {
                "application/json": {
                    "example": {
                        "status": "error",
                        "type": "/errors/not-found",
                        "title": "Not Found",
                        "detail": "Tool not found"
                    }
                }
            }
        }
    },
    summary="Validate tool definition",
    description="Validate a tool definition for correctness.",
)
async def validate_tool(
    request: Request,
    tool_name: str,
    tool_service: ToolServiceDep,
    user_id: CurrentUserDep,
    repo_name: str = Query("default", description="Repository name")
) -> StandardResponse[dict]:
    """
    Validate a tool definition.
    
    Returns:
        StandardResponse[dict]: Validation result
    
    Raises:
        NotFoundException: When tool is not found
        ValidationException: When validation fails
    """
    request_id = request.state.request_id
    
    try:
        logger.info(
            f"Validating tool: {tool_name}",
            extra={"request_id": request_id, "user_id": user_id, "tool_name": tool_name, "repo_name": repo_name}
        )
        
        # Load the tool
        tool = tool_service.load_tool(tool_name=tool_name, repo_name=repo_name, user_id=user_id)
        
        # Validate the tool
        tool_service.validate_tool(tool)
        
        logger.info(
            f"Tool validation successful: {tool_name}",
            extra={"request_id": request_id, "user_id": user_id, "tool_name": tool_name}
        )
        
        return success_response(
            data={"valid": True, "tool_name": tool_name},
            message=f"Tool '{tool_name}' is valid",
            meta={"request_id": request_id, "repo_name": repo_name}
        )
        
    except NotFoundException:
        logger.warning(
            f"Tool not found for validation: {tool_name}",
            extra={"request_id": request_id, "user_id": user_id, "tool_name": tool_name}
        )
        raise
    except ValidationException as e:
        logger.warning(
            f"Tool validation failed: {tool_name} - {str(e)}",
            extra={"request_id": request_id, "user_id": user_id, "tool_name": tool_name}
        )
        raise
    except Exception as e:
        logger.error(
            f"Failed to validate tool {tool_name}: {str(e)}",
            exc_info=True,
            extra={"request_id": request_id, "user_id": user_id, "tool_name": tool_name}
        )
        raise AppException(
            message="Failed to validate tool",
            detail=str(e)
        )


@router.post(
    "/{tool_name}/mock",
    response_model=StandardResponse[MockExecutionResponse],
    status_code=status.HTTP_200_OK,
    responses={
        404: {
            "description": "Tool not found",
            "content": {
                "application/json": {
                    "example": {
                        "status": "error",
                        "type": "/errors/not-found",
                        "title": "Not Found",
                        "detail": "Tool not found"
                    }
                }
            }
        },
        400: {
            "description": "Mock execution disabled",
            "content": {
                "application/json": {
                    "example": {
                        "status": "error",
                        "type": "/errors/bad-request",
                        "title": "Bad Request",
                        "detail": "Mock execution is disabled for this tool"
                    }
                }
            }
        }
    },
    summary="Execute mock response",
    description="Execute mock response for a tool with given parameters.",
)
async def execute_mock(
    request: Request,
    tool_name: str,
    mock_request: MockExecutionRequest,
    tool_service: ToolServiceDep,
    user_id: CurrentUserDep,
    repo_name: str = Query("default", description="Repository name")
) -> StandardResponse[MockExecutionResponse]:
    """
    Execute mock response for a tool.
    
    Returns:
        StandardResponse[MockExecutionResponse]: Mock execution result
    
    Raises:
        NotFoundException: When tool is not found
        BadRequestException: When mock is disabled
        AppException: When execution fails
    """
    request_id = request.state.request_id
    
    try:
        # Mask sensitive parameters before logging
        masked_params = {
            k: ("***" if k.lower() in {"token", "api_key", "password", "secret"} else v)
            for k, v in list(mock_request.parameters.items())[:20]
        }
        logger.info(
            f"Executing mock for tool: {tool_name}",
            extra={
                "request_id": request_id,
                "user_id": user_id,
                "tool_name": tool_name,
                "repo_name": repo_name,
                "parameters": masked_params
            }
        )
        
        # Load the tool
        tool = tool_service.load_tool(tool_name=tool_name, repo_name=repo_name, user_id=user_id)
        
        # Get mock response
        mock_response = tool_service.get_mock_response(tool)
        
        if mock_response is None:
            raise BadRequestException(
                message=f"Mock execution is disabled for tool '{tool_name}'",
                context={"tool_name": tool_name, "mock_enabled": False}
            )
        
        # Create response
        response = MockExecutionResponse(
            response=mock_response,
            tool_name=tool_name,
            parameters_used=mock_request.parameters
        )
        
        logger.info(
            f"Successfully executed mock for tool: {tool_name}",
            extra={"request_id": request_id, "user_id": user_id, "tool_name": tool_name}
        )
        
        return success_response(
            data=response,
            message=f"Mock executed successfully for tool '{tool_name}'",
            meta={"request_id": request_id, "repo_name": repo_name}
        )
        
    except NotFoundException:
        logger.warning(
            f"Tool not found for mock execution: {tool_name}",
            extra={"request_id": request_id, "user_id": user_id, "tool_name": tool_name}
        )
        raise
    except BadRequestException:
        raise
    except Exception as e:
        logger.error(
            f"Failed to execute mock for tool {tool_name}: {str(e)}",
            exc_info=True,
            extra={"request_id": request_id, "user_id": user_id, "tool_name": tool_name}
        )
        raise AppException(
            message="Failed to execute mock",
            detail=str(e)
        )