"""
Additional unit tests for RAG Todo Chatbot
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from backend.src.services.task_service import TaskService
from backend.src.services.conversation_service import ConversationService
from backend.src.services.rag_service import RAGService
from backend.src.mcp.tools import MCPTaskTools
from backend.src.models.task import Task, TaskBase, Priority, Category
from backend.src.models.conversation import Conversation
from backend.src.models.message import Message
from datetime import datetime, timedelta
from sqlmodel import Session


class TestTaskServiceUnit:
    """
    Unit tests for TaskService
    """
    
    def setup_method(self):
        self.mock_session = Mock(spec=Session)
    
    def test_create_task_success(self):
        """
        Test successful task creation
        """
        task_data = TaskBase(
            title="Test Task",
            description="Test Description",
            user_id="test-user-123"
        )
        
        with patch('backend.src.services.task_service.logger') as mock_logger:
            result = TaskService.create_task(self.mock_session, task_data)
            
            # Verify session methods were called
            self.mock_session.add.assert_called_once()
            self.mock_session.commit.assert_called_once()
            self.mock_session.refresh.assert_called_once()
            
            # Verify logger was called
            mock_logger.info.assert_called()
    
    def test_create_task_empty_title_error(self):
        """
        Test that creating a task with empty title raises an error
        """
        task_data = TaskBase(
            title="",  # Empty title
            description="Test Description",
            user_id="test-user-123"
        )
        
        with patch('backend.src.services.task_service.logger'), \
             pytest.raises(ValueError, match="Task title cannot be empty"):
            TaskService.create_task(self.mock_session, task_data)
    
    def test_get_tasks_with_filters(self):
        """
        Test retrieving tasks with various filters
        """
        with patch('backend.src.services.task_service.select') as mock_select, \
             patch('backend.src.services.task_service.logger'):
            
            # Mock the query execution
            mock_exec_result = Mock()
            mock_exec_result.all.return_value = []
            self.mock_session.exec.return_value = mock_exec_result
            
            # Test with various filters
            result = TaskService.get_tasks(
                self.mock_session,
                "test-user-123",
                status="completed",
                priority="HIGH",
                category="WORK"
            )
            
            # Verify the session.exec was called
            assert self.mock_session.exec.called
    
    def test_complete_task_success(self):
        """
        Test successful task completion
        """
        # Mock a task object
        mock_task = Mock()
        mock_task.id = 1
        mock_task.completed = False
        mock_task.user_id = "test-user-123"
        mock_task.title = "Test Task"
        
        with patch('backend.src.services.task_service.TaskService.get_task', return_value=mock_task), \
             patch('backend.src.services.task_service.logger') as mock_logger:
            
            result = TaskService.complete_task(self.mock_session, 1, "test-user-123")
            
            # Verify task properties were updated
            assert mock_task.completed is True
            assert mock_task.updated_at is not None
            
            # Verify session methods were called
            self.mock_session.add.assert_called_once_with(mock_task)
            self.mock_session.commit.assert_called_once()
            self.mock_session.refresh.assert_called_once_with(mock_task)
            
            # Verify logger was called
            mock_logger.info.assert_called()
    
    def test_complete_task_not_found(self):
        """
        Test completing a non-existent task raises an error
        """
        with patch('backend.src.services.task_service.TaskService.get_task', return_value=None), \
             pytest.raises(ValueError, match="Task with ID 999 not found for user test-user-123"):
            TaskService.complete_task(self.mock_session, 999, "test-user-123")


class TestConversationServiceUnit:
    """
    Unit tests for ConversationService
    """
    
    def setup_method(self):
        self.mock_session = Mock(spec=Session)
    
    def test_create_conversation(self):
        """
        Test creating a conversation
        """
        result = ConversationService.create_conversation(self.mock_session, "test-user-123")
        
        # Verify session methods were called
        self.mock_session.add.assert_called_once()
        self.mock_session.commit.assert_called_once()
        self.mock_session.refresh.assert_called_once()
    
    def test_add_message(self):
        """
        Test adding a message to a conversation
        """
        result = ConversationService.add_message(
            self.mock_session,
            "test-user-123",
            1,
            "user",
            "Test message content"
        )
        
        # Verify session methods were called
        self.mock_session.add.assert_called_once()
        self.mock_session.commit.assert_called_once()
        self.mock_session.refresh.assert_called_once()


class TestRAGServiceUnit:
    """
    Unit tests for RAGService
    """
    
    def setup_method(self):
        with patch('backend.src.services.rag_service.cohere.Client'):
            self.rag_service = RAGService("fake-api-key")
    
    def test_retrieve_context_empty_inputs(self):
        """
        Test retrieving context with empty inputs
        """
        result = self.rag_service.retrieve_context("user-123", "test query", [], [])
        
        # Should return an empty string or minimal context
        assert isinstance(result, str)
    
    def test_extract_task_reference_explicit_id(self):
        """
        Test extracting task reference by explicit ID
        """
        # Create mock tasks
        mock_task1 = Mock()
        mock_task1.id = 123
        mock_task1.title = "Meeting with John"
        
        mock_task2 = Mock()
        mock_task2.id = 456
        mock_task2.title = "Buy groceries"
        
        tasks = [mock_task1, mock_task2]
        
        # Test extracting by ID
        result = self.rag_service.extract_task_reference("Complete task 123", tasks)
        assert result == mock_task1
        
        result = self.rag_service.extract_task_reference("Delete task 456", tasks)
        assert result == mock_task2
    
    def test_extract_task_reference_by_title(self):
        """
        Test extracting task reference by title
        """
        # Create mock tasks
        mock_task1 = Mock()
        mock_task1.id = 123
        mock_task1.title = "Meeting with John"
        
        mock_task2 = Mock()
        mock_task2.id = 456
        mock_task2.title = "Buy groceries"
        
        tasks = [mock_task1, mock_task2]
        
        # Test extracting by title
        result = self.rag_service.extract_task_reference("Complete the meeting with John task", tasks)
        assert result == mock_task1
        
        result = self.rag_service.extract_task_reference("I need to buy groceries", tasks)
        assert result == mock_task2
    
    def test_extract_task_reference_most_recent(self):
        """
        Test extracting the most recent task when using contextual references
        """
        # Create mock tasks
        mock_task1 = Mock()
        mock_task1.id = 123
        mock_task1.title = "Old Task"
        
        mock_task2 = Mock()
        mock_task2.id = 456
        mock_task2.title = "Recent Task"
        
        tasks = [mock_task1, mock_task2]  # Recent task is last in the list
        
        # Test extracting most recent task with contextual reference
        result = self.rag_service.extract_task_reference("Complete that task", tasks)
        assert result == mock_task2  # Should return the most recent task


class TestMCPTaskToolsUnit:
    """
    Unit tests for MCPTaskTools
    """
    
    def setup_method(self):
        # Mock the database session
        self.mock_session = Mock()
        
        # Patch the get_session function to return our mock
        patcher = patch('backend.src.mcp.tools.get_session')
        self.mock_get_session = patcher.start()
        self.mock_get_session.return_value.__iter__.return_value = iter([self.mock_session])
        self.addCleanup(patcher.stop)
    
    def addCleanup(self, func):
        """Helper method to simulate unittest's addCleanup"""
        import atexit
        atexit.register(func)
    
    def test_add_task_success(self):
        """
        Test successful task addition via MCP tool
        """
        with patch('backend.src.mcp.tools.TaskService') as mock_task_service, \
             patch('backend.src.mcp.tools.logger') as mock_logger:
            
            # Create a mock task object
            mock_task = Mock()
            mock_task.id = 123
            mock_task.completed = False
            mock_task.title = "Test Task"
            
            mock_task_service.create_task.return_value = mock_task
            
            # Call the MCP tool
            result = MCPTaskTools.add_task(
                user_id="test-user-123",
                title="Test Task",
                description="Test Description"
            )
            
            # Verify the result format
            assert result["task_id"] == 123
            assert result["status"] == "pending"
            assert result["title"] == "Test Task"
            
            # Verify TaskService was called
            mock_task_service.create_task.assert_called_once()
    
    def test_list_tasks_success(self):
        """
        Test successful task listing via MCP tool
        """
        with patch('backend.src.mcp.tools.TaskService') as mock_task_service, \
             patch('backend.src.mcp.tools.logger') as mock_logger:
            
            # Create mock task objects
            mock_task1 = Mock()
            mock_task1.id = 1
            mock_task1.title = "Task 1"
            mock_task1.completed = False
            mock_task1.description = "Description 1"
            mock_task1.priority = Mock()
            mock_task1.priority.value = "high"
            mock_task1.category = Mock()
            mock_task1.category.value = "work"
            mock_task1.due_date = datetime(2023, 12, 31)
            mock_task1.estimated_duration_minutes = 60
            
            mock_tasks = [mock_task1]
            mock_task_service.get_tasks.return_value = mock_tasks
            
            # Call the MCP tool
            result = MCPTaskTools.list_tasks(user_id="test-user-123")
            
            # Verify the result format
            assert "tasks" in result
            assert len(result["tasks"]) == 1
            assert result["tasks"][0]["id"] == 1
            assert result["tasks"][0]["title"] == "Task 1"
    
    def test_complete_task_success(self):
        """
        Test successful task completion via MCP tool
        """
        with patch('backend.src.mcp.tools.TaskService') as mock_task_service, \
             patch('backend.src.mcp.tools.logger') as mock_logger:
            
            # Create a mock task object
            mock_task = Mock()
            mock_task.id = 123
            mock_task.completed = True
            mock_task.title = "Completed Task"
            
            mock_task_service.complete_task.return_value = mock_task
            
            # Call the MCP tool
            result = MCPTaskTools.complete_task(
                user_id="test-user-123",
                task_id=123
            )
            
            # Verify the result format
            assert result["task_id"] == 123
            assert result["status"] == "completed"
            assert result["title"] == "Completed Task"
            
            # Verify TaskService was called
            mock_task_service.complete_task.assert_called_once()
    
    def test_delete_task_success(self):
        """
        Test successful task deletion via MCP tool
        """
        with patch('backend.src.mcp.tools.TaskService') as mock_task_service, \
             patch('backend.src.mcp.tools.logger') as mock_logger:
            
            # Create a mock task object
            mock_task = Mock()
            mock_task.id = 123
            mock_task.completed = False
            mock_task.title = "Deleted Task"
            
            mock_task_service.get_task.return_value = mock_task
            mock_task_service.delete_task.return_value = True
            
            # Call the MCP tool
            result = MCPTaskTools.delete_task(
                user_id="test-user-123",
                task_id=123
            )
            
            # Verify the result format
            assert result["task_id"] == 123
            assert result["status"] == "deleted"
            assert result["title"] == "Deleted Task"
            
            # Verify TaskService methods were called
            mock_task_service.get_task.assert_called_once()
            mock_task_service.delete_task.assert_called_once()
    
    def test_update_task_success(self):
        """
        Test successful task update via MCP tool
        """
        with patch('backend.src.mcp.tools.TaskService') as mock_task_service, \
             patch('backend.src.mcp.tools.logger') as mock_logger:
            
            # Create a mock task object
            mock_task = Mock()
            mock_task.id = 123
            mock_task.completed = False
            mock_task.title = "Updated Task"
            
            mock_task_service.get_task.return_value = mock_task
            mock_task_service.update_task.return_value = mock_task
            
            # Call the MCP tool
            result = MCPTaskTools.update_task(
                user_id="test-user-123",
                task_id=123,
                title="Updated Task"
            )
            
            # Verify the result format
            assert result["task_id"] == 123
            assert result["status"] == "pending"  # Because completed=False
            assert result["title"] == "Updated Task"
            
            # Verify TaskService methods were called
            mock_task_service.get_task.assert_called_once()
            mock_task_service.update_task.assert_called_once()