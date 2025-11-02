"""
Tools API endpoints for CRUD operations on mock tools.
Follows standardized response patterns with proper exception handling.
"""
import logging
import base64
from typing import List
from fastapi import APIRouter, Request, Query, status, Path

from api.deps import ToolMetaServiceDep, CurrentUserDep, CurrentSessionDep
from middlewares.rest import (
    StandardResponse,
    success_response,
    AppException,
    NotFoundException,
    ValidationException,
)
from services.artifacts.tool.models import (
    ToolMeta,
    ToolData
)

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get(
    "/",
    response_model=StandardResponse[List[ToolMeta]],
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
async def discover(
    request: Request,
    tool_meta_service: ToolMetaServiceDep,
    user_id: CurrentUserDep,
    repo_name: str = Query("default", description="Repository name")
) -> StandardResponse[List[ToolMeta]]:
    """
    List all tools in a repository.
    
    Returns:
        StandardResponse[List[ToolMeta]]: List of tool metadata
    
    Raises:
        AppException: When tool listing fails
    """
    request_id = request.state.request_id
    
    try:
        logger.info(
            f"Listing tools in repository: {repo_name}",
            extra={"request_id": request_id, "user_id": user_id, "repo_name": repo_name}
        )
        
        # Discover all tools in the repository
        tool_metas = await tool_meta_service.discover(user_id=user_id, repo_name=repo_name)
        
        logger.info(
            f"Successfully retrieved {len(tool_metas)} tools",
            extra={"request_id": request_id, "user_id": user_id, "tool_count": len(tool_metas)}
        )
        
        return success_response(
            data=tool_metas,
            message=f"Retrieved {len(tool_metas)} tools from repository '{repo_name}'",
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
    "/{repo_name}/{file_path}",
    response_model=StandardResponse[ToolMeta],
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
    description="Retrieve a specific tool definition by file path.",
)
async def get(
    request: Request,
    tool_meta_service: ToolMetaServiceDep,
    user_id: CurrentUserDep,
    repo_name: str = Path(..., description="Base64-encoded Repository name"),
    file_path: str = Path(..., description="Base64-encoded Tool file path")
) -> StandardResponse[ToolMeta]:
    """
    Get a specific tool definition.
    
    Returns:
        StandardResponse[ToolMeta]: Tool metadata
    
    Raises:
        NotFoundException: When tool is not found
        AppException: When retrieval fails
    """
    request_id = request.state.request_id
    
    try:
        # Decode base64-encoded reponame, file path
        decoded_repo_name = base64.b64decode(repo_name).decode('utf-8')
        decoded_file_path = base64.b64decode(file_path).decode('utf-8')
        
        logger.info(
            f"Retrieving tool from {decoded_file_path}",
            extra={"request_id": request_id, "user_id": user_id, "file_path": decoded_file_path, "repo_name": repo_name}
        )
        
        tool_meta = await tool_meta_service.get(user_id=user_id, repo_name=decoded_repo_name, file_path=decoded_file_path)
        
        if not tool_meta:
            raise NotFoundException(
                resource="Tool",
                identifier=decoded_file_path
            )
        
        logger.info(
            f"Successfully retrieved tool from {decoded_file_path}",
            extra={"request_id": request_id, "user_id": user_id, "file_path": decoded_file_path}
        )
        
        return success_response(
            data=tool_meta.model_dump(mode='json'),
            message=f"Tool retrieved successfully",
            meta={"request_id": request_id}
        )
        
    except (NotFoundException, AppException):
        raise
    except Exception as e:
        try:
            decoded_repo_name = base64.b64decode(repo_name).decode('utf-8')
            decoded_file_path = base64.b64decode(file_path).decode('utf-8')
        except:
            decoded_repo_name = repo_name
            decoded_file_path = file_path
        logger.error(
            f"Failed to retrieve tool from {decoded_file_path}: {str(e)}",
            exc_info=True,
            extra={"request_id": request_id, "user_id": user_id, "file_path": decoded_file_path}
        )
        raise AppException(
            message="Failed to retrieve tool",
            detail=str(e)
        )


@router.post(
    "/{repo_name}/{file_path}",
    response_model=StandardResponse[ToolMeta],
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
        404: {
            "description": "Repository not found",
            "content": {
                "application/json": {
                    "example": {
                        "status": "error",
                        "type": "/errors/not-found",
                        "title": "Not Found",
                        "detail": "Repository not found"
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
                        "detail": "Failed to save tool"
                    }
                }
            }
        }
    },
    summary="Save tool",
    description="Save a tool (create or update). Provide file_path for updates, or use 'new' for creation with auto-generated path.",
)
async def save(
    request: Request,
    tool_data: ToolData,
    tool_meta_service: ToolMetaServiceDep,
    user_id: CurrentUserDep,
    user_session: CurrentSessionDep,
    repo_name: str = Path(..., description="Base64-encoded repository name"),
    file_path: str = Path(..., description="Base64-encoded tool file path or 'new' for creation")
) -> StandardResponse[ToolMeta]:
    """
    Save a tool (create or update).
    
    If file_path is provided and not 'new', updates the existing tool.
    If file_path is 'new', creates a new tool with auto-generated path.
    
    Returns:
        StandardResponse[ToolMeta]: Saved tool metadata with PR info
    
    Raises:
        ValidationException: When tool validation fails
        NotFoundException: When repository not found
        AppException: When save operation fails
    """
    request_id = request.state.request_id
    
    try:
        # Decode base64-encoded repo_name
        decoded_repo_name = base64.b64decode(repo_name).decode('utf-8')
        
        # Decode base64-encoded file path if provided (skip for 'new')
        decoded_file_path = None
        if file_path and file_path not in ('new', 'null', 'undefined'):
            try:
                decoded_file_path = base64.b64decode(file_path).decode('utf-8')
            except:
                decoded_file_path = None
        
        action = "Updating" if decoded_file_path else "Creating"
        logger.info(
            f"{action} tool: {tool_data.tool.name}",
            extra={
                "request_id": request_id,
                "user_id": user_id,
                "tool_name": tool_data.tool.name,
                "repo_name": decoded_repo_name,
                "file_path": decoded_file_path
            }
        )
        
        # Get OAuth token and user info from session
        oauth_token = getattr(user_session, 'oauth_token', None)
        
        # Get user information for git commit author
        user = getattr(user_session, 'user', None)
        author_name = (getattr(user, 'oauth_name', None)
                       or getattr(user, 'oauth_username', None))
        author_email = getattr(user, 'oauth_email', None)
        
        # Save the tool with git workflow
        saved_tool_meta, pr_info = await tool_meta_service.save(
            user_id=user_id,
            repo_name=decoded_repo_name,
            artifact_data=tool_data,
            file_path=decoded_file_path,
            oauth_token=oauth_token,
            author_name=author_name,
            author_email=author_email,
            user_session=user_session
        )
        
        logger.info(
            f"Successfully saved tool: {tool_data.tool.name}",
            extra={"request_id": request_id, "user_id": user_id, "tool_name": tool_data.tool.name}
        )
        
        return success_response(
            data=saved_tool_meta.model_dump(mode='json'),
            message=f"Tool '{tool_data.tool.name}' saved successfully",
            meta={"request_id": request_id}
        )
        
    except ValidationException:
        logger.warning(
            f"Tool validation failed: {tool_data.tool.name}",
            extra={"request_id": request_id, "user_id": user_id, "tool_name": tool_data.tool.name}
        )
        raise
    except Exception as e:
        logger.error(
            f"Failed to create/update tool {tool_data.tool.name}: {str(e)}",
            exc_info=True,
            extra={"request_id": request_id, "user_id": user_id, "tool_name": tool_data.tool.name}
        )
        raise AppException(
            message="Failed to create/update tool",
            detail=str(e)
        )


