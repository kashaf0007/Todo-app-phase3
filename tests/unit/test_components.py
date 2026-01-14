"""
Unit tests for the RAG Todo Chatbot API
Testing individual components in isolation
"""

import pytest
from unittest.mock import MagicMock, patch
from backend.src.services.task_service import TaskService
from backend.src.services.rag_service import RAGService
from backend.src.mcp.tools import MCPTaskTools
from backend.src.models.task import Task, TaskBase, Priority, Category, TaskStatus


def test_task_service_create_task():
    """
    Unit test for TaskService.create_task method
    """
    # Mock session
    mock_session = MagicMock()
    
    # Create test task data
    task_data = TaskBase(
        title="Test Task",
        description="Test Description",
        user_id="test-user-id",
        priority=Priority.MEDIUM,
        category=Category.PERSONAL
    )
    
    # Mock task object that will be returned
    mock_task = MagicMock(spec=Task)
    mock_task.id = 1
    mock_task.title = "Test Task"
    mock_task.completed = False
    mock_task.user_id = "test-user-id"
    mock_task.priority = Priority.MEDIUM
    mock_task.category = Category.PERSONAL
    
    # Patch the Task constructor to return our mock
    with patch('backend.src.services.task_service.Task') as MockTask:
        MockTask.from_orm.return_value = mock_task
        MockTask.return_value = mock_task
        
        # Call the method
        result = TaskService.create_task(mock_session, task_data)
        
        # Verify the result
        assert result.id == 1
        assert result.title == "Test Task"
        assert result.user_id == "test-user-id"
        
        # Verify session methods were called
        mock_session.add.assert_called_once()
        mock_session.commit.assert_called_once()
        mock_session.refresh.assert_called_once()


def test_task_service_get_tasks():
    """
    Unit test for TaskService.get_tasks method
    """
    # Mock session
    mock_session = MagicMock()
    
    # Mock task objects
    mock_task1 = MagicMock(spec=Task)
    mock_task1.id = 1
    mock_task1.title = "Task 1"
    mock_task1.completed = False
    mock_task1.user_id = "test-user-id"
    mock_task1.priority = Priority.HIGH
    mock_task1.category = Category.WORK
    
    mock_task2 = MagicMock(spec=Task)
    mock_task2.id = 2
    mock_task2.title = "Task 2"
    mock_task2.completed = True
    mock_task2.user_id = "test-user-id"
    mock_task2.priority = Priority.LOW
    mock_task2.category = Category.PERSONAL
    
    mock_tasks = [mock_task1, mock_task2]
    
    # Mock the exec method to return our tasks
    mock_exec_result = MagicMock()
    mock_exec_result.all.return_value = mock_tasks
    mock_session.exec.return_value = mock_exec_result
    
    # Call the method
    result = TaskService.get_tasks(mock_session, "test-user-id")
    
    # Verify the result
    assert len(result) == 2
    assert result[0].id == 1
    assert result[1].id == 2
    
    # Verify session methods were called
    mock_session.exec.assert_called_once()


def test_task_service_update_task():
    """
    Unit test for TaskService.update_task method
    """
    # Mock session
    mock_session = MagicMock()
    
    # Mock current task
    mock_current_task = MagicMock(spec=Task)
    mock_current_task.id = 1
    mock_current_task.title = "Old Title"
    mock_current_task.description = "Old Description"
    mock_current_task.completed = False
    mock_current_task.user_id = "test-user-id"
    mock_current_task.priority = Priority.MEDIUM
    mock_current_task.category = Category.PERSONAL
    
    # Mock updated task
    mock_updated_task = MagicMock(spec=Task)
    mock_updated_task.id = 1
    mock_updated_task.title = "New Title"
    mock_updated_task.description = "New Description"
    mock_updated_task.completed = False
    mock_updated_task.user_id = "test-user-id"
    mock_updated_task.priority = Priority.HIGH
    mock_updated_task.category = Category.WORK
    
    # Mock the get_task method to return the current task
    with patch('backend.src.services.task_service.TaskService.get_task', return_value=mock_current_task):
        # Mock task data for update
        update_task_data = TaskBase(
            title="New Title",
            description="New Description",
            user_id="test-user-id",
            priority=Priority.HIGH,
            category=Category.WORK
        )
        
        # Call the method
        result = TaskService.update_task(mock_session, 1, "test-user-id", update_task_data)
        
        # Verify the result
        assert result.id == 1
        assert result.title == "New Title"
        assert result.description == "New Description"
        assert result.priority == Priority.HIGH
        assert result.category == Category.WORK
        
        # Verify session methods were called
        mock_session.add.assert_called_once()
        mock_session.commit.assert_called_once()
        mock_session.refresh.assert_called_once()


