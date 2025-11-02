"""
Eval Execution Meta Service.

Handles execution history management for evals including:
- Retrieving execution history
- Saving execution results
- File-based storage in .promptrepo/evals/<eval-name>/executions/ directory
"""

import logging
from datetime import datetime
from typing import List, Optional, Tuple

from schemas.artifact_type_enum import ArtifactType
from services.artifacts.artifact_meta_interface import ArtifactMetaInterface
from services.local_repo.local_repo_service import LocalRepoService
from services.local_repo.models import PRInfo
from services.file_operations.file_operations_service import FileOperationsService
from middlewares.rest.exceptions import NotFoundException, AppException

from .models import (
    EvalExecutionResult,
    EvalExecutionData,
    EvalExecutionMeta
)

logger = logging.getLogger(__name__)


class EvalExecutionMetaService(ArtifactMetaInterface[EvalExecutionData, EvalExecutionMeta]):
    """
    Eval execution metadata service using constructor injection.
    
    This service handles:
    - Execution history retrieval
    - Execution result storage
    - File-based storage in .promptrepo/evals/<eval-name>/executions/ directory
    """

    EXECUTIONS_DIR = ArtifactType.EVAL_EXECUTION
    EXECUTION_SUFFIX = f".{ArtifactType.EVAL_EXECUTION}.yaml"
    
    def __init__(
        self,
        local_repo_service: LocalRepoService
    ):
        """
        Initialize EvalExecutionMetaService with injected dependencies.
        
        Args:
            local_repo_service: Local repository service for file I/O
        """
        self.local_repo_service = local_repo_service
    
    async def discover(
        self,
        user_id: str,
        repo_name: str
    ) -> List[EvalExecutionMeta]:
        """
        Discover all execution metadata across all evals in a repository.
        
        Args:
            user_id: User ID
            repo_name: Repository name
            
        Returns:
            List[EvalExecutionMeta]: List of all execution metadata
        """
        repo_path = self.local_repo_service.get_repo_path(user_id, repo_name)
        
        if not repo_path.exists():
            raise NotFoundException(
                resource="Repository",
                identifier=repo_name
            )
        
        # Use LocalRepoService discovery to find all eval files
        discovery_result = self.local_repo_service.discover_artifacts(user_id, repo_name)
        eval_files = discovery_result.get_files_by_type(ArtifactType.EVAL)
        
        all_executions = []
        
        # For each eval file, list its executions
        for eval_file_path in eval_files:
            try:
                executions = await self.list_executions_for_eval(user_id, repo_name, eval_file_path)
                all_executions.extend(executions)
            except Exception as e:
                logger.warning(f"Failed to load executions for {eval_file_path}: {e}")
                continue
        
        logger.info(f"Discovered {len(all_executions)} executions in {repo_name}")
        return all_executions
    
    async def get(
        self,
        user_id: str,
        repo_name: str,
        file_path: str
    ) -> Optional[EvalExecutionMeta]:
        """
        Get execution metadata by file path.
        
        Args:
            user_id: User ID
            repo_name: Repository name
            file_path: Relative path to execution file from repo root
            
        Returns:
            Optional[EvalExecutionMeta]: Execution metadata if found
        """
        repo_path = self.local_repo_service.get_repo_path(user_id, repo_name)
        
        if not repo_path.exists():
            raise NotFoundException(
                resource="Repository",
                identifier=repo_name
            )
        
        full_file_path = repo_path / file_path
        
        if not full_file_path.exists():
            raise NotFoundException(
                resource="Execution",
                identifier=file_path
            )
        
        try:
            file_ops = FileOperationsService()
            exec_data_raw = file_ops.load_yaml_file(full_file_path)
            
            if not exec_data_raw or "execution" not in exec_data_raw:
                raise AppException(message=f"Invalid execution file: {file_path}")
            
            exec_result = exec_data_raw["execution"]
            
            # Parse datetime fields
            executed_at = exec_result.get("executed_at")
            if isinstance(executed_at, str):
                executed_at = datetime.fromisoformat(executed_at)
            exec_result["executed_at"] = executed_at
            
            # Parse test results executed_at
            for test_result in exec_result.get("test_results", []):
                test_executed_at = test_result.get("executed_at")
                if isinstance(test_executed_at, str):
                    test_result["executed_at"] = datetime.fromisoformat(test_executed_at)
            
            execution_result = EvalExecutionResult(**exec_result)
            
            return EvalExecutionMeta(
                execution=execution_result,
                repo_name=repo_name,
                file_path=file_path
            )
        except Exception as e:
            logger.error(f"Failed to load execution from {file_path}: {e}")
            raise AppException(message=f"Error loading execution {file_path}: {str(e)}")
    
    async def save(
        self,
        user_id: str,
        repo_name: str,
        artifact_data: EvalExecutionData,
        file_path: Optional[str] = None,
        oauth_token: Optional[str] = None,
        author_name: Optional[str] = None,
        author_email: Optional[str] = None,
        user_session = None
    ) -> Tuple[EvalExecutionMeta, Optional[PRInfo]]:
        """
        Save execution data using LocalRepoService for git workflow.
        
        Args:
            user_id: User ID
            repo_name: Repository name
            artifact_data: Execution data to save
            file_path: Optional file path (if None, generates from eval name and timestamp)
            oauth_token: Optional OAuth token for git operations
            author_name: Optional git commit author name
            author_email: Optional git commit author email
            user_session: Optional user session for PR creation
            
        Returns:
            Tuple[EvalExecutionMeta, Optional[PRInfo]]: Saved execution metadata and PR info
        """
        repo_path = self.local_repo_service.get_repo_path(user_id, repo_name)
        
        if not repo_path.exists():
            raise NotFoundException(
                resource="Repository",
                identifier=repo_name
            )
        
        execution_result = artifact_data.execution
        
        # Generate file path if not provided
        if not file_path:
            # Find the eval file to determine where to save the execution
            # For now, we'll save in .promptrepo/evals/executions/{eval_name}-{timestamp}.eval_execution.yaml
            timestamp = execution_result.executed_at.strftime("%Y-%m-%dT%H-%M-%S")
            eval_name = execution_result.eval_name
            file_path = f".promptrepo/evals/executions/{eval_name}-{timestamp}{self.EXECUTION_SUFFIX}"
        
        # Convert to dict for YAML serialization
        exec_dict = artifact_data.model_dump(mode='json')
        
        # Save using FileOperationsService (for simplicity, not using git workflow for executions)
        full_file_path = repo_path / file_path
        full_file_path.parent.mkdir(parents=True, exist_ok=True)
        
        file_ops = FileOperationsService()
        save_result = file_ops.save_yaml_file(full_file_path, exec_dict)
        
        if not save_result.success:
            raise AppException(message=f"Failed to save execution to {file_path}")
        
        logger.info(f"Saved execution for {execution_result.eval_name} to {file_path}")
        
        # For now, we don't create PRs for executions (they're data, not definitions)
        # But we return the metadata in the expected format
        
        execution_meta = EvalExecutionMeta(
            execution=execution_result,
            repo_name=repo_name,
            file_path=file_path
        )
        
        return execution_meta, None
    
    async def delete(
        self,
        user_id: str,
        repo_name: str,
        file_path: str
    ) -> bool:
        """
        Delete an execution by file path.
        
        Args:
            user_id: User ID
            repo_name: Repository name
            file_path: Relative path to execution file from repo root
            
        Returns:
            bool: True if deletion was successful
        """
        repo_path = self.local_repo_service.get_repo_path(user_id, repo_name)
        
        if not repo_path.exists():
            raise NotFoundException(
                resource="Repository",
                identifier=repo_name
            )
        
        full_file_path = repo_path / file_path
        
        if not full_file_path.exists():
            raise NotFoundException(
                resource="Execution",
                identifier=file_path
            )
        
        try:
            full_file_path.unlink()
            logger.info(f"Deleted execution at {file_path} from {repo_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete execution at {file_path}: {e}")
            raise AppException(message=f"Failed to delete execution: {str(e)}")
    
    async def list_executions_for_eval(
        self,
        user_id: str,
        repo_name: str,
        file_path: str,
        limit: int = 10
    ) -> List[EvalExecutionMeta]:
        """List execution history for a specific eval.
        
        Args:
            user_id: User ID
            repo_name: Repository name
            file_path: Relative path to eval file from repo root
            limit: Maximum number of executions to return
            
        Returns:
            List[EvalExecutionMeta]: List of execution metadata
        """
        repo_path = self.local_repo_service.get_repo_path(user_id, repo_name)
        
        if not repo_path.exists():
            raise NotFoundException(
                resource="Repository",
                identifier=repo_name
            )
        
        # Get executions directory (eval file parent / executions)
        eval_file = repo_path / file_path
        executions_dir = eval_file.parent / self.EXECUTIONS_DIR
        
        # If executions directory doesn't exist, return empty list
        if not executions_dir.exists():
            return []
        
        # Load all execution files
        executions = []
        file_ops = FileOperationsService()
        
        for exec_file in executions_dir.glob(f"*{self.EXECUTION_SUFFIX}"):
            try:
                exec_data_raw = file_ops.load_yaml_file(exec_file)
                
                if not exec_data_raw or "execution" not in exec_data_raw:
                    logger.warning(f"Invalid execution file: {exec_file}")
                    continue
                
                exec_result = exec_data_raw["execution"]
                
                # Parse datetime fields
                executed_at = exec_result.get("executed_at")
                if isinstance(executed_at, str):
                    executed_at = datetime.fromisoformat(executed_at)
                exec_result["executed_at"] = executed_at
                
                # Parse test results executed_at
                for test_result in exec_result.get("test_results", []):
                    test_executed_at = test_result.get("executed_at")
                    if isinstance(test_executed_at, str):
                        test_result["executed_at"] = datetime.fromisoformat(test_executed_at)
                
                execution_result = EvalExecutionResult(**exec_result)
                
                # Get relative path for the execution file
                relative_exec_path = str(exec_file.relative_to(repo_path))
                
                execution_meta = EvalExecutionMeta(
                    execution=execution_result,
                    repo_name=repo_name,
                    file_path=relative_exec_path
                )
                executions.append(execution_meta)
            except Exception as e:
                logger.error(f"Failed to load execution file {exec_file}: {e}")
                continue
        
        # Sort by execution time (newest first) and limit
        executions.sort(key=lambda x: x.execution.executed_at, reverse=True)
        
        return executions[:limit]
    
    async def get_latest_execution(
        self,
        user_id: str,
        repo_name: str,
        file_path: str
    ) -> Optional[EvalExecutionMeta]:
        """Get latest execution result for an eval.
        
        Args:
            user_id: User ID
            repo_name: Repository name
            file_path: Relative path to eval file from repo root
        """
        executions = await self.list_executions_for_eval(user_id, repo_name, file_path, limit=1)
        return executions[0] if executions else None
    
    async def save_execution_result(
        self,
        user_id: str,
        repo_name: str,
        file_path: str,
        execution_result: EvalExecutionResult
    ) -> bool:
        """
        Save execution result to YAML file.
        
        This is a helper method used by EvalExecutionService.
        
        Args:
            user_id: User ID
            repo_name: Repository name
            file_path: Relative path to eval file from repo root
            execution_result: Execution result to save
            
        Returns:
            True if save was successful, False otherwise
        """
        # Wrap in EvalExecutionData and use the save method
        execution_data = EvalExecutionData(execution=execution_result)
        
        try:
            await self.save(
                user_id=user_id,
                repo_name=repo_name,
                artifact_data=execution_data,
                file_path=None  # Let it generate the path
            )
            return True
        except Exception as e:
            logger.error(f"Failed to save execution result: {e}")
            return False
    
    def validate(self, artifact_data: EvalExecutionData) -> EvalExecutionData:
        """
        Validate eval execution data using Pydantic model.
        
        Args:
            artifact_data: The eval execution data to validate
            
        Returns:
            The validated eval execution data
            
        Raises:
            ValidationException: If validation fails
        """
        from middlewares.rest.exceptions import ValidationException
        
        try:
            # If it's already EvalExecutionData, validate it
            if isinstance(artifact_data, EvalExecutionData):
                validated = EvalExecutionData.model_validate(artifact_data.model_dump())
            else:
                # Handle dict input
                validated = EvalExecutionData.model_validate(artifact_data)
            
            logger.debug(f"Eval execution data validated successfully")
            return validated
        except Exception as e:
            logger.error(f"Eval execution validation failed: {str(e)}")
            raise ValidationException(f"Invalid eval execution data: {str(e)}")