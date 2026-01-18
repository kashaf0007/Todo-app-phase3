import os
import sys
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv(dotenv_path="backend/.env")

# Add backend/src to the Python path
sys.path.insert(0, os.path.join(os.getcwd(), 'backend', 'src'))

from backend.src.database import get_session
from backend.src.models import User
from sqlmodel import select

print("Testing database connection...")

try:
    # Create a session and try to query the user
    session_gen = get_session()
    session = next(session_gen)

    try:
        print("Session created successfully")

        # Try to find the user with the specific UUID
        user_id = "eb47925b-6507-466d-9a22-6057f6993734"
        user = session.exec(select(User).where(User.id == user_id)).first()

        if user:
            print(f"Found user: {user.id}, {user.email}")
        else:
            print(f"User with ID {user_id} not found in database")

        # Also try to count all users
        all_users = session.exec(select(User)).all()
        print(f"Total users in database: {len(all_users)}")

    finally:
        # Close the session
        next(session_gen, None)

except Exception as e:
    print(f"Database query error: {e}")
    import traceback
    traceback.print_exc()