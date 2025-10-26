"""
Unit tests for tools API endpoints.
Tests CRUD operations for mock tool definitions.
"""
import pytest
from unittest.mock import MagicMock, Mock, AsyncMock
from fastapi import Request

from services.tool.models import (
    ToolDefinition,
    ToolParameterType,
    ToolSummary,
    MockConfig,
    ParametersDefinition,
    ParameterSchema
)
from middlewares.rest import (
    NotFoundException,
    ValidationException,
    BadRequestException,
    StandardResponse
)
from api.v0.tools.tools import (
    list_tools,
    get_tool,
    create_tool,
    delete_tool,
    validate_tool,
    execute_mock
)
from api.v0.tools.models import (
    CreateToolRequest,
    MockExecutionRequest,
    ToolSaveResponse
)
from database.models.user_sessions import UserSessions
from database.models.user import User


@pytest.fixture
def mock_request():
    """Mock FastAPI request object with request_id"""
    request = Mock(spec=Request)
    request.state = Mock()
    request.state.request_id = "test_request_id"
    return request


@pytest.fixture
def mock_tool_service():
    """Mock tool service for testing."""
    service = MagicMock()
    service.list_tools = MagicMock()
    service.load_tool = MagicMock()
    service.save_tool = AsyncMock()
    service.delete_tool = MagicMock()
    service.validate_tool = MagicMock()
    service.get_mock_response = MagicMock()
    return service


@pytest.fixture
def mock_user_session():
    """Mock user session for testing."""
    session = Mock(spec=UserSessions)
    session.user_id = "test-user"
    session.oauth_token = "test-oauth-token"
    session.user = Mock(spec=User)
    session.user.oauth_name = "Test User"
    session.user.oauth_username = "testuser"
    session.user.oauth_email = "test@example.com"
    return session


@pytest.fixture
def sample_tool_definition():
    """Sample tool definition for testing."""
    return ToolDefinition(
        name="test_tool",
        description="A test tool",
        parameters=ParametersDefinition(
            type="object",
            properties={
                "param1": ParameterSchema(
                    type=ToolParameterType.STRING,
                    description="First parameter",
                    enum=None,
                    default=None
                )
            },
            required=["param1"]
        ),
        mock=MockConfig(
            enabled=True,
            response="Mock response for test tool",
            static_response=None,
            conditional_rules=None,
            python_code=None
        )
    )


@pytest.fixture
def sample_tool_summary():
    """Sample tool summary for testing."""
    return ToolSummary(
        name="test_tool",
        description="A test tool",
        mock_enabled=True,
        parameter_count=1,
        required_count=1
    )


class TestListTools:
    """Tests for the list_tools endpoint."""
    
    @pytest.mark.asyncio
    async def test_list_tools_success(self, mock_request, mock_tool_service, sample_tool_summary):
        """Test successful listing of tools."""
        # Arrange
        tools_list = [sample_tool_summary]
        mock_tool_service.list_tools.return_value = tools_list
        
        # Act
        result = await list_tools(
            request=mock_request,
            tool_service=mock_tool_service,
            user_id="test-user",
            repo_name="test-repo"
        )
        
        # Assert
        assert isinstance(result, StandardResponse)
        assert result.status == "success"
        assert result.data is not None
        assert len(result.data) == 1
        assert result.data[0].name == "test_tool"
        mock_tool_service.list_tools.assert_called_once_with(repo_name="test-repo", user_id="test-user")
    
    @pytest.mark.asyncio
    async def test_list_tools_empty(self, mock_request, mock_tool_service):
        """Test listing when no tools exist."""
        # Arrange
        mock_tool_service.list_tools.return_value = []
        
        # Act
        result = await list_tools(
            request=mock_request,
            tool_service=mock_tool_service,
            user_id="test-user",
            repo_name="default"
        )
        
        # Assert
        assert isinstance(result, StandardResponse)
        assert result.status == "success"
        assert result.data is not None
        assert len(result.data) == 0
        mock_tool_service.list_tools.assert_called_once_with(repo_name="default", user_id="test-user")


class TestGetTool:
    """Tests for the get_tool endpoint."""
    
    @pytest.mark.asyncio
    async def test_get_tool_success(self, mock_request, mock_tool_service, sample_tool_definition):
        """Test successful retrieval of a tool."""
        # Arrange
        mock_tool_service.load_tool.return_value = sample_tool_definition
        
        # Act
        result = await get_tool(
            request=mock_request,
            tool_name="test_tool",
            tool_service=mock_tool_service,
            user_id="test-user",
            repo_name="default"
        )
        
        # Assert
        assert isinstance(result, StandardResponse)
        assert result.status == "success"
        assert result.data is not None
        assert result.data["name"] == "test_tool"
        mock_tool_service.load_tool.assert_called_once_with(
            tool_name="test_tool",
            repo_name="default",
            user_id="test-user"
        )
    
    @pytest.mark.asyncio
    async def test_get_tool_not_found(self, mock_request, mock_tool_service):
        """Test retrieval of non-existent tool."""
        # Arrange
        mock_tool_service.load_tool.side_effect = NotFoundException(
            resource="Tool",
            identifier="nonexistent"
        )
        
        # Act & Assert
        with pytest.raises(NotFoundException):
            await get_tool(
                request=mock_request,
                tool_name="nonexistent",
                tool_service=mock_tool_service,
                user_id="test-user",
                repo_name="default"
            )


