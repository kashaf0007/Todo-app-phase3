"""
Test script to make a real sign-in request to check if the endpoint works
"""
import requests
import json

# Test the actual sign-in endpoint with proper headers
try:
    response = requests.post(
        "http://localhost:8000/api/auth/sign-in/email",
        headers={
            "Origin": "http://localhost:3000",
            "Content-Type": "application/json",
        },
        json={
            "email": "test@example.com",
            "password": "testpassword"
        }
    )
    
    print("Sign-in Response Status:", response.status_code)
    print("Response Headers containing 'access-control':")
    for header, value in response.headers.items():
        if "access-control" in header.lower():
            print(f"  {header}: {value}")
            
    print(f"Response Body: {response.text}")
    
except requests.exceptions.ConnectionError:
    print("Cannot connect to the backend server at http://localhost:8000")
    print("Make sure the backend server is running.")
except Exception as e:
    print(f"Error testing sign-in: {e}")