"""
Task CRUD API Endpoints
Six REST endpoints for task management with strict user isolation.
"""

from typing import List, Optional
from datetime import datetime, timezone
from fastapi import APIRouter, Depends, HTTPException, status, Request
from fastapi.responses import Response
from sqlmodel import Session, select
from pydantic import BaseModel, Field

from ...database import get_session
from ...models import Task, User
from ..dependencies import get_current_user


router = APIRouter()


# Request/Response Models

class TaskCreate(BaseModel):
    """Request model for creating new task"""
    title: str = Field(..., min_length=1, max_length=255, description="Task title (required)")
    description: Optional[str] = Field(None, max_length=2000, description="Optional task description")
    priority: Optional[str] = Field(None, description="Task priority (LOW, MEDIUM, HIGH)")
    category: Optional[str] = Field(None, description="Task category (WORK, PERSONAL, SHOPPING, HEALTH, FINANCE, OTHER)")
    due_date: Optional[datetime] = Field(None, description="Task due date (ISO format)")

    class Config:
        json_schema_extra = {
            "example": {
                "title": "Buy groceries",
                "description": "Milk, eggs, bread",
                "priority": "HIGH",
                "category": "SHOPPING",
                "due_date": "2026-01-20T00:00:00Z"
            }
        }


class TaskUpdate(BaseModel):
    """Request model for updating task"""
    title: str = Field(..., min_length=1, max_length=255, description="Updated task title (required)")
    description: Optional[str] = Field(None, max_length=2000, description="Updated task description")
    status: Optional[str] = Field(None, description="Updated task status")
    priority: Optional[str] = Field(None, description="Task priority (LOW, MEDIUM, HIGH)")
    category: Optional[str] = Field(None, description="Task category (WORK, PERSONAL, SHOPPING, HEALTH, FINANCE, OTHER)")
    due_date: Optional[datetime] = Field(None, description="Task due date (ISO format)")

    class Config:
        json_schema_extra = {
            "example": {
                "title": "Buy groceries and supplies",
                "description": "Milk, eggs, bread, cleaning supplies",
                "status": "IN_PROGRESS",
                "priority": "HIGH",
                "category": "SHOPPING",
                "due_date": "2026-01-20T00:00:00Z"
            }
        }


class TaskCompletionToggle(BaseModel):
    """Request model for toggling task completion"""
    completed: bool = Field(..., description="New completion status")

    class Config:
        json_schema_extra = {
            "example": {"completed": True}
        }


class TaskResponse(BaseModel):
    """Response model for task data"""
    id: int
    user_id: str
    title: str
    description: Optional[str]
    completed: bool
    status: Optional[str]
    priority: Optional[str]
    category: Optional[str]
    due_date: Optional[datetime]
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }


# API Endpoints

