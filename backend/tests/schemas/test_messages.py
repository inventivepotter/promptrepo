"""
Unit tests for message schemas.
"""
import pytest
from datetime import datetime
from typing import Literal
from pydantic import ValidationError

from schemas.messages import (
    AIMessageSchema,
    BaseMessageSchema,
    ConversationSchema,
    SystemMessageSchema,
    ToolCallSchema,
    ToolMessageSchema,
    ToolResponseSchema,
    UserMessageSchema,
)


class TestToolCallSchema:
    """Test cases for ToolCallSchema."""

    def test_valid_tool_call(self):
        """Test creating a valid tool call."""
        tool_call = ToolCallSchema(
            id="call_123",
            name="search_files",
            arguments={"path": ".", "regex": ".*\\.py$"}
        )
        assert tool_call.id == "call_123"
        assert tool_call.name == "search_files"
        assert tool_call.arguments["path"] == "."
        assert tool_call.arguments["regex"] == ".*\\.py$"

    def test_tool_call_with_empty_arguments(self):
        """Test tool call with no arguments."""
        tool_call = ToolCallSchema(
            id="call_456",
            name="list_files"
        )
        assert tool_call.arguments == {}

    def test_tool_call_missing_required_fields(self):
        """Test tool call validation fails without required fields."""
        with pytest.raises(ValidationError):
            ToolCallSchema(name="search_files")  # type: ignore


class TestToolResponseSchema:
    """Test cases for ToolResponseSchema."""

    def test_valid_tool_response(self):
        """Test creating a valid tool response."""
        response = ToolResponseSchema(
            tool_call_id="call_123",
            tool_name="search_files",
            content="Found 5 files",
            is_error=False,
            execution_time_ms=125.5
        )
        assert response.tool_call_id == "call_123"
        assert response.tool_name == "search_files"
        assert response.content == "Found 5 files"
        assert response.is_error is False
        assert response.execution_time_ms == 125.5

    def test_tool_response_with_error(self):
        """Test tool response for error case."""
        response = ToolResponseSchema(
            tool_call_id="call_456",
            tool_name="invalid_tool",
            content="Tool not found",
            is_error=True
        )
        assert response.is_error is True
        assert response.execution_time_ms is None

    def test_tool_response_with_metadata(self):
        """Test tool response with metadata."""
        response = ToolResponseSchema(
            tool_call_id="call_789",
            tool_name="execute_command",
            content="Command executed",
            metadata={"exit_code": 0, "stderr": ""}
        )
        assert response.metadata is not None
        assert response.metadata["exit_code"] == 0


class TestUserMessageSchema:
    """Test cases for UserMessageSchema."""

    def test_valid_user_message(self):
        """Test creating a valid user message."""
        message = UserMessageSchema(
            content="Hello, can you help me?",
            user_id="user_123"
        )
        assert message.role == "user"
        assert message.content == "Hello, can you help me?"
        assert message.user_id == "user_123"

    def test_user_message_without_user_id(self):
        """Test user message without user ID."""
        message = UserMessageSchema(content="Test message")
        assert message.user_id is None

    def test_user_message_with_timestamp(self):
        """Test user message with custom timestamp."""
        now = datetime.utcnow()
        message = UserMessageSchema(
            content="Test",
            timestamp=now
        )
        assert message.timestamp == now


class TestAIMessageSchema:
    """Test cases for AIMessageSchema."""

    def test_valid_ai_message(self):
        """Test creating a valid AI message."""
        message = AIMessageSchema(
            content="I'll help you with that.",
            model="claude-sonnet-4.5"
        )
        assert message.role == "assistant"
        assert message.content == "I'll help you with that."
        assert message.model == "claude-sonnet-4.5"

    def test_ai_message_with_tool_calls(self):
        """Test AI message with tool calls."""
        tool_call = ToolCallSchema(
            id="call_123",
            name="search_files",
            arguments={"path": "."}
        )
        message = AIMessageSchema(
            content="I'll search for files.",
            tool_calls=[tool_call],
            finish_reason="tool_calls"
        )
        assert message.tool_calls is not None
        assert len(message.tool_calls) == 1
        assert message.tool_calls[0].name == "search_files"
        assert message.finish_reason == "tool_calls"

    def test_ai_message_with_token_usage(self):
        """Test AI message with token usage."""
        message = AIMessageSchema(
            content="Response",
            token_usage={"input_tokens": 100, "output_tokens": 50}
        )
        assert message.token_usage is not None
        assert message.token_usage["input_tokens"] == 100
        assert message.token_usage["output_tokens"] == 50

    def test_ai_message_finish_reasons(self):
        """Test different finish reasons."""
        reasons: list[Literal["stop", "length", "tool_calls", "content_filter"]] = [
            "stop", "length", "tool_calls", "content_filter"
        ]
        for reason in reasons:
            message = AIMessageSchema(
                content="Test",
                finish_reason=reason
            )
            assert message.finish_reason == reason


