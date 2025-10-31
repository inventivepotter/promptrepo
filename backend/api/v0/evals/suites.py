"""
Eval CRUD endpoints with standardized responses.
"""
import logging
from typing import List
from fastapi import APIRouter, Request, status, Body, Query

from services.evals.models import EvalData, EvalSummary
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
    "",
    response_model=StandardResponse[List[EvalSummary]],
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
async def list_evals(
    request: Request,
    eval_service: EvalMetaServiceDep,
    user_id: CurrentUserDep,
    repo_name: str = Query(..., description="Repository name")
) -> StandardResponse[List[EvalSummary]]:
    """
    List all evals in a repository.
    
    Returns:
        StandardResponse[List[EvalSummary]]: List of eval summaries

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
        
        evals = await eval_service.list_evals(user_id, repo_name)
        
        logger.info(
            f"Found {len(evals)} evals in {repo_name}",
            extra={"request_id": request_id, "user_id": user_id}
        )
        
        return success_response(
            data=evals,
            message=f"Found {len(evals)} eval suites",
            meta={"request_id": request_id}
        )
        
    except (NotFoundException, AppException):
        raise
    except Exception as e:
        logger.error(
            f"Failed to list eval suites: {str(e)}",
            exc_info=True,
            extra={"request_id": request_id, "user_id": user_id}
        )
        raise AppException(
            message="Failed to list eval suites",
            detail=str(e)
        )


@router.get(
    "/{eval_name}",
    response_model=StandardResponse[EvalData],
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
                        "detail": "Eval suite not found"
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
async def get_eval(
    request: Request,
    eval_service: EvalMetaServiceDep,
    user_id: CurrentUserDep,
    name: str,
    repo_name: str = Query(..., description="Repository name")
) -> StandardResponse[EvalData]:
    """
    Get specific eval suite definition.
    
    Returns:
        StandardResponse[EvalSuiteData]: Eval suite definition
    
    Raises:
        NotFoundException: When suite doesn't exist
        AppException: When retrieval fails
    """
    request_id = request.state.request_id
    
    try:
        logger.info(
            f"Getting eval suite {name} from repo {repo_name}",
            extra={"request_id": request_id, "user_id": user_id}
        )
        
        eval_data = await eval_service.get_eval(user_id, repo_name, name)
        
        logger.info(
            f"Retrieved eval suite {name}",
            extra={"request_id": request_id, "user_id": user_id}
        )
        
        return success_response(
            data=eval_data,
            message="Eval retrieved successfully",
            meta={"request_id": request_id}
        )
        
    except (NotFoundException, AppException):
        raise
    except Exception as e:
        logger.error(
            f"Failed to get eval suite {name}: {str(e)}",
            exc_info=True,
            extra={"request_id": request_id, "user_id": user_id}
        )
        raise AppException(
            message=f"Failed to retrieve eval suite {name}",
            detail=str(e)
        )


@router.post(
    "",
    response_model=StandardResponse[EvalData],
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
                        "detail": "Failed to save eval suite"
                    }
                }
            }
        }
    },
    summary="Create or update eval suite",
    description="Create a new eval suite or update an existing one. The suite name is taken from the request body.",
)
async def save_eval(
    request: Request,
    eval_service: EvalMetaServiceDep,
    user_id: CurrentUserDep,
    user_session: CurrentSessionDep,
    eval_data: EvalData = Body(...),
    repo_name: str = Query(..., description="Repository name")
) -> StandardResponse[EvalData]:
    """
    Create or update eval suite with git workflow integration.
    
    Returns:
        StandardResponse[EvalSuiteData]: Saved eval suite
    
    Raises:
        NotFoundException: When repository doesn't exist
        AppException: When save fails
    """
    request_id = request.state.request_id
    
    try:
        logger.info(
            f"Saving eval suite {eval_data.eval.name} to repo {repo_name}",
            extra={"request_id": request_id, "user_id": user_id}
        )
        
        # Get OAuth token and user info from session
        oauth_token = getattr(user_session, 'oauth_token', None)
        
        # Get user information for git commit author
        user = user_session.user if hasattr(user_session, 'user') else None
        author_name = user.oauth_name or user.oauth_username if user else None
        author_email = user.oauth_email if user else None
        
        saved_eval, pr_info = await eval_service.save_eval(
            user_id=user_id,
            repo_name=repo_name,
            eval_data=eval_data,
            oauth_token=oauth_token,
            author_name=author_name,
            author_email=author_email,
            user_session=user_session
        )
        
        logger.info(
            f"Saved eval suite {eval_data.eval.name}",
            extra={"request_id": request_id, "user_id": user_id}
        )
        
        return success_response(
            data=saved_eval,
            message="Eval saved successfully",
            meta={"request_id": request_id}
        )
        
    except (NotFoundException, AppException):
        raise
    except Exception as e:
        logger.error(
            f"Failed to save eval suite {eval_data.eval.name}: {str(e)}",
            exc_info=True,
            extra={"request_id": request_id, "user_id": user_id}
        )
        raise AppException(
            message=f"Failed to save eval suite {eval_data.eval.name}",
            detail=str(e)
        )


@router.delete(
    "/{eval_name}",
    response_model=StandardResponse[dict],
    status_code=status.HTTP_200_OK,
    responses={
        404: {
            "description": "Eval suite not found",
            "content": {
                "application/json": {
                    "example": {
                        "status": "error",
                        "type": "/errors/not-found",
                        "title": "Not Found",
                        "detail": "Eval suite not found"
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
                        "detail": "Failed to delete eval suite"
                    }
                }
            }
        }
    },
    summary="Delete eval suite",
    description="Delete an eval suite and all its execution history.",
)
async def delete_eval(
    request: Request,
    eval_service: EvalMetaServiceDep,
    user_id: CurrentUserDep,
    name: str,
    repo_name: str = Query(..., description="Repository name")
) -> StandardResponse[dict]:
    """
    Delete eval suite.
    
    Returns:
        StandardResponse[dict]: Deletion confirmation
    
    Raises:
        NotFoundException: When suite doesn't exist
        AppException: When deletion fails
    """
    request_id = request.state.request_id
    
    try:
        logger.info(
            f"Deleting eval suite {name} from repo {repo_name}",
            extra={"request_id": request_id, "user_id": user_id}
        )
        
        success = await eval_service.delete_eval(user_id, repo_name, name)
        
        if not success:
            raise AppException(
                message=f"Failed to delete eval suite {name}"
            )
        
        logger.info(
            f"Deleted eval suite {name}",
            extra={"request_id": request_id, "user_id": user_id}
        )
        
        return success_response(
            data={"deleted": True, "suite_name": name},
            message="Eval suite deleted successfully",
            meta={"request_id": request_id}
        )
        
    except (NotFoundException, AppException):
        raise
    except Exception as e:
        logger.error(
            f"Failed to delete eval suite {name}: {str(e)}",
            exc_info=True,
            extra={"request_id": request_id, "user_id": user_id}
        )
        raise AppException(
            message=f"Failed to delete eval suite {name}",
            detail=str(e)
        )