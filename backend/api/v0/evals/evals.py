"""
Eval CRUD endpoints with standardized responses.
"""
import logging
import base64
from typing import List
from fastapi import APIRouter, Request, status, Body, Query, Path

from services.artifacts.evals.models import EvalData, EvalMeta
from api.deps import EvalMetaServiceDep, CurrentUserDep, CurrentSessionDep
from middlewares.rest import (
    StandardResponse,
    success_response,
    AppException,
    NotFoundException
)

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get(
    "/",
    response_model=StandardResponse[List[EvalMeta]],
    status_code=status.HTTP_200_OK,
    responses={
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
                        "detail": "Failed to list evals"
                    }
                }
            }
        }
    },
    summary="List evals",
    description="Get list of all evals in a repository with summary information.",
)
async def discover(
    request: Request,
    eval_service: EvalMetaServiceDep,
    user_id: CurrentUserDep,
    repo_name: str = Query(..., description="Repository name")
) -> StandardResponse[List[EvalMeta]]:
    """
    List all evals in a repository.
    
    Returns:
        StandardResponse[List[EvalMeta]]: List of eval metadata

    Raises:
        NotFoundException: When repository doesn't exist
        AppException: When listing fails
    """
    request_id = request.state.request_id
    
    try:
        logger.info(
            f"Listing evals for repo {repo_name}",
            extra={"request_id": request_id, "user_id": user_id}
        )
        
        evals = await eval_service.discover(user_id=user_id, repo_name=repo_name)
        
        logger.info(
            f"Found {len(evals)} evals in {repo_name}",
            extra={"request_id": request_id, "user_id": user_id}
        )
        
        return success_response(
            data=evals,
            message=f"Found {len(evals)} evals",
            meta={"request_id": request_id}
        )
        
    except (NotFoundException, AppException):
        raise
    except Exception as e:
        logger.error(
            f"Failed to list evals: {str(e)}",
            exc_info=True,
            extra={"request_id": request_id, "user_id": user_id}
        )
        raise AppException(
            message="Failed to list evals",
            detail=str(e)
        )


@router.get(
    "/{repo_name}/{file_path}",
    response_model=StandardResponse[EvalMeta],
    status_code=status.HTTP_200_OK,
    responses={
        404: {
            "description": "Eval not found",
            "content": {
                "application/json": {
                    "example": {
                        "status": "error",
                        "type": "/errors/not-found",
                        "title": "Not Found",
                        "detail": "Eval not found"
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
                        "detail": "Failed to retrieve eval"
                    }
                }
            }
        }
    },
    summary="Get eval",
    description="Get detailed information about a specific eval including all eval definitions.",
)
async def get(
    request: Request,
    eval_service: EvalMetaServiceDep,
    user_id: CurrentUserDep,
    repo_name: str = Path(..., description="Base64-encoded repository name"),
    file_path: str = Path(..., description="Base64-encoded eval file path")
) -> StandardResponse[EvalMeta]:
    """
    Get specific eval definition.
    
    Returns:
        StandardResponse[EvalMeta]: Eval metadata
    
    Raises:
        NotFoundException: When eval doesn't exist
        AppException: When retrieval fails
    """
    request_id = request.state.request_id
    
    try:
        # Decode base64-encoded repo_name and file path
        decoded_repo_name = base64.b64decode(repo_name).decode('utf-8')
        decoded_file_path = base64.b64decode(file_path).decode('utf-8')
        
        logger.info(
            f"Getting eval from {decoded_file_path} in repo {decoded_repo_name}",
            extra={"request_id": request_id, "user_id": user_id, "file_path": decoded_file_path}
        )
        
        eval_meta = await eval_service.get(user_id=user_id, repo_name=decoded_repo_name, file_path=decoded_file_path)
        
        if not eval_meta:
            raise NotFoundException(
                resource="Eval",
                identifier=decoded_file_path
            )
        
        logger.info(
            f"Retrieved eval from {decoded_file_path}",
            extra={"request_id": request_id, "user_id": user_id, "file_path": decoded_file_path}
        )
        
        return success_response(
            data=eval_meta.model_dump(mode='json'),
            message="Eval retrieved successfully",
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
            f"Failed to get eval from {decoded_file_path}: {str(e)}",
            exc_info=True,
            extra={"request_id": request_id, "user_id": user_id, "file_path": decoded_file_path}
        )
        raise AppException(
            message="Failed to retrieve eval",
            detail=str(e)
        )


