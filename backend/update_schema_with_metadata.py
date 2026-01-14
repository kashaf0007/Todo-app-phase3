"""
Script to update the database schema to add new metadata columns to the tasks table
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
        # Check if status column exists
        result = conn.execute(text("""
            SELECT COUNT(*) 
            FROM pragma_table_info('tasks') 
            WHERE name = 'status'
        """))
        
        if result.fetchone()[0] == 0:
            print("Adding status column to tasks table...")
            conn.execute(text("ALTER TABLE tasks ADD COLUMN status VARCHAR DEFAULT 'todo'"))
        
        # Check if actual_duration_minutes column exists
        result = conn.execute(text("""
            SELECT COUNT(*) 
            FROM pragma_table_info('tasks') 
            WHERE name = 'actual_duration_minutes'
        """))
        
        if result.fetchone()[0] == 0:
            print("Adding actual_duration_minutes column to tasks table...")
            conn.execute(text("ALTER TABLE tasks ADD COLUMN actual_duration_minutes INTEGER"))
        
        # Check if tags column exists
        result = conn.execute(text("""
            SELECT COUNT(*) 
            FROM pragma_table_info('tasks') 
            WHERE name = 'tags'
        """))
        
        if result.fetchone()[0] == 0:
            print("Adding tags column to tasks table...")
            conn.execute(text("ALTER TABLE tasks ADD COLUMN tags VARCHAR"))
        
        # Check if parent_task_id column exists
        result = conn.execute(text("""
            SELECT COUNT(*) 
            FROM pragma_table_info('tasks') 
            WHERE name = 'parent_task_id'
        """))
        
        if result.fetchone()[0] == 0:
            print("Adding parent_task_id column to tasks table...")
            conn.execute(text("ALTER TABLE tasks ADD COLUMN parent_task_id INTEGER"))
        
        # Check if position column exists
        result = conn.execute(text("""
            SELECT COUNT(*) 
            FROM pragma_table_info('tasks') 
            WHERE name = 'position'
        """))
        
        if result.fetchone()[0] == 0:
            print("Adding position column to tasks table...")
            conn.execute(text("ALTER TABLE tasks ADD COLUMN position INTEGER DEFAULT 0"))
        
        # Check if reminder_sent column exists
        result = conn.execute(text("""
            SELECT COUNT(*) 
            FROM pragma_table_info('tasks') 
            WHERE name = 'reminder_sent'
        """))
        
        if result.fetchone()[0] == 0:
            print("Adding reminder_sent column to tasks table...")
            conn.execute(text("ALTER TABLE tasks ADD COLUMN reminder_sent BOOLEAN DEFAULT 0"))
        
        # Check if dependencies column exists
        result = conn.execute(text("""
            SELECT COUNT(*) 
            FROM pragma_table_info('tasks') 
            WHERE name = 'dependencies'
        """))
        
        if result.fetchone()[0] == 0:
            print("Adding dependencies column to tasks table...")
            conn.execute(text("ALTER TABLE tasks ADD COLUMN dependencies VARCHAR"))

        # Commit the changes
        conn.commit()
    
    print("Schema update completed!")

if __name__ == "__main__":
    update_schema()