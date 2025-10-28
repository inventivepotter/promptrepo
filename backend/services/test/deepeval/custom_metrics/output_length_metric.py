"""
Output Length metric for DeepEval.

This deterministic metric validates that output length is within
specified minimum and maximum bounds.
"""

from deepeval.metrics import BaseMetric
from deepeval.test_case import LLMTestCase


class OutputLengthMetric(BaseMetric):
    """
    Deterministic metric that validates output length constraints.
    
    This metric checks if the actual output length is within
    specified minimum and maximum bounds, returning 1.0
    for valid lengths and 0.0 for invalid ones.
    """
    
    def __init__(self):
        """Initialize OutputLengthMetric."""
        self.score = 0.0
        self.reason = ""
        self.success = False
        self.error = None
    
    def measure(self, test_case: LLMTestCase) -> float:
        """
        Measure if output length is within specified bounds.
        
        Args:
            test_case: The test case containing length constraints and actual output
            
        Returns:
            The validation score (1.0 for valid length, 0.0 for invalid)
        """
        try:
            # Get length constraints from test case
            min_length = getattr(test_case, 'min_length', None)
            max_length = getattr(test_case, 'max_length', None)
            length_unit = getattr(test_case, 'length_unit', 'characters')
            
            if min_length is None and max_length is None:
                self.error = "At least one of min_length or max_length is required for output length evaluation"
                raise ValueError(self.error)
            
            if not test_case.actual_output:
                self.error = "Actual output is required for output length evaluation"
                raise ValueError(self.error)
            
            # Calculate actual length based on unit
            if length_unit == 'words':
                actual_length = len(test_case.actual_output.split())
            else:  # Default to characters
                actual_length = len(test_case.actual_output)
            
            # Check length constraints
            min_violation = min_length is not None and actual_length < min_length
            max_violation = max_length is not None and actual_length > max_length
            
            if not min_violation and not max_violation:
                self.score = 1.0
                self.reason = f"Output length ({actual_length} {length_unit}) is within bounds"
            else:
                self.score = 0.0
                violations = []
                if min_violation:
                    violations.append(f"below minimum of {min_length} {length_unit}")
                if max_violation:
                    violations.append(f"above maximum of {max_length} {length_unit}")
                self.reason = f"Output length ({actual_length} {length_unit}) is {' and '.join(violations)}"
            
            self.success = self.score == 1.0
            return self.score
            
        except Exception as e:
            self.error = f"Failed to measure output length: {str(e)}"
            self.success = False
            raise
    
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