from sqlmodel import SQLModel, Field
from datetime import datetime, timezone
from typing import Optional


class ConversationBase(SQLModel):
    user_id: str = Field(foreign_key="users.id")  # Fixed table name to match User model


class Conversation(ConversationBase, table=True):
    __tablename__ = "conversations"

    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))  # Fixed to use timezone-aware datetime
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), sa_column_kwargs={"onupdate": lambda: datetime.now(timezone.utc)})  # Fixed to use timezone-aware datetime