def test_rag_service_extract_task_reference():
    """
    Unit test for RAGService.extract_task_reference method
    """
    # Create sample tasks
    task1 = MagicMock(spec=Task)
    task1.id = 1
    task1.title = "Buy groceries"
    task1.completed = False
    
    task2 = MagicMock(spec=Task)
    task2.id = 2
    task2.title = "Walk the dog"
    task2.completed = True
    
    tasks = [task1, task2]
    
    # Initialize RAG service (we'll mock the Cohere client)
    with patch('backend.src.services.rag_service.cohere.Client'):
        rag_service = RAGService("fake-api-key")
        
        # Test exact title match
        result = rag_service.extract_task_reference("Complete the buy groceries task", tasks)
        assert result.id == 1
        assert result.title == "Buy groceries"
        
        # Test no match
        result = rag_service.extract_task_reference("Schedule a meeting", tasks)
        assert result is None
        
        # Test with "that task" reference (should return last task)
        result = rag_service.extract_task_reference("Mark that task as complete", tasks)
        assert result.id == 2  # Last task
        assert result.title == "Walk the dog"


def test_mcp_task_tools_add_task():
    """
    Unit test for MCPTaskTools.add_task method
    """
    # Mock session
    mock_session_gen = MagicMock()
    mock_session = MagicMock()
    mock_session_gen.__enter__ = MagicMock(return_value=mock_session)
    mock_session_gen.__exit__ = MagicMock(return_value=None)
    
    # Mock task service
    with patch('backend.src.mcp.tools.TaskService') as mock_task_service_class:
        # Create mock task
        mock_task = MagicMock(spec=Task)
        mock_task.id = 1
        mock_task.title = "Test Task"
        mock_task.completed = False
        
        # Configure the mock
        mock_task_service_class.create_task.return_value = mock_task
        
        # Mock the get_session generator
        with patch('backend.src.mcp.tools.get_session', return_value=mock_session_gen):
            # Call the method
            result = MCPTaskTools.add_task(
                user_id="test-user-id",
                title="Test Task",
                description="Test Description",
                priority="MEDIUM",
                category="PERSONAL"
            )
            
            # Verify the result
            assert result["task_id"] == 1
            assert result["title"] == "Test Task"
            assert result["status"] == "pending"
            
            # Verify TaskService.create_task was called
            mock_task_service_class.create_task.assert_called_once()