@router.post(
    "/{repo_name}/{file_path}",
    response_model=StandardResponse[EvalMeta],
    status_code=status.HTTP_200_OK,
    responses={
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
                        "detail": "Failed to save eval"
                    }
                }
            }
        }
    },
    summary="Create or update eval",
    description="Create a new eval or update an existing one. Provide file_path for updates, or use 'new' for creation with auto-generated path.",
)
async def save(
    request: Request,
    eval_service: EvalMetaServiceDep,
    user_id: CurrentUserDep,
    user_session: CurrentSessionDep,
    eval_data: EvalData = Body(...),
    repo_name: str = Path(..., description="Base64-encoded repository name"),
    file_path: str = Path(..., description="Base64-encoded eval file path or 'new' for creation")
) -> StandardResponse[EvalMeta]:
    """
    Create or update eval with git workflow integration.
    
    Returns:
        StandardResponse[EvalMeta]: Saved eval metadata
    
    Raises:
        NotFoundException: When repository doesn't exist
        AppException: When save fails
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
            f"{action} eval {eval_data.eval.name} in repo {decoded_repo_name}",
            extra={"request_id": request_id, "user_id": user_id, "repo_name": decoded_repo_name, "file_path": decoded_file_path}
        )
        
        # Get OAuth token and user info from session
        oauth_token = getattr(user_session, 'oauth_token', None)
        
        # Get user information for git commit author
        user = getattr(user_session, 'user', None)
        author_name = (getattr(user, 'oauth_name', None)
                       or getattr(user, 'oauth_username', None))
        author_email = getattr(user, 'oauth_email', None)
        
        saved_eval_meta, pr_info = await eval_service.save(
            user_id=user_id,
            repo_name=decoded_repo_name,
            artifact_data=eval_data,
            file_path=decoded_file_path,
            oauth_token=oauth_token,
            author_name=author_name,
            author_email=author_email,
            user_session=user_session
        )
        
        logger.info(
            f"Saved eval {eval_data.eval.name}",
            extra={"request_id": request_id, "user_id": user_id}
        )
        
        return success_response(
            data=saved_eval_meta.model_dump(mode='json'),
            message="Eval saved successfully",
            meta={"request_id": request_id}
        )
        
    except (NotFoundException, AppException):
        raise
    except Exception as e:
        logger.error(
            f"Failed to save eval {eval_data.eval.name}: {str(e)}",
            exc_info=True,
            extra={"request_id": request_id, "user_id": user_id}
        )
        raise AppException(
            message=f"Failed to save eval {eval_data.eval.name}",
            detail=str(e)
        )


@router.delete(
    "/{repo_name}/{file_path}",
    response_model=StandardResponse[dict],
    status_code=status.HTTP_200_OK,
    responses={
        404: {
            "description": "Eval not found",
            "content": {
                "application/json": {
                    "example": {
                        "status": "error",
                        "type": "/errors/not-found",
                        "title": "Not Found",
                        "detail": "Eval not found"
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
                        "detail": "Failed to delete eval"
                    }
                }
            }
        }
    },
    summary="Delete eval",
    description="Delete an eval and all its execution history.",
)
async def delete(
    request: Request,
    eval_service: EvalMetaServiceDep,
    user_id: CurrentUserDep,
    repo_name: str = Path(..., description="Base64-encoded repository name"),
    file_path: str = Path(..., description="Base64-encoded eval file path")
) -> StandardResponse[dict]:
    """
    Delete eval.
    
    Returns:
        StandardResponse[dict]: Deletion confirmation
    
    Raises:
        NotFoundException: When eval doesn't exist
        AppException: When deletion fails
    """
    request_id = request.state.request_id
    
    try:
        # Decode base64-encoded repo_name and file path
        decoded_repo_name = base64.b64decode(repo_name).decode('utf-8')
        decoded_file_path = base64.b64decode(file_path).decode('utf-8')
        
        logger.info(
            f"Deleting eval from {decoded_file_path} in repo {decoded_repo_name}",
            extra={"request_id": request_id, "user_id": user_id, "file_path": decoded_file_path}
        )
        
        success = await eval_service.delete(user_id=user_id, repo_name=decoded_repo_name, file_path=decoded_file_path)
        
        if not success:
            raise NotFoundException(
                resource="Eval",
                identifier=decoded_file_path
            )
        
        logger.info(
            f"Deleted eval from {decoded_file_path}",
            extra={"request_id": request_id, "user_id": user_id, "file_path": decoded_file_path}
        )
        
        return success_response(
            data={"deleted": True, "file_path": decoded_file_path},
            message="Eval deleted successfully",
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
            f"Failed to delete eval from {decoded_file_path}: {str(e)}",
            exc_info=True,
            extra={"request_id": request_id, "user_id": user_id, "file_path": decoded_file_path}
        )
        raise AppException(
            message="Failed to delete eval",
            detail=str(e)
        )