@router.get("/api/{user_id}/tasks", response_model=List[TaskResponse])
async def list_tasks(
    user_id: str,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    List all tasks for authenticated user (FR-027, FR-013).

    Security: user_id path parameter IGNORED - user derived from JWT only.
    Tasks filtered by current_user.id for strict user isolation (FR-048).
    """
    # CRITICAL: Use current_user.id from JWT, NOT user_id from path
    statement = select(Task).where(
        Task.user_id == current_user.id
    ).order_by(Task.created_at.desc())  # Newest first (Assumption 5)

    tasks = session.exec(statement).all()

    return tasks


@router.post("/api/{user_id}/tasks", response_model=TaskResponse, status_code=status.HTTP_201_CREATED)
async def create_task(
    user_id: str,
    task_data: TaskCreate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Create new task for authenticated user (FR-028, FR-011, FR-012).

    Security: Task automatically assigned to current_user.id from JWT.
    Path parameter user_id IGNORED for security.
    """
    # CRITICAL: Use current_user.id from JWT for task ownership
    new_task = Task(
        user_id=current_user.id,  # From JWT, not request
        title=task_data.title.strip(),
        description=task_data.description.strip() if task_data.description else None,
        priority=task_data.priority,
        category=task_data.category,
        due_date=task_data.due_date,
        completed=False  # Default per FR-026
    )

    session.add(new_task)
    session.commit()
    session.refresh(new_task)

    return new_task


@router.get("/api/{user_id}/tasks/{id}", response_model=TaskResponse)
async def get_task(
    user_id: str,
    id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Get specific task details (FR-029).

    Security: Verifies task belongs to authenticated user (FR-049).
    Returns 404 if task doesn't exist OR belongs to different user.
    """
    task = session.exec(
        select(Task).where(
            Task.id == id,
            Task.user_id == current_user.id  # Ownership check
        )
    ).first()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    return task


@router.put("/api/{user_id}/tasks/{id}", response_model=TaskResponse)
async def update_task(
    user_id: str,
    id: int,
    task_data: TaskUpdate,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Update task title, description, and status (FR-030, FR-015).

    Security: Verifies task ownership before updating (FR-049).
    Returns 404 if task doesn't exist OR belongs to different user.
    """
    task = session.exec(
        select(Task).where(
            Task.id == id,
            Task.user_id == current_user.id  # Ownership check
        )
    ).first()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    # Validate title not empty
    if not task_data.title.strip():
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Title cannot be empty"
        )

    # Update fields
    task.title = task_data.title.strip()
    task.description = task_data.description.strip() if task_data.description else None
    if task_data.status is not None:
        task.status = task_data.status
    if task_data.priority is not None:
        task.priority = task_data.priority
    if task_data.category is not None:
        task.category = task_data.category
    if task_data.due_date is not None:
        task.due_date = task_data.due_date
    task.updated_at = datetime.now(timezone.utc)  # Explicitly update timestamp

    session.add(task)
    session.commit()
    session.refresh(task)

    return task


@router.delete("/api/{user_id}/tasks/{id}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_task(
    user_id: str,
    id: int,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Permanently delete task (FR-031, FR-017).

    Security: Verifies task ownership before deletion (FR-049).
    Returns 404 if task doesn't exist OR belongs to different user.
    """
    task = session.exec(
        select(Task).where(
            Task.id == id,
            Task.user_id == current_user.id  # Ownership check
        )
    ).first()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    session.delete(task)
    session.commit()

    return None  # 204 No Content


@router.patch("/api/{user_id}/tasks/{id}/complete", response_model=TaskResponse)
async def toggle_task_completion(
    user_id: str,
    id: int,
    completion_data: TaskCompletionToggle,
    current_user: User = Depends(get_current_user),
    session: Session = Depends(get_session)
):
    """
    Toggle task completion status (FR-032, FR-016).

    Security: Verifies task ownership before updating (FR-049).
    Returns 404 if task doesn't exist OR belongs to different user.
    """
    task = session.exec(
        select(Task).where(
            Task.id == id,
            Task.user_id == current_user.id  # Ownership check
        )
    ).first()

    if not task:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Task not found"
        )

    # Update completion status
    task.completed = completion_data.completed
    task.updated_at = datetime.now(timezone.utc)  # Explicitly update timestamp

    session.add(task)
    session.commit()
    session.refresh(task)

    return task


# Explicitly handle OPTIONS requests for CORS - without authentication dependencies
@router.options("/api/{user_id}/tasks", include_in_schema=False)
async def options_tasks(user_id: str):
    """
    Handle OPTIONS request for tasks endpoint.
    This ensures proper CORS handling without authentication.
    """
    response = Response()
    response.headers["Allow"] = "GET, POST, OPTIONS"
    return response


@router.options("/api/{user_id}/tasks/{id}", include_in_schema=False)
async def options_task_detail(user_id: str, id: int):
    """
    Handle OPTIONS request for task detail endpoint.
    This ensures proper CORS handling without authentication.
    """
    response = Response()
    response.headers["Allow"] = "GET, PUT, DELETE, PATCH, OPTIONS"
    return response
