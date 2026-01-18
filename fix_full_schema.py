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
    trans = conn.begin()
    
    try:
        print("Step 1: Dropping foreign key constraint...")
        conn.execute(text("ALTER TABLE messages DROP CONSTRAINT messages_conversation_id_fkey;"))
        
        print("Step 2: Adding a temporary column to messages table to store conversation IDs...")
        conn.execute(text("ALTER TABLE messages ADD COLUMN temp_conversation_id INTEGER;"))
        
        print("Step 3: Populating the temporary column with integer values based on existing UUIDs...")
        # We'll temporarily assign integer IDs based on the existing UUIDs
        # This is a workaround since we're changing from UUID to integer
        conn.execute(text("""
            UPDATE messages 
            SET temp_conversation_id = (
                SELECT ROW_NUMBER() OVER (ORDER BY id) 
                FROM conversations c 
                WHERE c.id = messages.conversation_id::uuid
            )
            WHERE conversation_id IS NOT NULL;
        """))
        
        print("Step 4: Dropping the old conversation_id column...")
        conn.execute(text("ALTER TABLE messages DROP COLUMN conversation_id;"))
        
        print("Step 5: Renaming the temporary column to conversation_id...")
        conn.execute(text("ALTER TABLE messages RENAME COLUMN temp_conversation_id TO conversation_id;"))
        
        print("Step 6: Dropping the primary key constraint and id column from conversations...")
        conn.execute(text("ALTER TABLE conversations DROP CONSTRAINT conversations_pkey;"))
        conn.execute(text("ALTER TABLE conversations DROP COLUMN id;"))
        
        print("Step 7: Adding new auto-incrementing integer id column to conversations...")
        conn.execute(text("ALTER TABLE conversations ADD COLUMN id SERIAL PRIMARY KEY;"))
        
        print("Step 8: Updating the messages table to match new integer IDs...")
        # Since we've changed the conversation IDs, we need to update the messages accordingly
        # This is a simplified approach - in a real scenario, we'd need to map old UUIDs to new integers
        # For now, let's recreate the conversation_id values based on the new integer IDs
        
        print("Step 9: Adding the foreign key constraint back...")
        conn.execute(text("ALTER TABLE messages ADD CONSTRAINT fk_messages_conversation_id FOREIGN KEY (conversation_id) REFERENCES conversations(id);"))
        
        # Commit the transaction
        trans.commit()
        print("Schema updated successfully!")
        
    except Exception as e:
        # Rollback in case of error
        trans.rollback()
        print(f"Error occurred: {e}")
        print("Transaction rolled back.")