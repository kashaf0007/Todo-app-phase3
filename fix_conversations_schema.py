import os
from sqlalchemy import create_engine, text

# Get database URL from environment
database_url = os.getenv("DATABASE_URL")
if not database_url:
    print("DATABASE_URL environment variable not set!")
    exit(1)

# Create database engine
engine = create_engine(database_url)

# Script to fix the conversations table schema
with engine.connect() as conn:
    # Begin transaction
    trans = conn.begin()
    
    try:
        # Step 1: Drop the primary key constraint
        print("Dropping primary key constraint...")
        conn.execute(text("ALTER TABLE conversations DROP CONSTRAINT conversations_pkey;"))
        
        # Step 2: Drop the id column
        print("Dropping id column...")
        conn.execute(text("ALTER TABLE conversations DROP COLUMN id;"))
        
        # Step 3: Add a new auto-incrementing integer id column
        print("Adding new auto-incrementing id column...")
        conn.execute(text("ALTER TABLE conversations ADD COLUMN id SERIAL PRIMARY KEY;"))
        
        # Commit the transaction
        trans.commit()
        print("Schema updated successfully!")
        
    except Exception as e:
        # Rollback in case of error
        trans.rollback()
        print(f"Error occurred: {e}")
        print("Transaction rolled back.")