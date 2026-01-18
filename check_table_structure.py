import os
from sqlalchemy import create_engine, text

# Get database URL from environment
database_url = os.getenv("DATABASE_URL")
if not database_url:
    print("DATABASE_URL environment variable not set!")
    exit(1)

# Create database engine
engine = create_engine(database_url)

# Query the information schema to get column info
with engine.connect() as conn:
    result = conn.execute(text("""
        SELECT column_name, data_type, is_nullable, column_default 
        FROM information_schema.columns 
        WHERE table_name = 'conversations'
        ORDER BY ordinal_position;
    """))
    
    print("Columns in conversations table:")
    for row in result:
        print(f"  {row.column_name}: {row.data_type}, nullable: {row.is_nullable}, default: {row.column_default}")