"""
Test script to check if the tasks endpoint works correctly
"""
import requests
import json

# First, let's register a user
try:
    print("Step 1: Registering a test user...")
    register_response = requests.post(
        "http://localhost:8000/api/auth/sign-up/email",
        headers={
            "Origin": "http://localhost:3000",
            "Content-Type": "application/json",
        },
        json={
            "email": "tasktest@example.com",
            "password": "securepassword123",
            "name": "Task Test User"
        }
    )
    
    print("Register Response Status:", register_response.status_code)
    if register_response.status_code == 200:
        response_data = register_response.json()
        user_id = response_data['user']['id']
        token = response_data['session']['token']
        print(f"User registered successfully! User ID: {user_id}")
        print(f"Token: {token[:20]}...")  # Show only first 20 chars of token
        
        print("\nStep 2: Creating a test task...")
        # Create a test task
        task_response = requests.post(
            f"http://localhost:8000/api/{user_id}/tasks",
            headers={
                "Origin": "http://localhost:3000",
                "Content-Type": "application/json",
                "Authorization": f"Bearer {token}"  # Include the token
            },
            json={
                "title": "Test Task",
                "description": "This is a test task"
            }
        )
        
        print("Task Creation Response Status:", task_response.status_code)
        if task_response.status_code == 201:
            task_data = task_response.json()
            task_id = task_data['id']
            print(f"Task created successfully! Task ID: {task_id}")
            
            print("\nStep 3: Fetching tasks for the user...")
            # Now try to fetch tasks for this user
            tasks_response = requests.get(
                f"http://localhost:8000/api/{user_id}/tasks",
                headers={
                    "Origin": "http://localhost:3000",
                    "Content-Type": "application/json",
                    "Authorization": f"Bearer {token}"  # Include the token
                }
            )
            
            print("Tasks Fetch Response Status:", tasks_response.status_code)
            if tasks_response.status_code == 200:
                tasks = tasks_response.json()
                print(f"Successfully fetched {len(tasks)} tasks")
                print("Tasks:", json.dumps(tasks, indent=2))
            else:
                print("Tasks fetch failed:", tasks_response.text)
        else:
            print("Task creation failed:", task_response.text)
    else:
        print("Registration failed:", register_response.text)
    
except requests.exceptions.ConnectionError:
    print("Cannot connect to the backend server at http://localhost:8000")
    print("Make sure the backend server is running.")
except Exception as e:
    print(f"Error testing tasks endpoint: {e}")
    import traceback
    traceback.print_exc()