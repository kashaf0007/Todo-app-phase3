"""
Test script to check CORS headers properly
"""
import requests

print("Testing CORS headers...")

# Test preflight request (OPTIONS)
try:
    print("\n1. Testing OPTIONS preflight request...")
    options_response = requests.options(
        "http://localhost:8000/api/eb47925b-6507-466d-9a22-6057f6993734/tasks",
        headers={
            "Origin": "http://localhost:3000",
            "Access-Control-Request-Method": "GET",
            "Access-Control-Request-Headers": "X-Requested-With, Content-Type, Authorization"
        }
    )
    
    print(f"OPTIONS response status: {options_response.status_code}")
    
    # Check for CORS headers
    cors_headers = {}
    for header, value in options_response.headers.items():
        if 'access-control' in header.lower():
            cors_headers[header] = value
    
    print(f"CORS headers in OPTIONS response: {cors_headers}")
    
    if cors_headers and options_response.status_code == 200:
        print("✓ OPTIONS request successful with CORS headers")
    else:
        print("✗ OPTIONS request failed or missing CORS headers")
        
except Exception as e:
    print(f"Error testing OPTIONS request: {e}")

# Test actual GET request with Origin header
try:
    print("\n2. Testing GET request with Origin header...")
    get_response = requests.get(
        "http://localhost:8000/api/eb47925b-6507-466d-9a22-6057f6993734/tasks",
        headers={
            "Origin": "http://localhost:3000",
            "Content-Type": "application/json"
        }
    )
    
    print(f"GET response status: {get_response.status_code}")
    
    # Check for CORS headers in GET response
    cors_headers_get = {}
    for header, value in get_response.headers.items():
        if 'access-control' in header.lower():
            cors_headers_get[header] = value
    
    print(f"CORS headers in GET response: {cors_headers_get}")
    
    if cors_headers_get:
        print("✓ GET request has CORS headers")
    else:
        print("✗ GET request missing CORS headers")
        
    # Even if authentication fails, CORS headers should still be present
    print(f"Response body: {get_response.json() if get_response.content else 'No content'}")
        
except Exception as e:
    print(f"Error testing GET request: {e}")
    import traceback
    traceback.print_exc()

print("\n3. Summary:")
print("- If OPTIONS request returns 200 with CORS headers, preflight is working")
print("- If GET request has CORS headers even with 401/403, CORS is configured correctly")
print("- The authentication error (401/403) is expected without proper token")