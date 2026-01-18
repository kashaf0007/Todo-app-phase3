"""
Test script to check if the backend server is running and accessible
"""
import requests
import sys
import os

# Add the backend src directory to the path so we can import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend', 'src'))

def test_backend_connectivity():
    print("Testing backend connectivity...")

    # Test the health endpoint
    try:
        response = requests.get("http://localhost:8000/health")
        print(f"Health check response: {response.status_code}")
        print(f"Health check data: {response.json()}")

        if response.status_code == 200:
            print("\n[SUCCESS] Backend server is running and accessible")
        else:
            print(f"\n[ERROR] Backend server returned status code: {response.status_code}")

    except requests.exceptions.ConnectionError:
        print("\n[ERROR] Backend server is not running or not accessible at http://localhost:8000")
        print("   Please start the backend server with: uvicorn src.main:app --reload")
        return False
    except Exception as e:
        print(f"\n[ERROR] Error connecting to backend: {str(e)}")
        return False

    # Test CORS preflight request to the tasks endpoint
    try:
        preflight_response = requests.options(
            "http://localhost:8000/api/eb47925b-6507-466d-9a22-6057f6993734/tasks",
            headers={
                "Origin": "http://localhost:3000",
                "Access-Control-Request-Method": "GET",
                "Access-Control-Request-Headers": "X-Requested-With, Content-Type, Authorization"
            }
        )
        print(f"\nPreflight request to tasks endpoint: {preflight_response.status_code}")

        # Print CORS headers if present
        cors_headers = {k: v for k, v in preflight_response.headers.items() if 'access-control' in k.lower()}
        if cors_headers:
            print("CORS headers received:")
            for header, value in cors_headers.items():
                print(f"  {header}: {value}")
        else:
            print("No CORS headers received in preflight response")

    except Exception as e:
        print(f"\n[ERROR] Error with preflight request: {str(e)}")

    return True

if __name__ == "__main__":
    test_backend_connectivity()