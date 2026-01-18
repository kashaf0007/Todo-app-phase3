"""
Test script to check if the tasks endpoint works correctly
"""
import requests
import json

# First, let's register a new test user
try:
    print("Step 1: Registering a new test user...")
    register_response = requests.post(
        "http://localhost:8000/api/auth/sign-up/email",
        headers={
            "Origin": "http://localhost:3000",
            "Content-Type": "application/json",
        },
        json={
            "email": "tasktest2@example.com",
            "password": "securepassword123",
            "name": "Task Test User 2"
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
                
                print("\nStep 4: Testing the problematic endpoint with UUID path...")
                # Test the specific endpoint that was failing
                specific_tasks_response = requests.get(
                    f"http://localhost:8000/api/{user_id}/tasks",
                    headers={
                        "Origin": "http://localhost:3000",
                        "Content-Type": "application/json",
                        "Authorization": f"Bearer {token}"
                    }
                )
                
                print("Specific Tasks Fetch Response Status:", specific_tasks_response.status_code)
                if specific_tasks_response.status_code == 200:
                    specific_tasks = specific_tasks_response.json()
                    print(f"Successfully fetched {len(specific_tasks)} tasks from specific endpoint")
                else:
                    print("Specific tasks fetch failed:", specific_tasks_response.text)
            else:
                print("Tasks fetch failed:", tasks_response.text)
        else:
            print("Task creation failed:", task_response.text)
    elif register_response.status_code == 400 and "already exists" in register_response.text:
        print("User already exists, using existing user...")
        # Try to sign in instead
        signin_response = requests.post(
            "http://localhost:8000/api/auth/sign-in/email",
            headers={
                "Origin": "http://localhost:3000",
                "Content-Type": "application/json",
            },
            json={
                "email": "tasktest2@example.com",
                "password": "securepassword123"
            }
        )
        
        if signin_response.status_code == 200:
            response_data = signin_response.json()
            user_id = response_data['user']['id']
            token = response_data['session']['token']
            print(f"Signed in successfully! User ID: {user_id}")
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
                    
                    print("\nStep 4: Testing the problematic endpoint with UUID path...")
                    # Test the specific endpoint that was failing
                    specific_tasks_response = requests.get(
                        f"http://localhost:8000/api/{user_id}/tasks",
                        headers={
                            "Origin": "http://localhost:3000",
                            "Content-Type": "application/json",
                            "Authorization": f"Bearer {token}"
                        }
                    )
                    
                    print("Specific Tasks Fetch Response Status:", specific_tasks_response.status_code)
                    if specific_tasks_response.status_code == 200:
                        specific_tasks = specific_tasks_response.json()
                        print(f"Successfully fetched {len(specific_tasks)} tasks from specific endpoint")
                    else:
                        print("Specific tasks fetch failed:", specific_tasks_response.text)
                else:
                    print("Tasks fetch failed:", tasks_response.text)
            else:
                print("Task creation failed:", task_response.text)
        else:
            print("Sign-in failed:", signin_response.text)
    else:
        print("Registration failed:", register_response.text)
    
except requests.exceptions.ConnectionError:
    print("Cannot connect to the backend server at http://localhost:8000")
    print("Make sure the backend server is running.")
except Exception as e:
    print(f"Error testing tasks endpoint: {e}")
    import traceback
    traceback.print_exc()