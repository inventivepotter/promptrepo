"""
Eval suite CRUD endpoints with standardized responses.
"""
import logging
from typing import List
from fastapi import APIRouter, Request, status, Body, Query

from services.evals.models import EvalSuiteData, EvalSuiteSummary
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
    response_model=StandardResponse[List[EvalSuiteSummary]],
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
                        "detail": "Failed to list eval suites"
                    }
                }
            }
        }
    },
    summary="List eval suites",
    description="Get list of all eval suites in a repository with summary information.",
)
async def list_eval_suites(
    request: Request,
    eval_service: EvalMetaServiceDep,
    user_id: CurrentUserDep,
    repo_name: str = Query(..., description="Repository name")
) -> StandardResponse[List[EvalSuiteSummary]]:
    """
    List all eval suites in a repository.
    
    Returns:
        StandardResponse[List[EvalSuiteSummary]]: List of eval suite summaries
    
    Raises:
        NotFoundException: When repository doesn't exist
        AppException: When listing fails
    """
    request_id = request.state.request_id
    
    try:
        logger.info(
            f"Listing eval suites for repo {repo_name}",
            extra={"request_id": request_id, "user_id": user_id}
        )
        
        suites = await eval_service.list_eval_suites(user_id, repo_name)
        
        logger.info(
            f"Found {len(suites)} eval suites in {repo_name}",
            extra={"request_id": request_id, "user_id": user_id}
        )
        
        return success_response(
            data=suites,
            message=f"Found {len(suites)} eval suites",
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
    "/{suite_name}",
    response_model=StandardResponse[EvalSuiteData],
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
                        "detail": "Failed to retrieve eval suite"
                    }
                }
            }
        }
    },
    summary="Get eval suite",
    description="Get detailed information about a specific eval suite including all eval definitions.",
)
async def get_eval_suite(
    request: Request,
    eval_service: EvalMetaServiceDep,
    user_id: CurrentUserDep,
    suite_name: str,
    repo_name: str = Query(..., description="Repository name")
) -> StandardResponse[EvalSuiteData]:
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
            f"Getting eval suite {suite_name} from repo {repo_name}",
            extra={"request_id": request_id, "user_id": user_id}
        )
        
        suite_data = await eval_service.get_eval_suite(user_id, repo_name, suite_name)
        
        logger.info(
            f"Retrieved eval suite {suite_name}",
            extra={"request_id": request_id, "user_id": user_id}
        )
        
        return success_response(
            data=suite_data,
            message="Eval suite retrieved successfully",
            meta={"request_id": request_id}
        )
        
    except (NotFoundException, AppException):
        raise
    except Exception as e:
        logger.error(
            f"Failed to get eval suite {suite_name}: {str(e)}",
            exc_info=True,
            extra={"request_id": request_id, "user_id": user_id}
        )
        raise AppException(
            message=f"Failed to retrieve eval suite {suite_name}",
            detail=str(e)
        )


@router.post(
    "",
    response_model=StandardResponse[EvalSuiteData],
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
async def save_eval_suite(
    request: Request,
    eval_service: EvalMetaServiceDep,
    user_id: CurrentUserDep,
    user_session: CurrentSessionDep,
    suite_data: EvalSuiteData = Body(...),
    repo_name: str = Query(..., description="Repository name")
) -> StandardResponse[EvalSuiteData]:
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
            f"Saving eval suite {suite_data.eval_suite.name} to repo {repo_name}",
            extra={"request_id": request_id, "user_id": user_id}
        )
        
        # Get OAuth token and user info from session
        oauth_token = getattr(user_session, 'oauth_token', None)
        
        # Get user information for git commit author
        user = user_session.user if hasattr(user_session, 'user') else None
        author_name = user.oauth_name or user.oauth_username if user else None
        author_email = user.oauth_email if user else None
        
        saved_suite, pr_info = await eval_service.save_eval_suite(
            user_id=user_id,
            repo_name=repo_name,
            suite_data=suite_data,
            oauth_token=oauth_token,
            author_name=author_name,
            author_email=author_email,
            user_session=user_session
        )
        
        logger.info(
            f"Saved eval suite {suite_data.eval_suite.name}",
            extra={"request_id": request_id, "user_id": user_id}
        )
        
        return success_response(
            data=saved_suite,
            message="Eval suite saved successfully",
            meta={"request_id": request_id}
        )
        
    except (NotFoundException, AppException):
        raise
    except Exception as e:
        logger.error(
            f"Failed to save eval suite {suite_data.eval_suite.name}: {str(e)}",
            exc_info=True,
            extra={"request_id": request_id, "user_id": user_id}
        )
        raise AppException(
            message=f"Failed to save eval suite {suite_data.eval_suite.name}",
            detail=str(e)
        )


@router.delete(
    "/{suite_name}",
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
async def delete_eval_suite(
    request: Request,
    eval_service: EvalMetaServiceDep,
    user_id: CurrentUserDep,
    suite_name: str,
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
            f"Deleting eval suite {suite_name} from repo {repo_name}",
            extra={"request_id": request_id, "user_id": user_id}
        )
        
        success = await eval_service.delete_eval_suite(user_id, repo_name, suite_name)
        
        if not success:
            raise AppException(
                message=f"Failed to delete eval suite {suite_name}"
            )
        
        logger.info(
            f"Deleted eval suite {suite_name}",
            extra={"request_id": request_id, "user_id": user_id}
        )
        
        return success_response(
            data={"deleted": True, "suite_name": suite_name},
            message="Eval suite deleted successfully",
            meta={"request_id": request_id}
        )
        
    except (NotFoundException, AppException):
        raise
    except Exception as e:
        logger.error(
            f"Failed to delete eval suite {suite_name}: {str(e)}",
            exc_info=True,
            extra={"request_id": request_id, "user_id": user_id}
        )
        raise AppException(
            message=f"Failed to delete eval suite {suite_name}",
            detail=str(e)
        )