"""
Simple test to verify the app can be imported and basic functionality works
"""
from backend.src.main import app
from fastapi.testclient import TestClient

def test_basic():
    client = TestClient(app)
    response = client.get("/health")
    print(f"Status: {response.status_code}")
    print(f"Data: {response.json()}")
    assert response.status_code == 200

if __name__ == "__main__":
    test_basic()
    print("Basic test passed!")