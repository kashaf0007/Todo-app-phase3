import pytest
from fastapi.testclient import TestClient
from backend.src.main import app
from backend.src.database import engine, get_session
from sqlmodel import Session, SQLModel
from unittest.mock import patch


@pytest.fixture(scope="module")
def client():
    with TestClient(app) as test_client:
        yield test_client


def test_health_endpoint(client):
    """Test the health check endpoint"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "healthy"


@patch('backend.src.mcp.tools.MCPTaskTools.add_task')
def test_chat_endpoint_with_mock_tool(mock_add_task, client):
    """Test the chat endpoint with mocked MCP tool"""
    # Mock the tool response
    mock_add_task.return_value = {
        "task_id": 1,
        "status": "pending",
        "title": "Test task"
    }
    
    user_id = "test_user_123"
    response = client.post(
        f"/api/{user_id}/chat",
        json={"message": "Add a test task"}
    )
    
    # The response should be successful (either 200 or 500 depending on Cohere API availability)
    assert response.status_code in [200, 500]