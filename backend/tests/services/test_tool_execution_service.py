"""
Unit tests for ToolExecutionService with focus on default parameter handling.
"""
import json
import pytest
from unittest.mock import Mock
from services.tool.tool_execution_service import ToolExecutionService
from services.tool.models import (
    ToolDefinition,
    ParametersDefinition,
    ParameterSchema,
    MockConfig,
    MockType,
    ToolParameterType
)
from services.llm.models import ChatMessage


class TestToolExecutionService:
    """Test cases for ToolExecutionService."""
    
    @pytest.fixture
    def mock_tool_service(self):
        """Create a mock tool service."""
        return Mock()
    
    @pytest.fixture
    def mock_chat_completion_service(self):
        """Create a mock chat completion service."""
        return Mock()
    
    @pytest.fixture
    def tool_execution_service(self, mock_tool_service, mock_chat_completion_service):
        """Create a ToolExecutionService instance."""
        return ToolExecutionService(
            tool_service=mock_tool_service,
            chat_completion_service=mock_chat_completion_service
        )
    
    @pytest.fixture
    def sample_tool_with_defaults(self):
        """Create a sample tool definition with default parameters."""
        return ToolDefinition(
            name="get_weather",
            description="Get weather information",
            parameters=ParametersDefinition(
                type="object",
                properties={
                    "location": ParameterSchema(
                        type=ToolParameterType.STRING,
                        description="City name",
                        enum=None,
                        default="New York"
                    ),
                    "units": ParameterSchema(
                        type=ToolParameterType.STRING,
                        description="Temperature units",
                        default="celsius",
                        enum=["celsius", "fahrenheit"]
                    ),
                    "include_forecast": ParameterSchema(
                        type=ToolParameterType.BOOLEAN,
                        description="Include forecast",
                        enum=None,
                        default=False
                    ),
                    "days": ParameterSchema(
                        type=ToolParameterType.NUMBER,
                        description="Forecast days",
                        enum=None,
                        default=3
                    )
                },
                required=["location"]
            ),
            mock=MockConfig(
                enabled=True,
                mock_type=MockType.STATIC,
                response=None,
                static_response='{"temperature": 72, "conditions": "sunny"}',
                conditional_rules=None,
                python_code=None
            )
        )
    
    @pytest.fixture
    def sample_tool_no_defaults(self):
        """Create a sample tool definition without default parameters."""
        return ToolDefinition(
            name="search_database",
            description="Search database",
            parameters=ParametersDefinition(
                type="object",
                properties={
                    "query": ParameterSchema(
                        type=ToolParameterType.STRING,
                        description="Search query",
                        enum=None,
                        default=None
                    ),
                    "limit": ParameterSchema(
                        type=ToolParameterType.NUMBER,
                        description="Result limit",
                        enum=None,
                        default=None
                    )
                },
                required=["query"]
            ),
            mock=MockConfig(
                enabled=True,
                mock_type=MockType.STATIC,
                response=None,
                static_response='{"results": []}',
                conditional_rules=None,
                python_code=None
            )
        )
    
    def test_apply_default_parameters_all_provided(
        self,
        tool_execution_service,
        sample_tool_with_defaults
    ):
        """Test that provided parameters are not overwritten."""
        provided_args = {
            "location": "London",
            "units": "fahrenheit",
            "include_forecast": True,
            "days": 5
        }
        
        result = tool_execution_service._apply_default_parameters(
            sample_tool_with_defaults,
            provided_args,
            request_id="test-123"
        )
        
        assert result == provided_args
        assert result["location"] == "London"
        assert result["units"] == "fahrenheit"
        assert result["include_forecast"] is True
        assert result["days"] == 5
    
    def test_apply_default_parameters_none_provided(
        self,
        tool_execution_service,
        sample_tool_with_defaults
    ):
        """Test that all defaults are applied when no parameters provided."""
        provided_args = {}
        
        result = tool_execution_service._apply_default_parameters(
            sample_tool_with_defaults,
            provided_args,
            request_id="test-123"
        )
        
        assert result["location"] == "New York"
        assert result["units"] == "celsius"
        assert result["include_forecast"] is False
        assert result["days"] == 3
    
    def test_apply_default_parameters_partial_provided(
        self,
        tool_execution_service,
        sample_tool_with_defaults
    ):
        """Test that defaults are applied only for missing parameters."""
        provided_args = {
            "location": "Paris",
            "include_forecast": True
        }
        
        result = tool_execution_service._apply_default_parameters(
            sample_tool_with_defaults,
            provided_args,
            request_id="test-123"
        )
        
        assert result["location"] == "Paris"  # Provided
        assert result["units"] == "celsius"  # Default
        assert result["include_forecast"] is True  # Provided
        assert result["days"] == 3  # Default
    
    def test_apply_default_parameters_no_defaults_available(
        self,
        tool_execution_service,
        sample_tool_no_defaults
    ):
        """Test behavior when parameters have no defaults."""
        provided_args = {"query": "test"}
        
        result = tool_execution_service._apply_default_parameters(
            sample_tool_no_defaults,
            provided_args,
            request_id="test-123"
        )
        
        # Only provided parameter should be in result
        assert result["query"] == "test"
        # Optional parameter without default should not be added
        assert "limit" not in result
    
    def test_apply_default_parameters_different_types(
        self,
        tool_execution_service
    ):
        """Test default parameters with different data types."""
        tool_def = ToolDefinition(
            name="test_tool",
            description="Test tool",
            parameters=ParametersDefinition(
                type="object",
                properties={
                    "string_param": ParameterSchema(
                        type=ToolParameterType.STRING,
                        description="String parameter",
                        enum=None,
                        default="default_string"
                    ),
                    "number_param": ParameterSchema(
                        type=ToolParameterType.NUMBER,
                        description="Number parameter",
                        enum=None,
                        default=42
                    ),
                    "boolean_param": ParameterSchema(
                        type=ToolParameterType.BOOLEAN,
                        description="Boolean parameter",
                        enum=None,
                        default=True
                    ),
                    "array_param": ParameterSchema(
                        type=ToolParameterType.ARRAY,
                        description="Array parameter",
                        enum=None,
                        default=["a", "b", "c"]
                    ),
                    "object_param": ParameterSchema(
                        type=ToolParameterType.OBJECT,
                        description="Object parameter",
                        enum=None,
                        default={"key": "value"}
                    )
                },
                required=[]
            ),
            mock=MockConfig(
                enabled=True,
                mock_type=MockType.STATIC,
                response=None,
                static_response='{"result": "ok"}',
                conditional_rules=None,
                python_code=None
            )
        )
        
        provided_args = {}
        
        result = tool_execution_service._apply_default_parameters(
            tool_def,
            provided_args,
            request_id="test-123"
        )
        
        assert result["string_param"] == "default_string"
        assert result["number_param"] == 42
        assert result["boolean_param"] is True
        assert result["array_param"] == ["a", "b", "c"]
        assert result["object_param"] == {"key": "value"}
    
    def test_generate_tool_responses_with_defaults(
        self,
        tool_execution_service,
        mock_tool_service,
        sample_tool_with_defaults
    ):
        """Test tool response generation with default parameter handling."""
        # Mock tool service to return tool definition and mock response
        mock_tool_service.load_tool.return_value = sample_tool_with_defaults
        mock_tool_service.get_mock_response.return_value = '{"temperature": 72, "conditions": "sunny"}'
        
        # Tool call with partial arguments
        tool_calls = [
            {
                "id": "call_123",
                "function": {
                    "name": "get_weather",
                    "arguments": '{"location": "Tokyo"}'
                }
            }
        ]
        
        result = tool_execution_service._generate_tool_responses(
            tool_calls,
            repo_name="test_repo",
            user_id="test_user",
            request_id="test-123"
        )
        
        # Should return one tool response
        assert len(result) == 1
        assert result[0].role == "tool"
        assert result[0].tool_call_id == "call_123"
        assert result[0].content == '{"temperature": 72, "conditions": "sunny"}'
        
        # Verify tool was loaded
        mock_tool_service.load_tool.assert_called_once_with(
            "get_weather",
            "test_repo",
            "test_user"
        )
    
    def test_generate_tool_responses_no_arguments(
        self,
        tool_execution_service,
        mock_tool_service,
        sample_tool_with_defaults
    ):
        """Test tool response generation when no arguments provided."""
        mock_tool_service.load_tool.return_value = sample_tool_with_defaults
        mock_tool_service.get_mock_response.return_value = '{"temperature": 72, "conditions": "sunny"}'
        
        # Tool call with no arguments (empty object)
        tool_calls = [
            {
                "id": "call_456",
                "function": {
                    "name": "get_weather",
                    "arguments": '{}'
                }
            }
        ]
        
        result = tool_execution_service._generate_tool_responses(
            tool_calls,
            repo_name="test_repo",
            user_id="test_user",
            request_id="test-456"
        )
        
        # Should still return tool response with defaults applied
        assert len(result) == 1
        assert result[0].role == "tool"
        assert result[0].tool_call_id == "call_456"
    
    def test_generate_tool_responses_invalid_json_arguments(
        self,
        tool_execution_service,
        mock_tool_service,
        sample_tool_with_defaults
    ):
        """Test handling of invalid JSON in tool call arguments."""
        mock_tool_service.load_tool.return_value = sample_tool_with_defaults
        mock_tool_service.get_mock_response.return_value = '{"temperature": 72, "conditions": "sunny"}'
        
        # Tool call with invalid JSON
        tool_calls = [
            {
                "id": "call_789",
                "function": {
                    "name": "get_weather",
                    "arguments": 'invalid json {'
                }
            }
        ]
        
        result = tool_execution_service._generate_tool_responses(
            tool_calls,
            repo_name="test_repo",
            user_id="test_user",
            request_id="test-789"
        )
        
        # Should still return mock response even with invalid arguments
        assert len(result) == 1
        assert result[0].role == "tool"
    
    def test_generate_tool_responses_multiple_tools(
        self,
        tool_execution_service,
        mock_tool_service,
        sample_tool_with_defaults,
        sample_tool_no_defaults
    ):
        """Test generation of responses for multiple tool calls."""
        # Configure mock to return different tools
        def load_tool_side_effect(name, repo, user):
            if name == "get_weather":
                return sample_tool_with_defaults
            elif name == "search_database":
                return sample_tool_no_defaults
            return None
        
        def get_mock_response_side_effect(tool):
            if tool.name == "get_weather":
                return '{"temperature": 72, "conditions": "sunny"}'
            elif tool.name == "search_database":
                return '{"results": []}'
            return None
        
        mock_tool_service.load_tool.side_effect = load_tool_side_effect
        mock_tool_service.get_mock_response.side_effect = get_mock_response_side_effect
        
        tool_calls = [
            {
                "id": "call_1",
                "function": {
                    "name": "get_weather",
                    "arguments": '{"location": "Berlin"}'
                }
            },
            {
                "id": "call_2",
                "function": {
                    "name": "search_database",
                    "arguments": '{"query": "test"}'
                }
            }
        ]
        
        result = tool_execution_service._generate_tool_responses(
            tool_calls,
            repo_name="test_repo",
            user_id="test_user",
            request_id="test-multi"
        )
        
        # Should return two tool responses
        assert len(result) == 2
        assert result[0].tool_call_id == "call_1"
        assert result[1].tool_call_id == "call_2"
    
    def test_ensure_json_string_with_primitive_integer(self, tool_execution_service):
        """Test that primitive integer values are wrapped in JSON object."""
        result = tool_execution_service._ensure_json_string("23")
        parsed = json.loads(result)
        assert isinstance(parsed, dict)
        assert "result" in parsed
        assert parsed["result"] == 23
    
    def test_ensure_json_string_with_primitive_float(self, tool_execution_service):
        """Test that primitive float values are wrapped in JSON object."""
        result = tool_execution_service._ensure_json_string("23.5")
        parsed = json.loads(result)
        assert isinstance(parsed, dict)
        assert "result" in parsed
        assert parsed["result"] == 23.5
    
    def test_ensure_json_string_with_primitive_boolean(self, tool_execution_service):
        """Test that primitive boolean values are wrapped in JSON object."""
        result = tool_execution_service._ensure_json_string("true")
        parsed = json.loads(result)
        assert isinstance(parsed, dict)
        assert "result" in parsed
        assert parsed["result"] is True
    
    def test_ensure_json_string_with_primitive_string(self, tool_execution_service):
        """Test that primitive string values are wrapped in JSON object."""
        result = tool_execution_service._ensure_json_string('"hello world"')
        parsed = json.loads(result)
        assert isinstance(parsed, dict)
        assert "result" in parsed
        assert parsed["result"] == "hello world"
    
    def test_ensure_json_string_with_object(self, tool_execution_service):
        """Test that JSON objects are returned as-is."""
        input_json = '{"temperature": 23, "units": "celsius"}'
        result = tool_execution_service._ensure_json_string(input_json)
        assert result == input_json
        parsed = json.loads(result)
        assert isinstance(parsed, dict)
        assert parsed["temperature"] == 23
    
    def test_ensure_json_string_with_array(self, tool_execution_service):
        """Test that JSON arrays are returned as-is."""
        input_json = '[1, 2, 3]'
        result = tool_execution_service._ensure_json_string(input_json)
        assert result == input_json
        parsed = json.loads(result)
        assert isinstance(parsed, list)
        assert parsed == [1, 2, 3]
    
    def test_ensure_json_string_with_plain_text(self, tool_execution_service):
        """Test that plain text is wrapped in JSON object."""
        result = tool_execution_service._ensure_json_string("plain text response")
        parsed = json.loads(result)
        assert isinstance(parsed, dict)
        assert "result" in parsed
        assert parsed["result"] == "plain text response"
    
    def test_ensure_json_string_with_empty_string(self, tool_execution_service):
        """Test that empty string returns null result."""
        result = tool_execution_service._ensure_json_string("")
        parsed = json.loads(result)
        assert isinstance(parsed, dict)
        assert "result" in parsed
        assert parsed["result"] is None
    
    def test_ensure_json_string_with_null(self, tool_execution_service):
        """Test that null value is wrapped properly."""
        result = tool_execution_service._ensure_json_string("null")
        parsed = json.loads(result)
        assert isinstance(parsed, dict)
        assert "result" in parsed
        assert parsed["result"] is None
    
    def test_generate_tool_responses_with_primitive_mock(
        self,
        tool_execution_service,
        mock_tool_service
    ):
        """Test tool response generation with primitive mock response."""
        # Create a tool with primitive mock response
        tool_def = ToolDefinition(
            name="temp_tool",
            description="Get temperature",
            parameters=ParametersDefinition(
                type="object",
                properties={
                    "city": ParameterSchema(
                        type=ToolParameterType.STRING,
                        description="City name",
                        enum=None,
                        default=None
                    ),
                    "unit": ParameterSchema(
                        type=ToolParameterType.STRING,
                        description="Temperature unit",
                        enum=None,
                        default="celsius"
                    )
                },
                required=["city"]
            ),
            mock=MockConfig(
                enabled=True,
                mock_type=MockType.STATIC,
                response=None,
                static_response="23",  # Primitive integer as string
                conditional_rules=None,
                python_code=None
            )
        )
        
        mock_tool_service.load_tool.return_value = tool_def
        mock_tool_service.get_mock_response.return_value = "23"
        
        tool_calls = [
            {
                "id": "call_temp",
                "function": {
                    "name": "temp_tool",
                    "arguments": '{"city": "new york"}'
                }
            }
        ]
        
        result = tool_execution_service._generate_tool_responses(
            tool_calls,
            repo_name="test_repo",
            user_id="test_user",
            request_id="test-primitive"
        )
        
        # Should return one tool response with wrapped primitive
        assert len(result) == 1
        assert result[0].role == "tool"
        assert result[0].tool_call_id == "call_temp"
        
        # Content should be valid JSON object
        parsed = json.loads(result[0].content)
        assert isinstance(parsed, dict)
        assert "result" in parsed
        assert parsed["result"] == 23