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

# Now import the database module to see what URL it uses
from backend.src.database import DATABASE_URL as DB_URL_IMPORTED, engine
print(f"\nDatabase URL from backend after import: {DB_URL_IMPORTED}")

# Test the connection
from sqlmodel import select
from backend.src.models import User
from backend.src.database import get_session

# Create a session and try to query
session_gen = get_session()
session = next(session_gen)

try:
    statement = select(User).where(User.id == "eb47925b-6507-466d-9a22-6057f6993734")
    result = session.exec(statement)
    user = result.first()
    
    if user:
        print(f"\nUser found in database: {user.id}, {user.email}")
    else:
        print("\nUser NOT found in database")
        
finally:
    session.close()