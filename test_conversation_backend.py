import os
import sys
sys.path.append(os.path.join(os.path.dirname(__file__), 'backend', 'src'))

from backend.src.services.conversation_service import ConversationService
from backend.src.database import get_session

print('Testing conversation creation...')

# Get a session
session_gen = get_session()
session = next(session_gen)

try:
    # Create a test conversation
    user_id = '3f33dd48-bd81-4952-8b2b-34ad4df751d3'
    conversation = ConversationService.create_conversation(session, user_id)
    print(f'Successfully created conversation with ID: {conversation.id}')
    
    # Test adding a message
    message = ConversationService.add_message(session, conversation.id, 'user', 'Hello, this is a test message.')
    print(f'Successfully added message with ID: {message.id}')
    
    # Test getting conversation messages
    messages = ConversationService.get_conversation_messages(session, conversation.id, user_id)
    print(f'Retrieved {len(messages)} messages from conversation')
    
    print('All tests passed!')
    
except Exception as e:
    print(f'Error occurred: {e}')
    import traceback
    traceback.print_exc()
finally:
    session.close()