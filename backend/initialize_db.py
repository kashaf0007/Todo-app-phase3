"""
Database initialization script
Creates all required tables if they don't exist
"""
import sys
import os
from sqlmodel import SQLModel, create_engine

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.database import DATABASE_URL
from src.models import User, Task

def initialize_database():
    print(f"Initializing database with URL: {DATABASE_URL}")

    # Create engine
    engine = create_engine(DATABASE_URL, echo=True)

    # Create all tables
    print("Creating tables...")
    SQLModel.metadata.create_all(engine)
    print("Tables created successfully!")

    # Verify tables exist
    from sqlalchemy import inspect
    inspector = inspect(engine)
    table_names = inspector.get_table_names()
    print(f"Current tables in database: {table_names}")

    required_tables = ['users', 'tasks']
    missing_tables = [table for table in required_tables if table not in table_names]

    if missing_tables:
        print(f"Missing tables: {missing_tables}")
        return False
    else:
        print("All required tables exist!")
        return True

if __name__ == "__main__":
    initialize_database()