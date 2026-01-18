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
        "description": "This is a test"
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
        print(f"  Completed: {task['completed']}")
        print(f"  Status: {task['status']}")
    else:
        print(f"✗ Failed to create task. Status: {response.status_code}, Response: {response.text}")
        return
    
    # Step 2: Update the task's status to 'In Progress'
    print(f"\n2. Updating task {task_id} status to 'IN_PROGRESS'...")
    status_update_data = {
        "title": task['title'],
        "description": task['description'],
        "status": "IN_PROGRESS"
    }
    
    response = requests.put(f"{BASE_URL}/api/{USER_ID}/tasks/{task_id}", 
                          headers=HEADERS, 
                          json=status_update_data)
    
    if response.status_code == 200:
        updated_task = response.json()
        print(f"✓ Task updated successfully!")
        print(f"  Task ID: {updated_task['id']}")
        print(f"  Title: {updated_task['title']}")
        print(f"  Description: {updated_task['description']}")
        print(f"  Status: {updated_task['status']}")
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
        print(f"  Status: {completed_task['status']}")
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