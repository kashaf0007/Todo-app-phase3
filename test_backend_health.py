"""
Test script to make a request to the backend to see if environment variables are loaded correctly
"""
import requests

try:
    # Test the health endpoint
    response = requests.get("http://localhost:8000/health")
    
    print("Health Check Response Status:", response.status_code)
    print("Health Check Response:", response.json())
    
    # Also try to make a simple GET request to see if we get a 500 error
    response2 = requests.get("http://localhost:8000/")
    
    print("\nRoot Endpoint Response Status:", response2.status_code)
    print("Root Endpoint Response:", response2.json() if response2.status_code == 200 else response2.text)
    
except requests.exceptions.ConnectionError:
    print("Cannot connect to the backend server at http://localhost:8000")
    print("Make sure the backend server is running.")
except Exception as e:
    print(f"Error testing endpoints: {e}")