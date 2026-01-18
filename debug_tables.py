import os
from sqlalchemy import create_engine, text

# Get database URL from environment
database_url = os.getenv("DATABASE_URL")
if not database_url:
    print("DATABASE_URL environment variable not set!")
    exit(1)

print(f"Database URL: {database_url[:50]}...")  # Print first 50 chars to verify

# Create database engine
engine = create_engine(database_url)

# Check all tables in the database
with engine.connect() as conn:
    result = conn.execute(text("""
        SELECT table_name
        FROM information_schema.tables
        WHERE table_schema = 'public'
        ORDER BY table_name;
    """))

    rows = result.fetchall()
    print(f"Number of tables found: {len(rows)}")
    
    print('Tables in the database:')
    for row in rows:
        print(f'  {row[0]}')

    # Check columns in conversations table specifically
    print()
    result = conn.execute(text("""
        SELECT column_name, data_type, is_nullable, column_default
        FROM information_schema.columns
        WHERE table_name = 'conversations'
        ORDER BY ordinal_position;
    """))
    
    rows = result.fetchall()
    print(f"Number of columns in conversations table: {len(rows)}")
    print('Columns in conversations table:')
    for row in rows:
        print(f'  {row[0]}: {row[1]}, nullable: {row[2]}, default: {row[3]}')