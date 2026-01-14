"""
Script to update the database schema to add missing columns to the tasks table
"""
import sys
import os
from sqlalchemy import create_engine, text

# Add the src directory to the path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.database import DATABASE_URL

def update_schema():
    print(f"Updating database schema with URL: {DATABASE_URL}")

    # Create engine
    engine = create_engine(DATABASE_URL, echo=True)

    # Connect to the database
    with engine.connect() as conn:
        # Check if priority column exists
        result = conn.execute(text("""
            SELECT COUNT(*) 
            FROM pragma_table_info('tasks') 
            WHERE name = 'priority'
        """))
        
        if result.fetchone()[0] == 0:
            print("Adding priority column to tasks table...")
            conn.execute(text("ALTER TABLE tasks ADD COLUMN priority VARCHAR DEFAULT 'MEDIUM'"))
        
        # Check if category column exists
        result = conn.execute(text("""
            SELECT COUNT(*) 
            FROM pragma_table_info('tasks') 
            WHERE name = 'category'
        """))
        
        if result.fetchone()[0] == 0:
            print("Adding category column to tasks table...")
            conn.execute(text("ALTER TABLE tasks ADD COLUMN category VARCHAR DEFAULT 'OTHER'"))
        
        # Check if due_date column exists
        result = conn.execute(text("""
            SELECT COUNT(*) 
            FROM pragma_table_info('tasks') 
            WHERE name = 'due_date'
        """))
        
        if result.fetchone()[0] == 0:
            print("Adding due_date column to tasks table...")
            conn.execute(text("ALTER TABLE tasks ADD COLUMN due_date DATETIME"))
        
        # Check if estimated_duration_minutes column exists
        result = conn.execute(text("""
            SELECT COUNT(*) 
            FROM pragma_table_info('tasks') 
            WHERE name = 'estimated_duration_minutes'
        """))
        
        if result.fetchone()[0] == 0:
            print("Adding estimated_duration_minutes column to tasks table...")
            conn.execute(text("ALTER TABLE tasks ADD COLUMN estimated_duration_minutes INTEGER"))

        # Commit the changes
        conn.commit()
    
    print("Schema update completed!")

if __name__ == "__main__":
    update_schema()