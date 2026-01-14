"""
Integration test for complex task management in the RAG Todo Chatbot API
Verifies that complex task operations work correctly across the entire system
"""

import pytest
import os
from fastapi.testclient import TestClient
from unittest.mock import patch, MagicMock, AsyncMock
from backend.src.main import app
from backend.src.models.task import Task
from backend.src.models.conversation import Conversation
from backend.src.models.message import Message
from backend.src.services.task_service import TaskService
from backend.src.services.conversation_service import ConversationService
from backend.src.mcp.tools import MCPTaskTools


def test_complex_task_management_integration():
    """
    Test complex task management scenarios that involve multiple operations:
    - Create multiple tasks with different priorities and categories
    - Update tasks based on contextual references
    - Complete tasks using natural language
    - Query tasks with complex filters
    """
    client = TestClient(app)
    
    # Mock user ID and token (these would come from authentication)
    user_id = "test-complex-user-id"
    auth_token = "fake-jwt-token-for-complex-test"
    
    with patch('backend.src.api.dependencies.get_current_user') as mock_get_current_user:
        # Mock the current user
        mock_user = AsyncMock()
        mock_user.id = user_id
        mock_get_current_user.return_value = mock_user
        
        # Scenario 1: Create multiple tasks with different attributes
        # Add a high priority work task
        response1 = client.post(
            f"/api/{user_id}/chat",
            json={
                "message": "Add a high priority work task to prepare quarterly report",
                "conversation_id": None
            },
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response1.status_code == 200
        response_data1 = response1.json()
        assert "response" in response_data1
        
        # Add a low priority personal task
        response2 = client.post(
            f"/api/{user_id}/chat",
            json={
                "message": "Add a low priority personal task to call mom",
                "conversation_id": response_data1["conversation_id"]
            },
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response2.status_code == 200
        response_data2 = response2.json()
        assert "response" in response_data2
        
        # Add a medium priority shopping task
        response3 = client.post(
            f"/api/{user_id}/chat",
            json={
                "message": "Add a medium priority shopping task to buy groceries",
                "conversation_id": response_data1["conversation_id"]
            },
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response3.status_code == 200
        response_data3 = response3.json()
        assert "response" in response3
        
        # Scenario 2: Query tasks with complex filters
        response4 = client.post(
            f"/api/{user_id}/chat",
            json={
                "message": "Show me all my work tasks",
                "conversation_id": response_data1["conversation_id"]
            },
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response4.status_code == 200
        response_data4 = response4.json()
        assert "response" in response_data4
        # Response should mention the work task we created
        
        # Scenario 3: Update a task using contextual reference
        response5 = client.post(
            f"/api/{user_id}/chat",
            json={
                "message": "Change the grocery task to high priority",
                "conversation_id": response_data1["conversation_id"]
            },
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response5.status_code == 200
        response_data5 = response5.json()
        assert "response" in response_data5
        
        # Scenario 4: Complete a task using contextual reference
        response6 = client.post(
            f"/api/{user_id}/chat",
            json={
                "message": "Mark the work task as complete",
                "conversation_id": response_data1["conversation_id"]
            },
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response6.status_code == 200
        response_data6 = response6.json()
        assert "response" in response_data6
        
        # Scenario 5: Query tasks again to verify changes
        response7 = client.post(
            f"/api/{user_id}/chat",
            json={
                "message": "What tasks do I have left?",
                "conversation_id": response_data1["conversation_id"]
            },
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response7.status_code == 200
        response_data7 = response7.json()
        assert "response" in response_data7
        
        print("✓ Complex task management integration test passed")


def test_cross_referencing_task_operations():
    """
    Test operations that involve referencing tasks across different conversations
    """
    client = TestClient(app)
    
    # Mock user ID and token
    user_id = "test-cross-ref-user-id"
    auth_token = "fake-jwt-token-for-cross-ref-test"
    
    with patch('backend.src.api.dependencies.get_current_user') as mock_get_current_user:
        # Mock the current user
        mock_user = AsyncMock()
        mock_user.id = user_id
        mock_get_current_user.return_value = mock_user
        
        # Create a task in one conversation
        response1 = client.post(
            f"/api/{user_id}/chat",
            json={
                "message": "Add a task to schedule dentist appointment",
                "conversation_id": None
            },
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response1.status_code == 200
        response_data1 = response1.json()
        conversation_id = response_data1["conversation_id"]
        assert "response" in response_data1
        
        # Reference the same task in a follow-up message
        response2 = client.post(
            f"/api/{user_id}/chat",
            json={
                "message": "Set a reminder for that task next Friday",
                "conversation_id": conversation_id
            },
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response2.status_code == 200
        response_data2 = response2.json()
        assert "response" in response_data2
        
        print("✓ Cross-referencing task operations test passed")


def test_complex_filtering_operations():
    """
    Test complex filtering operations that combine multiple criteria
    """
    client = TestClient(app)
    
    # Mock user ID and token
    user_id = "test-filtering-user-id"
    auth_token = "fake-jwt-token-for-filtering-test"
    
    with patch('backend.src.api.dependencies.get_current_user') as mock_get_current_user:
        # Mock the current user
        mock_user = AsyncMock()
        mock_user.id = user_id
        mock_get_current_user.return_value = mock_user
        
        # Add several tasks with different attributes
        tasks_to_create = [
            {"message": "Add a high priority work task to finish presentation", "category": "work"},
            {"message": "Add a low priority personal task to organize desk", "category": "personal"},
            {"message": "Add a medium priority shopping task to buy birthday gift", "category": "shopping"},
            {"message": "Add a high priority health task to book doctor appointment", "category": "health"}
        ]
        
        conversation_id = None
        for i, task_info in enumerate(tasks_to_create):
            response = client.post(
                f"/api/{user_id}/chat",
                json={
                    "message": task_info["message"],
                    "conversation_id": conversation_id
                },
                headers={"Authorization": f"Bearer {auth_token}"}
            )
            
            assert response.status_code == 200
            response_data = response.json()
            if i == 0:  # Store the conversation ID from the first request
                conversation_id = response_data["conversation_id"]
            assert "response" in response_data
        
        # Query for high priority work tasks
        response = client.post(
            f"/api/{user_id}/chat",
            json={
                "message": "Show me my high priority work tasks",
                "conversation_id": conversation_id
            },
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 200
        response_data = response.json()
        assert "response" in response_data
        
        # Query for non-work tasks
        response = client.post(
            f"/api/{user_id}/chat",
            json={
                "message": "Show me my tasks that are not work related",
                "conversation_id": conversation_id
            },
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response.status_code == 200
        response_data = response.json()
        assert "response" in response_data
        
        print("✓ Complex filtering operations test passed")


def test_contextual_task_modification():
    """
    Test modifying tasks based on conversation context and implicit references
    """
    client = TestClient(app)
    
    # Mock user ID and token
    user_id = "test-contextual-user-id"
    auth_token = "fake-jwt-token-for-contextual-test"
    
    with patch('backend.src.api.dependencies.get_current_user') as mock_get_current_user:
        # Mock the current user
        mock_user = AsyncMock()
        mock_user.id = user_id
        mock_get_current_user.return_value = mock_user
        
        # Start a conversation by adding a task
        response1 = client.post(
            f"/api/{user_id}/chat",
            json={
                "message": "I need to schedule a meeting with the marketing team",
                "conversation_id": None
            },
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response1.status_code == 200
        response_data1 = response1.json()
        conversation_id = response_data1["conversation_id"]
        assert "response" in response_data1
        
        # Follow up with a modification that refers to the previous task
        response2 = client.post(
            f"/api/{user_id}/chat",
            json={
                "message": "Actually, make it a video call and set it for next Monday",
                "conversation_id": conversation_id
            },
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response2.status_code == 200
        response_data2 = response2.json()
        assert "response" in response_data2
        
        # Another follow up to complete the task
        response3 = client.post(
            f"/api/{user_id}/chat",
            json={
                "message": "I had the meeting yesterday, mark it as completed",
                "conversation_id": conversation_id
            },
            headers={"Authorization": f"Bearer {auth_token}"}
        )
        
        assert response3.status_code == 200
        response_data3 = response3.json()
        assert "response" in response_data3
        
        print("✓ Contextual task modification test passed")


if __name__ == "__main__":
    test_complex_task_management_integration()
    test_cross_referencing_task_operations()
    test_complex_filtering_operations()
    test_contextual_task_modification()
    print("All complex task management integration tests passed!")