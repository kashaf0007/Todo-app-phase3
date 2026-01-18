from sqlmodel import SQLModel, Field
from datetime import datetime, timezone
from typing import Optional
import uuid


class MessageBase(SQLModel):
    # Removed user_id since it doesn't exist in the database table
    conversation_id: str = Field(foreign_key="conversations.id")  # Changed to str to match UUID in DB
    role: str = Field(regex="^(user|assistant)$")  # Either "user" or "assistant"
    content: str = Field(min_length=1)


class Message(MessageBase, table=True):
    __tablename__ = "messages"

    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))  # Fixed to use timezone-aware datetime