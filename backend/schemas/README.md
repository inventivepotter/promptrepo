# Message Schemas

This directory contains Pydantic schemas for different message types used in agent conversations.

## Overview

The message schemas provide type-safe models for representing conversations between users, AI assistants, and tools. These schemas support:

- User messages
- AI/Assistant messages with tool calls
- System messages for instructions
- Tool execution messages
- Complete conversation management

## Schema Files

### `messages.py`

Contains comprehensive message type definitions:

#### Core Message Types

1. **[`UserMessageSchema`](messages.py:82)** - Messages from users
   - Role: `"user"`
   - Contains user content and optional user ID
   - Tracks timestamp and metadata

2. **[`AIMessageSchema`](messages.py:108)** - Messages from AI assistant
   - Role: `"assistant"`
   - Supports tool calls
   - Tracks model, finish reason, and token usage
   - Optional metadata for additional context

3. **[`SystemMessageSchema`](messages.py:156)** - System instructions
   - Role: `"system"`
   - Priority levels: `"low"`, `"medium"`, `"high"`
   - Used for agent configuration and context

4. **[`ToolMessageSchema`](messages.py:181)** - Tool execution results
   - Role: `"tool"`
   - References the tool call ID
   - Indicates success or error state
   - Contains tool output

#### Supporting Schemas

5. **[`ToolCallSchema`](messages.py:16)** - Represents a tool invocation
   - Unique ID for tracking
   - Tool name and arguments
   - Used within AI messages

6. **[`ToolResponseSchema`](messages.py:38)** - Tool execution response
   - References tool call ID
   - Execution result content
   - Error state and execution time
   - Optional metadata

7. **[`ConversationSchema`](messages.py:209)** - Complete conversation
   - List of messages (any type)
   - User association
   - Timestamps for created/updated
   - Conversation-level metadata

## Usage Examples

### Creating a User Message

```python
from schemas.messages import UserMessageSchema

message = UserMessageSchema(
    content="Can you search for Python files?",
    user_id="user_123"
)
```

### Creating an AI Message with Tool Call

```python
from schemas.messages import AIMessageSchema, ToolCallSchema

tool_call = ToolCallSchema(
    id="call_abc123",
    name="search_files",
    arguments={"path": ".", "regex": ".*\\.py$"}
)

ai_message = AIMessageSchema(
    content="I'll search for Python files in the current directory.",
    model="claude-sonnet-4.5",
    tool_calls=[tool_call],
    finish_reason="tool_calls"
)
```

### Creating a Tool Response

```python
from schemas.messages import ToolMessageSchema

tool_response = ToolMessageSchema(
    content="Found 5 Python files: app.py, utils.py, models.py",
    tool_call_id="call_abc123",
    tool_name="search_files",
    is_error=False
)
```

### Building a Conversation

```python
from schemas.messages import (
    ConversationSchema,
    SystemMessageSchema,
    UserMessageSchema,
    AIMessageSchema
)

conversation = ConversationSchema(
    id="conv_123",
    user_id="user_123",
    messages=[
        SystemMessageSchema(
            content="You are a helpful coding assistant.",
            priority="high"
        ),
        UserMessageSchema(
            content="Hello!",
            user_id="user_123"
        ),
        AIMessageSchema(
            content="Hello! How can I help you today?",
            model="claude-sonnet-4.5"
        )
    ]
)
```

## Type Safety

All schemas use Pydantic for runtime type validation and provide:

- Automatic validation on instantiation
- JSON serialization/deserialization
- Type hints for IDE support
- Clear error messages for invalid data

## Testing

Comprehensive tests are available in [`backend/tests/schemas/test_messages.py`](../tests/schemas/test_messages.py).

Run tests with:
```bash
cd backend
uv run pytest tests/schemas/test_messages.py -v
```

## Integration

These schemas can be used:

- In API endpoints for request/response models
- With database models for ORM mapping
- In service layers for type-safe business logic
- For serializing conversation history
- In agent implementations for message handling