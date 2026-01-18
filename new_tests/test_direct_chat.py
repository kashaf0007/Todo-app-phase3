import asyncio
import sys
import os
from dotenv import load_dotenv
load_dotenv()

sys.path.insert(0, os.path.join(os.getcwd(), 'backend', 'src'))

from backend.src.api.chat_api import chat_endpoint
from backend.src.database import get_session
from backend.src.models import User
from sqlmodel import select
from fastapi import Request
from fastapi.datastructures import Headers
from starlette.datastructures import MutableHeaders
from backend.src.api.dependencies import get_current_user
from backend.src.api.chat_api import ChatRequest
import json

async def test_chat_functionality():
    print("Testing chat functionality directly...")
    
    # Create a mock request object
    headers = Headers({"authorization": "Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJlYjQ3OTI1Yi02NTA3LTQ2NmQtOWEyMi02MDU3ZjY5OTM3MzQiLCJleHAiOjE3NjkxNzE4MTAsImlhdCI6MTc2ODU2NzAxMCwidHlwZSI6ImFjY2VzcyJ9.Dq2Fe9Zq2YYp1OlWnIiijcfj2JbMLhyg225QVb8dcx4"})
    
    # Create a mock Starlette request
    from starlette.requests import Request as StarletteRequest
    from starlette.types import Scope
    from starlette.datastructures import Headers
    
    scope = {
        "type": "http",
        "method": "POST",
        "path": "/api/eb47925b-6507-466d-9a22-6057f6993734/chat",
        "headers": [(b"authorization", b"Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJzdWIiOiJlYjQ3OTI1Yi02NTA3LTQ2NmQtOWEyMi02MDU3ZjY5OTM3MzQiLCJleHAiOjE3NjkxNzE4MTAsImlhdCI6MTc2ODU2NzAxMCwidHlwZSI6ImFjY2VzcyJ9.Dq2Fe9Zq2YYp1OlWnIiijcfj2JbMLhyg225QVb8dcx4"),
                    (b"content-type", b"application/json")]
    }
    
    # Create the request object
    request = StarletteRequest(scope)
    
    # Create the chat request
    chat_request = ChatRequest(message="Add a new task to buy groceries")
    
    # Get the current user
    session_gen = get_session()
    session = next(session_gen)
    
    try:
        # Get the user from the database
        user = session.exec(select(User).where(User.id == "eb47925b-6507-466d-9a22-6057f6993734")).first()
        if not user:
            print("User not found in database")
            return
        
        print(f"Found user: {user.id}, {user.email}")
        
        # Call the chat endpoint function directly
        result = await chat_endpoint(
            request=request,
            user_id="eb47925b-6507-466d-9a22-6057f6993734",
            chat_request=chat_request,
            current_user=user
        )
        
        print("Chat endpoint result:", result)
        
    except Exception as e:
        print(f"Error calling chat endpoint: {e}")
        import traceback
        traceback.print_exc()
    finally:
        session.close()

# Run the test
if __name__ == "__main__":
    asyncio.run(test_chat_functionality())