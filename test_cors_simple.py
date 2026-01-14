"""
Simple test to check if CORS headers are present in responses
"""
import requests

# Test the actual endpoint that's having CORS issues
try:
    # First, let's try a simple OPTIONS request to check CORS preflight
    response = requests.options(
        "http://localhost:8000/api/auth/sign-in/email",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "POST",
            "Access-Control-Request-Headers": "Content-Type",
        }
    )
    
    print("OPTIONS Response Status:", response.status_code)
    print("Headers containing 'access-control':")
    for header, value in response.headers.items():
        if "access-control" in header.lower():
            print(f"  {header}: {value}")
            
    if response.status_code == 200:
        print("\nCORS preflight is working correctly!")
    else:
        print(f"\nCORS preflight failed with status: {response.status_code}")
        
except requests.exceptions.ConnectionError:
    print("Cannot connect to the backend server at http://localhost:8000")
    print("Make sure the backend server is running.")
except Exception as e:
    print(f"Error testing CORS: {e}")