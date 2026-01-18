import requests
import json
import time

# Use the generated token
token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJlYjQ3OTI1Yi02NTA3LTQ2NmQtOWEyMi02MDU3ZjY5OTM3MzQiLCJleHAiOjE3NjkxNzE4MTAsImlhdCI6MTc2ODU2NzAxMCwidHlwZSI6ImFjY2VzcyJ9.Dq2Fe9Zq2YYp1OlWnIiijcfj2JbMLhyg225QVb8dcx4'

headers = {
    'Authorization': f'Bearer {token}',
    'Content-Type': 'application/json'
}

# Test the chat endpoint with a message that should trigger the add_task MCP tool
test_message = "Add a new task to buy groceries"

data = {
    "message": test_message
}

print("Testing chat endpoint with message:", test_message)
response = requests.post('http://localhost:8000/api/eb47925b-6507-466d-9a22-6057f6993734/chat', headers=headers, json=data)
print('Status Code:', response.status_code)
print('Response:', response.text)

# Wait a bit to ensure the task was processed
time.sleep(1)

# Now test the list tasks endpoint to see if the task was added
print("\nTesting list tasks endpoint...")
response = requests.get('http://localhost:8000/api/eb47925b-6507-466d-9a22-6057f6993734/tasks', headers=headers)
print('Status Code:', response.status_code)
print('Response:', response.text)

# Test another message that should trigger list_tasks
test_message2 = "Show me my tasks"
data2 = {
    "message": test_message2
}

print("\nTesting chat endpoint with message:", test_message2)
response = requests.post('http://localhost:8000/api/eb47925b-6507-466d-9a22-6057f6993734/chat', headers=headers, json=data2)
print('Status Code:', response.status_code)
print('Response:', response.text)