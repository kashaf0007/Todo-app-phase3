import os
from dotenv import load_dotenv
from jose import jwt
from datetime import datetime, timedelta

# Load environment variables
load_dotenv(dotenv_path="backend/.env")

# Get the secret
secret = os.getenv("BETTER_AUTH_SECRET")
print(f"Secret: {secret}")

# Decode the token to verify it's valid
token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJlYjQ3OTI1Yi02NTA3LTQ2NmQtOWEyMi02MDU3ZjY5OTM3MzQiLCJleHAiOjE3NjkxMTI3MzgsImlhdCI6MTc2ODUwNzkzOCwidHlwZSI6ImFjY2VzcyJ9.xkvJMR07hRRGuAFzX6MOrOi9WangYbiObO4S8hPi_3M"

try:
    payload = jwt.decode(token, secret, algorithms=["HS256"])
    print(f"Decoded payload: {payload}")
    
    # Check if the user ID is correct
    user_id = payload.get("sub")
    print(f"User ID from token: {user_id}")
    
    # Verify the token is not expired
    exp_time = datetime.fromtimestamp(payload.get("exp"))
    current_time = datetime.utcnow()
    print(f"Token expires at: {exp_time}")
    print(f"Current time: {current_time}")
    print(f"Token expired: {current_time > exp_time}")
    
except Exception as e:
    print(f"Error decoding token: {e}")