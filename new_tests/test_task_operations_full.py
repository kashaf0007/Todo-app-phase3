import requests
import json
import time
from datetime import datetime
import os

# Server configuration
BASE_URL = "http://localhost:8000"
USER_ID = "164ef148-d943-4206-89df-56b0ec6cb7fe"  # Using the actual user ID from the token

# Headers for API requests - using the actual JWT token we got from sign-in
HEADERS = {
    "Content-Type": "application/json",
    "Authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiIxNjRlZjE0OC1kOTQzLTQyMDYtODlkZi01NmIwZWM2Y2I3ZmUiLCJlbWFpbCI6InRlc3R1c2VyQGV4YW1wbGUuY29tIiwiZXhwIjoxNzY5MTY5NDg2fQ.5Fwez0VeC_P25zA-G4m3751FaOUg-Whyzhl5OPgpE2c"
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

    response = requests.post(f"{BASE_URL}/api/{USER_ID}/tasks",
                            headers=HEADERS,
                            json=task_data)

    if response.status_code == 201:
        task = response.json()
        task_id = task['id']
        print(f"[SUCCESS] Task created successfully!")
        print(f"  Task ID: {task_id}")
        print(f"  Title: {task['title']}")
        print(f"  Description: {task['description']}")
        print(f"  Priority: {task['priority']}")
        print(f"  Category: {task['category']}")
        print(f"  Due Date: {task['due_date']}")
        print(f"  Status: {task['status']}")
        print(f"  Completed: {task['completed']}")
    else:
        print(f"[ERROR] Failed to create task. Status: {response.status_code}, Response: {response.text}")
        return

    # Step 2: Update the task's status to 'In Progress'
    print(f"\n2. Updating task {task_id} status to 'IN_PROGRESS'...")
    status_update_data = {
        "title": task['title'],
        "description": task['description'],
        "status": "IN_PROGRESS",
        "priority": task['priority'],
        "category": task['category'],
        "due_date": task['due_date']
    }

    response = requests.put(f"{BASE_URL}/api/{USER_ID}/tasks/{task_id}",
                          headers=HEADERS,
                          json=status_update_data)

    if response.status_code == 200:
        updated_task = response.json()
        print(f"[SUCCESS] Task updated successfully!")
        print(f"  Task ID: {updated_task['id']}")
        print(f"  Title: {updated_task['title']}")
        print(f"  Description: {updated_task['description']}")
        print(f"  Status: {updated_task['status']}")
        print(f"  Updated At: {updated_task['updated_at']}")
    else:
        print(f"[ERROR] Failed to update task. Status: {response.status_code}, Response: {response.text}")

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
        print(f"[SUCCESS] Task marked as completed successfully!")
        print(f"  Task ID: {completed_task['id']}")
        print(f"  Title: {completed_task['title']}")
        print(f"  Completed: {completed_task['completed']}")
        print(f"  Updated At: {completed_task['updated_at']}")
    else:
        print(f"[ERROR] Failed to mark task as completed. Status: {response.status_code}, Response: {response.text}")

    # Step 4: Delete the task
    print(f"\n4. Deleting task {task_id}...")
    response = requests.delete(f"{BASE_URL}/api/{USER_ID}/tasks/{task_id}",
                              headers=HEADERS)

    if response.status_code == 204:
        print(f"[SUCCESS] Task deleted successfully!")
        print(f"  Task ID: {task_id}")
    else:
        print(f"[ERROR] Failed to delete task. Status: {response.status_code}, Response: {response.text}")

if __name__ == "__main__":
    # Give the server a moment to start if needed
    print("Running task operations test...")
    test_task_operations()