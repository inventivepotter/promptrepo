"""
Main implementation of the Eval Service.

Handles eval operations including CRUD operations for test definitions
using constructor injection following SOLID principles.
"""

import logging
from datetime import datetime, timezone
from typing import List, Optional, Tuple, TYPE_CHECKING

from schemas.artifact_type_enum import ArtifactType
from services.artifacts.artifact_meta_interface import ArtifactMetaInterface
from services.local_repo.local_repo_service import LocalRepoService
from services.local_repo.models import PRInfo
from middlewares.rest.exceptions import NotFoundException, AppException

from .models import (
    EvalData,
    EvalDefinition,
    EvalMeta,
    EvalSummary
)

if TYPE_CHECKING:
    from .eval_execution_meta_service import EvalExecutionMetaService

logger = logging.getLogger(__name__)


class EvalMetaService(ArtifactMetaInterface[EvalData, EvalMeta]):
    """
    Main eval service implementation using constructor injection.
    
    This service handles:
    - CRUD operations for evals
    - Eval discovery in repositories
    - File-based storage in .promptrepo/evals/ directory
    """

    EVAL_FILE_SUFFIX = f".{ArtifactType.EVAL}.yaml"
    
    def __init__(
        self,
        local_repo_service: LocalRepoService,
        eval_execution_meta_service: Optional["EvalExecutionMetaService"] = None
    ):
        """
        Initialize EvalMetaService with injected dependencies.
        
        Args:
            local_repo_service: Local repository service for git operations and file I/O
            eval_execution_meta_service: Optional eval execution meta service for getting execution history
        """
        self.local_repo_service = local_repo_service
        self.eval_execution_meta_service = eval_execution_meta_service
    
    async def discover(
        self,
        user_id: str,
        repo_name: str
    ) -> List[EvalMeta]:
        """
        Discover all evals in a repository.
        
        Args:
            user_id: User ID
            repo_name: Repository name
            
        Returns:
            List[EvalMeta]: List of eval metadata
        """
        repo_path = self.local_repo_service.get_repo_path(user_id, repo_name)
        
        logger.info(f"Discovery: user_id={user_id}, repo_name={repo_name}, repo_path={repo_path}, exists={repo_path.exists()}")
        
        if not repo_path.exists():
            logger.error(f"Repository not found at {repo_path}")
            raise NotFoundException(
                resource="Repository",
                identifier=repo_name
            )
        
        # Use the generalized discovery from LocalRepoService
        discovery_result = self.local_repo_service.discover_artifacts(user_id, repo_name)
        
        # Get eval file paths
        eval_files = discovery_result.get_files_by_type(ArtifactType.EVAL)
        
        eval_data_list = []
        
        for eval_file_path in eval_files:
            try:
                eval_data = await self.get(user_id, repo_name, eval_file_path)
                if eval_data:
                    eval_data_list.append(eval_data)
            except Exception as e:
                logger.error(f"Failed to load eval {eval_file_path}: {e}")
                continue

        logger.info(f"Discovered {len(eval_data_list)} evals in {repo_name}")
        return eval_data_list
    
    async def get(
        self,
        user_id: str,
        repo_name: str,
        file_path: str
    ) -> Optional[EvalMeta]:
        """
        Get a single eval by file path.
        
        Args:
            user_id: User ID
            repo_name: Repository name
            file_path: Relative path to eval file from repo root
            
        Returns:
            Optional[EvalMeta]: Eval metadata if found, None otherwise
        """
        repo_path = self.local_repo_service.get_repo_path(user_id, repo_name)
        
        if not repo_path.exists():
            raise NotFoundException(
                resource="Repository",
                identifier=repo_name
            )
        
        # Load eval file using LocalRepoService
        eval_data_raw = self.local_repo_service.load_artifact(
            user_id=user_id,
            repo_name=repo_name,
            file_path=file_path,
            artifact_type=ArtifactType.EVAL
        )
        
        if not eval_data_raw or "eval" not in eval_data_raw:
            logger.warning(f"Invalid eval file: {file_path}")
            return None
        
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

        # Create EvalMeta with repository information
        return EvalMeta(
            eval=eval_definition,
            repo_name=repo_name,
            file_path=file_path,
            pr_info=None
        )

    async def save(
        self,
        user_id: str,
        repo_name: str,
        artifact_data: EvalData,
        file_path: Optional[str] = None,
        oauth_token: Optional[str] = None,
        author_name: Optional[str] = None,
        author_email: Optional[str] = None,
        user_session = None
    ) -> Tuple[EvalMeta, Optional[PRInfo]]:
        """
        Save an eval (create or update).
        
        Args:
            user_id: User ID
            repo_name: Repository name
            artifact_data: Eval data to save
            file_path: Optional file path for updates
            oauth_token: Optional OAuth token for git operations
            author_name: Optional git commit author name
            author_email: Optional git commit author email
            user_session: Optional user session for PR creation
            
        Returns:
            Tuple[EvalMeta, Optional[PRInfo]]: Saved eval metadata and PR info if created
        """
        repo_path = self.local_repo_service.get_repo_path(user_id, repo_name)
        
        if not repo_path.exists():
            raise NotFoundException(
                resource="Repository",
                identifier=repo_name
            )
        
        artifact_data.eval.updated_at = datetime.now(timezone.utc)
        
        # Convert to dict for YAML serialization
        eval_dict = artifact_data.model_dump(mode='json')
        
        # Save the artifact using LocalRepoService (includes git workflow)
        save_result = await self.local_repo_service.save_artifact(
            user_id=user_id,
            repo_name=repo_name,
            artifact_type=ArtifactType.EVAL,
            artifact_name=artifact_data.eval.name,
            artifact_data=eval_dict,
            file_path=file_path if file_path else None,
            oauth_token=oauth_token,
            author_name=author_name,
            author_email=author_email,
            user_session=user_session
        )
        
        action = "Updated" if save_result.is_update else "Created"
        logger.info(f"{action} eval {artifact_data.eval.name} in {repo_name}")
        
        # Reload the eval to get the latest state
        updated_eval = await self.get(user_id, repo_name, save_result.file_path)
        
        if not updated_eval:
            raise AppException(
                message=f"Failed to load saved eval from {save_result.file_path}"
            )
        
        # Attach PR info if available
        if save_result.pr_info:
            updated_eval.pr_info = save_result.pr_info.model_dump(mode='json')
        
        logger.info(f"Completed git workflow for eval: {artifact_data.eval.name} in {repo_name}")
        return updated_eval, save_result.pr_info
    
    async def delete(
        self,
        user_id: str,
        repo_name: str,
        file_path: str
    ) -> bool:
        """
        Delete an eval.
        
        Args:
            user_id: User ID
            repo_name: Repository name
            file_path: Relative path to eval file from repo root
            
        Returns:
            bool: True if deletion was successful, False otherwise
        """
        repo_path = self.local_repo_service.get_repo_path(user_id, repo_name)
        
        if not repo_path.exists():
            raise NotFoundException(
                resource="Repository",
                identifier=repo_name
            )
        
        eval_file = repo_path / file_path
        eval_dir = eval_file.parent
        
        if not eval_dir.exists():
            raise NotFoundException(
                resource="Eval",
                identifier=file_path
            )
        
        # Delete entire eval directory (including executions)
        try:
            import shutil
            shutil.rmtree(eval_dir)
            logger.info(f"Deleted eval at {file_path} from {repo_name}")
            return True
        except Exception as e:
            logger.error(f"Failed to delete eval at {file_path}: {e}")
            return False
    
    def validate(self, artifact_data: EvalData) -> EvalData:
        """
        Validate eval data using Pydantic model.
        
        Args:
            artifact_data: The eval data to validate
            
        Returns:
            The validated eval data
            
        Raises:
            ValidationException: If validation fails
        """
        from middlewares.rest.exceptions import ValidationException
        
        try:
            # If it's already EvalData, validate it
            if isinstance(artifact_data, EvalData):
                validated = EvalData.model_validate(artifact_data.model_dump())
            else:
                # Handle dict input
                validated = EvalData.model_validate(artifact_data)
            
            logger.debug(f"Eval '{validated.eval.name}' validated successfully")
            return validated
        except Exception as e:
            logger.error(f"Eval validation failed: {str(e)}")
            raise ValidationException(f"Invalid eval data: {str(e)}")