"""
Main implementation of the Eval Service.

Handles eval operations including CRUD operations for test definitions
and retrieval of execution history using constructor injection following SOLID principles.
"""

import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional, Tuple

from schemas.artifact_type_enum import ArtifactType
from schemas.hosting_type_enum import HostingType
from services.config.config_interface import IConfig
from services.local_repo.local_repo_service import LocalRepoService
from services.local_repo.models import PRInfo
from services.file_operations import FileOperationsService
from settings import settings
from middlewares.rest.exceptions import NotFoundException, AppException

from .models import (
    EvalData,
    EvalDefinition,
    EvalSummary,
    EvalExecutionResult,
    EvalExecutionData
)

logger = logging.getLogger(__name__)


class EvalMetaService:
    """
    Main eval service implementation using constructor injection.
    
    This service handles:
    - CRUD operations for evals
    - Eval discovery in repositories
    - Execution history retrieval
    - File-based storage in .promptrepo/evals/ directory
    """

    EVALS_DIR = ".promptrepo/evals"
    EVAL_FILENAME = "eval.yaml"
    EXECUTIONS_DIR = "executions"
    EXECUTION_SUFFIX = ".execution.yaml"
    
    def __init__(
        self,
        config_service: IConfig,
        file_ops_service: FileOperationsService,
        local_repo_service: LocalRepoService
    ):
        """
        Initialize EvalMetaService with injected dependencies.
        
        Args:
            config_service: Configuration service for hosting type
            file_ops_service: File operations service for file I/O
            local_repo_service: Local repository service for git operations
        """
        self.config_service = config_service
        self.file_ops = file_ops_service
        self.local_repo_service = local_repo_service
        
    def _get_repo_base_path(self, user_id: str) -> Path:
        """
        Get the base repository path based on hosting type.
        
        Args:
            user_id: ID of the user
            
        Returns:
            Path object for the repository base directory
        """
        hosting_config = self.config_service.get_hosting_config()
        
        if hosting_config.type == HostingType.INDIVIDUAL:
            return Path(settings.local_repo_path)
        else:
            return Path(settings.multi_user_repo_path) / user_id
    
    def _get_eval_path(self, repo_path: Path, eval_name: str) -> Path:
        """Get path to eval directory."""
        return repo_path / self.EVALS_DIR / eval_name
    
    def _get_eval_file_path(self, repo_path: Path, eval_name: str) -> Path:
        """Get path to eval.yaml file."""
        return self._get_eval_path(repo_path, eval_name) / self.EVAL_FILENAME
    
    def _get_executions_dir(self, repo_path: Path, eval_name: str) -> Path:
        """Get path to executions directory."""
        return self._get_eval_path(repo_path, eval_name) / self.EXECUTIONS_DIR
    
    async def list_evals(
        self,
        user_id: str,
        repo_name: str
    ) -> List[EvalSummary]:
        """List all evals in repository."""
        repo_base_path = self._get_repo_base_path(user_id)
        repo_path = repo_base_path / repo_name
        
        if not repo_path.exists():
            raise NotFoundException(
                resource="Repository",
                identifier=repo_name
            )
        
        evals_path = repo_path / self.EVALS_DIR
        
        # If evals directory doesn't exist, return empty list
        if not evals_path.exists():
            logger.info(f"No evals directory found in {repo_name}")
            return []
        
        summaries = []
        
        # Scan for eval directories
        for eval_dir in evals_path.iterdir():
            if not eval_dir.is_dir():
                continue
            
            eval_file = eval_dir / self.EVAL_FILENAME
            if not eval_file.exists():
                continue
            
            try:
                # Load eval definition
                eval_data = self.file_ops.load_yaml_file(eval_file)
                if not eval_data or "eval" not in eval_data:
                    logger.warning(f"Invalid eval file: {eval_file}")
                    continue
                
                eval_def = eval_data["eval"]
                
                # Get latest execution info
                latest_execution = await self.get_latest_execution(
                    user_id, repo_name, eval_dir.name
                )
                
                summary = EvalSummary(
                    name=eval_def.get("name", eval_dir.name),
                    description=eval_def.get("description", ""),
                    test_count=len(eval_def.get("tests", [])),
                    tags=eval_def.get("tags", []),
                    file_path=str(eval_file.relative_to(repo_path)),
                    last_execution=latest_execution.executed_at if latest_execution else None,
                    last_execution_passed=(
                        latest_execution.passed_tests == latest_execution.total_tests 
                        if latest_execution else None
                    )
                )
                
                summaries.append(summary)
            except Exception as e:
                logger.error(f"Failed to load eval {eval_dir.name}: {e}")
                continue

        logger.info(f"Found {len(summaries)} evals in {repo_name}")
        return summaries
    
    async def get_eval(
        self, 
        user_id: str, 
        repo_name: str, 
        eval_name: str
    ) -> EvalData:
        """Get specific eval definition."""
        repo_base_path = self._get_repo_base_path(user_id)
        repo_path = repo_base_path / repo_name
        
        if not repo_path.exists():
            raise NotFoundException(
                resource="Repository",
                identifier=repo_name
            )
        
        eval_file = self._get_eval_file_path(repo_path, eval_name)
        
        if not eval_file.exists():
            raise NotFoundException(
                resource="Eval",
                identifier=eval_name
            )
        
        # Load eval file
        eval_data_raw = self.file_ops.load_yaml_file(eval_file)
        
        if not eval_data_raw or "eval" not in eval_data_raw:
            raise AppException(
                message=f"Invalid eval file: {eval_name}"
            )
        
        # Parse datetime fields
        eval_def = eval_data_raw["eval"]
        
        created_at = eval_def.get("created_at")
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at)
        elif created_at is None:
            created_at = datetime.now(timezone.utc)
        
        updated_at = eval_def.get("updated_at")
        if isinstance(updated_at, str):
            updated_at = datetime.fromisoformat(updated_at)
        elif updated_at is None:
            updated_at = datetime.now(timezone.utc)
        
        eval_def["created_at"] = created_at
        eval_def["updated_at"] = updated_at
        
        # Create EvalDefinition from parsed data
        eval_definition = EvalDefinition(**eval_def)

        return EvalData(eval=eval_definition)

    async def save_eval(
        self,
        user_id: str,
        repo_name: str,
        eval_data: EvalData,
        oauth_token: Optional[str] = None,
        author_name: Optional[str] = None,
        author_email: Optional[str] = None,
        user_session = None
    ) -> Tuple[EvalData, Optional[PRInfo]]:
        """
        Create or update eval eval with full git workflow (save, add, commit, push, PR).
        
        This method performs the complete workflow in one go:
        1. Save eval to YAML file
        2. Stage the file
        3. Commit changes
        4. Push to remote
        5. Create PR (if applicable)
        
        Args:
            user_id: User ID
            repo_name: Repository name
            eval_data: Eval eval data to save
            oauth_token: Optional OAuth token for git operations
            author_name: Optional git commit author name
            author_email: Optional git commit author email
            user_session: Optional user session for PR creation
            
        Returns:
            Tuple[EvalevalData, Optional[PRInfo]]: Saved eval and PR info if created
        """
        repo_base_path = self._get_repo_base_path(user_id)
        repo_path = repo_base_path / repo_name
        
        if not repo_path.exists():
            raise NotFoundException(
                resource="Repository",
                identifier=repo_name
            )
        
        eval_name = eval_data.eval.name
        eval_file = self._get_eval_file_path(repo_path, eval_name)
        
        # Check if this is an update or create
        is_update = eval_file.exists()
        
        # Update timestamps
        if is_update:
            # Preserve created_at from existing file
            existing_data = self.file_ops.load_yaml_file(eval_file)
            if existing_data and "eval" in existing_data:
                created_at = existing_data["eval"].get("created_at")
                if created_at:
                    if isinstance(created_at, str):
                        eval_data.eval.created_at = datetime.fromisoformat(created_at)
                    else:
                        eval_data.eval.created_at = created_at
        
        eval_data.eval.updated_at = datetime.now(timezone.utc)
        
        # Convert to dict for YAML serialization
        eval_dict = eval_data.model_dump(mode='json')
        
        # Save to file
        success = self.file_ops.save_yaml_file(eval_file, eval_dict)
        
        if not success:
            raise AppException(
                message=f"Failed to save eval: {eval_name}"
            )
        
        action = "Updated" if is_update else "Created"
        logger.info(f"{action} eval {eval_name} in {repo_name}")
        
        # Get the relative file path for git operations
        file_path = f"{self.EVALS_DIR}/{eval_name}/{self.EVAL_FILENAME}"
        
        # Handle git workflow (branch, commit, push, PR creation)
        pr_info = await self.local_repo_service.handle_git_workflow_after_save(
            user_id=user_id,
            repo_name=repo_name,
            file_path=file_path,
            artifact_type=ArtifactType.EVAL,
            oauth_token=oauth_token,
            author_name=author_name,
            author_email=author_email,
            user_session=user_session
        )
        
        logger.info(f"Completed git workflow for eval: {eval_name} in {repo_name}")
        return eval_data, pr_info
    
    async def delete_eval(
        self, 
        user_id: str, 
        repo_name: str, 
        eval_name: str
    ) -> bool:
        """Delete eval."""
        repo_base_path = self._get_repo_base_path(user_id)
        repo_path = repo_base_path / repo_name
        
        if not repo_path.exists():
            raise NotFoundException(
                resource="Repository",
                identifier=repo_name
            )
        
        eval_dir = self._get_eval_path(repo_path, eval_name)
        
        if not eval_dir.exists():
            raise NotFoundException(
                resource="Eval",
                identifier=eval_name
            )
        
        # Delete entire eval directory (including executions)
        success = self.file_ops.delete_directory(eval_dir)
        
        if success:
            logger.info(f"Deleted eval {eval_name} from {repo_name}")
        else:
            logger.error(f"Failed to delete eval {eval_name}")
        
        return success
    
    async def get_latest_execution(
        self, 
        user_id: str, 
        repo_name: str, 
        eval_name: str
    ) -> Optional[EvalExecutionResult]:
        """Get latest execution result for an eval."""
        executions = await self.list_executions(user_id, repo_name, eval_name, limit=1)
        return executions[0] if executions else None
    
    async def list_executions(
        self, 
        user_id: str, 
        repo_name: str, 
        eval_name: str, 
        limit: int = 10
    ) -> List[EvalExecutionResult]:
        """List execution history for an eval."""
        repo_base_path = self._get_repo_base_path(user_id)
        repo_path = repo_base_path / repo_name
        
        if not repo_path.exists():
            raise NotFoundException(
                resource="Repository",
                identifier=repo_name
            )
        
        executions_dir = self._get_executions_dir(repo_path, eval_name)
        
        # If executions directory doesn't exist, return empty list
        if not executions_dir.exists():
            return []
        
        # Load all execution files
        executions = []
        
        for exec_file in executions_dir.glob(f"*{self.EXECUTION_SUFFIX}"):
            try:
                exec_data_raw = self.file_ops.load_yaml_file(exec_file)
                
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
                executions.append(execution_result)
            except Exception as e:
                logger.error(f"Failed to load execution file {exec_file}: {e}")
                continue
        
        # Sort by execution time (newest first) and limit
        executions.sort(key=lambda x: x.executed_at, reverse=True)
        
        return executions[:limit]
    
    async def save_execution_result(
        self,
        user_id: str,
        repo_name: str,
        eval_name: str,
        execution_result: EvalExecutionResult
    ) -> bool:
        """
        Save execution result to YAML file.
        
        This is a helper method used by EvalExecutionService.
        
        Args:
            user_id: User ID
            repo_name: Repository name
            eval_name: Eval eval name
            execution_result: Execution result to save
            
        Returns:
            True if save was successful, False otherwise
        """
        repo_base_path = self._get_repo_base_path(user_id)
        repo_path = repo_base_path / repo_name
        
        if not repo_path.exists():
            raise NotFoundException(
                resource="Repository",
                identifier=repo_name
            )
        
        executions_dir = self._get_executions_dir(repo_path, eval_name)
        
        # Create executions directory if it doesn't exist
        self.file_ops.create_directory(executions_dir)
        
        # Generate execution filename with timestamp
        timestamp = execution_result.executed_at.strftime("%Y-%m-%dT%H-%M-%S")
        exec_filename = f"{eval_name}-{timestamp}{self.EXECUTION_SUFFIX}"
        exec_file = executions_dir / exec_filename
        
        # Wrap execution result in EvalExecutionData
        execution_data = EvalExecutionData(execution=execution_result)
        
        # Convert to dict for YAML serialization
        exec_dict = execution_data.model_dump(mode='json')
        
        # Save to file
        success = self.file_ops.save_yaml_file(exec_file, exec_dict)
        
        if success:
            logger.info(f"Saved execution result for {eval_name} to {exec_file}")
        else:
            logger.error(f"Failed to save execution result for {eval_name}")
        
        return success