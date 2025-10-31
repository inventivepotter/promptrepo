"""
Main implementation of the Eval Service.

Handles eval suite operations including CRUD operations for eval definitions
and retrieval of execution history using constructor injection following SOLID principles.
"""

import logging
from datetime import datetime, timezone
from pathlib import Path
from typing import List, Optional, Dict, Any, Union, Tuple

from schemas.artifact_type_enum import ArtifactType
from schemas.hosting_type_enum import HostingType
from services.config.config_interface import IConfig
from services.local_repo.local_repo_service import LocalRepoService
from services.local_repo.models import PRInfo
from services.file_operations import FileOperationsService
from settings import settings
from middlewares.rest.exceptions import NotFoundException, AppException

from .models import (
    EvalSuiteData,
    EvalSuiteDefinition,
    EvalSuiteSummary,
    EvalSuiteExecutionResult,
    EvalSuiteExecutionData
)

logger = logging.getLogger(__name__)


class EvalMetaService:
    """
    Main eval service implementation using constructor injection.
    
    This service handles:
    - CRUD operations for eval suites
    - Eval suite discovery in repositories
    - Execution history retrieval
    - File-based storage in .promptrepo/evals/ directory
    """

    EVALS_DIR = ".promptrepo/evals"
    SUITE_FILENAME = "suite.yaml"
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
    
    def _get_suite_path(self, repo_path: Path, suite_name: str) -> Path:
        """Get path to eval suite directory."""
        return repo_path / self.EVALS_DIR / suite_name
    
    def _get_suite_file_path(self, repo_path: Path, suite_name: str) -> Path:
        """Get path to suite.yaml file."""
        return self._get_suite_path(repo_path, suite_name) / self.SUITE_FILENAME
    
    def _get_executions_dir(self, repo_path: Path, suite_name: str) -> Path:
        """Get path to executions directory."""
        return self._get_suite_path(repo_path, suite_name) / self.EXECUTIONS_DIR
    
    async def list_eval_suites(
        self,
        user_id: str,
        repo_name: str
    ) -> List[EvalSuiteSummary]:
        """List all eval suites in repository."""
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
        
        # Scan for suite directories
        for suite_dir in evals_path.iterdir():
            if not suite_dir.is_dir():
                continue
            
            suite_file = suite_dir / self.SUITE_FILENAME
            if not suite_file.exists():
                continue
            
            try:
                # Load suite definition
                suite_data = self.file_ops.load_yaml_file(suite_file)
                if not suite_data or "eval_suite" not in suite_data:
                    logger.warning(f"Invalid suite file: {suite_file}")
                    continue
                
                suite_def = suite_data["eval_suite"]
                
                # Get latest execution info
                latest_execution = await self.get_latest_execution(
                    user_id, repo_name, suite_dir.name
                )
                
                summary = EvalSuiteSummary(
                    name=suite_def.get("name", suite_dir.name),
                    description=suite_def.get("description", ""),
                    eval_count=len(suite_def.get("evals", [])),
                    tags=suite_def.get("tags", []),
                    file_path=str(suite_file.relative_to(repo_path)),
                    last_execution=latest_execution.executed_at if latest_execution else None,
                    last_execution_passed=(
                        latest_execution.passed_evals == latest_execution.total_evals 
                        if latest_execution else None
                    )
                )
                
                summaries.append(summary)
            except Exception as e:
                logger.error(f"Failed to load eval suite {suite_dir.name}: {e}")
                continue
        
        logger.info(f"Found {len(summaries)} eval suites in {repo_name}")
        return summaries
    
    async def get_eval_suite(
        self, 
        user_id: str, 
        repo_name: str, 
        suite_name: str
    ) -> EvalSuiteData:
        """Get specific eval suite definition."""
        repo_base_path = self._get_repo_base_path(user_id)
        repo_path = repo_base_path / repo_name
        
        if not repo_path.exists():
            raise NotFoundException(
                resource="Repository",
                identifier=repo_name
            )
        
        suite_file = self._get_suite_file_path(repo_path, suite_name)
        
        if not suite_file.exists():
            raise NotFoundException(
                resource="Eval suite",
                identifier=suite_name
            )
        
        # Load suite file
        suite_data_raw = self.file_ops.load_yaml_file(suite_file)
        
        if not suite_data_raw or "eval_suite" not in suite_data_raw:
            raise AppException(
                message=f"Invalid eval suite file: {suite_name}"
            )
        
        # Parse datetime fields
        suite_def = suite_data_raw["eval_suite"]
        
        created_at = suite_def.get("created_at")
        if isinstance(created_at, str):
            created_at = datetime.fromisoformat(created_at)
        elif created_at is None:
            created_at = datetime.now(timezone.utc)
        
        updated_at = suite_def.get("updated_at")
        if isinstance(updated_at, str):
            updated_at = datetime.fromisoformat(updated_at)
        elif updated_at is None:
            updated_at = datetime.now(timezone.utc)
        
        suite_def["created_at"] = created_at
        suite_def["updated_at"] = updated_at
        
        # Create EvalSuiteDefinition from parsed data
        suite_definition = EvalSuiteDefinition(**suite_def)

        return EvalSuiteData(eval_suite=suite_definition)

    async def save_eval_suite(
        self,
        user_id: str,
        repo_name: str,
        suite_data: EvalSuiteData,
        oauth_token: Optional[str] = None,
        author_name: Optional[str] = None,
        author_email: Optional[str] = None,
        user_session = None
    ) -> Tuple[EvalSuiteData, Optional[PRInfo]]:
        """
        Create or update eval suite with full git workflow (save, add, commit, push, PR).
        
        This method performs the complete workflow in one go:
        1. Save suite to YAML file
        2. Stage the file
        3. Commit changes
        4. Push to remote
        5. Create PR (if applicable)
        
        Args:
            user_id: User ID
            repo_name: Repository name
            suite_data: Eval suite data to save
            oauth_token: Optional OAuth token for git operations
            author_name: Optional git commit author name
            author_email: Optional git commit author email
            user_session: Optional user session for PR creation
            
        Returns:
            Tuple[EvalSuiteData, Optional[PRInfo]]: Saved suite and PR info if created
        """
        repo_base_path = self._get_repo_base_path(user_id)
        repo_path = repo_base_path / repo_name
        
        if not repo_path.exists():
            raise NotFoundException(
                resource="Repository",
                identifier=repo_name
            )
        
        suite_name = suite_data.eval_suite.name
        suite_file = self._get_suite_file_path(repo_path, suite_name)
        
        # Check if this is an update or create
        is_update = suite_file.exists()
        
        # Update timestamps
        if is_update:
            # Preserve created_at from existing file
            existing_data = self.file_ops.load_yaml_file(suite_file)
            if existing_data and "eval_suite" in existing_data:
                created_at = existing_data["eval_suite"].get("created_at")
                if created_at:
                    if isinstance(created_at, str):
                        suite_data.eval_suite.created_at = datetime.fromisoformat(created_at)
                    else:
                        suite_data.eval_suite.created_at = created_at
        
        suite_data.eval_suite.updated_at = datetime.now(timezone.utc)
        
        # Convert to dict for YAML serialization
        suite_dict = suite_data.model_dump(mode='json')
        
        # Save to file
        success = self.file_ops.save_yaml_file(suite_file, suite_dict)
        
        if not success:
            raise AppException(
                message=f"Failed to save eval suite: {suite_name}"
            )
        
        action = "Updated" if is_update else "Created"
        logger.info(f"{action} eval suite {suite_name} in {repo_name}")
        
        # Get the relative file path for git operations
        file_path = f"{self.EVALS_DIR}/{suite_name}/{self.SUITE_FILENAME}"
        
        # Handle git workflow (branch, commit, push, PR creation)
        pr_info = await self.local_repo_service.handle_git_workflow_after_save(
            user_id=user_id,
            repo_name=repo_name,
            file_path=file_path,
            artifact_type=ArtifactType.EVAL_SUITE,
            oauth_token=oauth_token,
            author_name=author_name,
            author_email=author_email,
            user_session=user_session
        )
        
        logger.info(f"Completed git workflow for eval suite: {suite_name} in {repo_name}")
        return suite_data, pr_info
    
    async def delete_eval_suite(
        self, 
        user_id: str, 
        repo_name: str, 
        suite_name: str
    ) -> bool:
        """Delete eval suite."""
        repo_base_path = self._get_repo_base_path(user_id)
        repo_path = repo_base_path / repo_name
        
        if not repo_path.exists():
            raise NotFoundException(
                resource="Repository",
                identifier=repo_name
            )
        
        suite_dir = self._get_suite_path(repo_path, suite_name)
        
        if not suite_dir.exists():
            raise NotFoundException(
                resource="Eval suite",
                identifier=suite_name
            )
        
        # Delete entire suite directory (including executions)
        success = self.file_ops.delete_directory(suite_dir)
        
        if success:
            logger.info(f"Deleted eval suite {suite_name} from {repo_name}")
        else:
            logger.error(f"Failed to delete eval suite {suite_name}")
        
        return success
    
    async def get_latest_execution(
        self, 
        user_id: str, 
        repo_name: str, 
        suite_name: str
    ) -> Optional[EvalSuiteExecutionResult]:
        """Get latest execution result for an eval suite."""
        executions = await self.list_executions(user_id, repo_name, suite_name, limit=1)
        return executions[0] if executions else None
    
    async def list_executions(
        self, 
        user_id: str, 
        repo_name: str, 
        suite_name: str, 
        limit: int = 10
    ) -> List[EvalSuiteExecutionResult]:
        """List execution history for an eval suite."""
        repo_base_path = self._get_repo_base_path(user_id)
        repo_path = repo_base_path / repo_name
        
        if not repo_path.exists():
            raise NotFoundException(
                resource="Repository",
                identifier=repo_name
            )
        
        executions_dir = self._get_executions_dir(repo_path, suite_name)
        
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
                
                # Parse eval results executed_at
                for eval_result in exec_result.get("eval_results", []):
                    eval_executed_at = eval_result.get("executed_at")
                    if isinstance(eval_executed_at, str):
                        eval_result["executed_at"] = datetime.fromisoformat(eval_executed_at)
                
                execution_result = EvalSuiteExecutionResult(**exec_result)
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
        suite_name: str,
        execution_result: EvalSuiteExecutionResult
    ) -> bool:
        """
        Save execution result to YAML file.
        
        This is a helper method used by EvalExecutionService.
        
        Args:
            user_id: User ID
            repo_name: Repository name
            suite_name: Eval suite name
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
        
        executions_dir = self._get_executions_dir(repo_path, suite_name)
        
        # Create executions directory if it doesn't exist
        self.file_ops.create_directory(executions_dir)
        
        # Generate execution filename with timestamp
        timestamp = execution_result.executed_at.strftime("%Y-%m-%dT%H-%M-%S")
        exec_filename = f"{suite_name}-{timestamp}{self.EXECUTION_SUFFIX}"
        exec_file = executions_dir / exec_filename
        
        # Wrap execution result in EvalSuiteExecutionData
        execution_data = EvalSuiteExecutionData(execution=execution_result)
        
        # Convert to dict for YAML serialization
        exec_dict = execution_data.model_dump(mode='json')
        
        # Save to file
        success = self.file_ops.save_yaml_file(exec_file, exec_dict)
        
        if success:
            logger.info(f"Saved execution result for {suite_name} to {exec_file}")
        else:
            logger.error(f"Failed to save execution result for {suite_name}")
        
        return success