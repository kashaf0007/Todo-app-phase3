"""
Integration test for multi-turn conversations in RAG Todo Chatbot
"""
import pytest
from unittest.mock import Mock, patch
from fastapi.testclient import TestClient
from backend.src.main import app
from backend.src.database import get_session
from backend.src.models.user import User
from backend.src.models.task import Task
from backend.src.models.conversation import Conversation
from backend.src.models.message import Message
from datetime import datetime
from sqlmodel import Session, select


class TestMultiTurnConversations:
    """
    Integration test for multi-turn conversations functionality
    """
    
    def setup_method(self):
        # Create a test client
        self.client = TestClient(app)
        
        # Mock Cohere client
        self.mock_cohere_client = Mock()
        self.mock_generate_response = Mock()
        self.mock_generate_response.text = "I've added the task for you."
        self.mock_cohere_client.generate.return_value = Mock(generations=[self.mock_generate_response])
        
        # Patch the Cohere client in the RAG service
        patcher = patch('backend.src.services.rag_service.cohere.Client', return_value=self.mock_cohere_client)
        self.mock_cohere_patcher = patcher.start()
        self.addCleanup(patcher.stop)
    
    def addCleanup(self, func):
        """Helper method to simulate unittest's addCleanup"""
        import atexit
        atexit.register(func)
    
    def test_multi_turn_conversation_flow(self):
        """
        Test a complete multi-turn conversation flow
        """
        # First, create a mock user in the database
        session_gen = get_session()
        session = next(session_gen)
        
        try:
            # Create a test user
            test_user = User(
                id="test-user-123",
                email="test@example.com",
                password_hash="hashed_password",
                created_at=datetime.now()
            )
            session.add(test_user)
            session.commit()
            
            # Simulate a multi-turn conversation
            headers = {"Authorization": "Bearer fake-jwt-token"}
            
            # Turn 1: User creates a task
            response1 = self.client.post(
                f"/api/test-user-123/chat",
                json={
                    "message": "Add a task to buy groceries"
                },
                headers=headers
            )
            
            assert response1.status_code == 200
            response_data1 = response1.json()
            conversation_id = response_data1["conversation_id"]
            
            # Turn 2: User asks about their tasks (should reference previous context)
            response2 = self.client.post(
                f"/api/test-user-123/chat",
                json={
                    "conversation_id": conversation_id,
                    "message": "What tasks do I have?"
                },
                headers=headers
            )
            
            assert response2.status_code == 200
            response_data2 = response2.json()
            
            # Turn 3: User marks the previous task as complete using contextual reference
            response3 = self.client.post(
                f"/api/test-user-123/chat",
                json={
                    "conversation_id": conversation_id,
                    "message": "Mark that grocery task as complete"
                },
                headers=headers
            )
            
            assert response3.status_code == 200
            response_data3 = response3.json()
            
            # Verify that the conversation maintained context across turns
            assert "grocery" in response_data2["response"].lower() or "task" in response_data2["response"].lower()
            assert "complete" in response_data3["response"].lower()
            
        finally:
            session.close()
    
    def test_conversation_history_includes_past_interactions(self):
        """
        Test that conversation history is properly maintained and accessible
        """
        # Create a test client
        client = TestClient(app)
        
        # Mock Cohere client
        with patch('backend.src.services.rag_service.cohere.Client') as mock_cohere:
            mock_instance = Mock()
            mock_response = Mock()
            mock_response.text = "I've processed your request."
            mock_instance.generate.return_value = Mock(generations=[mock_response])
            mock_cohere.return_value = mock_instance
            
            # Create a mock user in the database
            session_gen = get_session()
            session = next(session_gen)
            
            try:
                # Create a test user
                test_user = User(
                    id="test-user-456",
                    email="test2@example.com",
                    password_hash="hashed_password",
                    created_at=datetime.now()
                )
                session.add(test_user)
                session.commit()
                
                headers = {"Authorization": "Bearer fake-jwt-token"}
                
                # Start a conversation with multiple exchanges
                response1 = client.post(
                    f"/api/test-user-456/chat",
                    json={
                        "message": "I need to schedule a meeting with John tomorrow"
                    },
                    headers=headers
                )
                
                assert response1.status_code == 200
                data1 = response1.json()
                conversation_id = data1["conversation_id"]
                
                response2 = client.post(
                    f"/api/test-user-456/chat",
                    json={
                        "conversation_id": conversation_id,
                        "message": "Also add a reminder to prepare slides"
                    },
                    headers=headers
                )
                
                assert response2.status_code == 200
                
                response3 = client.post(
                    f"/api/test-user-456/chat",
                    json={
                        "conversation_id": conversation_id,
                        "message": "What did I just ask you for?"
                    },
                    headers=headers
                )
                
                assert response3.status_code == 200
                data3 = response3.json()
                
                # The response should reference the previous tasks
                response_text = data3["response"].lower()
                assert "meeting" in response_text or "slides" in response_text or "tasks" in response_text
                
            finally:
                session.close()
    
    def test_context_preservation_across_multiple_requests(self):
        """
        Test that context is preserved across multiple API requests in a conversation
        """
        # Create a test client
        client = TestClient(app)
        
        # Mock Cohere client
        with patch('backend.src.services.rag_service.cohere.Client') as mock_cohere:
            mock_instance = Mock()
            mock_response = Mock()
            mock_response.text = "I've processed your request."
            mock_instance.generate.return_value = Mock(generations=[mock_response])
            mock_cohere.return_value = mock_instance
            
            # Create a mock user in the database
            session_gen = get_session()
            session = next(session_gen)
            
            try:
                # Create a test user
                test_user = User(
                    id="test-user-789",
                    email="test3@example.com",
                    password_hash="hashed_password",
                    created_at=datetime.now()
                )
                session.add(test_user)
                session.commit()
                
                headers = {"Authorization": "Bearer fake-jwt-token"}
                
                # Start conversation to create a task
                response1 = client.post(
                    f"/api/test-user-789/chat",
                    json={
                        "message": "Create a task to call mom"
                    },
                    headers=headers
                )
                
                assert response1.status_code == 200
                data1 = response1.json()
                conversation_id = data1["conversation_id"]
                
                # Follow up with a contextual reference
                response2 = client.post(
                    f"/api/test-user-789/chat",
                    json={
                        "conversation_id": conversation_id,
                        "message": "Set a due date for that task next week"
                    },
                    headers=headers
                )
                
                assert response2.status_code == 200
                
                # Verify that the system understood the reference to the previous task
                data2 = response2.json()
                assert "call mom" in data2["response"].lower() or "task" in data2["response"].lower()
                
            finally:
                session.close()