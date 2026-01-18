"""
Test script to check if the backend server can access the database properly
"""
import os
import sys
from dotenv import load_dotenv

# Load environment variables
load_dotenv(dotenv_path="backend/.env")

# Override with test values
os.environ.setdefault("DATABASE_URL", "sqlite:///./todo_app.db")
os.environ.setdefault("BETTER_AUTH_SECRET", "your-super-secret-key-for-testing-purposes-only-32chars")
os.environ.setdefault("COHERE_API_KEY", "your-cohere-api-key-here")

# Add backend src to path
sys.path.insert(0, os.path.join(os.getcwd(), 'backend', 'src'))

# Import and test the config
from backend.src.config import get_settings

try:
    settings = get_settings()
    print(f"Database URL: {settings.database_url}")
    print(f"CORS Origins: {settings.cors_origins_list}")
    print("Settings loaded successfully!")
except Exception as e:
    print(f"Error loading settings: {e}")

# Test database connection
from backend.src.database import engine
from sqlmodel import select
from backend.src.models import User

try:
    with engine.connect() as conn:
        print("Database connection successful!")
        
    # Test querying the user
    from sqlmodel import Session
    with Session(engine) as session:
        user = session.exec(select(User).where(User.id == "eb47925b-6507-466d-9a22-6057f6993734")).first()
        if user:
            print(f"Test user found: {user.email}")
        else:
            print("Test user NOT found!")
            
except Exception as e:
    print(f"Database error: {e}")