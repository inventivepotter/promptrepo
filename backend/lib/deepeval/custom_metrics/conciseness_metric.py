"""
Conciseness metric for DeepEval.

This metric evaluates whether an LLM's response is brief and to the point,
without unnecessary filler or extra information that wasn't requested.
"""

from typing import Optional
from deepeval.metrics import GEval
from deepeval.test_case import LLMTestCaseParams


class ConcisenessMetric(GEval):
    """
    Custom metric to evaluate the conciseness of LLM responses.
    
    This metric assesses:
    - Brevity and directness of the response
    - Absence of unnecessary filler content
    - Focus on answering only what was asked
    - Avoidance of unrequested additional information
    """
    
    def __init__(
        self,
        threshold: float = 0.7,
        model: str = "gpt-4",
        strict_mode: bool = False
    ):
        """
        Initialize the ConcisenessMetric.
        
        Args:
            threshold: Minimum score to pass the evaluation (0.0 to 1.0)
            model: LLM model to use for evaluation
            strict_mode: Enable strict evaluation mode
        """
        super().__init__(
            name="Conciseness",
            criteria="Assess whether the response is concise and focused only on the essential points. It should avoid repetition, irrelevant details, and unnecessary elaboration.",
            evaluation_params=[LLMTestCaseParams.INPUT, LLMTestCaseParams.ACTUAL_OUTPUT],
            threshold=threshold,
            model=model,
            strict_mode=strict_mode
        )
    
    @property
    def __name__(self):
        return "ConcisenessMetric"