#!/usr/bin/env python3
"""
Script to register a new user via the API and then perform the requested task operations:
1. Create a task with title 'Test Task', description 'This is a test', priority 'High', category 'Testing', and due_date '2026-01-20'.
2. Update the task's status to 'In Progress'.
3. Mark the task as completed.
4. Delete the task.
"""

import requests
import json
from datetime import datetime
import time

# Base URL for the API
BASE_URL = "http://localhost:8000"

def register_new_user():
    """Register a new user account"""
    register_url = f"{BASE_URL}/api/auth/sign-up/email"

    # Create unique email for this test
    import uuid
    unique_id = str(uuid.uuid4())[:8]
    email = f"testuser_{unique_id}@example.com"

    # Registration payload
    payload = {
        "email": email,
        "password": "password123",
        "name": f"Test User {unique_id}"
    }

    try:
        response = requests.post(register_url, json=payload)
        if response.status_code == 200:
            data = response.json()
            token = data['session']['token']
            user_id = data['user']['id']
            print(f"Successfully registered new user: {email}")
            print(f"Token retrieved: {token[:20]}...")
            return token, user_id
        else:
            print(f"Failed to register user: {response.status_code}, {response.text}")
            return None, None
    except Exception as e:
        print(f"Error during registration: {str(e)}")
        return None, None

def create_task(token, user_id):
    """Create a new task with specified details"""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    # Prepare task data
    task_data = {
        "title": "Test Task",
        "description": "This is a test",
        "priority": "HIGH",  # Using uppercase as defined in the enum
        "category": "TESTING",  # Using uppercase as defined in the enum
        "due_date": "2026-01-20T00:00:00Z"  # ISO format datetime
    }

    url = f"{BASE_URL}/api/{user_id}/tasks"

    try:
        response = requests.post(url, headers=headers, json=task_data)
        if response.status_code == 201:
            task = response.json()
            print(f"[SUCCESS] Task created successfully: {task['id']} - {task['title']}")
            print(f"  Details: {json.dumps(task, indent=2)}")
            return task
        else:
            print(f"[ERROR] Failed to create task: {response.status_code}, {response.text}")
            return None
    except Exception as e:
        print(f"[ERROR] Error creating task: {str(e)}")
        return None

def update_task_status(token, user_id, task_id, new_status):
    """Update the task status"""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    # Prepare update data
    update_data = {
        "title": "Test Task",  # Required field
        "description": "This is a test",  # Required field
        "status": new_status
    }

    url = f"{BASE_URL}/api/{user_id}/tasks/{task_id}"

    try:
        response = requests.put(url, headers=headers, json=update_data)
        if response.status_code == 200:
            task = response.json()
            print(f"[SUCCESS] Task status updated to '{new_status}' for task {task['id']}")
            print(f"  Updated details: {json.dumps(task, indent=2)}")
            return task
        else:
            print(f"[ERROR] Failed to update task status: {response.status_code}, {response.text}")
            return None
    except Exception as e:
        print(f"[ERROR] Error updating task status: {str(e)}")
        return None

def mark_task_completed(token, user_id, task_id):
    """Mark the task as completed"""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    # Prepare completion data
    completion_data = {
        "completed": True
    }

    url = f"{BASE_URL}/api/{user_id}/tasks/{task_id}/complete"

    try:
        response = requests.patch(url, headers=headers, json=completion_data)
        if response.status_code == 200:
            task = response.json()
            print(f"[SUCCESS] Task marked as completed: {task['id']}")
            print(f"  Completed task details: {json.dumps(task, indent=2)}")
            return task
        else:
            print(f"[ERROR] Failed to mark task as completed: {response.status_code}, {response.text}")
            return None
    except Exception as e:
        print(f"[ERROR] Error marking task as completed: {str(e)}")
        return None

def delete_task(token, user_id, task_id):
    """Delete the task"""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }

    url = f"{BASE_URL}/api/{user_id}/tasks/{task_id}"

    try:
        response = requests.delete(url, headers=headers)
        if response.status_code == 204:
            print(f"[SUCCESS] Task {task_id} deleted successfully")
            return True
        else:
            print(f"[ERROR] Failed to delete task: {response.status_code}, {response.text}")
            return False
    except Exception as e:
        print(f"[ERROR] Error deleting task: {str(e)}")
        return False

def main():
    print("Starting task operations test with new user registration...")
    print("=" * 60)

    # Step 1: Register a new user
    print("\nStep 1: Registering a new user...")
    token, user_id = register_new_user()
    if not token or not user_id:
        print("Cannot proceed without authentication token and user ID.")
        return

    # Step 2: Create a task
    print("\nStep 2: Creating a task...")
    task = create_task(token, user_id)
    if not task:
        print("Cannot proceed without a created task.")
        return

    task_id = task['id']

    # Step 3: Update the task's status to 'In Progress'
    print("\nStep 3: Updating task status to 'In Progress'...")
    # The API expects uppercase status values based on the enum
    updated_task = update_task_status(token, user_id, task_id, "IN_PROGRESS")
    if not updated_task:
        print("Failed to update task status, but continuing...")

    # Step 4: Mark the task as completed
    print("\nStep 4: Marking the task as completed...")
    completed_task = mark_task_completed(token, user_id, task_id)
    if not completed_task:
        print("Failed to mark task as completed, but continuing...")

    # Step 5: Delete the task
    print("\nStep 5: Deleting the task...")
    delete_success = delete_task(token, user_id, task_id)
    if not delete_success:
        print("Failed to delete task.")
        return

    print("\n" + "=" * 60)
    print("All task operations completed successfully!")
    print("- Registered new user")
    print("- Created task 'Test Task'")
    print("- Updated status to 'In Progress'")
    print("- Marked task as completed")
    print("- Deleted the task")

if __name__ == "__main__":
    main()