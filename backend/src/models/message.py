from sqlmodel import SQLModel, Field
from datetime import datetime, timezone
from typing import Optional


class MessageBase(SQLModel):
    user_id: str = Field(foreign_key="users.id")  # Fixed table name to match User model
    conversation_id: int = Field(foreign_key="conversations.id")  # Fixed table name to match Conversation model
    role: str = Field(regex="^(user|assistant)$")  # Either "user" or "assistant"
    content: str = Field(min_length=1)


class Message(MessageBase, table=True):
    __tablename__ = "messages"

    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))  # Fixed to use timezone-aware datetime