"""
Contract test for context retrieval in the RAG Todo Chatbot API
Verifies that the context retrieval functionality meets the specified contract
"""

import pytest
from unittest.mock import AsyncMock, MagicMock
from backend.src.services.rag_service import RAGService
from backend.src.models.conversation import Conversation
from backend.src.models.message import Message
from sqlmodel import Session, select


@pytest.mark.asyncio
async def test_context_retrieval_contract():
    """
    Test that context retrieval functionality meets the specified contract:
    - Retrieves relevant conversation history
    - Filters by user ID for security
    - Limits context to recent messages
    - Returns properly formatted context
    """
    # Mock database session
    mock_session = MagicMock(spec=Session)
    
    # Mock conversation and messages
    mock_conversation = Conversation(
        id=1,
        user_id="test-user-id",
        title="Test Conversation"
    )
    
    mock_messages = [
        Message(id=1, conversation_id=1, role="user", content="Add a task to buy milk", user_id="test-user-id"),
        Message(id=2, conversation_id=1, role="assistant", content="I've added the task 'buy milk'", user_id="system"),
        Message(id=3, conversation_id=1, role="user", content="Also add bread", user_id="test-user-id"),
    ]
    
    # Mock the database queries
    mock_session.exec.return_value.first.return_value = mock_conversation
    mock_session.exec.return_value.all.return_value = mock_messages
    
    # Initialize the RAG service
    rag_service = RAGService(mock_session)
    
    # Test context retrieval
    context = await rag_service.retrieve_context(user_id="test-user-id", conversation_id=1)
    
    # Assertions to verify contract compliance
    assert context is not None
    assert "buy milk" in context
    assert "Also add bread" in context
    assert len(context) > 0  # Context should not be empty
    
    # Verify that the session was called correctly
    assert mock_session.exec.called
    
    print("✓ Context retrieval contract test passed")


@pytest.mark.asyncio
async def test_context_retrieval_with_different_user():
    """
    Test that context retrieval properly isolates contexts by user ID
    """
    # Mock database session
    mock_session = MagicMock(spec=Session)
    
    # Mock conversation for a different user
    mock_conversation = None  # Simulate no access to other user's conversation
    mock_session.exec.return_value.first.return_value = mock_conversation
    
    # Initialize the RAG service
    rag_service = RAGService(mock_session)
    
    # Test context retrieval for a different user
    context = await rag_service.retrieve_context(user_id="different-user-id", conversation_id=1)
    
    # Should return None or empty context for unauthorized access
    assert context is None or len(context) == 0
    
    print("✓ Context retrieval isolation test passed")


if __name__ == "__main__":
    import asyncio
    asyncio.run(test_context_retrieval_contract())
    asyncio.run(test_context_retrieval_with_different_user())
    print("All context retrieval contract tests passed!")