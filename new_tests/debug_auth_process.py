import os
import sys
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

print("Environment variables after loading:")
print(f"DATABASE_URL: {os.getenv('DATABASE_URL')}")
print(f"BETTER_AUTH_SECRET: {os.getenv('BETTER_AUTH_SECRET')}")

# Add backend/src to the Python path (like in start_server.py)
sys.path.insert(0, os.path.join(os.getcwd(), 'backend', 'src'))

# Import the config to see what it loads
from backend.src.config import get_settings
settings = get_settings()
print(f"\nSettings loaded:")
print(f"BETTER_AUTH_SECRET from config: {settings.better_auth_secret[:20]}...")

# Import the database module to see what URL it uses
from backend.src.database import DATABASE_URL as DB_URL_IMPORTED
print(f"Database URL from backend after import: {DB_URL_IMPORTED}")

# Test the connection
from sqlmodel import select
from backend.src.models import User
from backend.src.database import get_session

# Create a session and try to query
session_gen = get_session()
session = next(session_gen)

try:
    print("\nAttempting to query user from database...")
    statement = select(User).where(User.id == "eb47925b-6507-466d-9a22-6057f6993734")
    result = session.exec(statement)
    user = result.first()
    
    if user:
        print(f"SUCCESS: User found in database: {user.id}, {user.email}")
    else:
        print("ERROR: User NOT found in database")
        
finally:
    session.close()

# Now test JWT decoding with the token
from jose import jwt
import datetime

token = "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJlYjQ3OTI1Yi02NTA3LTQ2NmQtOWEyMi02MDU3ZjY5OTM3MzQiLCJleHAiOjE3NjkxMTI3MzgsImlhdCI6MTc2ODUwNzkzOCwidHlwZSI6ImFjY2VzcyJ9.xkvJMR07hRRGuAFzX6MOrOi9WangYbiObO4S8hPi_3M"

try:
    print(f"\nAttempting to decode JWT token...")
    payload = jwt.decode(token, settings.better_auth_secret, algorithms=["HS256"])
    print(f"Token decoded successfully: {payload}")
    
    user_id = payload.get("sub")
    print(f"User ID from token: {user_id}")
    
    # Check if this user exists in the database
    statement = select(User).where(User.id == user_id)
    result = session.exec(statement)
    user = result.first()
    
    if user:
        print(f"SUCCESS: User from token exists in database: {user.id}, {user.email}")
    else:
        print(f"ERROR: User from token does NOT exist in database: {user_id}")
        
except Exception as e:
    print(f"ERROR: Failed to decode JWT token: {e}")