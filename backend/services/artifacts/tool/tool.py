import inspect
import types
from typing import Any, Callable, Dict, List, Optional, Type, TYPE_CHECKING
from pydantic import BaseModel, Field, create_model

if TYPE_CHECKING:
    from services.artifacts.tool.models import ToolDefinition, ParameterSchema, ReturnsSchema


class ToolDefinitionError(Exception):
    """Raised when there's an error in the tool definition."""
    pass


class ToolExecutionError(Exception):
    """Raised when there's an error executing a tool function."""
    pass


def get_python_type_from_json_schema(
    schema: Dict[str, Any],
    field_name: str = ""
) -> Type:
    """
    Convert JSON schema to Python type with support for nested types.
    
    Args:
        schema: The JSON schema definition for a field
        field_name: The name of the field (for error messages)
    
    Returns:
        The corresponding Python type
        
    Raises:
        ToolDefinitionError: If the schema type is invalid or unsupported
    """
    if not isinstance(schema, dict):
        raise ToolDefinitionError(
            f"Schema for field '{field_name}' must be a dictionary, got {type(schema).__name__}"
        )
    
    json_type = schema.get("type")
    if not json_type:
        raise ToolDefinitionError(f"Missing 'type' in schema for field '{field_name}'")
    
    # Base type mapping
    type_mapping = {
        "string": str,
        "integer": int,
        "number": float,
        "boolean": bool,
    }
    
    # Handle simple types
    if json_type in type_mapping:
        return type_mapping[json_type]
    
    # Handle array types
    if json_type == "array":
        items_schema = schema.get("items")
        if items_schema:
            item_type = get_python_type_from_json_schema(items_schema, f"{field_name}[]")
            return List[item_type]  # type: ignore
        return list
    
    # Handle object types
    if json_type == "object":
        properties = schema.get("properties")
        if properties:
            # Create a nested Pydantic model for complex objects
            return create_pydantic_model_from_schema(
                properties,
                schema.get("required", []),
                f"{field_name.title().replace('_', '')}Type"
            )
        return dict
    
    # Fallback to string for unknown types
    return str


def create_pydantic_model_from_schema(
    properties: Dict[str, Dict[str, Any]],
    required_fields: List[str],
    model_name: str
) -> Type[BaseModel]:
    """
    Creates a Pydantic model from a schema's properties.
    
    Args:
        properties: The properties dictionary from the schema
        required_fields: List of required field names
        model_name: Name for the generated model
        
    Returns:
        A dynamically created Pydantic BaseModel class
        
    Raises:
        ToolDefinitionError: If the schema is invalid
    """
    if not properties:
        raise ToolDefinitionError(f"Cannot create model '{model_name}' with no properties")
    
    field_definitions: Dict[str, Any] = {}
    
    for field_name, field_schema in properties.items():
        try:
            field_type = get_python_type_from_json_schema(field_schema, field_name)
            field_description = field_schema.get("description", "")
            field_default = field_schema.get("default")
            
            # Determine if field is required
            is_required = field_name in required_fields
            
            if is_required and field_default is None:
                # Required field without default
                field_definitions[field_name] = (
                    field_type,
                    Field(description=field_description)
                )
            else:
                # Optional field or has default
                default_value = field_default if field_default is not None else None
                field_definitions[field_name] = (
                    Optional[field_type],  # type: ignore
                    Field(default=default_value, description=field_description)
                )
        except Exception as e:
            raise ToolDefinitionError(
                f"Error processing field '{field_name}' in model '{model_name}': {str(e)}"
            ) from e
    
    try:
        return create_model(model_name, **field_definitions)
    except Exception as e:
        raise ToolDefinitionError(
            f"Error creating Pydantic model '{model_name}': {str(e)}"
        ) from e


def get_python_type_from_parameter_schema(param_schema: 'ParameterSchema', field_name: str = "") -> Type:
    """
    Convert ParameterSchema to Python type.
    
    Args:
        param_schema: The ParameterSchema from ToolDefinition
        field_name: The name of the field (for error messages)
    
    Returns:
        The corresponding Python type
    """
    type_mapping = {
        "string": str,
        "integer": int,
        "number": float,
        "boolean": bool,
        "array": list,
        "object": dict,
    }
    
    param_type = param_schema.type.value if hasattr(param_schema.type, 'value') else param_schema.type
    return type_mapping.get(param_type, str)


