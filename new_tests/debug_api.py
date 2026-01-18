import requests
import json

# Use the generated token
token = 'eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJlYjQ3OTI1Yi02NTA3LTQ2NmQtOWEyMi02MDU3ZjY5OTM3MzQiLCJleHAiOjE3NjkxNzE4MTAsImlhdCI6MTc2ODU2NzAxMCwidHlwZSI6ImFjY2VzcyJ9.Dq2Fe9Zq2YYp1OlWnIiijcfj2JbMLhyg225QVb8dcx4'

headers = {
    'Authorization': f'Bearer {token}',
    'Content-Type': 'application/json'
}

print("Testing API endpoint...")
response = requests.get('http://localhost:8000/api/eb47925b-6507-466d-9a22-6057f6993734/tasks', headers=headers)
print('Status Code:', response.status_code)
print('Response:', response.text)
print('Headers received:', dict(response.headers))