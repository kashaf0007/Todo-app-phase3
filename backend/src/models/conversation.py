from sqlmodel import SQLModel, Field
from datetime import datetime, timezone
from typing import Optional
import uuid


class ConversationBase(SQLModel):
    user_id: str = Field(foreign_key="users.id")


class Conversation(ConversationBase, table=True):
    __tablename__ = "conversations"

    # Using UUID as primary key to match database schema
    id: str = Field(default_factory=lambda: str(uuid.uuid4()), primary_key=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), sa_column_kwargs={"onupdate": lambda: datetime.now(timezone.utc)})