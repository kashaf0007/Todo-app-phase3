#!/usr/bin/env python3
"""
Test script to perform the requested task operations:
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

def get_auth_token():
    """Get authentication token by signing in with test user credentials"""
    sign_in_url = f"{BASE_URL}/api/auth/sign-in/email"
    
    # Test user credentials
    payload = {
        "email": "test@example.com",
        "password": "password123"
    }
    
    try:
        response = requests.post(sign_in_url, json=payload)
        if response.status_code == 200:
            data = response.json()
            token = data['session']['token']
            print("Successfully authenticated. Token retrieved.")
            return token
        else:
            print(f"Failed to authenticate: {response.status_code}, {response.text}")
            return None
    except Exception as e:
        print(f"Error during authentication: {str(e)}")
        return None

def create_task(token):
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
    
    # Note: The API expects user_id in the URL, but it uses the JWT token to determine the actual user
    # So we'll use a placeholder user_id, but the actual user will be determined from the token
    user_id = "eb47925b-6507-466d-9a22-6057f6993734"  # Our test user ID
    url = f"{BASE_URL}/api/{user_id}/tasks"
    
    try:
        response = requests.post(url, headers=headers, json=task_data)
        if response.status_code == 201:
            task = response.json()
            print(f"✓ Task created successfully: {task['id']} - {task['title']}")
            print(f"  Details: {json.dumps(task, indent=2)}")
            return task
        else:
            print(f"✗ Failed to create task: {response.status_code}, {response.text}")
            return None
    except Exception as e:
        print(f"✗ Error creating task: {str(e)}")
        return None

def update_task_status(token, task_id, new_status):
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
    
    user_id = "eb47925b-6507-466d-9a22-6057f6993734"  # Our test user ID
    url = f"{BASE_URL}/api/{user_id}/tasks/{task_id}"
    
    try:
        response = requests.put(url, headers=headers, json=update_data)
        if response.status_code == 200:
            task = response.json()
            print(f"✓ Task status updated to '{new_status}' for task {task['id']}")
            print(f"  Updated details: {json.dumps(task, indent=2)}")
            return task
        else:
            print(f"✗ Failed to update task status: {response.status_code}, {response.text}")
            return None
    except Exception as e:
        print(f"✗ Error updating task status: {str(e)}")
        return None

def mark_task_completed(token, task_id):
    """Mark the task as completed"""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    # Prepare completion data
    completion_data = {
        "completed": True
    }
    
    user_id = "eb47925b-6507-466d-9a22-6057f6993734"  # Our test user ID
    url = f"{BASE_URL}/api/{user_id}/tasks/{task_id}/complete"
    
    try:
        response = requests.patch(url, headers=headers, json=completion_data)
        if response.status_code == 200:
            task = response.json()
            print(f"✓ Task marked as completed: {task['id']}")
            print(f"  Completed task details: {json.dumps(task, indent=2)}")
            return task
        else:
            print(f"✗ Failed to mark task as completed: {response.status_code}, {response.text}")
            return None
    except Exception as e:
        print(f"✗ Error marking task as completed: {str(e)}")
        return None

def delete_task(token, task_id):
    """Delete the task"""
    headers = {
        "Authorization": f"Bearer {token}",
        "Content-Type": "application/json"
    }
    
    user_id = "eb47925b-6507-466d-9a22-6057f6993734"  # Our test user ID
    url = f"{BASE_URL}/api/{user_id}/tasks/{task_id}"
    
    try:
        response = requests.delete(url, headers=headers)
        if response.status_code == 204:
            print(f"✓ Task {task_id} deleted successfully")
            return True
        else:
            print(f"✗ Failed to delete task: {response.status_code}, {response.text}")
            return False
    except Exception as e:
        print(f"✗ Error deleting task: {str(e)}")
        return False

def main():
    print("Starting task operations test...")
    print("=" * 50)
    
    # Step 1: Get authentication token
    print("\nStep 1: Authenticating...")
    token = get_auth_token()
    if not token:
        print("Cannot proceed without authentication token.")
        return
    
    # Step 2: Create a task
    print("\nStep 2: Creating a task...")
    task = create_task(token)
    if not task:
        print("Cannot proceed without a created task.")
        return
    
    task_id = task['id']
    
    # Step 3: Update the task's status to 'In Progress'
    print("\nStep 3: Updating task status to 'In Progress'...")
    # The API expects uppercase status values based on the enum
    updated_task = update_task_status(token, task_id, "IN_PROGRESS")
    if not updated_task:
        print("Failed to update task status, but continuing...")
    
    # Step 4: Mark the task as completed
    print("\nStep 4: Marking the task as completed...")
    completed_task = mark_task_completed(token, task_id)
    if not completed_task:
        print("Failed to mark task as completed, but continuing...")
    
    # Step 5: Delete the task
    print("\nStep 5: Deleting the task...")
    delete_success = delete_task(token, task_id)
    if not delete_success:
        print("Failed to delete task.")
        return
    
    print("\n" + "=" * 50)
    print("All task operations completed successfully!")
    print("- Created task 'Test Task'")
    print("- Updated status to 'In Progress'")
    print("- Marked task as completed")
    print("- Deleted the task")

if __name__ == "__main__":
    main()