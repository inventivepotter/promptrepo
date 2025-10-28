"""
JSON Schema Verification metric for DeepEval.

This deterministic metric validates that the output conforms to
the expected JSON schema structure.
"""

import json
from typing import Dict, Any, Optional
from deepeval.metrics import BaseMetric
from deepeval.test_case import LLMTestCase


class JsonSchemaVerificationMetric(BaseMetric):
    """
    Deterministic metric that validates output against expected JSON schema.
    
    This metric checks if the actual output is valid JSON and conforms
    to the expected schema structure, returning 1.0 for valid
    outputs and 0.0 for invalid ones.
    """
    
    def __init__(self):
        """Initialize JsonSchemaVerificationMetric."""
        self.score = 0.0
        self.reason = ""
        self.success = False
        self.error = None
    
    def measure(self, test_case: LLMTestCase) -> float:
        """
        Measure if output conforms to expected JSON schema.
        
        Args:
            test_case: The test case containing expected schema and actual output
            
        Returns:
            The validation score (1.0 for valid, 0.0 for invalid)
        """
        try:
            # Get expected schema from test case
            expected_schema = getattr(test_case, 'expected_schema', None)
            
            if not expected_schema:
                self.error = "Expected schema is required for JSON schema verification"
                raise ValueError(self.error)
            
            if not test_case.actual_output:
                self.error = "Actual output is required for JSON schema verification"
                raise ValueError(self.error)
            
            # Try to parse actual output as JSON
            try:
                actual_json = json.loads(test_case.actual_output)
            except json.JSONDecodeError as e:
                self.score = 0.0
                self.reason = f"Output is not valid JSON: {str(e)}"
                self.success = False
                return self.score
            
            # Validate against schema (basic structure validation)
            is_valid = self._validate_json_structure(actual_json, expected_schema)
            
            if is_valid:
                self.score = 1.0
                self.reason = "Output conforms to expected JSON schema"
            else:
                self.score = 0.0
                self.reason = "Output does not conform to expected JSON schema"
            
            self.success = self.score == 1.0
            return self.score
            
        except Exception as e:
            self.error = f"Failed to measure JSON schema verification: {str(e)}"
            self.success = False
            raise
    
    def _validate_json_structure(self, actual: Dict[str, Any], expected: Dict[str, Any]) -> bool:
        """
        Basic JSON structure validation.
        
        Args:
            actual: The actual JSON object
            expected: The expected schema structure
            
        Returns:
            True if structure matches, False otherwise
        """
        # Check if all required keys are present
        if isinstance(expected, dict):
            for key, value in expected.items():
                if key not in actual:
                    return False
                # Recursively validate nested structures
                if isinstance(value, dict) and isinstance(actual.get(key), dict):
                    if not self._validate_json_structure(actual[key], value):
                        return False
                elif isinstance(value, type) and not isinstance(actual.get(key), value):
                    return False
        return True
        return False
    
    async def a_measure(self, test_case: LLMTestCase) -> float:
        """
        Asynchronous version of measure method.
        
        Args:
            test_case: The test case to evaluate
            
        Returns:
            The validation score
        """
        return self.measure(test_case)
    
    def is_successful(self) -> bool:
        """Check if metric passed threshold."""
        return self.success if self.success is not None else False