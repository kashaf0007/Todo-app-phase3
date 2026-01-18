"""
Migration script to update the messages table to use UUID for conversation_id
instead of integer to match the conversations table primary key.
"""
import os
from sqlalchemy import create_engine, text
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Get the database URL
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    print("DATABASE_URL environment variable not set!")
    exit(1)

# Create engine
engine = create_engine(DATABASE_URL)

# Update the messages table to use UUID for conversation_id
with engine.connect() as conn:
    # First, drop the foreign key constraint
    try:
        conn.execute(text("ALTER TABLE messages DROP CONSTRAINT IF EXISTS messages_conversation_id_fkey"))
        print("Dropped foreign key constraint on messages table")
    except Exception as e:
        print(f"Could not drop foreign key constraint: {e}")
    
    # Change the column type to UUID
    try:
        conn.execute(text("ALTER TABLE messages ALTER COLUMN conversation_id TYPE UUID USING conversation_id::text::UUID"))
        print("Changed conversation_id column to UUID type")
    except Exception as e:
        print(f"Could not change column type: {e}")
        # If the above fails, we might need to handle it differently
        # Let's try a different approach
        try:
            # Add a temporary column
            conn.execute(text("ALTER TABLE messages ADD COLUMN temp_conversation_id UUID"))
            print("Added temporary UUID column")
            
            # Update the temporary column with UUID values
            conn.execute(text("UPDATE messages SET temp_conversation_id = conversation_id::text::UUID"))
            print("Updated temporary column with UUID values")
            
            # Drop the old column
            conn.execute(text("ALTER TABLE messages DROP COLUMN conversation_id"))
            print("Dropped old conversation_id column")
            
            # Rename the temporary column
            conn.execute(text("ALTER TABLE messages RENAME COLUMN temp_conversation_id TO conversation_id"))
            print("Renamed temporary column to conversation_id")
        except Exception as e2:
            print(f"Alternative approach also failed: {e2}")
    
    # Recreate the foreign key constraint
    try:
        conn.execute(text("ALTER TABLE messages ADD CONSTRAINT messages_conversation_id_fkey FOREIGN KEY (conversation_id) REFERENCES conversations(id)"))
        print("Recreated foreign key constraint")
    except Exception as e:
        print(f"Could not recreate foreign key constraint: {e}")
    
    # Commit the transaction
    conn.commit()

print("Migration completed!")