class TestCreateTool:
    """Tests for the create_tool endpoint."""
    
    @pytest.mark.asyncio
    async def test_create_tool_success(self, mock_request, mock_tool_service, mock_user_session, sample_tool_definition):
        """Test successful creation of a tool."""
        # Arrange
        tool_request = CreateToolRequest(
            name="new_tool",
            description="A new tool",
            parameters=ParametersDefinition(
                type="object",
                properties={},
                required=[]
            ),
            mock=MockConfig(
                enabled=True,
                response="Mock response",
                static_response=None,
                conditional_rules=None,
                python_code=None
            ),
            repo_name="default"
        )
        
        mock_tool_service.save_tool.return_value = (sample_tool_definition, None)
        
        # Act
        result = await create_tool(
            request=mock_request,
            tool_request=tool_request,
            tool_service=mock_tool_service,
            user_id="test-user",
            user_session=mock_user_session
        )
        
        # Assert
        assert isinstance(result, StandardResponse)
        assert result.status == "success"
        assert result.data is not None
        assert "tool" in result.data
        assert result.data["tool"]["name"] == "test_tool"
        mock_tool_service.save_tool.assert_called_once()


class TestDeleteTool:
    """Tests for the delete_tool endpoint."""
    
    @pytest.mark.asyncio
    async def test_delete_tool_success(self, mock_request, mock_tool_service):
        """Test successful deletion of a tool."""
        # Arrange
        mock_tool_service.delete_tool.return_value = None
        
        # Act
        result = await delete_tool(
            request=mock_request,
            tool_name="test_tool",
            tool_service=mock_tool_service,
            user_id="test-user",
            repo_name="default"
        )
        
        # Assert
        assert isinstance(result, StandardResponse)
        assert result.status == "success"
        assert result.data is not None
        assert result.data["deleted"] is True
        assert result.data["tool_name"] == "test_tool"
        mock_tool_service.delete_tool.assert_called_once_with(
            tool_name="test_tool",
            repo_name="default",
            user_id="test-user"
        )
    
    @pytest.mark.asyncio
    async def test_delete_tool_not_found(self, mock_request, mock_tool_service):
        """Test deletion of non-existent tool."""
        # Arrange
        mock_tool_service.delete_tool.side_effect = NotFoundException(
            resource="Tool",
            identifier="nonexistent"
        )
        
        # Act & Assert
        with pytest.raises(NotFoundException):
            await delete_tool(
                request=mock_request,
                tool_name="nonexistent",
                tool_service=mock_tool_service,
                user_id="test-user",
                repo_name="default"
            )


class TestValidateTool:
    """Tests for the validate_tool endpoint."""
    
    @pytest.mark.asyncio
    async def test_validate_tool_success(self, mock_request, mock_tool_service, sample_tool_definition):
        """Test successful validation of a tool."""
        # Arrange
        mock_tool_service.load_tool.return_value = sample_tool_definition
        mock_tool_service.validate_tool.return_value = None
        
        # Act
        result = await validate_tool(
            request=mock_request,
            tool_name="test_tool",
            tool_service=mock_tool_service,
            user_id="test-user",
            repo_name="default"
        )
        
        # Assert
        assert isinstance(result, StandardResponse)
        assert result.status == "success"
        assert result.data is not None
        assert result.data["valid"] is True
        assert result.data["tool_name"] == "test_tool"
    
    @pytest.mark.asyncio
    async def test_validate_tool_invalid(self, mock_request, mock_tool_service, sample_tool_definition):
        """Test validation of invalid tool."""
        # Arrange
        mock_tool_service.load_tool.return_value = sample_tool_definition
        mock_tool_service.validate_tool.side_effect = ValidationException(
            message="Validation failed"
        )
        
        # Act & Assert
        with pytest.raises(ValidationException):
            await validate_tool(
                request=mock_request,
                tool_name="test_tool",
                tool_service=mock_tool_service,
                user_id="test-user",
                repo_name="default"
            )


class TestExecuteMock:
    """Tests for the execute_mock endpoint."""
    
    @pytest.mark.asyncio
    async def test_execute_mock_success(self, mock_request, mock_tool_service, sample_tool_definition):
        """Test successful mock execution."""
        # Arrange
        mock_request_data = MockExecutionRequest(
            parameters={"param1": "value1"}
        )
        
        mock_tool_service.load_tool.return_value = sample_tool_definition
        mock_tool_service.get_mock_response.return_value = "Mock response"
        
        # Act
        result = await execute_mock(
            request=mock_request,
            tool_name="test_tool",
            mock_request=mock_request_data,
            tool_service=mock_tool_service,
            user_id="test-user",
            repo_name="default"
        )
        
        # Assert
        assert isinstance(result, StandardResponse)
        assert result.status == "success"
        assert result.data is not None
        assert result.data["response"] == "Mock response"
        assert result.data["tool_name"] == "test_tool"
        assert result.data["parameters_used"] == {"param1": "value1"}
    
    @pytest.mark.asyncio
    async def test_execute_mock_disabled(self, mock_request, mock_tool_service, sample_tool_definition):
        """Test mock execution when mock is disabled."""
        # Arrange
        mock_request_data = MockExecutionRequest(
            parameters={}
        )
        
        mock_tool_service.load_tool.return_value = sample_tool_definition
        mock_tool_service.get_mock_response.return_value = None  # Mock disabled
        
        # Act & Assert
        with pytest.raises(BadRequestException):
            await execute_mock(
                request=mock_request,
                tool_name="test_tool",
                mock_request=mock_request_data,
                tool_service=mock_tool_service,
                user_id="test-user",
                repo_name="default"
            )