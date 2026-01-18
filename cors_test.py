import requests

# Test the backend health endpoint to see if it's running and check CORS headers
try:
    response = requests.options('http://localhost:8000/health', 
                               headers={'Origin': 'http://localhost:3000'})
    print("OPTIONS Response Status Code:", response.status_code)
    print("Response Headers:")
    for header, value in response.headers.items():
        print(f"  {header}: {value}")
    
    # Also try a GET request
    response = requests.get('http://localhost:8000/health')
    print("\nGET Response Status Code:", response.status_code)
    print("GET Response Body:", response.json())
except Exception as e:
    print(f"Error connecting to backend: {e}")