"""
Contract test for all task operations in RAG Todo Chatbot
"""
import pytest
from unittest.mock import Mock, patch
from backend.src.mcp.tools import MCPTaskTools
from backend.src.models.task import TaskBase
from datetime import datetime


class TestTaskOperationsContract:
    """
    Contract test for all task operations in MCP tools
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
    
    def test_add_task_contract(self):
        """
        Test that add_task method has the correct signature and behavior
        """
        # Check that the method exists
        assert hasattr(MCPTaskTools, 'add_task')
        
        # Check method signature
        import inspect
        sig = inspect.signature(MCPTaskTools.add_task)
        params = list(sig.parameters.keys())
        
        # Expected parameters: cls, user_id, title, description=None, priority=None, category=None, due_date=None, estimated_duration_minutes=None
        expected_params = ['user_id', 'title', 'description', 'priority', 'category', 'due_date', 'estimated_duration_minutes']
        assert params[1:] == expected_params  # Skip 'cls'
        
        # Check return annotation if present
        assert sig.return_annotation is dict or sig.return_annotation is inspect.Signature.empty
    
    def test_list_tasks_contract(self):
        """
        Test that list_tasks method has the correct signature and behavior
        """
        # Check that the method exists
        assert hasattr(MCPTaskTools, 'list_tasks')
        
        # Check method signature
        import inspect
        sig = inspect.signature(MCPTaskTools.list_tasks)
        params = list(sig.parameters.keys())
        
        # Expected parameters: cls, user_id, status=None, priority=None, category=None, due_before=None, search_term=None
        expected_params = ['user_id', 'status', 'priority', 'category', 'due_before', 'search_term']
        assert params[1:] == expected_params  # Skip 'cls'
        
        # Check return annotation if present
        assert sig.return_annotation is dict or sig.return_annotation is inspect.Signature.empty
    
    def test_complete_task_contract(self):
        """
        Test that complete_task method has the correct signature and behavior
        """
        # Check that the method exists
        assert hasattr(MCPTaskTools, 'complete_task')
        
        # Check method signature
        import inspect
        sig = inspect.signature(MCPTaskTools.complete_task)
        params = list(sig.parameters.keys())
        
        # Expected parameters: cls, user_id, task_id
        expected_params = ['user_id', 'task_id']
        assert params[1:] == expected_params  # Skip 'cls'
        
        # Check return annotation if present
        assert sig.return_annotation is dict or sig.return_annotation is inspect.Signature.empty
    
    def test_delete_task_contract(self):
        """
        Test that delete_task method has the correct signature and behavior
        """
        # Check that the method exists
        assert hasattr(MCPTaskTools, 'delete_task')
        
        # Check method signature
        import inspect
        sig = inspect.signature(MCPTaskTools.delete_task)
        params = list(sig.parameters.keys())
        
        # Expected parameters: cls, user_id, task_id
        expected_params = ['user_id', 'task_id']
        assert params[1:] == expected_params  # Skip 'cls'
        
        # Check return annotation if present
        assert sig.return_annotation is dict or sig.return_annotation is inspect.Signature.empty
    
    def test_update_task_contract(self):
        """
        Test that update_task method has the correct signature and behavior
        """
        # Check that the method exists
        assert hasattr(MCPTaskTools, 'update_task')
        
        # Check method signature
        import inspect
        sig = inspect.signature(MCPTaskTools.update_task)
        params = list(sig.parameters.keys())
        
        # Expected parameters: cls, user_id, task_id, title=None, description=None, priority=None, category=None, due_date=None, estimated_duration_minutes=None
        expected_params = ['user_id', 'task_id', 'title', 'description', 'priority', 'category', 'due_date', 'estimated_duration_minutes']
        assert params[1:] == expected_params  # Skip 'cls'
        
        # Check return annotation if present
        assert sig.return_annotation is dict or sig.return_annotation is inspect.Signature.empty
    
    def test_additional_task_operation_contracts(self):
        """
        Test that additional task operation methods have correct signatures
        """
        # Check list_tasks_by_priority
        assert hasattr(MCPTaskTools, 'list_tasks_by_priority')
        sig = inspect.signature(MCPTaskTools.list_tasks_by_priority)
        params = list(sig.parameters.keys())
        expected_params = ['user_id', 'priority']
        assert params[1:] == expected_params  # Skip 'cls'
        
        # Check list_tasks_by_category
        assert hasattr(MCPTaskTools, 'list_tasks_by_category')
        sig = inspect.signature(MCPTaskTools.list_tasks_by_category)
        params = list(sig.parameters.keys())
        expected_params = ['user_id', 'category']
        assert params[1:] == expected_params  # Skip 'cls'
        
        # Check list_overdue_tasks
        assert hasattr(MCPTaskTools, 'list_overdue_tasks')
        sig = inspect.signature(MCPTaskTools.list_overdue_tasks)
        params = list(sig.parameters.keys())
        expected_params = ['user_id']
        assert params[1:] == expected_params  # Skip 'cls'
    
    def test_add_task_return_format(self):
        """
        Test that add_task returns data in the expected format
        """
        # Mock the TaskService.create_task method
        with patch('backend.src.mcp.tools.TaskService') as mock_task_service:
            # Create a mock task object
            mock_task = Mock()
            mock_task.id = 123
            mock_task.completed = False
            mock_task.title = "Test Task"
            
            mock_task_service.create_task.return_value = mock_task
            
            # Call the method
            result = MCPTaskTools.add_task(
                user_id="test-user-123",
                title="Test Task",
                description="Test Description"
            )
            
            # Verify the return format
            assert isinstance(result, dict)
            assert "task_id" in result
            assert "status" in result
            assert "title" in result
            assert result["task_id"] == 123
            assert result["status"] == "pending"
            assert result["title"] == "Test Task"
    
    def test_list_tasks_return_format(self):
        """
        Test that list_tasks returns data in the expected format
        """
        # Mock the TaskService.get_tasks method
        with patch('backend.src.mcp.tools.TaskService') as mock_task_service:
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
            
            # Call the method
            result = MCPTaskTools.list_tasks(user_id="test-user-123")
            
            # Verify the return format
            assert isinstance(result, dict)
            assert "tasks" in result
            assert isinstance(result["tasks"], list)
            
            if result["tasks"]:
                task = result["tasks"][0]
                assert "id" in task
                assert "title" in task
                assert "completed" in task
                assert "description" in task
                assert "priority" in task
                assert "category" in task
                assert "due_date" in task
                assert "estimated_duration_minutes" in task
    
    def test_complete_task_return_format(self):
        """
        Test that complete_task returns data in the expected format
        """
        # Mock the TaskService.complete_task method
        with patch('backend.src.mcp.tools.TaskService') as mock_task_service:
            # Create a mock task object
            mock_task = Mock()
            mock_task.id = 123
            mock_task.completed = True
            mock_task.title = "Completed Task"
            
            mock_task_service.complete_task.return_value = mock_task
            
            # Call the method
            result = MCPTaskTools.complete_task(
                user_id="test-user-123",
                task_id=123
            )
            
            # Verify the return format
            assert isinstance(result, dict)
            assert "task_id" in result
            assert "status" in result
            assert "title" in result
            assert result["task_id"] == 123
            assert result["status"] == "completed"
            assert result["title"] == "Completed Task"
    
    def test_delete_task_return_format(self):
        """
        Test that delete_task returns data in the expected format
        """
        # Mock the TaskService.get_task and TaskService.delete_task methods
        with patch('backend.src.mcp.tools.TaskService') as mock_task_service:
            # Create a mock task object
            mock_task = Mock()
            mock_task.id = 123
            mock_task.completed = False
            mock_task.title = "Deleted Task"
            
            mock_task_service.get_task.return_value = mock_task
            mock_task_service.delete_task.return_value = True
            
            # Call the method
            result = MCPTaskTools.delete_task(
                user_id="test-user-123",
                task_id=123
            )
            
            # Verify the return format
            assert isinstance(result, dict)
            assert "task_id" in result
            assert "status" in result
            assert "title" in result
            assert result["task_id"] == 123
            assert result["status"] == "deleted"
            assert result["title"] == "Deleted Task"
    
    def test_update_task_return_format(self):
        """
        Test that update_task returns data in the expected format
        """
        # Mock the TaskService.get_task and TaskService.update_task methods
        with patch('backend.src.mcp.tools.TaskService') as mock_task_service:
            # Create a mock task object
            mock_task = Mock()
            mock_task.id = 123
            mock_task.completed = False
            mock_task.title = "Updated Task"
            
            mock_task_service.get_task.return_value = mock_task
            mock_task_service.update_task.return_value = mock_task
            
            # Call the method
            result = MCPTaskTools.update_task(
                user_id="test-user-123",
                task_id=123,
                title="Updated Task"
            )
            
            # Verify the return format
            assert isinstance(result, dict)
            assert "task_id" in result
            assert "status" in result
            assert "title" in result
            assert result["task_id"] == 123
            assert result["status"] == "pending"  # Because completed=False
            assert result["title"] == "Updated Task"