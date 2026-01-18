from sqlmodel import Session, select
from typing import List, Optional
from ..models.conversation import Conversation, ConversationBase
from ..models.message import Message
from datetime import datetime


class ConversationService:
    @staticmethod
    def create_conversation(session: Session, user_id: str) -> Conversation:
        conversation = Conversation(user_id=user_id)
        session.add(conversation)
        session.commit()
        session.refresh(conversation)
        return conversation

    @staticmethod
    def get_conversation(session: Session, conversation_id: str, user_id: str) -> Optional[Conversation]:
        query = select(Conversation).where(
            Conversation.id == conversation_id,
            Conversation.user_id == user_id
        )
        return session.exec(query).first()

    @staticmethod
    def get_user_conversations(session: Session, user_id: str) -> List[Conversation]:
        query = select(Conversation).where(Conversation.user_id == user_id)
        return session.exec(query).all()

    @staticmethod
    def get_recent_conversations(session: Session, user_id: str, limit: int = 5) -> List[Conversation]:
        """
        Get recent conversations for a user, ordered by most recently updated
        """
        query = select(Conversation).where(
            Conversation.user_id == user_id
        ).order_by(Conversation.updated_at.desc()).limit(limit)
        return session.exec(query).all()

    @staticmethod
    def add_message(session: Session, user_id: str, conversation_id: str, role: str, content: str) -> Message:
        message = Message(
            conversation_id=conversation_id,
            role=role,
            content=content
        )
        session.add(message)
        session.commit()
        session.refresh(message)
        return message

    @staticmethod
    def get_conversation_messages(session: Session, conversation_id: str, user_id: str) -> List[Message]:
        # Note: We can't filter by user_id in messages table since it doesn't have that column
        # So we rely on the conversation belonging to the user (checked elsewhere)
        query = select(Message).where(
            Message.conversation_id == conversation_id
        ).order_by(Message.created_at)
        return session.exec(query).all()