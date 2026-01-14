"""
Test script to verify CORS configuration for Vercel frontend
"""
import requests

# Test the health endpoint to verify CORS headers
backend_url = "https://kashafaman123-todo-phase02.hf.space"

try:
    # Make a request to the health endpoint
    response = requests.options(
        f"{backend_url}/health",
        headers={
            "Origin": "https://hackathon2-phase1-five.vercel.app/docs",
            "Access-Control-Request-Method": "GET",
            "Access-Control-Request-Headers": "X-Requested-With"
        }
    )
    
    print("CORS Preflight Response Status:", response.status_code)
    print("CORS Headers:")
    for header, value in response.headers.items():
        if "access-control" in header.lower():
            print(f"  {header}: {value}")
    
    # Also test a simple GET request
    health_response = requests.get(f"{backend_url}/health")
    print(f"\nHealth Check Response: {health_response.status_code}")
    print(f"Health Check Data: {health_response.json()}")
    
    print("\nCORS configuration test completed successfully!")
    
except requests.exceptions.RequestException as e:
    print(f"Error testing backend: {e}")
    print("This could be because the Hugging Face space is not currently running.")
    print("Make sure your Hugging Face space is active before testing.")