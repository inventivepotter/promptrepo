"""Tool service models for managing mock tools based on simplified design."""

from enum import Enum
from typing import Any, Dict, List, Literal, Optional, Union
from pydantic import BaseModel, Field, field_validator


class ToolParameterType(str, Enum):
    """Parameter types for tool parameters."""
    STRING = "string"
    NUMBER = "number"
    BOOLEAN = "boolean"
    ARRAY = "array"
    OBJECT = "object"


class ParameterSchema(BaseModel):
    """Individual parameter property schema for OpenAI compatibility."""
    
    type: ToolParameterType = Field(
        description="Parameter type"
    )
    description: str = Field(description="Parameter description")
    enum: Optional[List[Any]] = Field(None, description="Allowed values")
    default: Optional[Any] = Field(None, description="Default value")
    
    @field_validator("default")
    @classmethod
    def validate_default_type(cls, v: Any, info) -> Any:
        """Validate that default value matches the parameter type."""
        if v is None:
            return v
            
        param_type = info.data.get("type")
        # Handle both enum and string values
        param_type_value = param_type.value if isinstance(param_type, ToolParameterType) else param_type
        
        if param_type_value == "string" and not isinstance(v, str):
            raise ValueError(f"Default value must be a string for type 'string', got {type(v)}")
        elif param_type_value == "number" and (not isinstance(v, (int, float)) or isinstance(v, bool)):
            raise ValueError(f"Default value must be a number for type 'number', got {type(v)}")
        elif param_type_value == "boolean" and not isinstance(v, bool):
            raise ValueError(f"Default value must be a boolean for type 'boolean', got {type(v)}")
        elif param_type_value == "array" and not isinstance(v, list):
            raise ValueError(f"Default value must be a list for type 'array', got {type(v)}")
        elif param_type_value == "object" and not isinstance(v, dict):
            raise ValueError(f"Default value must be a dict for type 'object', got {type(v)}")
        
        return v


class ParametersDefinition(BaseModel):
    """Parameters definition following OpenAI function schema."""
    
    type: Literal["object"] = Field(default="object", description="Always 'object' for OpenAI compatibility")
    properties: Dict[str, ParameterSchema] = Field(default_factory=dict, description="Parameter properties")
    required: List[str] = Field(default_factory=list, description="Required parameter names")
    
    @field_validator("required")
    @classmethod
    def validate_required(cls, v: List[str], info) -> List[str]:
        """Validate that required parameters exist in properties."""
        properties = info.data.get("properties", {})
        for param in v:
            if param not in properties:
                raise ValueError(f"Required parameter '{param}' not found in properties")
        return v


class ConditionalRule(BaseModel):
    """A single conditional rule for conditional mock."""
    
    conditions: Dict[str, Any] = Field(description="Parameter name-value pairs that must match")
    output: str = Field(description="Output to return when conditions match")


class MockType(str, Enum):
    """Types of mock responses."""
    STATIC = "static"
    CONDITIONAL = "conditional"
    PYTHON = "python"


class MockConfig(BaseModel):
    """Mock configuration for tool with support for multiple mock types."""
    
    enabled: bool = Field(default=True, description="Whether mock is enabled")
    mock_type: MockType = Field(default=MockType.STATIC, description="Type of mock response")
    
    # Legacy field for backward compatibility
    response: Optional[str] = Field(None, description="Mock response string (legacy/static)")
    
    # Type-specific fields
    static_response: Optional[str] = Field(None, description="Static mock response")
    conditional_rules: Optional[List[ConditionalRule]] = Field(None, description="Conditional mock rules")
    python_code: Optional[str] = Field(None, description="Python code for dynamic mock")
    
    @field_validator("mock_type", mode="before")
    @classmethod
    def validate_mock_type(cls, v: Any) -> MockType:
        """Validate and convert mock_type."""
        if v is None:
            return MockType.STATIC
        if isinstance(v, str):
            return MockType(v.lower())
        return v
    
    def model_post_init(self, __context: Any) -> None:
        """Post-initialization to handle backward compatibility."""
        # If response is set but static_response is not, migrate it
        if self.response and not self.static_response and self.mock_type == MockType.STATIC:
            self.static_response = self.response


class ToolDefinition(BaseModel):
    """Complete tool definition following simplified design."""
    
    name: str = Field(description="Tool name in function-name format")
    description: str = Field(description="Human-readable description")
    parameters: ParametersDefinition = Field(
        default_factory=lambda: ParametersDefinition(type="object", properties={}, required=[]),
        description="OpenAI-compatible parameters"
    )
    mock: MockConfig = Field(default_factory=lambda: MockConfig(), description="Mock configuration")
    
    @field_validator("name")
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Validate tool name format (function-name format)."""
        import re
        if not re.match(r"^[a-z][a-z0-9_]*$", v):
            raise ValueError(
                "Tool name must be in function-name format (lowercase, start with letter, "
                "contain only letters, numbers, and underscores)"
            )
        return v
    
    def to_openai_function(self) -> Dict[str, Any]:
        """Convert to OpenAI function format."""
        return {
            "name": self.name,
            "description": self.description,
            "parameters": self.parameters.model_dump(exclude_none=True)
        }


class ToolData(BaseModel):
    """Wrapper for tool YAML data."""
    
    tool: ToolDefinition = Field(description="Tool definition")


class ToolSummary(BaseModel):
    """Tool summary for listing.
    
    Note: file_path is populated during discovery and not stored in YAML files.
    """
    
    name: str = Field(description="Tool name")
    description: str = Field(description="Tool description")
    mock_enabled: bool = Field(description="Whether mock is enabled")
    parameter_count: int = Field(description="Number of parameters")
    required_count: int = Field(description="Number of required parameters")
    file_path: str = Field(description="Tool file path (populated during discovery, not stored in YAML)")