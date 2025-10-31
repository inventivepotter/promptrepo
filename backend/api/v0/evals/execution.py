"""
Eval execution endpoints with standardized responses.
"""
import logging
from typing import List, Optional
from fastapi import APIRouter, Request, status, Query, Body
from pydantic import BaseModel, Field

from services.evals.models import (
    EvalExecutionResult,
    EvalSuiteExecutionResult
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


class ExecuteEvalsRequest(BaseModel):
    """Request body for executing specific evals"""
    eval_names: Optional[List[str]] = Field(
        default=None,
        description="List of eval names to execute. If None, all evals are executed."
    )


@router.post(
    "/{suite_name}/execute",
    response_model=StandardResponse[EvalSuiteExecutionResult],
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
                        "detail": "Failed to execute eval suite"
                    }
                }
            }
        }
    },
    summary="Execute eval suite",
    description="Execute all evals in a suite or specific evals if eval_names are provided in request body.",
)
async def execute_eval_suite(
    request: Request,
    eval_execution_service: EvalExecutionServiceDep,
    user_id: CurrentUserDep,
    suite_name: str,
    repo_name: str = Query(..., description="Repository name"),
    request_body: ExecuteEvalsRequest = Body(default=ExecuteEvalsRequest())
) -> StandardResponse[EvalSuiteExecutionResult]:
    """
    Execute eval suite or specific evals within suite.
    
    Returns:
        StandardResponse[EvalSuiteExecutionResult]: Execution results
    
    Raises:
        NotFoundException: When suite or evals don't exist
        AppException: When execution fails
    """
    request_id = request.state.request_id
    
    try:
        eval_names = request_body.eval_names
        
        if eval_names:
            logger.info(
                f"Executing evals {eval_names} in suite {suite_name} from repo {repo_name}",
                extra={"request_id": request_id, "user_id": user_id}
            )
        else:
            logger.info(
                f"Executing all evals in suite {suite_name} from repo {repo_name}",
                extra={"request_id": request_id, "user_id": user_id}
            )
        
        execution_result = await eval_execution_service.execute_eval_suite(
            user_id, repo_name, suite_name, eval_names
        )
        
        logger.info(
            f"Eval suite execution completed: {execution_result.passed_evals}/{execution_result.total_evals} passed",
            extra={
                "request_id": request_id,
                "user_id": user_id,
                "suite_name": suite_name,
                "passed": execution_result.passed_evals,
                "failed": execution_result.failed_evals
            }
        )
        
        return success_response(
            data=execution_result,
            message=f"Eval suite executed: {execution_result.passed_evals}/{execution_result.total_evals} passed",
            meta={"request_id": request_id}
        )
        
    except (NotFoundException, AppException):
        raise
    except Exception as e:
        logger.error(
            f"Failed to execute eval suite {suite_name}: {str(e)}",
            exc_info=True,
            extra={"request_id": request_id, "user_id": user_id}
        )
        raise AppException(
            message=f"Failed to execute eval suite {suite_name}",
            detail=str(e)
        )


@router.post(
    "/{suite_name}/evals/{eval_name}/execute",
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
    summary="Execute single eval",
    description="Execute a specific eval from an eval suite.",
)
async def execute_single_eval(
    request: Request,
    eval_execution_service: EvalExecutionServiceDep,
    user_id: CurrentUserDep,
    suite_name: str,
    eval_name: str,
    repo_name: str = Query(..., description="Repository name")
) -> StandardResponse[EvalExecutionResult]:
    """
    Execute single eval.
    
    Returns:
        StandardResponse[EvalExecutionResult]: Eval execution result
    
    Raises:
        NotFoundException: When eval doesn't exist
        AppException: When execution fails
    """
    request_id = request.state.request_id
    
    try:
        logger.info(
            f"Executing eval {eval_name} in suite {suite_name} from repo {repo_name}",
            extra={"request_id": request_id, "user_id": user_id}
        )
        
        execution_result = await eval_execution_service.execute_single_eval(
            user_id, repo_name, suite_name, eval_name
        )
        
        logger.info(
            f"Eval execution completed: {eval_name} {'passed' if execution_result.overall_passed else 'failed'}",
            extra={
                "request_id": request_id,
                "user_id": user_id,
                "eval_name": eval_name,
                "passed": execution_result.overall_passed
            }
        )
        
        return success_response(
            data=execution_result,
            message=f"Eval {'passed' if execution_result.overall_passed else 'failed'}",
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


@router.get(
    "/{suite_name}/executions",
    response_model=StandardResponse[List[EvalSuiteExecutionResult]],
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
    description="Get execution history for an eval suite, ordered by execution time (newest first).",
)
async def get_execution_history(
    request: Request,
    eval_execution_service: EvalExecutionServiceDep,
    user_id: CurrentUserDep,
    suite_name: str,
    repo_name: str = Query(..., description="Repository name"),
    limit: int = Query(10, ge=1, le=100, description="Maximum number of executions to return")
) -> StandardResponse[List[EvalSuiteExecutionResult]]:
    """
    Get execution history for eval suite.
    
    Returns:
        StandardResponse[List[EvalSuiteExecutionResult]]: Execution history
    
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
        
        executions = await eval_execution_service.eval_meta_service.list_executions(
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
    response_model=StandardResponse[Optional[EvalSuiteExecutionResult]],
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
    description="Get the most recent execution result for an eval suite.",
)
async def get_latest_execution(
    request: Request,
    eval_execution_service: EvalExecutionServiceDep,
    user_id: CurrentUserDep,
    suite_name: str,
    repo_name: str = Query(..., description="Repository name")
) -> StandardResponse[Optional[EvalSuiteExecutionResult]]:
    """
    Get latest execution result for eval suite.
    
    Returns:
        StandardResponse[Optional[EvalSuiteExecutionResult]]: Latest execution or None
    
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
        
        latest_execution = await eval_execution_service.eval_meta_service.get_latest_execution(
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