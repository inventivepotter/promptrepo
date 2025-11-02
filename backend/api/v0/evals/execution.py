"""
Eval execution endpoints with standardized responses.
"""
import logging
from typing import List, Optional
from fastapi import APIRouter, Request, status, Query, Body
from pydantic import BaseModel, Field

from services.artifacts.evals.models import (
    TestExecutionResult,
    EvalExecutionResult
)
from api.deps import EvalExecutionServiceDep, CurrentUserDep
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
    "/{eval_name}/execute",
    response_model=StandardResponse[EvalExecutionResult],
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
                        "detail": "Failed to execute eval"
                    }
                }
            }
        }
    },
    summary="Execute eval",
    description="Execute all tests in an eval or specific tests if test_names are provided in request body.",
)
async def execute_eval(
    request: Request,
    eval_execution_service: EvalExecutionServiceDep,
    user_id: CurrentUserDep,
    eval_name: str,
    repo_name: str = Query(..., description="Repository name"),
    request_body: ExecuteTestsRequest = Body(default=ExecuteTestsRequest())
) -> StandardResponse[EvalExecutionResult]:
    """
    Execute eval or specific tests within eval.
    
    Returns:
        StandardResponse[EvalExecutionResult]: Execution results
    
    Raises:
        NotFoundException: When eval or tests don't exist
        AppException: When execution fails
    """
    request_id = request.state.request_id
    
    try:
        test_names = request_body.test_names
        
        if test_names:
            logger.info(
                f"Executing tests {test_names} in eval {eval_name} from repo {repo_name}",
                extra={"request_id": request_id, "user_id": user_id}
            )
        else:
            logger.info(
                f"Executing all tests in eval {eval_name} from repo {repo_name}",
                extra={"request_id": request_id, "user_id": user_id}
            )
        
        execution_result = await eval_execution_service.execute_eval(
            user_id, repo_name, eval_name, test_names
        )
        
        logger.info(
            f"Eval execution completed: {execution_result.passed_tests}/{execution_result.total_tests} passed",
            extra={
                "request_id": request_id,
                "user_id": user_id,
                "eval_name": eval_name,
                "passed": execution_result.passed_tests,
                "failed": execution_result.failed_tests
            }
        )
        
        return success_response(
            data=execution_result,
            message=f"Eval executed: {execution_result.passed_tests}/{execution_result.total_tests} passed",
            meta={"request_id": request_id}
        )
        
    except (NotFoundException, AppException):
        raise
    except Exception as e:
        logger.error(
            f"Failed to execute eval {eval_name}: {str(e)}",
            exc_info=True,
            extra={"request_id": request_id, "user_id": user_id}
        )
        raise AppException(
            message=f"Failed to execute eval {eval_name}",
            detail=str(e)
        )


@router.post(
    "/{eval_name}/tests/{test_name}/execute",
    response_model=StandardResponse[TestExecutionResult],
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
    description="Execute a specific test from an eval.",
)
async def execute_single_test(
    request: Request,
    eval_execution_service: EvalExecutionServiceDep,
    user_id: CurrentUserDep,
    eval_name: str,
    test_name: str,
    repo_name: str = Query(..., description="Repository name")
) -> StandardResponse[TestExecutionResult]:
    """
    Execute single test.
    
    Returns:
        StandardResponse[TestExecutionResult]: Test execution result
    
    Raises:
        NotFoundException: When test doesn't exist
        AppException: When execution fails
    """
    request_id = request.state.request_id
    
    try:
        logger.info(
            f"Executing test {test_name} in eval {eval_name} from repo {repo_name}",
            extra={"request_id": request_id, "user_id": user_id}
        )
        
        execution_result = await eval_execution_service.execute_single_test(
            user_id, repo_name, eval_name, test_name
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
    "/{eval_name}/executions",
    response_model=StandardResponse[List[EvalExecutionResult]],
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
    description="Get execution history for an eval, ordered by execution time (newest first).",
)
async def get_execution_history(
    request: Request,
    eval_execution_service: EvalExecutionServiceDep,
    user_id: CurrentUserDep,
    eval_name: str,
    repo_name: str = Query(..., description="Repository name"),
    limit: int = Query(10, ge=1, le=100, description="Maximum number of executions to return")
) -> StandardResponse[List[EvalExecutionResult]]:
    """
    Get execution history for eval.
    
    Returns:
        StandardResponse[List[EvalExecutionResult]]: Execution history
    
    Raises:
        NotFoundException: When repository doesn't exist
        AppException: When retrieval fails
    """
    request_id = request.state.request_id
    
    try:
        logger.info(
            f"Getting execution history for eval {eval_name} from repo {repo_name}",
            extra={"request_id": request_id, "user_id": user_id}
        )
        
        executions = await eval_execution_service.eval_execution_meta_service.list_executions_for_eval(
            user_id, repo_name, eval_name, limit
        )
        
        logger.info(
            f"Retrieved {len(executions)} executions for eval {eval_name}",
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
            f"Failed to get execution history for eval {eval_name}: {str(e)}",
            exc_info=True,
            extra={"request_id": request_id, "user_id": user_id}
        )
        raise AppException(
            message=f"Failed to retrieve execution history for eval {eval_name}",
            detail=str(e)
        )


@router.get(
    "/{eval_name}/executions/latest",
    response_model=StandardResponse[Optional[EvalExecutionResult]],
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
    description="Get the most recent execution result for an eval.",
)
async def get_latest_execution(
    request: Request,
    eval_execution_service: EvalExecutionServiceDep,
    user_id: CurrentUserDep,
    eval_name: str,
    repo_name: str = Query(..., description="Repository name")
) -> StandardResponse[Optional[EvalExecutionResult]]:
    """
    Get latest execution result for eval.
    
    Returns:
        StandardResponse[Optional[EvalExecutionResult]]: Latest execution or None
    
    Raises:
        NotFoundException: When repository doesn't exist
        AppException: When retrieval fails
    """
    request_id = request.state.request_id
    
    try:
        logger.info(
            f"Getting latest execution for eval {eval_name} from repo {repo_name}",
            extra={"request_id": request_id, "user_id": user_id}
        )
        
        latest_execution = await eval_execution_service.eval_execution_meta_service.get_latest_execution(
            user_id, repo_name, eval_name
        )
        
        if latest_execution:
            logger.info(
                f"Retrieved latest execution for eval {eval_name}",
                extra={"request_id": request_id, "user_id": user_id}
            )
            message = "Latest execution retrieved successfully"
        else:
            logger.info(
                f"No executions found for eval {eval_name}",
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
            f"Failed to get latest execution for eval {eval_name}: {str(e)}",
            exc_info=True,
            extra={"request_id": request_id, "user_id": user_id}
        )
        raise AppException(
            message=f"Failed to retrieve latest execution for eval {eval_name}",
            detail=str(e)
        )