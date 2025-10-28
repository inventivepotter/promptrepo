"""
Semantic Similarity metric for DeepEval.

This deterministic metric evaluates semantic similarity between
actual and expected output using word overlap and
conceptual matching rather than exact string matching.
"""

import re
from typing import Set, Optional
from deepeval.metrics import BaseMetric
from deepeval.test_case import LLMTestCase


class SemanticSimilarityMetric(BaseMetric):
    """
    Deterministic metric that evaluates semantic similarity.
    
    This metric analyzes the semantic content by comparing word
    frequency, important terms, and conceptual overlap between
    actual and expected outputs.
    """
    
    def __init__(self, threshold: float = 0.7):
        """
        Initialize SemanticSimilarityMetric.
        
        Args:
            threshold: Minimum semantic similarity score to pass evaluation (0.0 to 1.0)
        """
        self.threshold = threshold
        self.score = 0.0
        self.reason = ""
        self.success = False
        self.error = None
    
    def measure(self, test_case: LLMTestCase) -> float:
        """
        Measure semantic similarity between actual and expected output.
        
        Args:
            test_case: The test case containing input, actual_output, and expected_output
            
        Returns:
            The semantic similarity score (0.0 to 1.0)
        """
        try:
            if not test_case.expected_output:
                self.error = "Expected output is required for semantic similarity evaluation"
                raise ValueError(self.error)
            
            if not test_case.actual_output:
                self.error = "Actual output is required for semantic similarity evaluation"
                raise ValueError(self.error)
            
            # Extract and normalize words from both texts
            expected_words = self._extract_significant_words(test_case.expected_output)
            actual_words = self._extract_significant_words(test_case.actual_output)
            
            if not expected_words and not actual_words:
                self.score = 1.0
                self.reason = "Both outputs are empty - considered semantically identical"
                self.success = True
                return self.score
            
            if not expected_words or not actual_words:
                self.score = 0.0
                self.reason = "One output is empty while the other is not - no semantic similarity"
                self.success = False
                return self.score
            
            # Calculate Jaccard similarity for word sets
            expected_set = set(expected_words)
            actual_set = set(actual_words)
            
            # Word overlap
            intersection = expected_set & actual_set
            union = expected_set | actual_set
            
            if not union:
                self.score = 0.0
                self.reason = "No significant words found in either output"
            else:
                # Jaccard similarity: |A ∩ B| / |A ∪ B|
                jaccard_similarity = len(intersection) / len(union)
                
                # Bonus for exact word matches (weighted more heavily)
                exact_matches = len(intersection)
                expected_total = len(expected_set)
                coverage_bonus = exact_matches / expected_total if expected_total > 0 else 0
                
                # Combined score: 70% Jaccard, 30% coverage
                self.score = (jaccard_similarity * 0.7) + (coverage_bonus * 0.3)
            
            # Set reason based on similarity level
            if self.score >= 0.9:
                self.reason = f"Very high semantic similarity ({self.score:.2f}) - outputs convey nearly identical meaning"
            elif self.score >= 0.7:
                self.reason = f"High semantic similarity ({self.score:.2f}) - outputs convey very similar meaning"
            elif self.score >= 0.5:
                self.reason = f"Moderate semantic similarity ({self.score:.2f}) - outputs share some meaning but differ significantly"
            else:
                self.reason = f"Low semantic similarity ({self.score:.2f}) - outputs convey different meanings"
            
            # Success based on configured threshold
            self.success = self.score >= self.threshold
            
            return self.score
            
        except Exception as e:
            self.error = f"Failed to measure semantic similarity: {str(e)}"
            self.success = False
            raise
    
    def _extract_significant_words(self, text: str) -> list:
        """
        Extract significant words from text, filtering out common stop words.
        
        Args:
            text: The text to extract words from
            
        Returns:
            List of significant words (lowercase, no punctuation)
        """
        # Common English stop words to filter out
        stop_words = {
            'a', 'an', 'and', 'are', 'as', 'at', 'be', 'by', 'for', 'from',
            'has', 'he', 'in', 'is', 'it', 'its', 'of', 'on', 'that',
            'the', 'to', 'was', 'were', 'will', 'with', 'the', 'this', 'but',
            'they', 'have', 'had', 'what', 'said', 'each', 'which', 'their',
            'time', 'if', 'up', 'out', 'many', 'then', 'them', 'can',
            'would', 'there', 'been', 'may', 'use', 'such', 'about', 'after'
        }
        
        # Extract words, remove punctuation, convert to lowercase
        words = re.findall(r'\b\w+\b', text.lower())
        
        # Filter out stop words and short words (< 3 chars)
        significant_words = [
            word for word in words 
            if word not in stop_words and len(word) >= 3
        ]
        
        return significant_words
    
    async def a_measure(self, test_case: LLMTestCase) -> float:
        """
        Asynchronous version of measure method.
        
        Args:
            test_case: The test case to evaluate
            
        Returns:
            The semantic similarity score
        """
        return self.measure(test_case)
    
    def is_successful(self) -> bool:
        """Check if metric passed threshold."""
        return self.success if self.success is not None else False