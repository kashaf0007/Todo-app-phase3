"""
Test script to verify the CORS and authentication fixes
"""
import requests
import json

# Test the health endpoint first
print("Testing health endpoint...")
try:
    health_response = requests.get("http://localhost:8000/health")
    print(f"Health Check Response: {health_response.status_code}")
    if health_response.status_code == 200:
        print(f"Health Check Data: {health_response.json()}")
    else:
        print(f"Health Check Error: {health_response.text}")
except Exception as e:
    print(f"Error testing health endpoint: {e}")

print("\nTesting tasks endpoint without authentication (should return 401/403, not 500)...")

# Test the tasks endpoint without authentication - should return 401/403, not 500
try:
    tasks_response = requests.get(
        "http://localhost:8000/api/eb47925b-6507-466d-9a22-6057f6993734/tasks",
        headers={
            "Origin": "http://localhost:3000",
            "Content-Type": "application/json",
        }
    )

    print(f"Tasks endpoint response status: {tasks_response.status_code}")
    if tasks_response.status_code in [401, 403]:
        print(f"SUCCESS: Correctly returns {tasks_response.status_code} (instead of 500 error)")
        print(f"Response: {tasks_response.json()}")
    elif tasks_response.status_code == 500:
        print("FAILURE: Still returns 500 Internal Server Error - fix didn't work")
        print(f"Response: {tasks_response.text}")
    else:
        print(f"Different status code: {tasks_response.status_code}")
        print(f"Response: {tasks_response.text}")

except requests.exceptions.ConnectionError:
    print("Cannot connect to the backend server at http://localhost:8000")
    print("Make sure the backend server is running.")
except Exception as e:
    print(f"Error testing tasks endpoint: {e}")
    import traceback
    traceback.print_exc()

print("\nTesting CORS preflight request...")

# Test CORS preflight request
try:
    cors_response = requests.options(
        "http://localhost:8000/api/eb47925b-6507-466d-9a22-6057f6993734/tasks",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "GET",
            "Access-Control-Request-Headers": "X-Requested-With, Authorization"
        }
    )

    print(f"CORS preflight response status: {cors_response.status_code}")
    cors_headers = {k: v for k, v in cors_response.headers.items() if 'access-control' in k.lower()}
    print(f"CORS headers: {cors_headers}")

    if cors_response.status_code == 200 and cors_headers:
        print("SUCCESS: CORS preflight request successful")
    else:
        print("FAILURE: CORS preflight request failed")

except Exception as e:
    print(f"Error testing CORS: {e}")
    import traceback
    traceback.print_exc()