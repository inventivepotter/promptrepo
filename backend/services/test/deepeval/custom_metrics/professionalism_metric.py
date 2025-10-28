"""
Professionalism metric for DeepEval.

This metric evaluates whether a response maintains a formal and professional
tone appropriate for the context, avoiding casual or ambiguous expressions.
"""

from typing import Optional
from deepeval.metrics import GEval
from deepeval.test_case import LLMTestCaseParams


class ProfessionalismMetric(GEval):
    """
    Custom metric to evaluate the professionalism of LLM responses.
    
    This metric assesses:
    - Professional tone throughout the response
    - Domain-appropriate formality and expertise
    - Contextual appropriateness without casual expressions
    - Clear, respectful language avoiding slang
    """
    
    def __init__(
        self,
        threshold: float = 0.7,
        model: str = "gpt-4",
        strict_mode: bool = False
    ):
        """
        Initialize the ProfessionalismMetric.
        
        Args:
            threshold: Minimum score to pass the evaluation (0.0 to 1.0)
            model: LLM model to use for evaluation
            strict_mode: Enable strict evaluation mode
        """
        super().__init__(
            name="Professionalism",
            evaluation_steps=[
                "Determine whether the actual output maintains a professional tone throughout.",
                "Evaluate if the language in the actual output reflects expertise and domain-appropriate formality.",
                "Ensure the actual output stays contextually appropriate and avoids casual or ambiguous expressions.",
                "Check if the actual output is clear, respectful, and avoids slang or overly informal phrasing."
            ],
            evaluation_params=[LLMTestCaseParams.ACTUAL_OUTPUT],
            threshold=threshold,
            model=model,
            strict_mode=strict_mode
        )
    
    @property
    def __name__(self):
        return "ProfessionalismMetric"