@router.delete(
    "/{repo_name}/{file_path}",
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
async def delete(
    request: Request,
    tool_meta_service: ToolMetaServiceDep,
    user_id: CurrentUserDep,
    repo_name: str = Path(..., description="Repository name"),
    file_path: str = Path(..., description="Base64-encoded tool file path")
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
        # Decode base64-encoded repo_name and file path
        decoded_repo_name = base64.b64decode(repo_name).decode('utf-8')
        decoded_file_path = base64.b64decode(file_path).decode('utf-8')
        
        logger.info(
            f"Deleting tool from {decoded_file_path}",
            extra={"request_id": request_id, "user_id": user_id, "file_path": decoded_file_path, "repo_name": decoded_repo_name}
        )
        
        success = await tool_meta_service.delete(user_id=user_id, repo_name=decoded_repo_name, file_path=decoded_file_path)
        
        if not success:
            raise NotFoundException(
                resource="Tool",
                identifier=decoded_file_path
            )
        
        logger.info(
            f"Successfully deleted tool from {decoded_file_path}",
            extra={"request_id": request_id, "user_id": user_id, "file_path": decoded_file_path}
        )
        
        return success_response(
            data={"deleted": True, "file_path": decoded_file_path},
            message=f"Tool deleted successfully",
            meta={"request_id": request_id}
        )
        
    except (NotFoundException, AppException):
        raise
    except Exception as e:
        try:
            decoded_repo_name = base64.b64decode(repo_name).decode('utf-8')
            decoded_file_path = base64.b64decode(file_path).decode('utf-8')
        except:
            decoded_repo_name = repo_name
            decoded_file_path = file_path
        logger.error(
            f"Failed to delete tool from {decoded_file_path}: {str(e)}",
            exc_info=True,
            extra={"request_id": request_id, "user_id": user_id, "file_path": decoded_file_path}
        )
        raise AppException(
            message="Failed to delete tool",
            detail=str(e)
        )


@router.post(
    "/{repo_name}/{file_path}/validate",
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
async def validate(
    request: Request,
    tool_meta_service: ToolMetaServiceDep,
    user_id: CurrentUserDep,
    repo_name: str = Path(..., description="Repository name"),
    file_path: str = Path(..., description="Base64-encoded tool file path")
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
        # Decode base64-encoded repo_name and file path
        decoded_repo_name = base64.b64decode(repo_name).decode('utf-8')
        decoded_file_path = base64.b64decode(file_path).decode('utf-8')
        
        logger.info(
            f"Validating tool from {decoded_file_path}",
            extra={"request_id": request_id, "user_id": user_id, "file_path": decoded_file_path, "repo_name": decoded_repo_name}
        )
        
        # Load the tool
        tool_meta = await tool_meta_service.get(user_id=user_id, repo_name=decoded_repo_name, file_path=decoded_file_path)
        
        if not tool_meta:
            raise NotFoundException(
                resource="Tool",
                identifier=decoded_file_path
            )
        
        # Validate the tool
        tool_meta_service.validate(tool_meta.tool)
        
        logger.info(
            f"Tool validation successful for {decoded_file_path}",
            extra={"request_id": request_id, "user_id": user_id, "file_path": decoded_file_path}
        )
        
        return success_response(
            data={"valid": True, "file_path": decoded_file_path},
            message=f"Tool is valid",
            meta={"request_id": request_id}
        )
        
    except (NotFoundException, ValidationException):
        raise
    except Exception as e:
        try:
            decoded_repo_name = base64.b64decode(repo_name).decode('utf-8')
            decoded_file_path = base64.b64decode(file_path).decode('utf-8')
        except:
            decoded_repo_name = repo_name
            decoded_file_path = file_path
        logger.error(
            f"Failed to validate tool from {decoded_file_path}: {str(e)}",
            exc_info=True,
            extra={"request_id": request_id, "user_id": user_id, "file_path": decoded_file_path}
        )
        raise AppException(
            message="Failed to validate tool",
            detail=str(e)
        )