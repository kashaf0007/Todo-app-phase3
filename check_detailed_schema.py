import os
from sqlalchemy import create_engine, text

# Get database URL from environment
database_url = os.getenv("DATABASE_URL")
if not database_url:
    print("DATABASE_URL environment variable not set!")
    exit(1)

# Create database engine
engine = create_engine(database_url)

# Query the information schema to get detailed column info
with engine.connect() as conn:
    # Get detailed column information
    result = conn.execute(text("""
        SELECT 
            column_name,
            data_type,
            is_nullable,
            column_default,
            is_identity,
            identity_generation
        FROM information_schema.columns
        WHERE table_name = 'conversations'
        ORDER BY ordinal_position;
    """))
    
    print("Detailed columns in conversations table:")
    for row in result:
        print(f"  {row.column_name}: {row.data_type}, nullable: {row.is_nullable}, default: {row.column_default}, identity: {row.is_identity}, identity_gen: {row.identity_generation}")

    print()
    
    # Get constraint information
    result = conn.execute(text("""
        SELECT 
            con.conname AS constraint_name,
            pg_get_constraintdef(con.oid) AS constraint_def
        FROM pg_constraint con
        JOIN pg_class tbl ON tbl.oid = con.conrelid
        WHERE tbl.relname = 'conversations';
    """))

    print("Constraints on conversations table:")
    for row in result:
        print(f"  {row.constraint_name}: {row.constraint_def}")