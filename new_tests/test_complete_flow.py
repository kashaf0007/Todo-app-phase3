import requests
import json
import time

# Server configuration
BASE_URL = "http://localhost:8000"

def test_task_operations_with_new_user():
    print("Creating a new user and testing task operations...")
    
    # Step 1: Register a new user
    print("\n1. Registering a new user...")
    signup_data = {
        "email": "testuser@example.com",
        "password": "password123",
        "name": "Test User"
    }
    
    response = requests.post(f"{BASE_URL}/api/auth/sign-up/email", 
                           json=signup_data)
    
    if response.status_code == 200:
        auth_response = response.json()
        user_id = auth_response['user']['id']
        token = auth_response['session']['token']
        
        print(f"SUCCESS: User registered successfully!")
        print(f"  User ID: {user_id}")
        print(f"  Token: {token[:20]}... (truncated)")
        
        # Set up headers with the new token
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {token}"
        }
    else:
        print(f"ERROR: Failed to register user. Status: {response.status_code}, Response: {response.text}")
        return
    
    # Step 2: Create a task with title 'Test Task', description 'This is a test', 
    # priority 'High', category 'Testing', and due_date '2026-01-20'
    print(f"\n2. Creating a task for user {user_id}...")
    task_data = {
        "title": "Test Task",
        "description": "This is a test"
    }
    
    response = requests.post(f"{BASE_URL}/api/{user_id}/tasks", 
                            headers=headers, 
                            json=task_data)
    
    if response.status_code == 201:
        task = response.json()
        task_id = task['id']
        print(f"SUCCESS: Task created successfully!")
        print(f"  Task ID: {task_id}")
        print(f"  Title: {task['title']}")
        print(f"  Description: {task['description']}")
        print(f"  Completed: {task['completed']}")
        print(f"  Status: {task['status']}")
    else:
        print(f"ERROR: Failed to create task. Status: {response.status_code}, Response: {response.text}")
        return
    
    # Step 3: Update the task's status to 'In Progress'
    print(f"\n3. Updating task {task_id} status to 'IN_PROGRESS'...")
    status_update_data = {
        "title": task['title'],
        "description": task['description'],
        "status": "IN_PROGRESS"
    }
    
    response = requests.put(f"{BASE_URL}/api/{user_id}/tasks/{task_id}", 
                          headers=headers, 
                          json=status_update_data)
    
    if response.status_code == 200:
        updated_task = response.json()
        print(f"SUCCESS: Task updated successfully!")
        print(f"  Task ID: {updated_task['id']}")
        print(f"  Title: {updated_task['title']}")
        print(f"  Description: {updated_task['description']}")
        print(f"  Status: {updated_task['status']}")
        print(f"  Updated At: {updated_task['updated_at']}")
    else:
        print(f"ERROR: Failed to update task. Status: {response.status_code}, Response: {response.text}")
    
    # Step 4: Mark the task as completed
    print(f"\n4. Marking task {task_id} as completed...")
    completion_data = {
        "completed": True
    }
    
    response = requests.patch(f"{BASE_URL}/api/{user_id}/tasks/{task_id}/complete", 
                             headers=headers, 
                             json=completion_data)
    
    if response.status_code == 200:
        completed_task = response.json()
        print(f"SUCCESS: Task marked as completed successfully!")
        print(f"  Task ID: {completed_task['id']}")
        print(f"  Title: {completed_task['title']}")
        print(f"  Completed: {completed_task['completed']}")
        print(f"  Status: {completed_task['status']}")
        print(f"  Updated At: {completed_task['updated_at']}")
    else:
        print(f"ERROR: Failed to mark task as completed. Status: {response.status_code}, Response: {response.text}")
    
    # Step 5: Delete the task
    print(f"\n5. Deleting task {task_id}...")
    response = requests.delete(f"{BASE_URL}/api/{user_id}/tasks/{task_id}", 
                              headers=headers)
    
    if response.status_code == 204:
        print(f"SUCCESS: Task deleted successfully!")
        print(f"  Task ID: {task_id}")
    else:
        print(f"ERROR: Failed to delete task. Status: {response.status_code}, Response: {response.text}")

if __name__ == "__main__":
    test_task_operations_with_new_user()