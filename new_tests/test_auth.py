"""
Test script to verify JWT authentication works correctly
"""
import os
from jose import jwt
from datetime import datetime, timedelta
from sqlmodel import Session, create_engine, select
from backend.src.models import User

# Set the environment variables
os.environ["DATABASE_URL"] = "sqlite:///./todo_app.db"
os.environ["BETTER_AUTH_SECRET"] = "your-super-secret-key-for-testing-purposes-only-32chars"

# Import after setting environment
from backend.src.database import DATABASE_URL, engine

# Create a JWT token for the test user
secret = os.environ["BETTER_AUTH_SECRET"]
payload = {
    "sub": "eb47925b-6507-466d-9a22-6057f6993734",  # User ID
    "exp": datetime.utcnow() + timedelta(days=7),  # Token expires in 7 days
    "iat": datetime.utcnow(),  # Issued at
    "type": "access"  # Token type
}

token = jwt.encode(payload, secret, algorithm="HS256")
print(f"Generated token: {token}")

# Verify the token can be decoded
try:
    decoded_payload = jwt.decode(token, secret, algorithms=["HS256"])
    print(f"Token decoded successfully: {decoded_payload}")
    
    # Verify user exists in DB
    session = Session(engine)
    user = session.exec(select(User).where(User.id == decoded_payload["sub"])).first()
    if user:
        print(f"User found in database: {user.id}, {user.email}")
    else:
        print("User NOT found in database!")
    session.close()
    
except Exception as e:
    print(f"Error decoding token: {e}")