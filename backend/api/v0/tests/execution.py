"""
Test execution endpoints with standardized responses.
"""
import logging
from typing import List, Optional
from fastapi import APIRouter, Request, status, Query, Body
from pydantic import BaseModel, Field

from services.test.models import (
    UnitTestExecutionResult,
    TestSuiteExecutionResult
)
from api.deps import TestExecutionServiceDep, CurrentUserDep
from middlewares.rest import (
    StandardResponse,
    success_response,
    AppException,
    NotFoundException
)

logger = logging.getLogger(__name__)

router = APIRouter()


class ExecuteTestsRequest(BaseModel):
    """Request body for executing specific tests"""
    test_names: Optional[List[str]] = Field(
        default=None,
        description="List of test names to execute. If None, all tests are executed."
    )


@router.post(
    "/{suite_name}/execute",
    response_model=StandardResponse[TestSuiteExecutionResult],
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
                        "detail": "Failed to execute test suite"
                    }
                }
            }
        }
    },
    summary="Execute test suite",
    description="Execute all tests in a suite or specific tests if test_names are provided in request body.",
)
async def execute_test_suite(
    request: Request,
    test_execution_service: TestExecutionServiceDep,
    user_id: CurrentUserDep,
    suite_name: str,
    repo_name: str = Query(..., description="Repository name"),
    request_body: ExecuteTestsRequest = Body(default=ExecuteTestsRequest())
) -> StandardResponse[TestSuiteExecutionResult]:
    """
    Execute test suite or specific tests within suite.
    
    Returns:
        StandardResponse[TestSuiteExecutionResult]: Execution results
    
    Raises:
        NotFoundException: When suite or tests don't exist
        AppException: When execution fails
    """
    request_id = request.state.request_id
    
    try:
        test_names = request_body.test_names
        
        if test_names:
            logger.info(
                f"Executing tests {test_names} in suite {suite_name} from repo {repo_name}",
                extra={"request_id": request_id, "user_id": user_id}
            )
        else:
            logger.info(
                f"Executing all tests in suite {suite_name} from repo {repo_name}",
                extra={"request_id": request_id, "user_id": user_id}
            )
        
        execution_result = await test_execution_service.execute_test_suite(
            user_id, repo_name, suite_name, test_names
        )
        
        logger.info(
            f"Test suite execution completed: {execution_result.passed_tests}/{execution_result.total_tests} passed",
            extra={
                "request_id": request_id,
                "user_id": user_id,
                "suite_name": suite_name,
                "passed": execution_result.passed_tests,
                "failed": execution_result.failed_tests
            }
        )
        
        return success_response(
            data=execution_result,
            message=f"Test suite executed: {execution_result.passed_tests}/{execution_result.total_tests} passed",
            meta={"request_id": request_id}
        )
        
    except (NotFoundException, AppException):
        raise
    except Exception as e:
        logger.error(
            f"Failed to execute test suite {suite_name}: {str(e)}",
            exc_info=True,
            extra={"request_id": request_id, "user_id": user_id}
        )
        raise AppException(
            message=f"Failed to execute test suite {suite_name}",
            detail=str(e)
        )


@router.post(
    "/{suite_name}/tests/{test_name}/execute",
    response_model=StandardResponse[UnitTestExecutionResult],
    status_code=status.HTTP_200_OK,
    responses={
        404: {
            "description": "Test not found",
            "content": {
                "application/json": {
                    "example": {
                        "status": "error",
                        "type": "/errors/not-found",
                        "title": "Not Found",
                        "detail": "Test not found"
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
                        "detail": "Failed to execute test"
                    }
                }
            }
        }
    },
    summary="Execute single test",
    description="Execute a specific test from a test suite.",
)
async def execute_single_test(
    request: Request,
    test_execution_service: TestExecutionServiceDep,
    user_id: CurrentUserDep,
    suite_name: str,
    test_name: str,
    repo_name: str = Query(..., description="Repository name")
) -> StandardResponse[UnitTestExecutionResult]:
    """
    Execute single test.
    
    Returns:
        StandardResponse[UnitTestExecutionResult]: Test execution result
    
    Raises:
        NotFoundException: When test doesn't exist
        AppException: When execution fails
    """
    request_id = request.state.request_id
    
    try:
        logger.info(
            f"Executing test {test_name} in suite {suite_name} from repo {repo_name}",
            extra={"request_id": request_id, "user_id": user_id}
        )
        
        execution_result = await test_execution_service.execute_single_test(
            user_id, repo_name, suite_name, test_name
        )
        
        logger.info(
            f"Test execution completed: {test_name} {'passed' if execution_result.overall_passed else 'failed'}",
            extra={
                "request_id": request_id,
                "user_id": user_id,
                "test_name": test_name,
                "passed": execution_result.overall_passed
            }
        )
        
        return success_response(
            data=execution_result,
            message=f"Test {'passed' if execution_result.overall_passed else 'failed'}",
            meta={"request_id": request_id}
        )
        
    except (NotFoundException, AppException):
        raise
    except Exception as e:
        logger.error(
            f"Failed to execute test {test_name}: {str(e)}",
            exc_info=True,
            extra={"request_id": request_id, "user_id": user_id}
        )
        raise AppException(
            message=f"Failed to execute test {test_name}",
            detail=str(e)
        )


