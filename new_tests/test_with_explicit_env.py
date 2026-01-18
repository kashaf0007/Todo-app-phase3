import os
import subprocess
import sys

# Set the environment variable explicitly before importing anything
os.environ["DATABASE_URL"] = "sqlite:///./todo_app.db"
os.environ["BETTER_AUTH_SECRET"] = "supersecretkeyformyappthatisatleast32characterslong"

# Add backend/src to the Python path
sys.path.insert(0, os.path.join(os.getcwd(), 'backend', 'src'))

# Now import and test
from backend.src.database import DATABASE_URL as db_url
print(f"Database URL after explicit setting: {db_url}")

# Test the connection
from sqlmodel import select
from backend.src.models import User
from backend.src.database import get_session

# Create a session and try to query
session_gen = get_session()
session = next(session_gen)

try:
    print("Attempting to query user from database...")
    statement = select(User).where(User.id == "eb47925b-6507-466d-9a22-6057f6993734")
    result = session.exec(statement)
    user = result.first()
    
    if user:
        print(f"SUCCESS: User found in database: {user.id}, {user.email}")
    else:
        print("ERROR: User NOT found in database")
        
finally:
    session.close()