"""
Simple test to check if the database tables exist
"""
import sys
import os

# Add the backend/src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from sqlalchemy import inspect
from src.database import engine

# Create an inspector to check the database schema
inspector = inspect(engine)

# Get table names
table_names = inspector.get_table_names()
print(f"Tables in database: {table_names}")

# Check if 'user' or 'users' table exists
if 'user' in table_names or 'users' in table_names:
    print("User table exists!")
else:
    print("User table does not exist. Need to run migrations.")

# Print all table names
for table_name in table_names:
    print(f"Table: {table_name}")
    columns = inspector.get_columns(table_name)
    for col in columns:
        print(f"  - {col['name']} ({col['type']})")