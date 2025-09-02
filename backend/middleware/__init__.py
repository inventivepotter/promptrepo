"""
Middleware package for PromptRepo backend.
"""
from .auth_middleware import AuthMiddleware

__all__ = ["AuthMiddleware"]