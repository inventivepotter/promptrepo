"""
Request and response models for the tools API endpoints.
"""
from typing import Optional, Dict, Any
from pydantic import BaseModel, Field

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