@router.get(
    "/{suite_name}/executions",
    response_model=StandardResponse[List[TestSuiteExecutionResult]],
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
                        "detail": "Failed to retrieve execution history"
                    }
                }
            }
        }
    },
    summary="Get execution history",
    description="Get execution history for a test suite, ordered by execution time (newest first).",
)
async def get_execution_history(
    request: Request,
    test_execution_service: TestExecutionServiceDep,
    user_id: CurrentUserDep,
    suite_name: str,
    repo_name: str = Query(..., description="Repository name"),
    limit: int = Query(10, ge=1, le=100, description="Maximum number of executions to return")
) -> StandardResponse[List[TestSuiteExecutionResult]]:
    """
    Get execution history for test suite.
    
    Returns:
        StandardResponse[List[TestSuiteExecutionResult]]: Execution history
    
    Raises:
        NotFoundException: When repository doesn't exist
        AppException: When retrieval fails
    """
    request_id = request.state.request_id
    
    try:
        logger.info(
            f"Getting execution history for suite {suite_name} from repo {repo_name}",
            extra={"request_id": request_id, "user_id": user_id}
        )
        
        executions = await test_execution_service.test_service.list_executions(
            user_id, repo_name, suite_name, limit
        )
        
        logger.info(
            f"Retrieved {len(executions)} executions for suite {suite_name}",
            extra={"request_id": request_id, "user_id": user_id}
        )
        
        return success_response(
            data=executions,
            message=f"Retrieved {len(executions)} executions",
            meta={"request_id": request_id}
        )
        
    except (NotFoundException, AppException):
        raise
    except Exception as e:
        logger.error(
            f"Failed to get execution history for suite {suite_name}: {str(e)}",
            exc_info=True,
            extra={"request_id": request_id, "user_id": user_id}
        )
        raise AppException(
            message=f"Failed to retrieve execution history for suite {suite_name}",
            detail=str(e)
        )


@router.get(
    "/{suite_name}/executions/latest",
    response_model=StandardResponse[Optional[TestSuiteExecutionResult]],
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
                        "detail": "Failed to retrieve latest execution"
                    }
                }
            }
        }
    },
    summary="Get latest execution",
    description="Get the most recent execution result for a test suite.",
)
async def get_latest_execution(
    request: Request,
    test_execution_service: TestExecutionServiceDep,
    user_id: CurrentUserDep,
    suite_name: str,
    repo_name: str = Query(..., description="Repository name")
) -> StandardResponse[Optional[TestSuiteExecutionResult]]:
    """
    Get latest execution result for test suite.
    
    Returns:
        StandardResponse[Optional[TestSuiteExecutionResult]]: Latest execution or None
    
    Raises:
        NotFoundException: When repository doesn't exist
        AppException: When retrieval fails
    """
    request_id = request.state.request_id
    
    try:
        logger.info(
            f"Getting latest execution for suite {suite_name} from repo {repo_name}",
            extra={"request_id": request_id, "user_id": user_id}
        )
        
        latest_execution = await test_execution_service.test_service.get_latest_execution(
            user_id, repo_name, suite_name
        )
        
        if latest_execution:
            logger.info(
                f"Retrieved latest execution for suite {suite_name}",
                extra={"request_id": request_id, "user_id": user_id}
            )
            message = "Latest execution retrieved successfully"
        else:
            logger.info(
                f"No executions found for suite {suite_name}",
                extra={"request_id": request_id, "user_id": user_id}
            )
            message = "No executions found"
        
        return success_response(
            data=latest_execution,
            message=message,
            meta={"request_id": request_id}
        )
        
    except (NotFoundException, AppException):
        raise
    except Exception as e:
        logger.error(
            f"Failed to get latest execution for suite {suite_name}: {str(e)}",
            exc_info=True,
            extra={"request_id": request_id, "user_id": user_id}
        )
        raise AppException(
            message=f"Failed to retrieve latest execution for suite {suite_name}",
            detail=str(e)
        )