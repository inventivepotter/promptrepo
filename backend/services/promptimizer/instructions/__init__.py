"""
Provider-specific prompt engineering instructions.

This module contains best practices and guidelines for crafting
effective prompts for different LLM providers.
"""
from services.promptimizer.instructions.openai_instructions import OPENAI_INSTRUCTIONS
from services.promptimizer.instructions.anthropic_instructions import ANTHROPIC_INSTRUCTIONS
from services.promptimizer.instructions.google_instructions import GOOGLE_INSTRUCTIONS
from services.promptimizer.instructions.default_instructions import DEFAULT_INSTRUCTIONS
from services.promptimizer.instructions.owasp_guardrails import OWASP_2025_GUARDRAILS

__all__ = [
    "OPENAI_INSTRUCTIONS",
    "ANTHROPIC_INSTRUCTIONS",
    "GOOGLE_INSTRUCTIONS",
    "DEFAULT_INSTRUCTIONS",
    "OWASP_2025_GUARDRAILS",
]
