"""Tool service for managing mock tool definitions."""

import logging
from pathlib import Path
from typing import List, Optional, Tuple

import yaml
from pydantic import ValidationError

from schemas.artifact_type_enum import ArtifactType
from schemas.hosting_type_enum import HostingType
from services.config.config_interface import IConfig
from services.file_operations import FileOperationsService
from services.local_repo.local_repo_service import LocalRepoService
from services.local_repo.models import PRInfo
from services.tool.models import (
    ToolData,
    ToolDefinition,
    ToolSummary
)
from settings import settings
from middlewares.rest.exceptions import NotFoundException, ValidationException

logger = logging.getLogger(__name__)


class ToolService:
    """Service for managing tool definitions."""
    
    TOOLS_DIR = ".promptrepo/mock_tools"
    TOOL_FILE_SUFFIX = ".tool.yaml"
    
    def __init__(
        self,
        config_service: IConfig,
        local_repo_service: LocalRepoService,
        file_operations_service: FileOperationsService
    ):
        """Initialize tool service with dependencies.
        
        Args:
            config_service: Configuration service for hosting type
            local_repo_service: Service for local repository operations
            file_operations_service: Service for file operations
        """
        self.config_service = config_service
        self.local_repo_service = local_repo_service
        self.file_operations_service = file_operations_service
    
    def _get_repo_base_path(self, user_id: str) -> Path:
        """Get the base repository path based on hosting type.
        
        Args:
            user_id: ID of the user
            
        Returns:
            Path object for the repository base directory
        """
        hosting_config = self.config_service.get_hosting_config()
        
        if hosting_config.type == HostingType.INDIVIDUAL:
            # Use local_repo_path for individual hosting
            return Path(settings.local_repo_path)
        else:
            # Use multi_user_repo_path with user scoping for organization
            return Path(settings.multi_user_repo_path) / user_id
    
    def _get_tool_path(self, tool_name: str, repo_name: str, user_id: str) -> Path:
        """Get the full path for a tool file.
        
        Args:
            tool_name: Name of the tool
            repo_name: Name of the repository
            user_id: ID of the user
            
        Returns:
            Path to the tool file
        """
        repo_base_path = self._get_repo_base_path(user_id)
        repo_path = repo_base_path / repo_name
        return repo_path / self.TOOLS_DIR / f"{tool_name}{self.TOOL_FILE_SUFFIX}"
    
    def _get_tools_dir(self, repo_name: str, user_id: str) -> Path:
        """Get the tools directory path for a repository.
        
        Args:
            repo_name: Name of the repository
            user_id: ID of the user
            
        Returns:
            Path to the tools directory
        """
        repo_base_path = self._get_repo_base_path(user_id)
        repo_path = repo_base_path / repo_name
        return repo_path / self.TOOLS_DIR
    
    def load_tool(self, tool_name: str, repo_name: str, user_id: str) -> ToolDefinition:
        """Load a tool definition from YAML file.
        
        Args:
            tool_name: Name of the tool
            repo_name: Name of the repository
            user_id: ID of the user
            
        Returns:
            Tool definition
            
        Raises:
            NotFoundException: If tool file not found
            ValidationException: If tool file is invalid
        """
        tool_path = self._get_tool_path(tool_name, repo_name, user_id)
        
        if not tool_path.exists():
            logger.warning(f"Tool file not found: {tool_path}")
            raise NotFoundException(resource="Tool", identifier=f"{repo_name}:{tool_name}")
        
        try:
            # Read the YAML file using the correct method
            yaml_data = self.file_operations_service.load_yaml_file(str(tool_path))
            
            if not yaml_data:
                raise ValidationException(f"Failed to load YAML file for tool '{tool_name}'")
            
            # Parse and validate the tool data
            tool_data = ToolData(**yaml_data)
            
            logger.info(f"Successfully loaded tool: {tool_name} from {repo_name}")
            return tool_data.tool
            
        except yaml.YAMLError as e:
            logger.error(f"Failed to parse YAML for tool {tool_name}: {e}")
            raise ValidationException(f"Invalid YAML format in tool file: {e}")
        except ValidationError as e:
            logger.error(f"Tool validation failed for {tool_name}: {e}")
            raise ValidationException(f"Tool validation failed: {e}")
        except Exception as e:
            logger.error(f"Failed to load tool {tool_name}: {e}")
            raise ValidationException(f"Failed to load tool: {e}")
    
    def discover_tools(self, repo_name: str, user_id: str) -> List[str]:
        """
        Discover tool files in a repository using the generalized artifact discovery.
        
        Uses LocalRepoService.discover_artifacts() to find all .tool.yaml files
        in a single efficient scan.
        
        Args:
            repo_name: Name of the repository
            user_id: ID of the user
            
        Returns:
            List of tool file paths
        """
        # Use the generalized discovery from LocalRepoService
        discovery_result = self.local_repo_service.discover_artifacts(user_id, repo_name)
        
        # Get tool file paths
        tool_files = discovery_result.get_files_by_type(ArtifactType.TOOL)
        
        logger.info(f"Discovered {len(tool_files)} tools in {repo_name} for user {user_id}")
        return tool_files
    
    def list_tools(self, repo_name: str, user_id: str) -> List[ToolSummary]:
        """List all tools in a repository.
        
        Args:
            repo_name: Name of the repository
            user_id: ID of the user
            
        Returns:
            List of tool summaries with file_path populated
        """
        # Use the new discovery method
        tool_files = self.discover_tools(repo_name, user_id)
        summaries = []
        
        # Get repo base path to construct file:// URIs
        repo_base_path = self._get_repo_base_path(user_id)
        repo_path = repo_base_path / repo_name
        
        for tool_file_path in tool_files:
            try:
                # Extract tool name from file path
                # File path format: .promptrepo/mock_tools/tool_name.tool.yaml
                tool_name = Path(tool_file_path).stem.replace(self.TOOL_FILE_SUFFIX.replace('.yaml', ''), '')
                
                # Load the tool
                tool = self.load_tool(tool_name, repo_name, user_id)
                
                # Construct file:// URI with relative path from repo root
                file_uri = f"file:///{tool_file_path}"
                
                # Create summary with file_path populated
                summary = ToolSummary(
                    name=tool.name,
                    description=tool.description,
                    mock_enabled=tool.mock.enabled,
                    parameter_count=len(tool.parameters.properties),
                    required_count=len(tool.parameters.required),
                    file_path=file_uri
                )
                summaries.append(summary)
                
            except Exception as e:
                logger.warning(f"Failed to load tool from {tool_file_path}: {e}")
                # Skip invalid tools in listing
                continue
        
        logger.info(f"Found {len(summaries)} tools in {repo_name}")
        return summaries
    
    async def save_tool(
        self,
        tool: ToolDefinition,
        repo_name: str,
        user_id: str,
        oauth_token: Optional[str] = None,
        author_name: Optional[str] = None,
        author_email: Optional[str] = None,
        user_session = None
    ) -> Tuple[ToolDefinition, Optional[PRInfo]]:
        """Save a tool definition with full git workflow (save, add, commit, push, PR).
        
        This method performs the complete workflow in one go:
        1. Validate the tool
        2. Save to YAML file
        3. Stage the file
        4. Commit changes
        5. Push to remote
        6. Create PR (if applicable)
        
        Args:
            tool: Tool definition to save
            repo_name: Name of the repository
            user_id: ID of the user
            oauth_token: Optional OAuth token for git operations
            author_name: Optional git commit author name
            author_email: Optional git commit author email
            user_session: Optional user session for PR creation
            
        Returns:
            Tuple[ToolDefinition, Optional[PRInfo]]: Saved tool and PR info if created
            
        Raises:
            ValidationException: If tool validation or save fails
        """
        # Validate the tool first
        self.validate_tool(tool)
        
        # Get the tool path
        tool_path = self._get_tool_path(tool.name, repo_name, user_id)
        
        # Ensure tools directory exists
        tools_dir = self._get_tools_dir(repo_name, user_id)
        tools_dir.mkdir(parents=True, exist_ok=True)
        
        try:
            # Create the tool data wrapper
            tool_data = ToolData(tool=tool)
            
            # Convert to dict and save as YAML
            # Use mode='json' to convert enums and other types to JSON-serializable values
            data_dict = tool_data.model_dump(mode='json', exclude_none=True, exclude_unset=True)
            
            # Save the file using the correct method
            success = self.file_operations_service.save_yaml_file(str(tool_path), data_dict)
            
            if not success:
                raise ValidationException(
                    f"Failed to save tool file to {tool_path}. Check file permissions and directory structure."
                )
            
            logger.info(f"Successfully saved tool: {tool.name} to {repo_name}")
            
        except ValidationException:
            raise
        except Exception as e:
            logger.error(f"Failed to save tool {tool.name}: {e}", exc_info=True)
            raise ValidationException(f"Failed to save tool: {str(e)}")
        
        # Get the relative file path for git operations
        file_path = f"{self.TOOLS_DIR}/{tool.name}{self.TOOL_FILE_SUFFIX}"
        
        # Handle git workflow (branch, commit, push, PR creation)
        pr_info = await self.local_repo_service.handle_git_workflow_after_save(
            user_id=user_id,
            repo_name=repo_name,
            file_path=file_path,
            artifact_type=ArtifactType.TOOL,
            oauth_token=oauth_token,
            author_name=author_name,
            author_email=author_email,
            user_session=user_session
        )
        
        logger.info(f"Completed git workflow for tool: {tool.name} in {repo_name}")
        return tool, pr_info
    
    def delete_tool(self, tool_name: str, repo_name: str, user_id: str) -> None:
        """Delete a tool YAML file.
        
        Args:
            tool_name: Name of the tool
            repo_name: Name of the repository
            user_id: ID of the user
            
        Raises:
            NotFoundException: If tool not found
        """
        tool_path = self._get_tool_path(tool_name, repo_name, user_id)
        
        if not tool_path.exists():
            logger.warning("Tool file not found for deletion: %s", tool_path)
            raise NotFoundException(resource="Tool", identifier=f"{repo_name}:{tool_name}")
        
        try:
            tool_path.unlink()
            logger.info(f"Successfully deleted tool: {tool_name} from {repo_name}")
        except Exception as e:
            logger.exception("Failed to delete tool %s", tool_name)
            raise ValidationException("Failed to delete tool") from e
    
    def validate_tool(self, tool: ToolDefinition) -> None:
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
    
    def get_mock_response(self, tool: ToolDefinition) -> Optional[str]:
        """Get the mock response for a tool.
        
        Args:
            tool: Tool definition
            
        Returns:
            Mock response string if mock is enabled, None otherwise
        """
        if not tool.mock.enabled:
            logger.debug(f"Mock is disabled for tool: {tool.name}")
            return None
        
        # Handle different mock types
        from services.tool.models import MockType
        
        if tool.mock.mock_type == MockType.STATIC:
            response = tool.mock.static_response
            logger.debug(f"Returning static mock response for tool: {tool.name}")
            return response
        elif tool.mock.mock_type == MockType.CONDITIONAL:
            # For conditional mocks, return a placeholder or None
            # Actual conditional logic should be handled elsewhere with parameters
            logger.warning(f"Conditional mock type not yet implemented for tool: {tool.name}")
            return None
        elif tool.mock.mock_type == MockType.PYTHON:
            # For Python mocks, return a placeholder or None
            # Actual Python execution should be handled elsewhere
            logger.warning(f"Python mock type not yet implemented for tool: {tool.name}")
            return None
        else:
            logger.warning(f"Unknown mock type for tool: {tool.name}")
            return None