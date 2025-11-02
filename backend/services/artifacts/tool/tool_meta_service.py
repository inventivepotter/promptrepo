"""Tool metadata service for managing tool definition CRUD operations."""

import logging
from datetime import datetime, timezone
from typing import List, Optional, Tuple

from schemas.artifact_type_enum import ArtifactType
from services.artifacts.artifact_meta_interface import ArtifactMetaInterface
from services.local_repo.local_repo_service import LocalRepoService
from services.local_repo.models import PRInfo
from services.artifacts.tool.models import (
    ToolData,
    ToolDefinition,
    ToolSummary,
    ToolMeta
)
from middlewares.rest.exceptions import ValidationException

logger = logging.getLogger(__name__)


class ToolMetaService(ArtifactMetaInterface[ToolData, ToolMeta]):
    """Service for managing tool metadata (CRUD operations on tool definitions)."""

    TOOL_FILE_SUFFIX = f".{ArtifactType.TOOL}.yaml"
    
    def __init__(
        self,
        local_repo_service: LocalRepoService,
    ):
        """Initialize tool service with dependencies.
        
        Args:
            local_repo_service: Service for local repository operations
        """
        self.local_repo_service = local_repo_service
    
    
    async def discover(self, user_id: str, repo_name: str) -> List[ToolMeta]:
        """
        Discover all tool artifacts in a repository.
        
        Args:
            user_id: User ID
            repo_name: Repository name
            
        Returns:
            List[ToolMeta]: List of tool metadata
        """
        # Use the generalized discovery from LocalRepoService
        discovery_result = self.local_repo_service.discover_artifacts(user_id, repo_name)
        
        # Get tool file paths
        tool_files = discovery_result.get_files_by_type(ArtifactType.TOOL)
        
        tool_metas = []
        for tool_file_path in tool_files:
            try:
                tool_meta = await self.get(user_id, repo_name, tool_file_path)
                if tool_meta:
                    tool_metas.append(tool_meta)
            except Exception as e:
                logger.warning(f"Failed to load tool from {tool_file_path}: {e}")
                continue
        
        logger.info(f"Discovered {len(tool_metas)} tools in {repo_name} for user {user_id}")
        return tool_metas
    
    async def save(
        self,
        user_id: str,
        repo_name: str,
        artifact_data: ToolData,
        file_path: Optional[str] = None,
        oauth_token: Optional[str] = None,
        author_name: Optional[str] = None,
        author_email: Optional[str] = None,
        user_session = None
    ) -> Tuple[ToolMeta, Optional[PRInfo]]:
        """
        Save a tool artifact (create or update).
        
        Args:
            user_id: User ID
            repo_name: Repository name
            artifact_data: Tool data to save
            file_path: Optional file path for updates
            oauth_token: Optional OAuth token for git operations
            author_name: Optional git commit author name
            author_email: Optional git commit author email
            user_session: Optional user session for PR creation
            
        Returns:
            Tuple[ToolMeta, Optional[PRInfo]]: Saved tool metadata and PR info if created
        """
        # Validate the tool data
        validated = self.validate(artifact_data)
        tool = validated.tool
        
        tool.updated_at = datetime.now(timezone.utc)
        
        try:
            # Convert to dict and save as YAML
            data_dict = validated.model_dump(mode='json', exclude_none=True, exclude_unset=True)
            
            # Save the artifact using LocalRepoService (includes git workflow)
            save_result = await self.local_repo_service.save_artifact(
                user_id=user_id,
                repo_name=repo_name,
                artifact_type=ArtifactType.TOOL,
                artifact_name=tool.name,
                artifact_data=data_dict,
                file_path=file_path if file_path else None,
                oauth_token=oauth_token,
                author_name=author_name,
                author_email=author_email,
                user_session=user_session
            )
            
            action = "Updated" if save_result.is_update else "Created"
            logger.info(f"{action} tool: {tool.name} in {repo_name}")
            
        except ValidationException:
            raise
        except Exception as e:
            logger.error(f"Failed to save tool {tool.name}: {e}", exc_info=True)
            raise ValidationException(f"Failed to save tool: {str(e)}")
        
        logger.info(f"Completed save workflow for tool: {tool.name} in {repo_name}")
        
        # Create ToolMeta response
        tool_meta = ToolMeta(
            tool=ToolData(tool=tool),
            repo_name=repo_name,
            file_path=save_result.file_path,
            pr_info=save_result.pr_info.model_dump(mode='json') if save_result.pr_info else None
        )
        
        return tool_meta, save_result.pr_info
    
    async def delete(self, user_id: str, repo_name: str, file_path: str) -> bool:
        """
        Delete a tool artifact.
        
        Args:
            user_id: User ID
            repo_name: Repository name
            file_path: Relative path to tool file from repo root
            
        Returns:
            bool: True if deletion was successful
        """
        # Get repository path and construct full tool path
        repo_path = self.local_repo_service.get_repo_path(user_id, repo_name)
        tool_path = repo_path / file_path
        
        if not tool_path.exists():
            logger.warning("Tool file not found for deletion: %s", tool_path)
            return False
        
        try:
            tool_path.unlink()
            logger.info(f"Successfully deleted tool at {file_path} from {repo_name}")
            return True
        except Exception as e:
            logger.exception("Failed to delete tool at %s", file_path)
            return False
    
    async def get(self, user_id: str, repo_name: str, file_path: str) -> Optional[ToolMeta]:
        """
        Get a single tool artifact by file path.
        
        Args:
            user_id: User ID
            repo_name: Repository name
            file_path: Relative path to tool file from repo root
            
        Returns:
            Optional[ToolMeta]: Tool metadata if found, None otherwise
        """
        try:
            # Load the YAML file using LocalRepoService
            yaml_data = self.local_repo_service.load_artifact(
                user_id=user_id,
                repo_name=repo_name,
                file_path=file_path,
                artifact_type=ArtifactType.TOOL
            )
            
            if not yaml_data:
                logger.warning(f"Tool file not found or empty: {file_path}")
                return None
            
            # Parse and validate the tool data
            tool_data = ToolData(**yaml_data)
            
            # Create ToolMeta response
            tool_meta = ToolMeta(
                tool=tool_data,
                repo_name=repo_name,
                file_path=file_path,
                pr_info=None
            )
            
            logger.info(f"Successfully loaded tool from {file_path} in {repo_name}")
            return tool_meta
            
        except Exception as e:
            logger.error(f"Failed to get tool {file_path}: {e}")
            return None
    
    def _validate_tool(self, tool: ToolDefinition) -> None:
        """Validate a tool definition.
        
        Args:
            tool: Tool definition to validate
            
        Raises:
            ValidationException: If validation fails
        """
        # Check that all required parameters are defined in properties
        for param_name in tool.parameters.required:
            if param_name not in tool.parameters.properties:
                raise ValidationException(
                    f"Required parameter '{param_name}' not found in parameter properties"
                )
        
        # Check that parameter defaults match their types
        for param_name, param_prop in tool.parameters.properties.items():
            if param_prop.default is not None:
                # Type validation is already done in the model validator
                pass
        
        # Check that enum values match the parameter type
        for param_name, param_prop in tool.parameters.properties.items():
            if param_prop.enum:
                for enum_value in param_prop.enum:
                    if param_prop.type == "string" and not isinstance(enum_value, str):
                        raise ValidationException(
                            f"Enum value must be string for parameter '{param_name}'"
                        )
                    elif param_prop.type == "number" and not isinstance(enum_value, (int, float)):
                        raise ValidationException(
                            f"Enum value must be number for parameter '{param_name}'"
                        )
                    elif param_prop.type == "boolean" and not isinstance(enum_value, bool):
                        raise ValidationException(
                            f"Enum value must be boolean for parameter '{param_name}'"
                        )
        
        logger.debug(f"Tool '{tool.name}' passed validation")
    
    def validate(self, artifact_data: ToolData) -> ToolData:
        """
        Validate tool data using Pydantic model.
        
        Args:
            artifact_data: The tool data to validate
            
        Returns:
            The validated tool data
            
        Raises:
            ValidationException: If validation fails
        """
        try:
            # If it's already a ToolData, validate it
            if isinstance(artifact_data, ToolData):
                validated = ToolData.model_validate(artifact_data.model_dump())
            else:
                # Handle dict input
                validated = ToolData.model_validate(artifact_data)
            
            # Run additional validation logic on the tool definition
            self._validate_tool(validated.tool)
            
            logger.debug(f"Tool '{validated.tool.name}' validated successfully")
            return validated
        except ValidationException:
            raise
        except Exception as e:
            logger.error(f"Tool validation failed: {str(e)}")
            raise ValidationException(f"Invalid tool data: {str(e)}")