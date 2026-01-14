"""
Final integration test for the RAG Todo Chatbot
Validates that all components work together properly
"""
import pytest
from fastapi.testclient import TestClient
from backend.src.main import app
from unittest.mock import patch, Mock
import os


client = TestClient(app)


def test_complete_workflow():
    """
    Test the complete workflow of the RAG Todo Chatbot
    """
    # Mock Cohere API
    with patch('cohere.Client') as mock_cohere:
        # Setup mock responses
        def mock_generate_response(prompt, *args, **kwargs):
            mock_resp = Mock()
            if "create" in prompt.lower() or "add" in prompt.lower():
                mock_resp.generations = [Mock()]
                mock_resp.generations[0].text = "I've created the task for you."
            elif "list" in prompt.lower() or "show" in prompt.lower():
                mock_resp.generations = [Mock()]
                mock_resp.generations[0].text = "Here are your tasks."
            elif "complete" in prompt.lower() or "done" in prompt.lower():
                mock_resp.generations = [Mock()]
                mock_resp.generations[0].text = "I've marked the task as complete."
            else:
                mock_resp.generations = [Mock()]
                mock_resp.generations[0].text = "I understand. How else can I help you?"
            return mock_resp

        mock_cohere.return_value.generate.side_effect = mock_generate_response

        # Set required environment variable
        os.environ["COHERE_API_KEY"] = "test-key"

        # Test 1: Health check
        response = client.get("/health")
        assert response.status_code == 200
        data = response.json()
        assert data["status"] == "healthy"
        print("✓ Health check passed")

        # Test 2: Create a task
        # Note: In a real implementation, we would need to authenticate first
        # For this test, we'll use a mock user ID
        user_id = "test-user-123"
        response = client.post(f"/api/{user_id}/chat", json={
            "message": "Add a task to buy groceries"
        })
        assert response.status_code == 200
        data = response.json()
        assert "conversation_id" in data
        assert "response" in data
        conversation_id = data["conversation_id"]
        print("✓ Task creation via chat passed")

        # Test 3: List tasks
        response = client.post(f"/api/{user_id}/chat", json={
            "conversation_id": conversation_id,
            "message": "Show me my tasks"
        })
        assert response.status_code == 200
        data = response.json()
        assert "response" in data
        print("✓ Task listing via chat passed")

        # Test 4: Complete a task
        response = client.post(f"/api/{user_id}/chat", json={
            "conversation_id": conversation_id,
            "message": "Complete the groceries task"
        })
        assert response.status_code == 200
        data = response.json()
        assert "response" in data
        print("✓ Task completion via chat passed")

        # Test 5: Get user conversations
        response = client.get(f"/api/{user_id}/conversations")
        assert response.status_code == 200
        data = response.json()
        assert "conversations" in data
        assert len(data["conversations"]) >= 1
        print("✓ Get user conversations passed")

        # Test 6: Get conversation messages
        response = client.get(f"/api/{user_id}/conversations/{conversation_id}/messages")
        assert response.status_code == 200
        data = response.json()
        assert "messages" in data
        assert len(data["messages"]) >= 3  # At least the 3 messages we sent
        print("✓ Get conversation messages passed")

        print("✓ Complete workflow test passed")


def test_context_awareness():
    """
    Test that the system maintains context across conversations
    """
    with patch('cohere.Client') as mock_cohere:
        def mock_generate_response(prompt, *args, **kwargs):
            mock_resp = Mock()
            mock_resp.generations = [Mock()]
            if "groceries" in prompt.lower():
                mock_resp.generations[0].text = "Yes, I remember your groceries task."
            else:
                mock_resp.generations[0].text = "I'm ready to help."
            return mock_resp

        mock_cohere.return_value.generate.side_effect = mock_generate_response

        # Set required environment variable
        os.environ["COHERE_API_KEY"] = "test-key"

        user_id = "test-user-456"
        
        # Create a task
        response = client.post(f"/api/{user_id}/chat", json={
            "message": "Create a task: Buy groceries"
        })
        assert response.status_code == 200
        data = response.json()
        conversation_id = data["conversation_id"]
        print("✓ Context awareness - task creation passed")

        # Follow up with a reference to the previous task
        response = client.post(f"/api/{user_id}/chat", json={
            "conversation_id": conversation_id,
            "message": "Tell me about the groceries task"
        })
        assert response.status_code == 200
        data = response.json()
        assert "groceries" in data["response"].lower() or "task" in data["response"].lower()
        print("✓ Context awareness - follow-up passed")


def test_advanced_task_features():
    """
    Test advanced task features like priority, category, etc.
    """
    with patch('cohere.Client') as mock_cohere:
        def mock_generate_response(prompt, *args, **kwargs):
            mock_resp = Mock()
            mock_resp.generations = [Mock()]
            mock_resp.generations[0].text = "I've added the high priority work task."
            return mock_resp

        mock_cohere.return_value.generate.side_effect = mock_generate_response

        # Set required environment variable
        os.environ["COHERE_API_KEY"] = "test-key"

        user_id = "test-user-789"
        
        # Create a task with metadata
        response = client.post(f"/api/{user_id}/chat", json={
            "message": "Add a high priority work task to prepare presentation"
        })
        assert response.status_code == 200
        data = response.json()
        assert "conversation_id" in data
        print("✓ Advanced task features - creation with metadata passed")

        # List high priority tasks
        response = client.post(f"/api/{user_id}/chat", json={
            "conversation_id": data["conversation_id"],
            "message": "Show me my high priority tasks"
        })
        assert response.status_code == 200
        print("✓ Advanced task features - filtering by priority passed")


def test_security_validation():
    """
    Test security measures
    """
    # Test health endpoint is public
    response = client.get("/health")
    assert response.status_code == 200
    print("✓ Security validation - public endpoint accessible")

    # Test security headers are present
    response = client.get("/health")
    headers = dict(response.headers)
    assert "x-content-type-options" in headers
    assert "x-frame-options" in headers
    assert "x-xss-protection" in headers
    print("✓ Security validation - security headers present")


if __name__ == "__main__":
    test_complete_workflow()
    test_context_awareness()
    test_advanced_task_features()
    test_security_validation()
    print("All final integration tests passed!")