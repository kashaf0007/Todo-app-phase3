"""
Script to generate a JWT token for the test user
"""
import os
from datetime import datetime, timedelta
from jose import jwt
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(dotenv_path="backend/.env")

# Load the secret from environment
secret = os.getenv("BETTER_AUTH_SECRET", "your-super-secret-key-for-testing-purposes-only-32chars")

# Create a JWT token for the test user
payload = {
    "sub": "eb47925b-6507-466d-9a22-6057f6993734",  # User ID
    "exp": datetime.utcnow() + timedelta(days=7),  # Token expires in 7 days
    "iat": datetime.utcnow(),  # Issued at
    "type": "access"  # Token type
}

token = jwt.encode(payload, secret, algorithm="HS256")
print("JWT Token for test user:")
print(token)
print("\nUse this token in your Authorization header as: Bearer <token>")