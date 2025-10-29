import inspect
import types
from typing import Dict, Any, Optional, Callable, Type, Union, List, get_args, get_origin
from pydantic import BaseModel, Field, create_model, ValidationError


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


def create_return_model_from_schema(
    returns_schema: Optional[Dict[str, Any]],
    function_name: str
) -> Optional[Type[BaseModel]]:
    """
    Creates a Pydantic model dynamically from the 'returns' schema in the tool JSON.
    
    Args:
        returns_schema: The 'returns' field from the OpenAI tool JSON definition
        function_name: The name of the function (used for naming the model)
    
    Returns:
        A dynamically created Pydantic BaseModel class, or None if no returns schema is provided
        
    Raises:
        ToolDefinitionError: If the returns schema is invalid
    """
    if not returns_schema:
        return None
    
    if not isinstance(returns_schema, dict):
        raise ToolDefinitionError(
            f"Returns schema for function '{function_name}' must be a dictionary"
        )
    
    schema_type = returns_schema.get("type")
    if schema_type != "object":
        # For non-object return types, we don't create a model
        return None
    
    properties = returns_schema.get("properties", {})
    if not properties:
        return None
    
    required_fields = returns_schema.get("required", [])
    model_name = f"{function_name.title().replace('_', '')}Response"
    
    return create_pydantic_model_from_schema(properties, required_fields, model_name)


def validate_tool_json(tool_json: Dict[str, Any]) -> None:
    """
    Validates the structure of the tool JSON definition.
    
    Args:
        tool_json: The OpenAI tool definition
        
    Raises:
        ToolDefinitionError: If the tool JSON is invalid
    """
    if not isinstance(tool_json, dict):
        raise ToolDefinitionError("Tool JSON must be a dictionary")
    
    if tool_json.get("type") != "function":
        raise ToolDefinitionError(f"Tool type must be 'function', got '{tool_json.get('type')}'")
    
    func_info = tool_json.get("function")
    if not func_info:
        raise ToolDefinitionError("Missing 'function' field in tool JSON")
    
    if not isinstance(func_info, dict):
        raise ToolDefinitionError("'function' field must be a dictionary")
    
    # Validate required fields
    if not func_info.get("name"):
        raise ToolDefinitionError("Missing 'name' in function definition")
    
    if not isinstance(func_info["name"], str):
        raise ToolDefinitionError("Function 'name' must be a string")
    
    if not func_info.get("description"):
        raise ToolDefinitionError("Missing 'description' in function definition")
    
    parameters = func_info.get("parameters")
    if not parameters:
        raise ToolDefinitionError("Missing 'parameters' in function definition")
    
    if not isinstance(parameters, dict):
        raise ToolDefinitionError("'parameters' field must be a dictionary")
    
    if parameters.get("type") != "object":
        raise ToolDefinitionError("Parameters type must be 'object'")
    
    if "properties" not in parameters:
        raise ToolDefinitionError("Missing 'properties' in parameters definition")


def create_dynamic_tool_function(
    tool_json: Dict[str, Any],
    function_logic: Callable[..., Any]
) -> Callable[..., Any]:
    """
    Creates a callable function dynamically from an OpenAI tool JSON definition.

    Args:
        tool_json: The OpenAI tool definition
        function_logic: The actual Python function that contains the logic to be executed

    Returns:
        The dynamically created function with proper signature and return type

    Raises:
        ToolDefinitionError: If the tool JSON is invalid
        ToolExecutionError: If there's an error creating the function
    """
    # Validate the tool JSON structure
    validate_tool_json(tool_json)
    
    try:
        # Extract function metadata
        func_info = tool_json["function"]
        name = func_info["name"]
        docstring = func_info["description"]
        parameters = func_info["parameters"]["properties"]
        required_params = func_info["parameters"].get("required", [])
        
        # Extract return type if available
        returns_schema = func_info.get("returns")
        return_model = create_return_model_from_schema(returns_schema, name)

        # Create parameter list for function signature
        param_list = []
        for param_name, param_details in parameters.items():
            try:
                param_type = get_python_type_from_json_schema(param_details, param_name)
                
                if param_name in required_params:
                    # Required parameter
                    param = inspect.Parameter(
                        param_name,
                        inspect.Parameter.POSITIONAL_OR_KEYWORD,
                        annotation=param_type
                    )
                else:
                    # Optional parameter
                    default_value = param_details.get("default")
                    param = inspect.Parameter(
                        param_name,
                        inspect.Parameter.POSITIONAL_OR_KEYWORD,
                        default=default_value,
                        annotation=Optional[param_type]  # type: ignore
                    )
                param_list.append(param)
            except Exception as e:
                raise ToolDefinitionError(
                    f"Error creating parameter '{param_name}' for function '{name}': {str(e)}"
                ) from e

        # Create function signature with return annotation
        return_annotation = return_model if return_model else Any
        signature = inspect.Signature(param_list, return_annotation=return_annotation)

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
        dynamic_func.__doc__ = docstring
        dynamic_func.__tool_json__ = tool_json  # type: ignore
        
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


# --- Demo with tool JSON ---

if __name__ == "__main__":
    openai_tool_json = {
        "type": "function",
        "function": {
            "name": "get_current_weather",
            "description": "Get the current weather in a given location. The `unit` parameter is optional.",
            "parameters": {
                "type": "object",
                "properties": {
                    "location": {
                        "type": "string",
                        "description": "The city and state, e.g. San Francisco, CA",
                        "examples": ["San Francisco, CA", "New York, NY", "London, UK"]
                    },
                    "unit": {
                        "type": "string",
                        "enum": ["celsius", "fahrenheit"],
                        "description": "The temperature unit to use for the weather result",
                        "default": "fahrenheit"
                    },
                },
                "required": ["location"],
                "additionalProperties": False
            },
            "returns": {
                "type": "object",
                "properties": {
                    "location": {"type": "string", "description": "The requested location"},
                    "temperature": {"type": "number", "description": "The current temperature"},
                    "unit": {"type": "string", "description": "The temperature unit"},
                    "description": {"type": "string", "description": "Weather description"},
                    "humidity": {"type": "number", "description": "Humidity percentage"}
                },
                "required": ["location", "temperature", "unit"]
            }
        }
    }

    # Generic mock function
    def generic_mock_function(function_name: str, **kwargs: Any) -> Any:
        """Generic mock function that returns mock data."""
        return f"Mock response for {function_name} with parameters: {kwargs}"

    # Create the callable function dynamically
    get_current_weather_callable = create_dynamic_tool_function(
        openai_tool_json,
        lambda **kwargs: generic_mock_function(openai_tool_json["function"]["name"], **kwargs)
    )

    # Test the generated function
    print(f"Function name: {get_current_weather_callable.__name__}")
    print(f"Docstring: {get_current_weather_callable.__doc__}")
    print(f"Signature: {inspect.signature(get_current_weather_callable)}")
    print(f"Return model: {getattr(get_current_weather_callable, '__return_model__', None)}")
    print()

    # Call the dynamic function
    result1 = get_current_weather_callable(location="San Francisco, CA")
    print(f"Result 1: {result1}")
    print()

    # Call with optional parameter
    result2 = get_current_weather_callable(location="London, UK", unit="celsius")
    print(f"Result 2: {result2}")
    print()

    # Test error handling
    try:
        get_current_weather_callable()
    except TypeError as e:
        print(f"Caught expected error: {e}")