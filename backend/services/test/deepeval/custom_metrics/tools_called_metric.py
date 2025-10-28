"""
Tools Called metric for DeepEval.

This deterministic metric verifies that the correct tools were called
during agent execution by comparing expected and actual tool calls.
"""

from typing import List, Dict, Any, Optional
from deepeval.metrics import BaseMetric
from deepeval.test_case import LLMTestCase


class ToolsCalledMetric(BaseMetric):
    """
    Deterministic metric that verifies correct tools were called during execution.
    
    This metric compares the list of tools that were expected to be called
    against the actual tools that were called, returning a score based on
    the correctness and completeness of tool usage.
    """
    
    def __init__(self):
        """Initialize ToolsCalledMetric."""
        self.score = 0.0
        self.reason = ""
        self.success = False
        self.error = None
    
    def measure(self, test_case: LLMTestCase) -> float:
        """
        Measure if correct tools were called during execution.
        
        Args:
            test_case: The test case containing tool execution information
            
        Returns:
            The similarity score (1.0 for perfect match, 0.0-1.0 for partial matches)
        """
        try:
            # Get expected and actual tools from test case
            # These would need to be stored in custom attributes or passed differently
            # For now, we'll assume they're available as attributes
            expected_tools = getattr(test_case, 'expected_tools', [])
            actual_tools = getattr(test_case, 'tools_called', [])
            
            if not expected_tools:
                self.error = "Expected tools list is required for tools called evaluation"
                raise ValueError(self.error)
            
            if not actual_tools:
                self.error = "Actual tools list is required for tools called evaluation"
                raise ValueError(self.error)
            
            # Convert to comparable format (tool names)
            expected_tool_names = {tool.get('name', str(tool)) for tool in expected_tools}
            actual_tool_names = {tool.get('name', str(tool)) for tool in actual_tools}
            
            # Calculate score based on matches
            if expected_tool_names == actual_tool_names:
                self.score = 1.0
                self.reason = "All expected tools were called correctly"
            else:
                # Calculate partial score based on overlap
                matches = len(expected_tool_names & actual_tool_names)
                total_expected = len(expected_tool_names)
                self.score = matches / total_expected if total_expected > 0 else 0.0
                
                missing_tools = expected_tool_names - actual_tool_names
                extra_tools = actual_tool_names - expected_tool_names
                
                reason_parts = []
                if missing_tools:
                    reason_parts.append(f"Missing tools: {missing_tools}")
                if extra_tools:
                    reason_parts.append(f"Extra tools: {extra_tools}")
                if matches > 0:
                    reason_parts.append(f"Correct tools: {expected_tool_names & actual_tool_names}")
                
                self.reason = f"Tool call mismatch. {'; '.join(reason_parts)}"
            
            # Success based on perfect match
            self.success = self.score == 1.0
            
            return self.score
            
        except Exception as e:
            self.error = f"Failed to measure tools called: {str(e)}"
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