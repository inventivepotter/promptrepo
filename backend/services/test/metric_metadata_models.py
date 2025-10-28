"""
Pydantic models for metrics metadata API response.

These models define the structure of metadata returned by the metrics metadata endpoint.
"""

from typing import Dict, Any, List, TypeAlias
from pydantic import BaseModel, Field


class MetricMetadataModel(BaseModel):
    """
    Metadata for a single metric type.
    
    This model describes all information needed by the frontend to:
    - Display metric information to users
    - Dynamically generate configuration forms
    - Validate user input
    """
    
    type: str = Field(
        description="Metric type identifier (e.g., 'exact_match', 'professionalism')"
    )
    category: str = Field(
        description="Metric category: 'deterministic' or 'non_deterministic'"
    )
    description: str = Field(
        description="Human-readable description of what this metric evaluates"
    )
    required_expected_fields: List[str] = Field(
        description="List of field names the user must provide in test definition"
    )
    required_actual_fields: List[str] = Field(
        description="List of field names that must be present from test execution"
    )
    field_schema: Dict[str, Any] = Field(
        description="JSON schema for expected fields configuration (for dynamic form generation)"
    )
    
    class Config:
        json_schema_extra = {
            "example": {
                "type": "exact_match",
                "category": "deterministic",
                "description": "Compares the actual output exactly against the expected output",
                "required_expected_fields": ["expected_output"],
                "required_actual_fields": ["actual_output"],
                "field_schema": {
                    "type": "object",
                    "properties": {
                        "expected_output": {
                            "type": "string",
                            "description": "Expected output for exact comparison"
                        }
                    },
                    "required": ["expected_output"]
                }
            }
        }


# Type alias for metrics metadata response
# Dict mapping metric type to its metadata
MetricsMetadataResponse: TypeAlias = Dict[str, MetricMetadataModel]