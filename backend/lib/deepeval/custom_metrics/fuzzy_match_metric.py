"""
Fuzzy Match metric for DeepEval.

This deterministic metric uses fuzzy string matching to compare
actual output against expected output with some tolerance for
minor differences like whitespace, punctuation, or case variations.
"""

import json
from difflib import SequenceMatcher
from typing import Optional
from deepeval.metrics import BaseMetric
from deepeval.test_case import LLMTestCase


class FuzzyMatchMetric(BaseMetric):
    """
    Deterministic metric that performs fuzzy string matching.
    
    This metric uses sequence matching to calculate similarity
    between actual and expected outputs, allowing for minor
    differences while still measuring overall similarity.
    """
    
    def __init__(self, threshold: float = 0.8, json_field: Optional[str] = None):
        """
        Initialize FuzzyMatchMetric.
        
        Args:
            threshold: Minimum similarity ratio to pass evaluation (0.0 to 1.0)
            json_field: Optional JSON field path to extract text from for fuzzy matching.
                       Supports nested paths with dot notation (e.g., "data.result.text")
        """
        self.threshold = threshold
        self.json_field = json_field
        self.score = 0.0
        self.reason = ""
        self.success = False
        self.error = None
    
    def measure(self, test_case: LLMTestCase) -> float:
        """
        Measure fuzzy similarity between actual and expected output.
        
        Args:
            test_case: The test case containing input, actual_output, and expected_output
            
        Returns:
            The similarity score (0.0 to 1.0 based on sequence matching)
        """
        try:
            if not test_case.expected_output:
                self.error = "Expected output is required for fuzzy match evaluation"
                raise ValueError(self.error)
            
            if not test_case.actual_output:
                self.error = "Actual output is required for fuzzy match evaluation"
                raise ValueError(self.error)
            
            # Extract text from JSON field if specified
            expected_text = self._extract_text_from_output(test_case.expected_output)
            actual_text = self._extract_text_from_output(test_case.actual_output)
            
            # Normalize both strings (remove extra whitespace, normalize case)
            expected_normalized = ' '.join(expected_text.strip().split())
            actual_normalized = ' '.join(actual_text.strip().split())
            
            # Use SequenceMatcher for fuzzy matching
            matcher = SequenceMatcher(None, expected_normalized, actual_normalized)
            similarity_ratio = matcher.ratio()
            
            # Set score
            self.score = similarity_ratio
            
            # Set reason based on similarity level
            if similarity_ratio >= 0.95:
                self.reason = f"Very high similarity ({similarity_ratio:.2f}) - outputs are essentially identical"
            elif similarity_ratio >= 0.8:
                self.reason = f"High similarity ({similarity_ratio:.2f}) - outputs are very similar with minor differences"
            elif similarity_ratio >= 0.6:
                self.reason = f"Moderate similarity ({similarity_ratio:.2f}) - outputs have some similarities but notable differences"
            else:
                self.reason = f"Low similarity ({similarity_ratio:.2f}) - outputs are significantly different"
            
            # Success based on configured threshold
            self.success = self.score >= self.threshold
            
            return self.score
            
        except Exception as e:
            self.error = f"Failed to measure fuzzy match: {str(e)}"
            self.success = False
            raise
    
    async def a_measure(self, test_case: LLMTestCase) -> float:
        """
        Asynchronous version of measure method.
        
        Args:
            test_case: The test case to evaluate
            
        Returns:
            The similarity score
        """
        return self.measure(test_case)
    
    def is_successful(self) -> bool:
        """Check if metric passed threshold."""
        return self.success if self.success is not None else False
    
    def _extract_text_from_output(self, output: str) -> str:
        """
        Extract text from output, optionally from a specific JSON field.
        
        Args:
            output: The output string to process
            
        Returns:
            The extracted text for comparison
        """
        if not self.json_field:
            # If no json_field specified, use the entire output
            return output
        
        try:
            # Try to parse as JSON
            parsed_json = json.loads(output)
            
            # Extract nested field using dot notation
            field_parts = self.json_field.split('.')
            current_value = parsed_json
            
            for part in field_parts:
                if isinstance(current_value, dict) and part in current_value:
                    current_value = current_value[part]
                else:
                    self.error = f"Field '{self.json_field}' not found in JSON output"
                    raise ValueError(self.error)
            
            # Convert extracted value to string if it isn't already
            if isinstance(current_value, str):
                return current_value
            else:
                return json.dumps(current_value)
                
        except json.JSONDecodeError:
            self.error = f"Output is not valid JSON, but json_field '{self.json_field}' was specified"
            raise ValueError(self.error)
        except (KeyError, TypeError) as e:
            self.error = f"Failed to extract field '{self.json_field}' from JSON: {str(e)}"
            raise ValueError(self.error)