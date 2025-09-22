"""
Tests for context middleware in backend/middlewares/context_middleware.py
"""
import pytest
from unittest.mock import Mock, AsyncMock, patch
from fastapi import Request
from starlette.responses import Response
import uuid

from middlewares.context_middleware import ContextMiddleware


class TestContextMiddleware:
    """Test cases for ContextMiddleware"""

    @pytest.fixture
    def mock_app(self):
        """Mock ASGI app"""
        return Mock()

    @pytest.fixture
    def mock_request(self):
        """Mock FastAPI Request"""
        request = Mock(spec=Request)
        request.state = Mock()
        request.headers = {}
        request.method = "GET"
        request.url = Mock()
        request.url.path = "/test/path"
        return request

    @pytest.fixture
    def mock_response(self):
        """Mock Response"""
        response = Mock(spec=Response)
        response.headers = {}
        return response

    @pytest.fixture
    def middleware(self, mock_app):
        """ContextMiddleware instance"""
        return ContextMiddleware(mock_app)

    async def test_dispatch_generates_request_id(self, middleware, mock_request, mock_response):
        """Test that middleware generates a unique request ID"""
        call_next = AsyncMock(return_value=mock_response)
        
        with patch('uuid.uuid4') as mock_uuid:
            mock_uuid.return_value = uuid.UUID('12345678-1234-5678-9012-123456789012')
            
            result = await middleware.dispatch(mock_request, call_next)
            
            # Verify request ID was set on request state
            assert mock_request.state.request_id == '12345678-1234-5678-9012-123456789012'
            
            # Verify request ID was added to response headers
            assert result.headers['X-Request-ID'] == '12345678-1234-5678-9012-123456789012'

    async def test_dispatch_uses_existing_correlation_id(self, middleware, mock_request, mock_response):
        """Test that middleware uses existing correlation ID from headers"""
        mock_request.headers = {'X-Correlation-ID': 'existing-correlation-id'}
        call_next = AsyncMock(return_value=mock_response)
        
        await middleware.dispatch(mock_request, call_next)
        
        # Verify correlation ID was set from header
        assert mock_request.state.correlation_id == 'existing-correlation-id'

    async def test_dispatch_generates_correlation_id_when_missing(self, middleware, mock_request, mock_response):
        """Test that middleware generates correlation ID when not provided"""
        call_next = AsyncMock(return_value=mock_response)
        
        with patch('uuid.uuid4') as mock_uuid:
            mock_uuid.side_effect = [
                uuid.UUID('12345678-1234-5678-9012-123456789012'),  # request_id
                uuid.UUID('87654321-4321-8765-2109-876543210987')   # correlation_id
            ]
            
            await middleware.dispatch(mock_request, call_next)
            
            # Verify correlation ID was generated
            assert mock_request.state.correlation_id == '87654321-4321-8765-2109-876543210987'

    async def test_dispatch_calls_next_middleware(self, middleware, mock_request, mock_response):
        """Test that middleware calls the next middleware in chain"""
        call_next = AsyncMock(return_value=mock_response)
        
        result = await middleware.dispatch(mock_request, call_next)
        
        # Verify call_next was called with the request
        call_next.assert_called_once_with(mock_request)
        
        # Verify the response is returned
        assert result == mock_response

    async def test_dispatch_logs_request_info(self, middleware, mock_request, mock_response):
        """Test that middleware logs request information"""
        call_next = AsyncMock(return_value=mock_response)
        
        with patch('middlewares.context_middleware.logger') as mock_logger:
            await middleware.dispatch(mock_request, call_next)
            
            # Verify debug log was called with request info
            mock_logger.debug.assert_called_once()
            log_call = mock_logger.debug.call_args
            assert "Processing request: GET /test/path" in log_call[0][0]
            
            # Verify extra context was provided
            extra = log_call[1]['extra']
            assert 'request_id' in extra
            assert 'correlation_id' in extra

    async def test_dispatch_handles_empty_correlation_header(self, middleware, mock_request, mock_response):
        """Test that middleware handles empty correlation ID header"""
        mock_request.headers = {'X-Correlation-ID': ''}
        call_next = AsyncMock(return_value=mock_response)
        
        with patch('uuid.uuid4') as mock_uuid:
            mock_uuid.side_effect = [
                uuid.UUID('12345678-1234-5678-9012-123456789012'),  # request_id
                uuid.UUID('87654321-4321-8765-2109-876543210987')   # correlation_id
            ]
            
            await middleware.dispatch(mock_request, call_next)
            
            # Verify correlation ID was generated when header is empty
            assert mock_request.state.correlation_id == '87654321-4321-8765-2109-876543210987'

    async def test_dispatch_preserves_response_properties(self, middleware, mock_request):
        """Test that middleware preserves original response properties"""
        original_response = Mock(spec=Response)
        original_response.headers = {'Content-Type': 'application/json'}
        call_next = AsyncMock(return_value=original_response)
        
        result = await middleware.dispatch(mock_request, call_next)
        
        # Verify original response is returned
        assert result == original_response
        
        # Verify original headers are preserved
        assert result.headers['Content-Type'] == 'application/json'
        
        # Verify request ID header was added
        assert 'X-Request-ID' in result.headers

    async def test_dispatch_request_state_persistence(self, middleware, mock_request, mock_response):
        """Test that request state persists across middleware calls"""
        call_next = AsyncMock(return_value=mock_response)
        
        # Add some initial state
        mock_request.state.existing_value = 'test'
        
        await middleware.dispatch(mock_request, call_next)
        
        # Verify existing state is preserved
        assert mock_request.state.existing_value == 'test'
        
        # Verify new state was added
        assert hasattr(mock_request.state, 'request_id')
        assert hasattr(mock_request.state, 'correlation_id')

    async def test_dispatch_different_http_methods(self, middleware, mock_request, mock_response):
        """Test that middleware works with different HTTP methods"""
        call_next = AsyncMock(return_value=mock_response)
        
        methods = ['GET', 'POST', 'PUT', 'DELETE', 'PATCH', 'OPTIONS']
        
        for method in methods:
            mock_request.method = method
            mock_request.url.path = f'/test/{method.lower()}'
            
            with patch('middlewares.context_middleware.logger') as mock_logger:
                await middleware.dispatch(mock_request, call_next)
                
                # Verify log contains correct method
                log_call = mock_logger.debug.call_args[0][0]
                assert f"Processing request: {method} /test/{method.lower()}" in log_call

    async def test_middleware_initialization(self, mock_app):
        """Test that middleware initializes correctly"""
        middleware = ContextMiddleware(mock_app)
        
        # Verify app is stored
        assert hasattr(middleware, 'app')
        
        # Verify it's a BaseHTTPMiddleware
        from starlette.middleware.base import BaseHTTPMiddleware
        assert isinstance(middleware, BaseHTTPMiddleware)