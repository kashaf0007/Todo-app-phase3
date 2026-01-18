"""Check conversation table structure in the database"""
from src.database import engine
import sqlalchemy

# Connect and query for table structure
with engine.connect() as conn:
    # Check conversations table structure
    print("=== CONVERSATIONS TABLE STRUCTURE ===")
    conv_cols = conn.execute(
        sqlalchemy.text("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns
            WHERE table_schema = 'public' AND table_name = 'conversations'
            ORDER BY ordinal_position
        """)
    ).fetchall()

    if conv_cols:
        for col in conv_cols:
            print(f"  {col[0]}: {col[1]} (nullable: {col[2]}, default: {col[3]})")
    else:
        print("  No columns found - table may not exist")

    # Check if conversations table exists
    table_check = conn.execute(
        sqlalchemy.text("""
            SELECT EXISTS (
                SELECT FROM information_schema.tables 
                WHERE table_schema = 'public' 
                AND table_name = 'conversations'
            );
        """)
    ).fetchone()[0]
    
    print(f"\nTable exists: {table_check}")
    
    # Also check all tables in the schema
    print("\n=== ALL TABLES IN SCHEMA ===")
    all_tables = conn.execute(
        sqlalchemy.text("""
            SELECT table_name 
            FROM information_schema.tables 
            WHERE table_schema = 'public'
            ORDER BY table_name;
        """)
    ).fetchall()
    
    for table in all_tables:
        print(f"  {table[0]}")