import os
from sqlalchemy import create_engine, text

# Get database URL from environment
database_url = os.getenv("DATABASE_URL")
if not database_url:
    print("DATABASE_URL environment variable not set!")
    exit(1)

print("Connecting to database...")

# Create database engine
engine = create_engine(database_url)

with engine.connect() as conn:
    print("Connection successful!")
    
    # Check messages table structure
    result = conn.execute(text("""
        SELECT column_name, data_type, is_nullable, column_default
        FROM information_schema.columns
        WHERE table_name = 'messages'
        ORDER BY ordinal_position;
    """))

    rows = result.fetchall()
    print(f"Found {len(rows)} columns in messages table:")
    for row in rows:
        print(f"  {row[0]}: {row[1]}, nullable: {row[2]}, default: {row[3]}")
    
    # Also check for foreign keys from messages to conversations
    result = conn.execute(text("""
        SELECT 
            tc.constraint_name,
            tc.table_name, 
            kcu.column_name, 
            ccu.table_name AS foreign_table_name,
            ccu.column_name AS foreign_column_name
        FROM 
            information_schema.table_constraints AS tc
            JOIN information_schema.key_column_usage AS kcu
              ON tc.constraint_name = kcu.constraint_name
            JOIN information_schema.constraint_column_usage AS ccu
              ON ccu.constraint_name = tc.constraint_name
        WHERE 
            tc.constraint_type = 'FOREIGN KEY' 
            AND tc.table_name = 'messages'
            AND ccu.table_name = 'conversations';
    """))

    fk_rows = result.fetchall()
    print(f"\nFound {len(fk_rows)} foreign key constraints from messages to conversations:")
    for row in fk_rows:
        print(f"  Constraint '{row[0]}': {row[1]}.{row[2]} -> {row[3]}.{row[4]}")