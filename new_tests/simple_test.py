import requests
import json
import time

# Use the generated token
token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJlYjQ3OTI1Yi02NTA3LTQ2NmQtOWEyMi02MDU3ZjY5OTM3MzQiLCJleHAiOjE3NjkxNzE4MTAsImlhdCI6MTc2ODU2NzAxMCwidHlwZSI6ImFjY2VzcyJ9.Dq2Fe9Zq2YYp1OlWnIiijcfj2JbMLhyg225QVb8dcx4'

headers = {
    'Authorization': f'Bearer {token}',
    'Content-Type': 'application/json'
}

# Test the health endpoint first
print("Testing health endpoint...")
try:
    response = requests.get('http://localhost:8000/health', headers=headers)
    print('Health Status Code:', response.status_code)
    print('Health Response:', response.text)
except Exception as e:
    print('Health check failed:', str(e))

# Test the tasks endpoint
print("\nTesting tasks endpoint...")
try:
    response = requests.get('http://localhost:8000/api/eb47925b-6507-466d-9a22-6057f6993734/tasks', headers=headers)
    print('Tasks Status Code:', response.status_code)
    print('Tasks Response (first 200 chars):', response.text[:200])
except Exception as e:
    print('Tasks check failed:', str(e))

# Test the chat endpoint with a simple message
test_message = "Say hello"
data = {
    "message": test_message
}

print("\nTesting chat endpoint with message:", test_message)
try:
    response = requests.post('http://localhost:8000/api/eb47925b-6507-466d-9a22-6057f6993734/chat', headers=headers, json=data)
    print('Chat Status Code:', response.status_code)
    print('Chat Response (first 200 chars):', response.text[:200])
except Exception as e:
    print('Chat check failed:', str(e))

print("\nTest completed.")