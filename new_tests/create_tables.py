"""
Script to create database tables using SQLite
"""
import sys
import os
from sqlmodel import SQLModel, create_engine

# Use SQLite directly
DATABASE_URL = "sqlite:///./todo_app.db"

# Import models after loading environment
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend/src'))
from backend.src.models import User, Task  # noqa: E402
from backend.src.models.conversation import Conversation  # noqa: E402

def create_tables():
    print(f"Creating tables with URL: {DATABASE_URL}")

    # Create engine
    engine = create_engine(DATABASE_URL, echo=True)

    # Create all tables
    print("Creating tables...")
    SQLModel.metadata.create_all(bind=engine)
    print("Tables created successfully!")

if __name__ == "__main__":
    create_tables()