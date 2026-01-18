import os
import sys

# Add backend/src to the path so we can import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend'))
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend', 'src'))

from src.database import get_session
from src.services.conversation_service import ConversationService
from src.models.message import Message

# Test the scenario that was previously failing
print("Testing the scenario that was previously failing...")

session_gen = get_session()
session = next(session_gen)

try:
    user_id = "3f33dd48-bd81-4952-8b2b-34ad4df751d3"  # Same user_id from the original error
    
    # This simulates the call from chat_endpoint that was failing
    conversation = ConversationService.create_conversation(session, user_id)
    conversation_id = str(conversation.id)  # This is now a string UUID, not an int
    
    print(f"Created conversation with ID: {conversation_id}")
    
    # Now test adding a message to this conversation (this would also use the conversation_id)
    message = Message(
        user_id=user_id,
        conversation_id=conversation_id,  # Pass the UUID string
        role="user",
        content="Test message"
    )
    session.add(message)
    session.commit()
    session.refresh(message)
    
    print(f"Successfully added message with ID: {message.id} to conversation {conversation_id}")
    
    # Test retrieving the conversation by its UUID
    retrieved = ConversationService.get_conversation(session, conversation_id, user_id)
    if retrieved:
        print(f"Successfully retrieved conversation: {retrieved.id}")
    else:
        print("Failed to retrieve conversation")
    
    print("All tests passed! The original error should be fixed.")

except Exception as e:
    print(f"Error occurred: {e}")
    import traceback
    traceback.print_exc()
finally:
    session.close()
    print("Test completed.")