"""
Test script to simulate the exact request that's failing
"""
import requests

def test_failing_request():
    print("Testing the exact failing request...")
    
    # This simulates what the browser sends as a preflight request
    print("\n1. Sending OPTIONS request (preflight)...")
    try:
        options_response = requests.options(
            "http://localhost:8000/api/eb47925b-6507-466d-9a22-6057f6993734/tasks",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "GET",
                "Access-Control-Request-Headers": "authorization,content-type",
            }
        )
        print(f"OPTIONS response status: {options_response.status_code}")
        print(f"OPTIONS response headers: {dict(options_response.headers)}")
        
        # Check for CORS headers
        cors_headers = [h for h in options_response.headers.keys() if 'access-control' in h.lower()]
        if cors_headers:
            print("CORS headers present in OPTIONS response:")
            for header in cors_headers:
                print(f"  {header}: {options_response.headers[header]}")
        else:
            print("No CORS headers in OPTIONS response")
            
    except Exception as e:
        print(f"Error with OPTIONS request: {str(e)}")
    
    print("\n2. Testing with a dummy auth token to see if that resolves the issue...")
    try:
        # Try the GET request with a dummy auth header to see if authentication is the issue
        get_response = requests.get(
            "http://localhost:8000/api/eb47925b-6507-466d-9a22-6057f6993734/tasks",
            headers={
                "Origin": "http://localhost:3000",
                "Authorization": "Bearer dummy-token"  # This will fail authentication but might help identify the issue
            }
        )
        print(f"GET response status with dummy token: {get_response.status_code}")
        print(f"GET response headers: {dict(get_response.headers)}")
    except Exception as e:
        print(f"Error with GET request: {str(e)}")

if __name__ == "__main__":
    test_failing_request()