def test_mcp_task_tools_list_tasks():
    """
    Unit test for MCPTaskTools.list_tasks method
    """
    # Mock session
    mock_session_gen = MagicMock()
    mock_session = MagicMock()
    mock_session_gen.__enter__ = MagicMock(return_value=mock_session)
    mock_session_gen.__exit__ = MagicMock(return_value=None)
    
    # Mock tasks
    mock_task1 = MagicMock(spec=Task)
    mock_task1.id = 1
    mock_task1.title = "Task 1"
    mock_task1.completed = False
    mock_task1.description = "Description 1"
    mock_task1.priority = MagicMock()
    mock_task1.priority.value = "HIGH"
    mock_task1.category = MagicMock()
    mock_task1.category.value = "WORK"
    mock_task1.status = MagicMock()
    mock_task1.status.value = "todo"
    
    mock_task2 = MagicMock(spec=Task)
    mock_task2.id = 2
    mock_task2.title = "Task 2"
    mock_task2.completed = True
    mock_task2.description = "Description 2"
    mock_task2.priority = MagicMock()
    mock_task2.priority.value = "LOW"
    mock_task2.category = MagicMock()
    mock_task2.category.value = "PERSONAL"
    mock_task2.status = MagicMock()
    mock_task2.status.value = "done"
    
    mock_tasks = [mock_task1, mock_task2]
    
    # Mock the TaskService
    with patch('backend.src.mcp.tools.TaskService') as mock_task_service_class:
        mock_task_service_class.get_tasks.return_value = mock_tasks
        
        # Mock the get_session generator
        with patch('backend.src.mcp.tools.get_session', return_value=mock_session_gen):
            # Call the method
            result = MCPTaskTools.list_tasks(user_id="test-user-id")
            
            # Verify the result
            assert "tasks" in result
            assert len(result["tasks"]) == 2
            
            # Check first task
            assert result["tasks"][0]["id"] == 1
            assert result["tasks"][0]["title"] == "Task 1"
            assert result["tasks"][0]["completed"] == False
            assert result["tasks"][0]["priority"] == "HIGH"
            assert result["tasks"][0]["category"] == "WORK"
            assert result["tasks"][0]["status"] == "todo"
            
            # Check second task
            assert result["tasks"][1]["id"] == 2
            assert result["tasks"][1]["title"] == "Task 2"
            assert result["tasks"][1]["completed"] == True
            assert result["tasks"][1]["priority"] == "LOW"
            assert result["tasks"][1]["category"] == "PERSONAL"
            assert result["tasks"][1]["status"] == "done"
            
            # Verify TaskService.get_tasks was called
            mock_task_service_class.get_tasks.assert_called_once()


def test_mcp_task_tools_update_task():
    """
    Unit test for MCPTaskTools.update_task method
    """
    # Mock session
    mock_session_gen = MagicMock()
    mock_session = MagicMock()
    mock_session_gen.__enter__ = MagicMock(return_value=mock_session)
    mock_session_gen.__exit__ = MagicMock(return_value=None)
    
    # Mock current and updated tasks
    mock_current_task = MagicMock(spec=Task)
    mock_current_task.id = 1
    mock_current_task.title = "Old Title"
    mock_current_task.completed = False
    mock_current_task.description = "Old Description"
    mock_current_task.priority = MagicMock()
    mock_current_task.priority.value = "MEDIUM"
    mock_current_task.category = MagicMock()
    mock_current_task.category.value = "PERSONAL"
    mock_current_task.status = MagicMock()
    mock_current_task.status.value = "todo"
    
    mock_updated_task = MagicMock(spec=Task)
    mock_updated_task.id = 1
    mock_updated_task.title = "New Title"
    mock_updated_task.completed = False
    mock_updated_task.description = "New Description"
    mock_updated_task.priority = MagicMock()
    mock_updated_task.priority.value = "HIGH"
    mock_updated_task.category = MagicMock()
    mock_updated_task.category.value = "WORK"
    mock_updated_task.status = MagicMock()
    mock_updated_task.status.value = "in_progress"
    
    # Mock the TaskService
    with patch('backend.src.mcp.tools.TaskService') as mock_task_service_class:
        mock_task_service_class.get_task.return_value = mock_current_task
        mock_task_service_class.update_task.return_value = mock_updated_task
        
        # Mock the get_session generator
        with patch('backend.src.mcp.tools.get_session', return_value=mock_session_gen):
            # Call the method
            result = MCPTaskTools.update_task(
                user_id="test-user-id",
                task_id=1,
                title="New Title",
                description="New Description",
                priority="HIGH",
                category="WORK",
                status="in_progress"
            )
            
            # Verify the result
            assert result["task_id"] == 1
            assert result["title"] == "New Title"
            assert result["status"] == "pending"  # Since completed is still False
            
            # Verify TaskService methods were called
            mock_task_service_class.get_task.assert_called_once_with(mock_session, 1, "test-user-id")
            mock_task_service_class.update_task.assert_called_once()


if __name__ == "__main__":
    test_task_service_create_task()
    test_task_service_get_tasks()
    test_task_service_update_task()
    test_rag_service_extract_task_reference()
    test_mcp_task_tools_add_task()
    test_mcp_task_tools_list_tasks()
    test_mcp_task_tools_update_task()
    print("All unit tests passed!")