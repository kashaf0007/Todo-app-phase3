"""
Test script to verify CORS configuration
"""
import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend', 'src'))

from backend.src.main import app
from starlette.testclient import TestClient

# Create a test client
client = TestClient(app)

# Test CORS preflight request
response = client.options(
    "/api/auth/sign-in/email",
    headers={
        "Origin": "http://localhost:3000",
        "Access-Control-Request-Method": "POST",
        "Access-Control-Request-Headers": "Content-Type",
    },
)

print("CORS Preflight Response Status:", response.status_code)
print("CORS Headers:")
for header, value in response.headers.items():
    if "access-control" in header.lower():
        print(f"  {header}: {value}")

if response.status_code == 200:
    print("\nCORS is properly configured!")
else:
    print(f"\nCORS configuration issue. Status code: {response.status_code}")