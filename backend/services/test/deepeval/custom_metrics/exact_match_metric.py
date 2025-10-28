"""
Exact Match metric for DeepEval.

This deterministic metric compares the actual output exactly against
the expected output to determine if they match precisely.
"""

from typing import Optional
from deepeval.metrics import BaseMetric
from deepeval.test_case import LLMTestCase


class ExactMatchMetric(BaseMetric):
    """
    Deterministic metric that checks if actual output exactly matches expected output.
    
    This metric performs a strict string comparison between the actual and expected
    outputs, returning a score of 1.0 for exact matches and 0.0 otherwise.
    """
    
    def __init__(
        self
    ):
        """
        Initialize the ExactMatchMetric.
        
        Args:
            threshold: Minimum score to pass the evaluation (typically 1.0 for exact match)
            strict_mode: Enable strict evaluation mode
        """
        self.score = 0.0
        self.reason = ""
        self.success = False
        self.error = None
    
    def measure(self, test_case: LLMTestCase) -> float:
        """
        Measure the exact match between actual and expected output.
        
        Args:
            test_case: The test case containing input, actual_output, and expected_output
            
        Returns:
            The similarity score (1.0 for exact match, 0.0 otherwise)
        """
        try:
            if not test_case.expected_output:
                self.error = "Expected output is required for exact match evaluation"
                raise ValueError(self.error)
            
            if not test_case.actual_output:
                self.error = "Actual output is required for exact match evaluation"
                raise ValueError(self.error)
            
            # Perform exact string comparison with None checks
            actual = test_case.actual_output.strip()
            expected = test_case.expected_output.strip()
            is_exact_match = actual == expected
            
            # Set score based on exact match
            self.score = 1.0 if is_exact_match else 0.0
            
            # Set reason
            if is_exact_match:
                self.reason = "Actual output exactly matches the expected output"
            else:
                self.reason = f"Actual output does not match expected output. Expected: '{test_case.expected_output}', Got: '{test_case.actual_output}'"
            
            # For exact match, success is based on whether there was an exact match
            self.success = self.score == 1.0
            
            return self.score
            
        except Exception as e:
            self.error = f"Failed to measure exact match: {str(e)}"
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
        """Check if the metric passed the threshold."""
        return self.success if self.success is not None else False