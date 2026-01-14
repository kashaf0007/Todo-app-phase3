"""
Unit tests for advanced task features
"""
import pytest
from unittest.mock import Mock, patch, MagicMock
from datetime import datetime, timedelta
from backend.src.models.task import Task, Priority, Category
from backend.src.services.task_service import TaskService
from backend.src.mcp.tools import MCPTaskTools
from sqlmodel import Session, select


def test_task_model_with_metadata():
    """
    Test that the Task model supports all new metadata fields
    """
    # Create a task with all metadata
    task = Task(
        title="Test Task",
        description="Test Description",
        user_id="test-user-123",
        priority=Priority.HIGH,
        category=Category.WORK,
        due_date=datetime.utcnow() + timedelta(days=7),
        estimated_duration_minutes=60
    )

    # Verify all fields are set correctly
    assert task.title == "Test Task"
    assert task.description == "Test Description"
    assert task.user_id == "test-user-123"
    assert task.priority == Priority.HIGH
    assert task.category == Category.WORK
    assert task.due_date is not None
    assert task.estimated_duration_minutes == 60

    print("✓ Task model with metadata fields works correctly")


def test_task_service_advanced_filters():
    """
    Test advanced filtering in TaskService
    """
    # Mock the session
    mock_session = Mock(spec=Session)
    
    # Mock the query execution
    mock_exec_result = Mock()
    mock_exec_result.all.return_value = [
        Task(id=1, title="High Priority Task", user_id="test-user", priority=Priority.HIGH),
        Task(id=2, title="Another High Priority Task", user_id="test-user", priority=Priority.HIGH)
    ]
    mock_session.exec.return_value = mock_exec_result
    
    # Test get_tasks_by_priority
    tasks = TaskService.get_tasks_by_priority(mock_session, "test-user", Priority.HIGH.value)
    
    # Verify the query was constructed correctly
    assert mock_session.exec.called
    assert len(tasks) == 2
    
    print("✓ Task service advanced filtering works correctly")


def test_mcp_tools_add_task_with_metadata():
    """
    Test MCP tools add_task with metadata
    """
    with patch('backend.src.database.get_session') as mock_get_session, \
         patch('backend.src.services.task_service.TaskService') as mock_task_service:
        
        # Setup mocks
        mock_session = Mock()
        mock_get_session.return_value.__iter__.return_value = [mock_session]
        
        mock_task = Task(
            id=1,
            title="Test Task",
            user_id="test-user",
            priority=Priority.HIGH,
            category=Category.WORK,
            due_date=datetime.utcnow()
        )
        mock_task_service.create_task.return_value = mock_task
        
        # Call the method
        result = MCPTaskTools.add_task(
            user_id="test-user",
            title="Test Task",
            priority="HIGH",
            category="WORK",
            due_date=datetime.utcnow().isoformat()
        )
        
        # Verify the result
        assert result["task_id"] == 1
        assert result["title"] == "Test Task"
        
        print("✓ MCP tools add_task with metadata works correctly")


def test_mcp_tools_update_task_with_metadata():
    """
    Test MCP tools update_task with metadata
    """
    with patch('backend.src.database.get_session') as mock_get_session, \
         patch('backend.src.services.task_service.TaskService') as mock_task_service:
        
        # Setup mocks
        mock_session = Mock()
        mock_get_session.return_value.__iter__.return_value = [mock_session]
        
        mock_task = Task(
            id=1,
            title="Updated Task",
            user_id="test-user",
            priority=Priority.LOW,
            category=Category.PERSONAL,
            due_date=datetime.utcnow()
        )
        mock_task_service.get_task.return_value = mock_task
        mock_task_service.update_task.return_value = mock_task
        
        # Call the method
        result = MCPTaskTools.update_task(
            user_id="test-user",
            task_id=1,
            title="Updated Task",
            priority="LOW",
            category="PERSONAL"
        )
        
        # Verify the result
        assert result["task_id"] == 1
        assert result["title"] == "Updated Task"
        
        print("✓ MCP tools update_task with metadata works correctly")


def test_mcp_tools_list_tasks_with_filters():
    """
    Test MCP tools list_tasks with advanced filters
    """
    with patch('backend.src.database.get_session') as mock_get_session, \
         patch('backend.src.services.task_service.TaskService') as mock_task_service:
        
        # Setup mocks
        mock_session = Mock()
        mock_get_session.return_value.__iter__.return_value = [mock_session]
        
        mock_tasks = [
            Task(
                id=1,
                title="Work Task",
                user_id="test-user",
                priority=Priority.HIGH,
                category=Category.WORK,
                due_date=datetime.utcnow()
            )
        ]
        mock_task_service.get_tasks.return_value = mock_tasks
        
        # Call the method
        result = MCPTaskTools.list_tasks(
            user_id="test-user",
            status="pending",
            priority="HIGH",
            category="WORK"
        )
        
        # Verify the result
        assert len(result["tasks"]) == 1
        assert result["tasks"][0]["id"] == 1
        assert result["tasks"][0]["priority"] == "high"
        assert result["tasks"][0]["category"] == "work"
        
        print("✓ MCP tools list_tasks with filters works correctly")


def test_task_model_enum_values():
    """
    Test that enum values are correctly handled in the Task model
    """
    # Test Priority enum
    assert Priority.HIGH.value == "high"
    assert Priority.MEDIUM.value == "medium"
    assert Priority.LOW.value == "low"
    
    # Test Category enum
    assert Category.WORK.value == "work"
    assert Category.PERSONAL.value == "personal"
    assert Category.SHOPPING.value == "shopping"
    assert Category.HEALTH.value == "health"
    assert Category.FINANCE.value == "finance"
    assert Category.OTHER.value == "other"
    
    print("✓ Task model enum values work correctly")


if __name__ == "__main__":
    test_task_model_with_metadata()
    test_task_service_advanced_filters()
    test_mcp_tools_add_task_with_metadata()
    test_mcp_tools_update_task_with_metadata()
    test_mcp_tools_list_tasks_with_filters()
    test_task_model_enum_values()
    print("All unit tests for advanced task features passed!")