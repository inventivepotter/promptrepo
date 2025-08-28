"""
Tests for the FastAPI application.
"""
import pytest
from fastapi.testclient import TestClient
from main import app

client = TestClient(app)


def test_read_root():
    """Test the root endpoint."""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert "message" in data
    assert "version" in data
    assert data["version"] == "0.1.0"


def test_health_check():
    """Test the health check endpoint."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    assert data["status"] == "healthy"
    assert data["message"] == "PromptRepo API is running successfully"
    assert data["version"] == "0.1.0"


def test_health_check_response_structure():
    """Test that health check response has the correct structure."""
    response = client.get("/health")
    assert response.status_code == 200
    data = response.json()
    
    # Verify all required fields are present
    required_fields = ["status", "message", "version"]
    for field in required_fields:
        assert field in data, f"Field '{field}' missing from health check response"
    
    # Verify field types
    assert isinstance(data["status"], str)
    assert isinstance(data["message"], str)
    assert isinstance(data["version"], str)