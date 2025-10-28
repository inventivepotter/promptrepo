"""
Test suite CRUD endpoints with standardized responses.
"""
import logging
from typing import List
from fastapi import APIRouter, Request, status, Body, Query

from services.test.models import TestSuiteData, TestSuiteSummary
from api.deps import TestServiceDep, CurrentUserDep
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
    response_model=StandardResponse[List[TestSuiteSummary]],
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
                        "detail": "Failed to list test suites"
                    }
                }
            }
        }
    },
    summary="List test suites",
    description="Get list of all test suites in a repository with summary information.",
)
async def list_test_suites(
    request: Request,
    test_service: TestServiceDep,
    user_id: CurrentUserDep,
    repo_name: str = Query(..., description="Repository name")
) -> StandardResponse[List[TestSuiteSummary]]:
    """
    List all test suites in a repository.
    
    Returns:
        StandardResponse[List[TestSuiteSummary]]: List of test suite summaries
    
    Raises:
        NotFoundException: When repository doesn't exist
        AppException: When listing fails
    """
    request_id = request.state.request_id
    
    try:
        logger.info(
            f"Listing test suites for repo {repo_name}",
            extra={"request_id": request_id, "user_id": user_id}
        )
        
        suites = await test_service.list_test_suites(user_id, repo_name)
        
        logger.info(
            f"Found {len(suites)} test suites in {repo_name}",
            extra={"request_id": request_id, "user_id": user_id}
        )
        
        return success_response(
            data=suites,
            message=f"Found {len(suites)} test suites",
            meta={"request_id": request_id}
        )
        
    except (NotFoundException, AppException):
        raise
    except Exception as e:
        logger.error(
            f"Failed to list test suites: {str(e)}",
            exc_info=True,
            extra={"request_id": request_id, "user_id": user_id}
        )
        raise AppException(
            message="Failed to list test suites",
            detail=str(e)
        )


@router.get(
    "/{suite_name}",
    response_model=StandardResponse[TestSuiteData],
    status_code=status.HTTP_200_OK,
    responses={
        404: {
            "description": "Test suite not found",
            "content": {
                "application/json": {
                    "example": {
                        "status": "error",
                        "type": "/errors/not-found",
                        "title": "Not Found",
                        "detail": "Test suite not found"
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
                        "detail": "Failed to retrieve test suite"
                    }
                }
            }
        }
    },
    summary="Get test suite",
    description="Get detailed information about a specific test suite including all test definitions.",
)
async def get_test_suite(
    request: Request,
    test_service: TestServiceDep,
    user_id: CurrentUserDep,
    suite_name: str,
    repo_name: str = Query(..., description="Repository name")
) -> StandardResponse[TestSuiteData]:
    """
    Get specific test suite definition.
    
    Returns:
        StandardResponse[TestSuiteData]: Test suite definition
    
    Raises:
        NotFoundException: When suite doesn't exist
        AppException: When retrieval fails
    """
    request_id = request.state.request_id
    
    try:
        logger.info(
            f"Getting test suite {suite_name} from repo {repo_name}",
            extra={"request_id": request_id, "user_id": user_id}
        )
        
        suite_data = await test_service.get_test_suite(user_id, repo_name, suite_name)
        
        logger.info(
            f"Retrieved test suite {suite_name}",
            extra={"request_id": request_id, "user_id": user_id}
        )
        
        return success_response(
            data=suite_data,
            message="Test suite retrieved successfully",
            meta={"request_id": request_id}
        )
        
    except (NotFoundException, AppException):
        raise
    except Exception as e:
        logger.error(
            f"Failed to get test suite {suite_name}: {str(e)}",
            exc_info=True,
            extra={"request_id": request_id, "user_id": user_id}
        )
        raise AppException(
            message=f"Failed to retrieve test suite {suite_name}",
            detail=str(e)
        )


@router.post(
    "",
    response_model=StandardResponse[TestSuiteData],
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
                        "detail": "Failed to save test suite"
                    }
                }
            }
        }
    },
    summary="Create or update test suite",
    description="Create a new test suite or update an existing one. The suite name is taken from the request body.",
)
async def save_test_suite(
    request: Request,
    test_service: TestServiceDep,
    user_id: CurrentUserDep,
    suite_data: TestSuiteData = Body(...),
    repo_name: str = Query(..., description="Repository name")
) -> StandardResponse[TestSuiteData]:
    """
    Create or update test suite.
    
    Returns:
        StandardResponse[TestSuiteData]: Saved test suite
    
    Raises:
        NotFoundException: When repository doesn't exist
        AppException: When save fails
    """
    request_id = request.state.request_id
    
    try:
        logger.info(
            f"Saving test suite {suite_data.test_suite.name} to repo {repo_name}",
            extra={"request_id": request_id, "user_id": user_id}
        )
        
        saved_suite = await test_service.save_test_suite(user_id, repo_name, suite_data)
        
        logger.info(
            f"Saved test suite {suite_data.test_suite.name}",
            extra={"request_id": request_id, "user_id": user_id}
        )
        
        return success_response(
            data=saved_suite,
            message="Test suite saved successfully",
            meta={"request_id": request_id}
        )
        
    except (NotFoundException, AppException):
        raise
    except Exception as e:
        logger.error(
            f"Failed to save test suite {suite_data.test_suite.name}: {str(e)}",
            exc_info=True,
            extra={"request_id": request_id, "user_id": user_id}
        )
        raise AppException(
            message=f"Failed to save test suite {suite_data.test_suite.name}",
            detail=str(e)
        )


@router.delete(
    "/{suite_name}",
    response_model=StandardResponse[dict],
    status_code=status.HTTP_200_OK,
    responses={
        404: {
            "description": "Test suite not found",
            "content": {
                "application/json": {
                    "example": {
                        "status": "error",
                        "type": "/errors/not-found",
                        "title": "Not Found",
                        "detail": "Test suite not found"
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
                        "detail": "Failed to delete test suite"
                    }
                }
            }
        }
    },
    summary="Delete test suite",
    description="Delete a test suite and all its execution history.",
)
async def delete_test_suite(
    request: Request,
    test_service: TestServiceDep,
    user_id: CurrentUserDep,
    suite_name: str,
    repo_name: str = Query(..., description="Repository name")
) -> StandardResponse[dict]:
    """
    Delete test suite.
    
    Returns:
        StandardResponse[dict]: Deletion confirmation
    
    Raises:
        NotFoundException: When suite doesn't exist
        AppException: When deletion fails
    """
    request_id = request.state.request_id
    
    try:
        logger.info(
            f"Deleting test suite {suite_name} from repo {repo_name}",
            extra={"request_id": request_id, "user_id": user_id}
        )
        
        success = await test_service.delete_test_suite(user_id, repo_name, suite_name)
        
        if not success:
            raise AppException(
                message=f"Failed to delete test suite {suite_name}"
            )
        
        logger.info(
            f"Deleted test suite {suite_name}",
            extra={"request_id": request_id, "user_id": user_id}
        )
        
        return success_response(
            data={"deleted": True, "suite_name": suite_name},
            message="Test suite deleted successfully",
            meta={"request_id": request_id}
        )
        
    except (NotFoundException, AppException):
        raise
    except Exception as e:
        logger.error(
            f"Failed to delete test suite {suite_name}: {str(e)}",
            exc_info=True,
            extra={"request_id": request_id, "user_id": user_id}
        )
        raise AppException(
            message=f"Failed to delete test suite {suite_name}",
            detail=str(e)
        )