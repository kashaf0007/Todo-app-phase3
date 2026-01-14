"""
Test script to register a user and get a valid user ID
"""
import requests
import json
import time

print("Testing user registration and authentication flow...")

# Register a new user with a unique email
unique_email = f"testuser_{int(time.time())}@example.com"
print(f"Using unique email: {unique_email}")

try:
    print("\n1. Registering a new user...")
    register_response = requests.post(
        "http://localhost:8000/api/auth/sign-up/email",
        headers={
            "Content-Type": "application/json",
        },
        json={
            "email": unique_email,
            "password": "securepassword123",
            "name": "Test User"
        }
    )

    print(f"Registration response status: {register_response.status_code}")
    if register_response.status_code == 200:
        response_data = register_response.json()
        user_id = response_data['user']['id']
        token = response_data['session']['token']
        print(f"SUCCESS: User registered successfully!")
        print(f"User ID: {user_id}")
        print(f"Token: {token[:20]}...")  # Show only first 20 chars of token

        print("\n2. Testing tasks endpoint with valid token...")
        # Test the tasks endpoint with the valid token
        tasks_response = requests.get(
            f"http://localhost:8000/api/{user_id}/tasks",
            headers={
                "Content-Type": "application/json",
                "Authorization": f"Bearer {token}"
            }
        )

        print(f"Tasks endpoint response status: {tasks_response.status_code}")
        if tasks_response.status_code == 200:
            tasks = tasks_response.json()
            print(f"SUCCESS: Successfully fetched {len(tasks)} tasks")
            if tasks:
                print("Sample task:", json.dumps(tasks[0], indent=2, default=str))
        else:
            print(f"FAILURE: Tasks endpoint failed with status {tasks_response.status_code}")
            print(f"Response: {tasks_response.text}")

    else:
        print(f"FAILURE: Registration failed with status {register_response.status_code}")
        print(f"Response: {register_response.text}")

except requests.exceptions.ConnectionError:
    print("FAILURE: Cannot connect to the backend server at http://localhost:8000")
    print("Make sure the backend server is running.")
except Exception as e:
    print(f"FAILURE: Error testing authentication flow: {e}")
    import traceback
    traceback.print_exc()