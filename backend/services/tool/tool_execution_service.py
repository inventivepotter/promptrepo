"""
Tool execution service for creating and managing callable tool functions.
"""
import json
import logging
from typing import Any, Callable, Dict, List, Optional

from services.tool.models import ContentType, MockType, ToolDefinition
from services.tool.tool import create_callable_from_tool_definition
from services.tool.tool_meta_service import ToolMetaService

logger = logging.getLogger(__name__)


class ToolExecutionService:
    """Service for creating callable tool functions with execution logic."""
    
    def __init__(self, tool_meta_service: ToolMetaService):
        """
        Initialize tool execution service.
        
        Args:
            tool_meta_service: Service for loading tool metadata
        """
        self.tool_meta_service = tool_meta_service
    
    def _create_mock_execution_logic(self, tool: ToolDefinition) -> Callable[..., Any]:
        """
        Create the execution logic for a tool based on its mock configuration.
        
        Args:
            tool: Tool definition with mock configuration
            
        Returns:
            A callable that executes the mock logic
        """
        def mock_logic(**kwargs: Any) -> Any:
            """Execute the mock logic based on tool configuration."""
            if not tool.mock.enabled:
                return self._format_response(
                    {"error": "Mock is disabled for this tool"},
                    ContentType.JSON
                )
            
            if tool.mock.mock_type == MockType.STATIC:
                response = tool.mock.static_response or ""
                return self._format_response(response, tool.mock.content_type)
            
            elif tool.mock.mock_type == MockType.CONDITIONAL:
                # Evaluate conditional rules
                if tool.mock.conditional_rules:
                    for rule in tool.mock.conditional_rules:
                        if self._evaluate_conditions(rule.conditions, kwargs):
                            return self._format_response(rule.output, tool.mock.content_type)
                
                # No matching rule found
                logger.warning(
                    f"No matching conditional rule for tool: {tool.name} with params: {kwargs}"
                )
                return self._format_response(
                    {"error": "No matching conditional rule"},
                    ContentType.JSON
                )
            
            elif tool.mock.mock_type == MockType.PYTHON:
                # TODO: Implement Python code execution with sandboxing
                logger.warning(f"Python mock type not yet implemented for tool: {tool.name}")
                return self._format_response(
                    {"error": "Python mocks not implemented"},
                    ContentType.JSON
                )
            
            return self._format_response({"error": "Unknown mock type"}, ContentType.JSON)
        
        return mock_logic
    
    def _evaluate_conditions(self, conditions: Dict[str, Any], params: Dict[str, Any]) -> bool:
        """
        Evaluate if the provided parameters match the conditions.
        
        Args:
            conditions: Dictionary of parameter name -> expected value
            params: Dictionary of parameter name -> actual value
            
        Returns:
            True if all conditions match, False otherwise
        """
        for param_name, expected_value in conditions.items():
            actual_value = params.get(param_name)
            
            # Handle None values
            if expected_value is None:
                if actual_value is not None:
                    return False
            elif actual_value != expected_value:
                return False
        
        return True
    
    def _format_response(self, response: Any, content_type: ContentType) -> Any:
        """
        Format the response based on the content type.
        
        Args:
            response: The response to format
            content_type: The desired content type
            
        Returns:
            Formatted response
        """
        if content_type == ContentType.JSON:
            # Ensure it's valid JSON
            if isinstance(response, str):
                try:
                    parsed = json.loads(response)
                    return json.dumps(parsed)
                except json.JSONDecodeError:
                    # Wrap in JSON if not valid
                    return json.dumps({"result": response})
            else:
                # Already a dict or other JSON-serializable type
                return json.dumps(response)
        
        else:  # ContentType.STRING or ContentType.XML
            # Return as-is for string/XML
            if isinstance(response, dict):
                # If dict was provided but string expected, convert to JSON string
                return json.dumps(response)
            return str(response)
    
    def create_callable_tools(
        self,
        tool_paths: List[str],
        repo_name: str,
        user_id: str
    ) -> List[Callable[..., Any]]:
        """
        Create callable functions from tool file paths.
        
        Args:
            tool_paths: List of tool file paths.
                       Format: 'file:///.promptrepo/mock_tools/tool_name.tool.yaml'
            repo_name: Name of the repository
            user_id: ID of the user
            
        Returns:
            List of callable functions
        """
        callable_tools = []
        
        # Extract tool names from file paths
        tools_to_load = []
        for tool_path in tool_paths:
            try:
                # file:///.promptrepo/mock_tools/temp_tool.tool.yaml -> temp_tool
                tool_name = tool_path.split('/')[-1].replace('.tool.yaml', '').replace('.tool.yml', '')
                tools_to_load.append(tool_name)
            except Exception as e:
                logger.warning(f"Failed to extract tool name from path {tool_path}: {e}")
                continue
        
        # Create callable functions for each tool
        for tool_name in tools_to_load:
            try:
                # Load the tool definition
                tool_def = self.tool_meta_service.load_tool(tool_name, repo_name, user_id)
                
                # Create the mock execution logic
                mock_logic = self._create_mock_execution_logic(tool_def)
                
                # Create the callable function
                callable_func = create_callable_from_tool_definition(tool_def, mock_logic)
                
                callable_tools.append(callable_func)
                
                logger.info(f"Created callable function for tool: {tool_name}")
                
            except Exception as e:
                logger.warning(f"Failed to create callable for tool {tool_name}: {e}")
                continue
        
        return callable_tools