import requests
import json

# Test the backend API endpoint
def test_api():
    # Replace with a valid user ID for testing
    user_id = "test_user_123"

    # Test URL
    url = f"http://localhost:8000/api/{user_id}/chat"

    # Test payload
    payload = {
        "conversation_id": None,
        "message": "Hello, can you help me with my tasks?"
    }

    # Headers
    headers = {
        "Content-Type": "application/json",
        "Authorization": "Bearer your-test-token-if-needed"
    }

    try:
        print(f"Testing API endpoint: {url}")
        print(f"Payload: {json.dumps(payload, indent=2)}")

        response = requests.post(url, json=payload, headers=headers)

        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")

        if response.status_code == 200:
            print("\n[SUCCESS] API endpoint is working correctly!")
        else:
            print(f"\n[ERROR] API endpoint returned status code {response.status_code}")

    except requests.exceptions.ConnectionError:
        print("\n[ERROR] Cannot connect to the API. Is the backend server running?")
    except Exception as e:
        print(f"\n[ERROR] Error occurred: {str(e)}")

if __name__ == "__main__":
    test_api()