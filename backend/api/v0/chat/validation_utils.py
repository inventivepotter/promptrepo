"""
Validation utilities for chat requests.
"""
from fastapi import HTTPException
from schemas.chat import ChatMessage


def validate_system_message(messages: list[ChatMessage]) -> None:
    """Validate that the first message is a system message."""
    if not messages:
        raise HTTPException(
            status_code=400,
            detail="Messages array cannot be empty. A system message is required to define the AI assistant's behavior."
        )
    
    if messages[0].role != "system":
        raise HTTPException(
            status_code=400,
            detail="First message must be a system message with role 'system'. Please provide a system prompt to define the AI assistant's behavior."
        )
        
    if not messages[0].content or not messages[0].content.strip():
        raise HTTPException(
            status_code=400,
            detail="System message content cannot be empty. Please provide a valid system prompt."
        )


def validate_provider_and_model(provider: str, model: str) -> None:
    """Validate provider and model fields."""
    if not provider or not provider.strip():
        raise HTTPException(
            status_code=400,
            detail="Provider field is required and cannot be empty"
        )
    
    if not model or not model.strip():
        raise HTTPException(
            status_code=400,
            detail="Model field is required and cannot be empty"
        )