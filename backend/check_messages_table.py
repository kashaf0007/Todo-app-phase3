"""Check messages table structure in the database"""
from src.database import engine
import sqlalchemy

# Connect and query for table structure
with engine.connect() as conn:
    # Check messages table structure
    print("=== MESSAGES TABLE STRUCTURE ===")
    msg_cols = conn.execute(
        sqlalchemy.text("""
            SELECT column_name, data_type, is_nullable, column_default
            FROM information_schema.columns
            WHERE table_schema = 'public' AND table_name = 'messages'
            ORDER BY ordinal_position
        """)
    ).fetchall()

    if msg_cols:
        for col in msg_cols:
            print(f"  {col[0]}: {col[1]} (nullable: {col[2]}, default: {col[3]})")
    else:
        print("  No columns found - table may not exist")