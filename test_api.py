import os
import sys
import requests
import json

# Add backend/src to the path so we can import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend', 'src'))

# Test the API endpoint directly
def test_chat_api():
    # Use the same user ID from the error
    user_id = "3f33dd48-bd81-4952-8b2b-34ad4df751d3"
    url = f"http://localhost:8000/api/{user_id}/chat"
    
    headers = {
        "Content-Type": "application/json",
        # You might need to add authorization header depending on your setup
        # "Authorization": "Bearer YOUR_TOKEN_HERE"
    }
    
    payload = {
        "message": "Hello, this is a test message."
    }
    
    try:
        response = requests.post(url, headers=headers, json=payload)
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        
        if response.status_code == 200:
            print("Success! The API is working correctly.")
        else:
            print(f"Error: {response.status_code} - {response.text}")
            
    except requests.exceptions.ConnectionError:
        print("Connection error: Could not connect to the server. Is it running on port 8000?")
    except Exception as e:
        print(f"An error occurred: {e}")

if __name__ == "__main__":
    test_chat_api()