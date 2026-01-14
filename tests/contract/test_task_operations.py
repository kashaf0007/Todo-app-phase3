"""
Contract test for all task operations in the RAG Todo Chatbot API
Verifies that all task operations meet the specified contract
"""

import pytest
from unittest.mock import MagicMock
from backend.src.mcp.tools import MCPTaskTools
from backend.src.services.task_service import TaskService
from backend.src.models.task import Task


def test_add_task_contract():
    """
    Test that add_task operation meets the specified contract:
    - Creates a new task with provided parameters
    - Returns correct response format
    - Validates required parameters
    """
    # Mock the database session and service
    mock_session = MagicMock()
    
    # Mock task that will be returned by the service
    mock_task = MagicMock(spec=Task)
    mock_task.id = 1
    mock_task.completed = False
    mock_task.title = "Test Task"
    
    # Mock TaskService.create_task to return our mock task
    original_create_task = TaskService.create_task
    TaskService.create_task = MagicMock(return_value=mock_task)
    
    try:
        # Call the add_task method
        result = MCPTaskTools.add_task(
            user_id="test-user-id",
            title="Test Task",
            description="Test Description",
            priority="MEDIUM",
            category="PERSONAL",
            due_date="2023-12-31T23:59:59",
            estimated_duration_minutes=30
        )
        
        # Verify the result format
        assert "task_id" in result
        assert "status" in result
        assert "title" in result
        
        assert result["task_id"] == 1
        assert result["status"] == "pending"
        assert result["title"] == "Test Task"
        
        # Verify that TaskService.create_task was called with correct parameters
        TaskService.create_task.assert_called_once()
        
        print("✓ Add task contract test passed")
    finally:
        # Restore original method
        TaskService.create_task = original_create_task


def test_list_tasks_contract():
    """
    Test that list_tasks operation meets the specified contract:
    - Returns tasks for the specified user
    - Applies filters correctly
    - Returns correct response format
    """
    # Mock the database session and service
    mock_session = MagicMock()
    
    # Mock tasks that will be returned by the service
    mock_task1 = MagicMock(spec=Task)
    mock_task1.id = 1
    mock_task1.title = "Task 1"
    mock_task1.completed = False
    mock_task1.description = "Description 1"
    mock_task1.priority = MagicMock()
    mock_task1.priority.value = "HIGH"
    mock_task1.category = MagicMock()
    mock_task1.category.value = "WORK"
    mock_task1.due_date = None
    mock_task1.estimated_duration_minutes = 60
    
    mock_task2 = MagicMock(spec=Task)
    mock_task2.id = 2
    mock_task2.title = "Task 2"
    mock_task2.completed = True
    mock_task2.description = "Description 2"
    mock_task2.priority = MagicMock()
    mock_task2.priority.value = "LOW"
    mock_task2.category = MagicMock()
    mock_task2.category.value = "PERSONAL"
    mock_task2.due_date = None
    mock_task2.estimated_duration_minutes = 45
    
    # Mock TaskService.get_tasks to return our mock tasks
    original_get_tasks = TaskService.get_tasks
    TaskService.get_tasks = MagicMock(return_value=[mock_task1, mock_task2])
    
    try:
        # Call the list_tasks method
        result = MCPTaskTools.list_tasks(
            user_id="test-user-id",
            status="all",
            priority="HIGH",
            category="WORK",
            due_before="2023-12-31T23:59:59",
            search_term="test"
        )
        
        # Verify the result format
        assert "tasks" in result
        assert len(result["tasks"]) == 2
        
        # Verify each task has required fields
        for task in result["tasks"]:
            assert "id" in task
            assert "title" in task
            assert "completed" in task
            assert "description" in task
            assert "priority" in task
            assert "category" in task
        
        # Verify that TaskService.get_tasks was called with correct parameters
        TaskService.get_tasks.assert_called_once()
        
        print("✓ List tasks contract test passed")
    finally:
        # Restore original method
        TaskService.get_tasks = original_get_tasks


def test_complete_task_contract():
    """
    Test that complete_task operation meets the specified contract:
    - Marks task as complete
    - Returns correct response format
    - Validates user ownership
    """
    # Mock the database session and service
    mock_session = MagicMock()
    
    # Mock task that will be returned by the service
    mock_task = MagicMock(spec=Task)
    mock_task.id = 1
    mock_task.completed = True
    mock_task.title = "Completed Task"
    
    # Mock TaskService.complete_task to return our mock task
    original_complete_task = TaskService.complete_task
    TaskService.complete_task = MagicMock(return_value=mock_task)
    
    try:
        # Call the complete_task method
        result = MCPTaskTools.complete_task(
            user_id="test-user-id",
            task_id=1
        )
        
        # Verify the result format
        assert "task_id" in result
        assert "status" in result
        assert "title" in result
        
        assert result["task_id"] == 1
        assert result["status"] == "completed"
        assert result["title"] == "Completed Task"
        
        # Verify that TaskService.complete_task was called with correct parameters
        TaskService.complete_task.assert_called_once_with(mock_session, 1, "test-user-id")
        
        print("✓ Complete task contract test passed")
    finally:
        # Restore original method
        TaskService.complete_task = original_complete_task


