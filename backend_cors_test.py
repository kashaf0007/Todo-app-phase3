import requests
import json

# Test the specific endpoint that's causing issues
headers = {
    'Content-Type': 'application/json',
    'Origin': 'http://localhost:3000'
}

# Try to make a request to the health endpoint first
try:
    response = requests.get('http://localhost:8000/health', headers=headers)
    print(f"Health endpoint response: {response.status_code}")
    print(f"Headers: {dict(response.headers)}")
    print(f"Body: {response.text}")
except Exception as e:
    print(f"Error reaching health endpoint: {e}")

print("\n" + "="*50 + "\n")

# Try to make a request to the chat endpoint (without authentication to see the error)
try:
    data = {"message": "test message"}
    response = requests.post('http://localhost:8000/api/test-user/chat', 
                            headers=headers, 
                            data=json.dumps(data))
    print(f"Chat endpoint response: {response.status_code}")
    print(f"Headers: {dict(response.headers)}")
    print(f"Body: {response.text}")
except Exception as e:
    print(f"Error reaching chat endpoint: {e}")