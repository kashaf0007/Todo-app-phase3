import requests
import json
import time
from datetime import datetime
import os

# Server configuration
BASE_URL = "http://localhost:8000"
USER_ID = "test-user-123"  # Using a test user ID

# Headers for API requests
HEADERS = {
    "Content-Type": "application/json",
    "Authorization": "Bearer fake-token-for-testing"  # Using a fake token since we're testing
}

def test_task_operations():
    print("Starting task operations test...")
    
    # Step 1: Create a task with title 'Test Task', description 'This is a test', 
    # priority 'High', category 'Testing', and due_date '2026-01-20'
    print("\n1. Creating a task...")
    task_data = {
        "title": "Test Task",
        "description": "This is a test",
        "priority": "HIGH",
        "category": "TESTING",
        "due_date": "2026-01-20T00:00:00Z"
    }
    
    # Since the API ignores the user_id in the path and gets it from JWT, we'll use a placeholder
    response = requests.post(f"{BASE_URL}/api/{USER_ID}/tasks", 
                            headers=HEADERS, 
                            json=task_data)
    
    if response.status_code == 201:
        task = response.json()
        task_id = task['id']
        print(f"✓ Task created successfully!")
        print(f"  Task ID: {task_id}")
        print(f"  Title: {task['title']}")
        print(f"  Description: {task['description']}")
        print(f"  Priority: {task['priority']}")
        print(f"  Category: {task['category']}")
        print(f"  Due Date: {task['due_date']}")
        print(f"  Status: {task['status']}")
        print(f"  Completed: {task['completed']}")
    else:
        print(f"✗ Failed to create task. Status: {response.status_code}, Response: {response.text}")
        return
    
    # Step 2: Update the task's status to 'In Progress'
    print(f"\n2. Updating task {task_id} status to 'IN PROGRESS'...")
    status_update_data = {
        "title": task['title'],
        "description": task['description']
    }
    
    # First, we need to update the task to change its status
    # Actually, looking at the API, there's no direct way to update just the status
    # The status field is not in the TaskUpdate model, so we need to update the task
    # using PUT which updates title and description but doesn't change status
    # Let me check if we can update the status through the PUT endpoint
    
    # Actually, looking more carefully at the models, I see that status is part of the Task model
    # but it's not part of the TaskUpdate model. Let me check if there's a specific endpoint
    # for updating status
    
    # Looking at the routes again, I see that status is part of the Task model but not exposed
    # in the TaskUpdate model. Let me see if there's a way to update just the status.
    # Actually, I think I need to use the PUT endpoint but include the status field.
    # But the TaskUpdate model doesn't include status.
    
    # Let me try to update the task with the same data but with status changed to IN_PROGRESS
    # Actually, I need to use the PATCH endpoint for completion, but there isn't one for status
    # Let me check if I can update the status through the PUT endpoint by extending the payload
    
    # Based on the API, I need to use PUT to update the task, but the TaskUpdate model
    # doesn't include status. So I'll need to update title/description and somehow change status
    # Actually, looking again, there might be an issue with the API design here.
    
    # Let me try to update the task title to trigger an update, though I can't change status
    # through the current API design based on the TaskUpdate model
    print("Note: The current API doesn't seem to have a direct way to update just the status field.")
    print("The TaskUpdate model only includes title and description.")
    print("For this test, I'll update the title to trigger an update.")
    
    update_data = {
        "title": "Test Task - Updated",
        "description": "This is a test"
    }
    
    response = requests.put(f"{BASE_URL}/api/{USER_ID}/tasks/{task_id}", 
                          headers=HEADERS, 
                          json=update_data)
    
    if response.status_code == 200:
        updated_task = response.json()
        print(f"✓ Task updated successfully!")
        print(f"  Task ID: {updated_task['id']}")
        print(f"  Title: {updated_task['title']}")
        print(f"  Description: {updated_task['description']}")
        print(f"  Status: {updated_task['status']} (unchanged due to API limitations)")
        print(f"  Updated At: {updated_task['updated_at']}")
    else:
        print(f"✗ Failed to update task. Status: {response.status_code}, Response: {response.text}")
    
    # Step 3: Mark the task as completed
    print(f"\n3. Marking task {task_id} as completed...")
    completion_data = {
        "completed": True
    }
    
    response = requests.patch(f"{BASE_URL}/api/{USER_ID}/tasks/{task_id}/complete", 
                             headers=HEADERS, 
                             json=completion_data)
    
    if response.status_code == 200:
        completed_task = response.json()
        print(f"✓ Task marked as completed successfully!")
        print(f"  Task ID: {completed_task['id']}")
        print(f"  Title: {completed_task['title']}")
        print(f"  Completed: {completed_task['completed']}")
        print(f"  Updated At: {completed_task['updated_at']}")
    else:
        print(f"✗ Failed to mark task as completed. Status: {response.status_code}, Response: {response.text}")
    
    # Step 4: Delete the task
    print(f"\n4. Deleting task {task_id}...")
    response = requests.delete(f"{BASE_URL}/api/{USER_ID}/tasks/{task_id}", 
                              headers=HEADERS)
    
    if response.status_code == 204:
        print(f"✓ Task deleted successfully!")
        print(f"  Task ID: {task_id}")
    else:
        print(f"✗ Failed to delete task. Status: {response.status_code}, Response: {response.text}")

if __name__ == "__main__":
    # Give the server a moment to start
    print("Waiting for server to start...")
    time.sleep(5)
    
    test_task_operations()