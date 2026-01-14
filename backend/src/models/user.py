"""
User Model
Represents an authenticated account holder who owns tasks.
User management handled by Better Auth on frontend; backend references users via user_id.
"""

from datetime import datetime, timezone
from typing import Optional
from sqlmodel import SQLModel, Field


class User(SQLModel, table=True):
    """
    User entity for authentication and task ownership.

    Note: User registration/authentication handled by Better Auth (frontend).
    Backend only reads users for task ownership validation.
    """
    __tablename__ = "users"

    # Primary key
    id: str = Field(primary_key=True, description="UUID v4 user identifier")

    # Authentication fields
    email: str = Field(
        unique=True,
        index=True,
        description="User email address for login (case-insensitive)"
    )
    password_hash: str = Field(
        description="Bcrypt hashed password (never exposed in API responses)"
    )

    # Timestamps
    created_at: datetime = Field(
        default_factory=lambda: datetime.now(timezone.utc),
        description="Account creation timestamp"
    )

    class Config:
        """Pydantic configuration"""
        json_schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "email": "user@example.com",
                "password_hash": "$2b$12$...",  # Bcrypt hash
                "created_at": "2025-12-30T10:00:00Z"
            }
        }
