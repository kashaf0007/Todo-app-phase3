import os
import sys

# Add backend/src to the path so we can import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'backend', 'src'))

# Test importing the main components
try:
    print("Testing imports...")
    
    # Test importing the main app
    from main import app
    print("✓ Successfully imported main app")
    
    # Test importing the chat API
    from api.chat_api import router as chat_router
    print("✓ Successfully imported chat API router")
    
    # Test importing the conversation service
    from services.conversation_service import ConversationService
    print("✓ Successfully imported ConversationService")
    
    # Test importing the models
    from models.conversation import Conversation
    from models.message import Message
    print("✓ Successfully imported models")
    
    print("\nAll imports successful! The backend code appears to be syntactically correct.")
    
except ImportError as e:
    print(f"Import error: {e}")
    import traceback
    traceback.print_exc()
except Exception as e:
    print(f"Other error: {e}")
    import traceback
    traceback.print_exc()