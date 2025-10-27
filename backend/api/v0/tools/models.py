"""
Request and response models for the tools API endpoints.
"""
from typing import Optional, Dict, Any, List
from pydantic import BaseModel, Field

from services.tool.models import (
    ParametersDefinition,
    MockConfig,
    ToolDefinition
)
from services.local_repo.models import PRInfo


class CreateToolRequest(BaseModel):
    """Request model for creating/updating a tool."""
    
    name: str = Field(description="Tool name in function-name format")
    description: str = Field(description="Human-readable description")
    parameters: ParametersDefinition = Field(
        default_factory=lambda: ParametersDefinition(type="object", properties={}, required=[]),
        description="OpenAI-compatible parameters"
    )
    mock: MockConfig = Field(description="Mock configuration")
    repo_name: Optional[str] = Field("default", description="Repository name")


class MockExecutionRequest(BaseModel):
    """Request model for executing mock response with parameters."""
    
    parameters: Dict[str, Any] = Field(
        default_factory=dict,
        description="Parameters to pass to the mock execution"
    )


class MockExecutionResponse(BaseModel):
    """Response model for mock execution."""
    
    response: str = Field(description="Mock response string")
    tool_name: str = Field(description="Name of the tool executed")
    parameters_used: Dict[str, Any] = Field(
        default_factory=dict,
        description="Parameters that were used in execution"
    )


class ToolSaveResponse(BaseModel):
    """Response model for tool save operation with git workflow."""
    
    tool: ToolDefinition = Field(description="The saved tool definition")
    pr_info: Optional[Dict[str, Any]] = Field(None, description="Pull request information if PR was created")