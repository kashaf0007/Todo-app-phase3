import os
import sys
import asyncio
from sqlmodel import Session

# Add backend/src to the path so we can import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend', 'src'))

from src.database import get_session
from src.services.conversation_service import ConversationService

# Get database URL from environment
database_url = os.getenv("DATABASE_URL")
if not database_url:
    print("DATABASE_URL environment variable not set!")
    exit(1)

print("Testing conversation creation...")

# Get a session and try to create a conversation
session_gen = get_session()
session = next(session_gen)

try:
    # Create a test conversation
    user_id = "test-user-id"
    conversation = ConversationService.create_conversation(session, user_id)

    print(f"Successfully created conversation with ID: {conversation.id}")
    print(f"Conversation user_id: {conversation.user_id}")
    print(f"Conversation created_at: {conversation.created_at}")

    # Verify we can retrieve it
    retrieved = ConversationService.get_conversation(session, conversation.id, user_id)
    if retrieved:
        print(f"Successfully retrieved conversation with ID: {retrieved.id}")
    else:
        print("Failed to retrieve the conversation")

except Exception as e:
    print(f"Error occurred: {e}")
    import traceback
    traceback.print_exc()
finally:
    session.close()
    print("Test completed.")