"""
Keyword Pattern Presence metric for DeepEval.

This deterministic metric checks for the presence of required
keywords or patterns in the output text.
"""

import re
from typing import List, Optional
from deepeval.metrics import BaseMetric
from deepeval.test_case import LLMTestCase


class KeywordPatternPresenceMetric(BaseMetric):
    """
    Deterministic metric that checks for required keywords or patterns.
    
    This metric verifies that specified keywords and regex patterns
    are present in the actual output, returning a score based
    on the percentage of matches found.
    """
    
    def __init__(self):
        """Initialize KeywordPatternPresenceMetric."""
        self.score = 0.0
        self.reason = ""
        self.success = False
        self.error = None
    
    def measure(self, test_case: LLMTestCase) -> float:
        """
        Measure if required keywords/patterns are present in output.
        
        Args:
            test_case: The test case containing expected keywords/patterns and actual output
            
        Returns:
            The presence score (0.0 to 1.0 based on matches)
        """
        try:
            # Get expected keywords and patterns from test case
            expected_keywords = getattr(test_case, 'expected_keywords', [])
            expected_patterns = getattr(test_case, 'expected_patterns', [])
            
            if not expected_keywords and not expected_patterns:
                self.error = "Expected keywords or patterns are required for keyword pattern presence evaluation"
                raise ValueError(self.error)
            
            if not test_case.actual_output:
                self.error = "Actual output is required for keyword pattern presence evaluation"
                raise ValueError(self.error)
            
            total_requirements = len(expected_keywords) + len(expected_patterns)
            if total_requirements == 0:
                self.score = 1.0
                self.reason = "No keywords or patterns to check"
                self.success = True
                return self.score
            
            matches_found = 0
            
            # Check for keyword matches (case-insensitive)
            output_lower = test_case.actual_output.lower()
            for keyword in expected_keywords:
                if keyword.lower() in output_lower:
                    matches_found += 1
            
            # Check for regex pattern matches
            for pattern in expected_patterns:
                try:
                    if re.search(pattern, test_case.actual_output, re.IGNORECASE):
                        matches_found += 1
                except re.error:
                    # Invalid regex pattern, count as not found
                    continue
            
            # Calculate score based on percentage of matches
            self.score = matches_found / total_requirements
            
            # Set reason
            if matches_found == total_requirements:
                self.reason = f"All {total_requirements} keywords/patterns found in output"
            else:
                missing = total_requirements - matches_found
                self.reason = f"Missing {missing} of {total_requirements} keywords/patterns in output"
            
            # Success based on all requirements being met
            self.success = self.score == 1.0
            
            return self.score
            
        except Exception as e:
            self.error = f"Failed to measure keyword pattern presence: {str(e)}"
            self.success = False
            raise
    
    async def a_measure(self, test_case: LLMTestCase) -> float:
        """
        Asynchronous version of measure method.
        
        Args:
            test_case: The test case to evaluate
            
        Returns:
            The presence score
        """
        return self.measure(test_case)
    
    def is_successful(self) -> bool:
        """Check if metric passed threshold."""
        return self.success if self.success is not None else False