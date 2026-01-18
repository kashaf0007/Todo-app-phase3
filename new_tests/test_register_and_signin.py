"""
Test script to try registering a user first, then signing in
"""
import requests
import json

# First, try to register a test user
try:
    print("Attempting to register a test user...")
    register_response = requests.post(
        "http://localhost:8000/api/auth/sign-up/email",
        headers={
            "Origin": "http://localhost:3000",
            "Content-Type": "application/json",
        },
        json={
            "email": "testuser@example.com",
            "password": "securepassword123",
            "name": "Test User"
        }
    )
    
    print("Register Response Status:", register_response.status_code)
    print("Register Response:", register_response.text)
    
    if register_response.status_code == 200:
        print("\nRegistration successful! Now trying to sign in...")
        
        # Now try to sign in with the registered user
        signin_response = requests.post(
            "http://localhost:8000/api/auth/sign-in/email",
            headers={
                "Origin": "http://localhost:3000",
                "Content-Type": "application/json",
            },
            json={
                "email": "testuser@example.com",
                "password": "securepassword123"
            }
        )
        
        print("Sign-in Response Status:", signin_response.status_code)
        print("Sign-in Response:", signin_response.text)
    else:
        print("\nRegistration failed. The sign-in will likely also fail.")
    
except requests.exceptions.ConnectionError:
    print("Cannot connect to the backend server at http://localhost:8000")
    print("Make sure the backend server is running.")
except Exception as e:
    print(f"Error testing auth endpoints: {e}")