class TestSystemMessageSchema:
    """Test cases for SystemMessageSchema."""

    def test_valid_system_message(self):
        """Test creating a valid system message."""
        message = SystemMessageSchema(
            content="You are a helpful assistant."
        )
        assert message.role == "system"
        assert message.content == "You are a helpful assistant."
        assert message.priority == "medium"

    def test_system_message_with_priority(self):
        """Test system message with different priorities."""
        priorities: list[Literal["low", "medium", "high"]] = ["low", "medium", "high"]
        for priority in priorities:
            message = SystemMessageSchema(
                content="System instruction",
                priority=priority
            )
            assert message.priority == priority


class TestToolMessageSchema:
    """Test cases for ToolMessageSchema."""

    def test_valid_tool_message(self):
        """Test creating a valid tool message."""
        message = ToolMessageSchema(
            content="File search complete",
            tool_call_id="call_123",
            tool_name="search_files"
        )
        assert message.role == "tool"
        assert message.content == "File search complete"
        assert message.tool_call_id == "call_123"
        assert message.tool_name == "search_files"
        assert message.is_error is False

    def test_tool_message_with_error(self):
        """Test tool message for error case."""
        message = ToolMessageSchema(
            content="Error: File not found",
            tool_call_id="call_456",
            tool_name="read_file",
            is_error=True
        )
        assert message.is_error is True


class TestConversationSchema:
    """Test cases for ConversationSchema."""

    def test_valid_conversation(self):
        """Test creating a valid conversation."""
        system_msg = SystemMessageSchema(content="You are helpful.")
        user_msg = UserMessageSchema(content="Hello!", user_id="user_123")
        ai_msg = AIMessageSchema(content="Hi there!")

        conversation = ConversationSchema(
            id="conv_123",
            messages=[system_msg, user_msg, ai_msg],
            user_id="user_123"
        )
        assert conversation.id == "conv_123"
        assert len(conversation.messages) == 3
        assert conversation.user_id == "user_123"

    def test_empty_conversation(self):
        """Test conversation with no messages."""
        conversation = ConversationSchema(
            id="conv_empty",
            messages=[]
        )
        assert len(conversation.messages) == 0

    def test_conversation_timestamps(self):
        """Test conversation created_at and updated_at."""
        conversation = ConversationSchema(
            id="conv_456",
            messages=[]
        )
        assert isinstance(conversation.created_at, datetime)
        assert isinstance(conversation.updated_at, datetime)

    def test_conversation_with_metadata(self):
        """Test conversation with metadata."""
        conversation = ConversationSchema(
            id="conv_789",
            messages=[],
            metadata={"session_id": "sess_123", "tags": ["important"]}
        )
        assert conversation.metadata is not None
        assert conversation.metadata["session_id"] == "sess_123"
        assert "important" in conversation.metadata["tags"]

    def test_mixed_message_types_in_conversation(self):
        """Test conversation with all message types."""
        messages = [
            SystemMessageSchema(content="System"),
            UserMessageSchema(content="User", user_id="u1"),
            AIMessageSchema(
                content="AI",
                tool_calls=[ToolCallSchema(id="c1", name="tool")]
            ),
            ToolMessageSchema(
                content="Tool result",
                tool_call_id="c1",
                tool_name="tool"
            )
        ]
        conversation = ConversationSchema(
            id="conv_mixed",
            messages=messages
        )
        assert len(conversation.messages) == 4
        assert conversation.messages[0].role == "system"
        assert conversation.messages[1].role == "user"
        assert conversation.messages[2].role == "assistant"
        assert conversation.messages[3].role == "tool"