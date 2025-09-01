"""
Message conversion utilities for chat completions.
"""
from schemas.chat import ChatMessage


def convert_to_any_llm_messages(messages: list[ChatMessage]) -> list[dict]:
    """Convert our ChatMessage format to any-llm format."""
    converted_messages = []
    for msg in messages:
        any_llm_msg: dict = {
            "role": msg.role,
            "content": msg.content
        }
        if msg.tool_call_id:
            any_llm_msg["tool_call_id"] = msg.tool_call_id
        if msg.tool_calls:
            any_llm_msg["tool_calls"] = msg.tool_calls
        converted_messages.append(any_llm_msg)
    return converted_messages