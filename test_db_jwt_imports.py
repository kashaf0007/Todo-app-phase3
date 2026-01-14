"""
Test script to check if there are issues with database session handling
"""
import sys
import os

# Add the backend/src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend', 'src'))

try:
    # Test database session
    from database import get_session
    print("+ Database session import successful")

    # Try to get a session
    session_gen = get_session()
    session = next(session_gen)
    print("+ Database session creation successful")

    # Test importing the User model
    from models.user import User
    print("+ User model import successful")

    # Test importing JWT functionality
    from jose import jwt
    print("+ JWT import successful")

    # Test importing bcrypt
    import bcrypt
    print("+ bcrypt import successful")

    print("+ All imports successful - no obvious issues with dependencies")

except Exception as e:
    print(f"- Error with imports or database: {e}")
    import traceback
    traceback.print_exc()