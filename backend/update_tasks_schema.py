"""
Script to update the tasks table schema with missing columns
"""
from sqlalchemy import Column, Integer, String, Boolean, DateTime, Text, create_engine
from sqlalchemy.sql import text
from src.database import engine
from src.config import get_settings

def add_missing_columns():
    """Add missing columns to the tasks table"""
    settings = get_settings()
    
    with engine.connect() as conn:
        # Add missing columns one by one
        missing_columns = [
            ("priority", "VARCHAR(20) DEFAULT 'MEDIUM'"),
            ("category", "VARCHAR(20) DEFAULT 'OTHER'"),
            ("status", "VARCHAR(20) DEFAULT 'TODO'"),
            ("due_date", "TIMESTAMP WITH TIME ZONE"),
            ("estimated_duration_minutes", "INTEGER"),
            ("actual_duration_minutes", "INTEGER"),
            ("tags", "TEXT"),
            ("parent_task_id", "INTEGER REFERENCES tasks(id)"),
            ("position", "INTEGER DEFAULT 0"),
            ("reminder_sent", "BOOLEAN DEFAULT FALSE"),
            ("dependencies", "TEXT")
        ]
        
        for col_name, col_def in missing_columns:
            try:
                # Check if column exists first
                result = conn.execute(text("""
                    SELECT column_name 
                    FROM information_schema.columns 
                    WHERE table_name = 'tasks' AND column_name = :col_name
                """), {"col_name": col_name}).fetchone()
                
                if not result:
                    print(f"Adding column {col_name} to tasks table...")
                    conn.execute(text(f"ALTER TABLE tasks ADD COLUMN {col_name} {col_def}"))
                    print(f"Successfully added {col_name}")
                else:
                    print(f"Column {col_name} already exists")
            except Exception as e:
                print(f"Error adding column {col_name}: {e}")
        
        conn.commit()
        print("Schema update completed!")

if __name__ == "__main__":
    add_missing_columns()