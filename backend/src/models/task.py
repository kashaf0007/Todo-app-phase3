from sqlmodel import SQLModel, Field
from datetime import datetime, timezone
from typing import Optional
import enum
from sqlalchemy import TypeDecorator, String


class Priority(str, enum.Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"


class Category(str, enum.Enum):
    WORK = "work"
    PERSONAL = "personal"
    SHOPPING = "shopping"
    HEALTH = "health"
    FINANCE = "finance"
    OTHER = "other"


class TaskStatus(str, enum.Enum):
    TODO = "TODO"
    IN_PROGRESS = "IN_PROGRESS"
    REVIEW = "REVIEW"
    DONE = "DONE"


class FlexibleTaskStatus(TypeDecorator):
    """
    A custom type that handles both old lowercase and new uppercase enum values
    to maintain backward compatibility with existing data
    """
    impl = String
    cache_ok = True

    def process_bind_param(self, value, dialect):
        if value is None:
            return value
        # Convert enum to string representation
        if isinstance(value, TaskStatus):
            return value.value
        return str(value).upper()  # Convert to uppercase for consistency

    def process_result_value(self, value, dialect):
        if value is None:
            return value
        # Handle both old lowercase and new uppercase values
        upper_value = value.upper()
        try:
            return TaskStatus(upper_value)
        except ValueError:
            # If it's not a valid enum value, return the original value
            # This handles edge cases where the DB has invalid values
            return TaskStatus.TODO  # Default to TODO for invalid values


class TaskBase(SQLModel):
    title: str = Field(min_length=1, max_length=255)
    description: Optional[str] = Field(default=None, max_length=2000)
    completed: bool = Field(default=False)
    user_id: str = Field(foreign_key="users.id")  # Fixed table name to match User model
    priority: Optional[Priority] = Field(default=Priority.MEDIUM)
    category: Optional[Category] = Field(default=Category.OTHER)
    status: Optional[TaskStatus] = Field(default=TaskStatus.TODO, sa_type=FlexibleTaskStatus)  # Enhanced status field with flexible type
    due_date: Optional[datetime] = Field(default=None)
    estimated_duration_minutes: Optional[int] = Field(default=None, ge=1, le=1440)  # Up to 24 hours
    actual_duration_minutes: Optional[int] = Field(default=None, ge=1)  # Actual time spent
    tags: Optional[str] = Field(default=None, max_length=500)  # Comma-separated tags
    parent_task_id: Optional[int] = Field(default=None, foreign_key="tasks.id")  # For subtasks
    position: Optional[int] = Field(default=0)  # For ordering tasks
    reminder_sent: bool = Field(default=False)  # Track if reminder was sent
    dependencies: Optional[str] = Field(default=None, max_length=500)  # Comma-separated task IDs this task depends on


class Task(TaskBase, table=True):
    __tablename__ = "tasks"

    id: Optional[int] = Field(default=None, primary_key=True)
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc), sa_column_kwargs={"onupdate": lambda: datetime.now(timezone.utc)})