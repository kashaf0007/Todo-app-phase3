"""
Test script to verify ConversationService.create_conversation function works properly
"""
import os
from sqlmodel import create_engine, Session
from backend.src.services.conversation_service import ConversationService
from backend.src.models.conversation import Conversation


def test_create_conversation():
    # Get database URL from environment
    database_url = os.getenv("DATABASE_URL")
    if not database_url:
        print("DATABASE_URL environment variable not set!")
        return

    # Create database engine
    engine = create_engine(database_url)

    # Create a session
    with Session(engine) as session:
        # Create a test conversation with a sample user_id
        user_id = "test-user-id-12345"  # This would normally come from auth

        try:
            conversation = ConversationService.create_conversation(session, user_id)
            print(f"Successfully created conversation with ID: {conversation.id}")
            print(f"User ID: {conversation.user_id}")
            print(f"Created at: {conversation.created_at}")
            print(f"Updated at: {conversation.updated_at}")

            # Verify the conversation was saved properly
            retrieved_conversation = session.get(Conversation, conversation.id)
            if retrieved_conversation:
                print("+ Conversation successfully saved to database")
                print(f"  Retrieved ID: {retrieved_conversation.id}")
                print(f"  Retrieved User ID: {retrieved_conversation.user_id}")
            else:
                print("- Failed to retrieve conversation from database")

        except Exception as e:
            print(f"Error creating conversation: {str(e)}")


if __name__ == "__main__":
    test_create_conversation()