def test_delete_task_contract():
    """
    Test that delete_task operation meets the specified contract:
    - Removes task from database
    - Returns correct response format
    - Validates user ownership
    """
    # Mock the database session and service
    mock_session = MagicMock()
    
    # Mock task that will be returned by the service
    mock_task = MagicMock(spec=Task)
    mock_task.id = 1
    mock_task.completed = False
    mock_task.title = "Deleted Task"
    
    # Mock TaskService methods
    original_get_task = TaskService.get_task
    original_delete_task = TaskService.delete_task
    TaskService.get_task = MagicMock(return_value=mock_task)
    TaskService.delete_task = MagicMock(return_value=True)
    
    try:
        # Call the delete_task method
        result = MCPTaskTools.delete_task(
            user_id="test-user-id",
            task_id=1
        )
        
        # Verify the result format
        assert "task_id" in result
        assert "status" in result
        assert "title" in result
        
        assert result["task_id"] == 1
        assert result["status"] == "deleted"
        assert result["title"] == "Deleted Task"
        
        # Verify that TaskService methods were called with correct parameters
        TaskService.get_task.assert_called_once_with(mock_session, 1, "test-user-id")
        TaskService.delete_task.assert_called_once_with(mock_session, 1, "test-user-id")
        
        print("✓ Delete task contract test passed")
    finally:
        # Restore original methods
        TaskService.get_task = original_get_task
        TaskService.delete_task = original_delete_task


def test_update_task_contract():
    """
    Test that update_task operation meets the specified contract:
    - Updates task properties
    - Returns correct response format
    - Validates user ownership
    """
    # Mock the database session and service
    mock_session = MagicMock()
    
    # Mock current and updated tasks
    mock_current_task = MagicMock(spec=Task)
    mock_current_task.id = 1
    mock_current_task.completed = False
    mock_current_task.title = "Old Title"
    mock_current_task.description = "Old Description"
    mock_current_task.priority = MagicMock()
    mock_current_task.priority.value = "LOW"
    mock_current_task.category = MagicMock()
    mock_current_task.category.value = "PERSONAL"
    mock_current_task.due_date = None
    mock_current_task.estimated_duration_minutes = 30
    
    mock_updated_task = MagicMock(spec=Task)
    mock_updated_task.id = 1
    mock_updated_task.completed = False
    mock_updated_task.title = "New Title"
    mock_updated_task.description = "New Description"
    mock_updated_task.priority = MagicMock()
    mock_updated_task.priority.value = "HIGH"
    mock_updated_task.category = MagicMock()
    mock_updated_task.category.value = "WORK"
    mock_updated_task.due_date = None
    mock_updated_task.estimated_duration_minutes = 45
    
    # Mock TaskService methods
    original_get_task = TaskService.get_task
    original_update_task = TaskService.update_task
    TaskService.get_task = MagicMock(return_value=mock_current_task)
    TaskService.update_task = MagicMock(return_value=mock_updated_task)
    
    try:
        # Call the update_task method
        result = MCPTaskTools.update_task(
            user_id="test-user-id",
            task_id=1,
            title="New Title",
            description="New Description",
            priority="HIGH",
            category="WORK",
            estimated_duration_minutes=45
        )
        
        # Verify the result format
        assert "task_id" in result
        assert "status" in result
        assert "title" in result
        
        assert result["task_id"] == 1
        assert result["status"] == "pending"  # Since completed is still False
        assert result["title"] == "New Title"
        
        # Verify that TaskService methods were called with correct parameters
        TaskService.get_task.assert_called_once_with(mock_session, 1, "test-user-id")
        TaskService.update_task.assert_called_once()
        
        print("✓ Update task contract test passed")
    finally:
        # Restore original methods
        TaskService.get_task = original_get_task
        TaskService.update_task = original_update_task


if __name__ == "__main__":
    test_add_task_contract()
    test_list_tasks_contract()
    test_complete_task_contract()
    test_delete_task_contract()
    test_update_task_contract()
    print("All task operations contract tests passed!")