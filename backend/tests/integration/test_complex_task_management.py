"""
Integration test for complex task management in RAG Todo Chatbot
"""
import pytest
from unittest.mock import Mock, patch
from fastapi.testclient import TestClient
from backend.src.main import app
from backend.src.database import get_session
from backend.src.models.user import User
from backend.src.models.task import Task, Priority, Category
from datetime import datetime, timedelta
from sqlmodel import Session, select


class TestComplexTaskManagement:
    """
    Integration test for complex task management functionality
    """
    
    def setup_method(self):
        # Create a test client
        self.client = TestClient(app)
        
        # Mock Cohere client
        self.mock_cohere_client = Mock()
        self.mock_generate_response = Mock()
        self.mock_generate_response.text = "I've processed your request."
        self.mock_cohere_client.generate.return_value = Mock(generations=[self.mock_generate_response])
        
        # Patch the Cohere client in the RAG service
        patcher = patch('backend.src.services.rag_service.cohere.Client', return_value=self.mock_cohere_client)
        self.mock_cohere_patcher = patcher.start()
        self.addCleanup(patcher.stop)
    
    def addCleanup(self, func):
        """Helper method to simulate unittest's addCleanup"""
        import atexit
        atexit.register(func)
    
    def test_complex_task_creation_with_metadata(self):
        """
        Test creating tasks with multiple metadata fields (priority, category, due date, etc.)
        """
        # Create a mock user in the database
        session_gen = get_session()
        session = next(session_gen)
        
        try:
            # Create a test user
            test_user = User(
                id="test-user-complex-1",
                email="complex1@example.com",
                password_hash="hashed_password",
                created_at=datetime.now()
            )
            session.add(test_user)
            session.commit()
            
            headers = {"Authorization": "Bearer fake-jwt-token"}
            
            # Create a complex task with multiple attributes
            response = self.client.post(
                f"/api/test-user-complex-1/chat",
                json={
                    "message": "Add a high priority work task to prepare quarterly report due next Friday with estimated duration of 120 minutes"
                },
                headers=headers
            )
            
            assert response.status_code == 200
            response_data = response.json()
            
            # Verify the response contains appropriate acknowledgment
            assert "prepare quarterly report" in response_data["response"].lower()
            
        finally:
            session.close()
    
    def test_advanced_task_filtering_and_search(self):
        """
        Test advanced filtering capabilities (by priority, category, due date, etc.)
        """
        # Create a test client
        client = TestClient(app)
        
        # Mock Cohere client
        with patch('backend.src.services.rag_service.cohere.Client') as mock_cohere:
            mock_instance = Mock()
            mock_response = Mock()
            mock_response.text = "Here are your high priority work tasks."
            mock_instance.generate.return_value = Mock(generations=[mock_response])
            mock_cohere.return_value = mock_instance
            
            # Create a mock user in the database
            session_gen = get_session()
            session = next(session_gen)
            
            try:
                # Create a test user
                test_user = User(
                    id="test-user-complex-2",
                    email="complex2@example.com",
                    password_hash="hashed_password",
                    created_at=datetime.now()
                )
                session.add(test_user)
                session.commit()
                
                headers = {"Authorization": "Bearer fake-jwt-token"}
                
                # Request high priority work tasks
                response = client.post(
                    f"/api/test-user-complex-2/chat",
                    json={
                        "message": "Show me my high priority work tasks that are overdue"
                    },
                    headers=headers
                )
                
                assert response.status_code == 200
                response_data = response.json()
                
                # Verify the response addresses the specific request
                assert "high priority" in response_data["response"].lower() or "work" in response_data["response"].lower()
                
            finally:
                session.close()
    
    def test_task_dependency_and_relationship_management(self):
        """
        Test managing tasks that have dependencies or relationships
        """
        # Create a test client
        client = TestClient(app)
        
        # Mock Cohere client
        with patch('backend.src.services.rag_service.cohere.Client') as mock_cohere:
            mock_instance = Mock()
            mock_response = Mock()
            mock_response.text = "I've created both tasks and noted their relationship."
            mock_instance.generate.return_value = Mock(generations=[mock_response])
            mock_cohere.return_value = mock_instance
            
            # Create a mock user in the database
            session_gen = get_session()
            session = next(session_gen)
            
            try:
                # Create a test user
                test_user = User(
                    id="test-user-complex-3",
                    email="complex3@example.com",
                    password_hash="hashed_password",
                    created_at=datetime.now()
                )
                session.add(test_user)
                session.commit()
                
                headers = {"Authorization": "Bearer fake-jwt-token"}
                
                # Create related tasks
                response1 = client.post(
                    f"/api/test-user-complex-3/chat",
                    json={
                        "message": "Create a task to research vendors for the office renovation"
                    },
                    headers=headers
                )
                
                assert response1.status_code == 200
                data1 = response1.json()
                conversation_id = data1["conversation_id"]
                
                # Create dependent task
                response2 = client.post(
                    f"/api/test-user-complex-3/chat",
                    json={
                        "conversation_id": conversation_id,
                        "message": "Create a task to select a vendor based on the research, this depends on the research task"
                    },
                    headers=headers
                )
                
                assert response2.status_code == 200
                
                # Try to query about task relationships
                response3 = client.post(
                    f"/api/test-user-complex-3/chat",
                    json={
                        "conversation_id": conversation_id,
                        "message": "Which tasks are related to the office renovation?"
                    },
                    headers=headers
                )
                
                assert response3.status_code == 200
                data3 = response3.json()
                
                # The response should include information about related tasks
                assert "office renovation" in data3["response"].lower()
                
            finally:
                session.close()
    
    def test_batch_task_operations(self):
        """
        Test performing operations on multiple tasks at once
        """
        # Create a test client
        client = TestClient(app)
        
        # Mock Cohere client
        with patch('backend.src.services.rag_service.cohere.Client') as mock_cohere:
            mock_instance = Mock()
            mock_response = Mock()
            mock_response.text = "I've marked all your work tasks as complete."
            mock_instance.generate.return_value = Mock(generations=[mock_response])
            mock_cohere.return_value = mock_instance
            
            # Create a mock user in the database
            session_gen = get_session()
            session = next(session_gen)
            
            try:
                # Create a test user
                test_user = User(
                    id="test-user-complex-4",
                    email="complex4@example.com",
                    password_hash="hashed_password",
                    created_at=datetime.now()
                )
                session.add(test_user)
                session.commit()
                
                headers = {"Authorization": "Bearer fake-jwt-token"}
                
                # Create multiple tasks
                client.post(
                    f"/api/test-user-complex-4/chat",
                    json={
                        "message": "Add a task to review document A"
                    },
                    headers=headers
                )
                
                client.post(
                    f"/api/test-user-complex-4/chat",
                    json={
                        "message": "Add a task to review document B"
                    },
                    headers=headers
                )
                
                client.post(
                    f"/api/test-user-complex-4/chat",
                    json={
                        "message": "Add a task to review document C"
                    },
                    headers=headers
                )
                
                # Perform batch operation
                response = client.post(
                    f"/api/test-user-complex-4/chat",
                    json={
                        "message": "Mark all review tasks as complete"
                    },
                    headers=headers
                )
                
                assert response.status_code == 200
                response_data = response.json()
                
                # The response should acknowledge the batch operation
                assert "review" in response_data["response"].lower() or "complete" in response_data["response"].lower()
                
            finally:
                session.close()
    
    def test_task_recurrence_and_reminders(self):
        """
        Test creating recurring tasks or setting up reminders
        """
        # Create a test client
        client = TestClient(app)
        
        # Mock Cohere client
        with patch('backend.src.services.rag_service.cohere.Client') as mock_cohere:
            mock_instance = Mock()
            mock_response = Mock()
            mock_response.text = "I've set up a recurring task for your weekly team meeting."
            mock_instance.generate.return_value = Mock(generations=[mock_response])
            mock_cohere.return_value = mock_instance
            
            # Create a mock user in the database
            session_gen = get_session()
            session = next(session_gen)
            
            try:
                # Create a test user
                test_user = User(
                    id="test-user-complex-5",
                    email="complex5@example.com",
                    password_hash="hashed_password",
                    created_at=datetime.now()
                )
                session.add(test_user)
                session.commit()
                
                headers = {"Authorization": "Bearer fake-jwt-token"}
                
                # Create a recurring task
                response = client.post(
                    f"/api/test-user-complex-5/chat",
                    json={
                        "message": "Add a recurring task to attend the team meeting every Tuesday at 10am"
                    },
                    headers=headers
                )
                
                assert response.status_code == 200
                response_data = response.json()
                
                # The response should acknowledge the recurring nature
                assert "recurring" in response_data["response"].lower() or "weekly" in response_data["response"].lower()
                
            finally:
                session.close()
    
    def test_complex_task_modification(self):
        """
        Test modifying multiple aspects of a task in a single request
        """
        # Create a test client
        client = TestClient(app)
        
        # Mock Cohere client
        with patch('backend.src.services.rag_service.cohere.Client') as mock_cohere:
            mock_instance = Mock()
            mock_response = Mock()
            mock_response.text = "I've updated the task with all your requested changes."
            mock_instance.generate.return_value = Mock(generations=[mock_response])
            mock_cohere.return_value = mock_instance
            
            # Create a mock user in the database
            session_gen = get_session()
            session = next(session_gen)
            
            try:
                # Create a test user
                test_user = User(
                    id="test-user-complex-6",
                    email="complex6@example.com",
                    password_hash="hashed_password",
                    created_at=datetime.now()
                )
                session.add(test_user)
                session.commit()
                
                headers = {"Authorization": "Bearer fake-jwt-token"}
                
                # First, create a task
                response1 = client.post(
                    f"/api/test-user-complex-6/chat",
                    json={
                        "message": "Add a task to prepare presentation"
                    },
                    headers=headers
                )
                
                assert response1.status_code == 200
                data1 = response1.json()
                conversation_id = data1["conversation_id"]
                
                # Modify multiple aspects of the task
                response2 = client.post(
                    f"/api/test-user-complex-6/chat",
                    json={
                        "conversation_id": conversation_id,
                        "message": "Change the presentation task to high priority, set category to work, due date to Friday, and estimated duration to 90 minutes"
                    },
                    headers=headers
                )
                
                assert response2.status_code == 200
                response_data = response2.json()
                
                # The response should acknowledge all the changes
                assert "presentation" in response_data["response"].lower()
                
            finally:
                session.close()