def create_return_model_from_returns_schema(
    returns_schema: Optional['ReturnsSchema'],
    function_name: str
) -> Optional[Type[BaseModel]]:
    """
    Creates a Pydantic model from ReturnsSchema.
    
    Args:
        returns_schema: The ReturnsSchema from ToolDefinition
        function_name: The name of the function (used for naming the model)
    
    Returns:
        A dynamically created Pydantic BaseModel class, or None if no returns schema is provided
    """
    if not returns_schema:
        return None
    
    schema_type = returns_schema.type.value if hasattr(returns_schema.type, 'value') else returns_schema.type
    if schema_type != "object":
        return None
    
    if not returns_schema.properties:
        return None
    
    # Convert ParameterSchema properties to dict format for create_pydantic_model_from_schema
    properties_dict = {}
    for prop_name, prop_schema in returns_schema.properties.items():
        properties_dict[prop_name] = {
            "type": prop_schema.type.value if hasattr(prop_schema.type, 'value') else prop_schema.type,
            "description": prop_schema.description or "",
            "default": prop_schema.default,
            "enum": prop_schema.enum
        }
    
    required_fields = returns_schema.required or []
    model_name = f"{function_name.title().replace('_', '')}Response"
    
    return create_pydantic_model_from_schema(properties_dict, required_fields, model_name)


def validate_tool_definition(tool_def: 'ToolDefinition') -> None:
    """
    Validates a ToolDefinition.
    
    Args:
        tool_def: The ToolDefinition to validate
        
    Raises:
        ToolDefinitionError: If the tool definition is invalid
    """
    if not tool_def.name:
        raise ToolDefinitionError("Tool name is required")
    
    if not tool_def.description:
        raise ToolDefinitionError("Tool description is required")
    
    # Validate that all required parameters exist in properties
    for param_name in tool_def.parameters.required:
        if param_name not in tool_def.parameters.properties:
            raise ToolDefinitionError(
                f"Required parameter '{param_name}' not found in parameter properties"
            )
    
    # Validate returns schema if present
    if tool_def.returns:
        schema_type = tool_def.returns.type.value if hasattr(tool_def.returns.type, 'value') else tool_def.returns.type
        if schema_type == "object":
            if tool_def.returns.properties:
                # Validate that all required return properties exist
                for required_prop in (tool_def.returns.required or []):
                    if required_prop not in tool_def.returns.properties:
                        raise ToolDefinitionError(
                            f"Required return property '{required_prop}' not found in return properties"
                        )


def create_callable_from_tool_definition(
    tool_def: 'ToolDefinition',
    function_logic: Callable[..., Any]
) -> Callable[..., Any]:
    """
    Creates a callable function directly from a ToolDefinition model.
    
    Args:
        tool_def: The ToolDefinition model from YAML
        function_logic: The actual Python function that contains the logic to be executed
    
    Returns:
        The dynamically created function with proper signature and return type
    
    Raises:
        ToolDefinitionError: If the tool definition is invalid
        ToolExecutionError: If there's an error creating the function
    """
    # Validate the tool definition
    validate_tool_definition(tool_def)
    
    try:
        name = tool_def.name
        docstring = tool_def.description
        
        # Extract return type if available
        return_model = create_return_model_from_returns_schema(tool_def.returns, name)
        
        # Create parameter list for function signature and annotations dict
        param_list = []
        annotations = {}
        
        for param_name, param_schema in tool_def.parameters.properties.items():
            try:
                param_type = get_python_type_from_parameter_schema(param_schema, param_name)
                
                if param_name in tool_def.parameters.required:
                    # Required parameter
                    param = inspect.Parameter(
                        param_name,
                        inspect.Parameter.POSITIONAL_OR_KEYWORD,
                        annotation=param_type
                    )
                    annotations[param_name] = param_type
                else:
                    # Optional parameter
                    default_value = param_schema.default
                    param = inspect.Parameter(
                        param_name,
                        inspect.Parameter.POSITIONAL_OR_KEYWORD,
                        default=default_value,
                        annotation=Optional[param_type]  # type: ignore
                    )
                    annotations[param_name] = Optional[param_type]  # type: ignore
                param_list.append(param)
            except Exception as e:
                raise ToolDefinitionError(
                    f"Error creating parameter '{param_name}' for function '{name}': {str(e)}"
                ) from e
        
        # Create function signature with return annotation
        return_annotation = return_model if return_model else Any
        signature = inspect.Signature(param_list, return_annotation=return_annotation)
        annotations['return'] = return_annotation
        
        # Define wrapper function that calls the actual logic
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            try:
                return function_logic(*args, **kwargs)
            except Exception as e:
                raise ToolExecutionError(
                    f"Error executing function '{name}': {str(e)}"
                ) from e
        
        # Create the dynamic function
        dynamic_func = types.FunctionType(
            wrapper.__code__,
            wrapper.__globals__,
            name=name,
            argdefs=wrapper.__defaults__,
            closure=wrapper.__closure__
        )
        
        # Attach metadata to the function
        dynamic_func.__signature__ = signature  # type: ignore
        dynamic_func.__annotations__ = annotations  # CRITICAL: Add annotations dict for type hints
        dynamic_func.__doc__ = docstring
        dynamic_func.__tool_definition__ = tool_def  # type: ignore
        
        # Store the return model for runtime validation if needed
        if return_model:
            dynamic_func.__return_model__ = return_model  # type: ignore
        
        return dynamic_func
        
    except ToolDefinitionError:
        raise
    except Exception as e:
        raise ToolExecutionError(
            f"Unexpected error creating dynamic function: {str(e)}"
        ) from e