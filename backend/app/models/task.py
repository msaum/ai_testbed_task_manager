"""
Task data model definition.
"""
from datetime import datetime
from uuid import uuid4
from typing import Optional
from pydantic import BaseModel, Field

from app.models.project import Project


Priority = str  # "low", "medium", "high"
TaskStatus = str  # "active", "completed"


class Task(BaseModel):
    """
    Represents a task in the task manager.
    """
    id: str = Field(default_factory=lambda: str(uuid4()))
    title: str = Field(..., min_length=1)
    notes: str = ""
    status: TaskStatus = "active"
    priority: Priority = "medium"
    due_date: Optional[datetime] = None
    project: str = "Inbox"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    def save(self) -> None:
        """Update the updated_at timestamp to current time."""
        self.updated_at = datetime.utcnow()

    class Config:
        json_schema_extra = {
            "example": {
                "id": "550e8400-e29b-41d4-a716-446655440000",
                "title": "Complete project",
                "notes": "Finish the API design",
                "status": "active",
                "priority": "high",
                "due_date": "2026-02-15T23:59:59Z",
                "project": "Work",
                "created_at": "2026-02-09T10:00:00Z",
                "updated_at": "2026-02-09T10:00:00Z"
            }
        }


class TaskCreate(BaseModel):
    """Request model for creating a task."""
    title: str = Field(..., min_length=1)
    notes: str = ""
    priority: Priority = "medium"
    due_date: Optional[datetime] = None
    project: str = "Inbox"


class TaskUpdate(BaseModel):
    """Request model for updating a task."""
    title: Optional[str] = Field(None, min_length=1)
    notes: Optional[str] = None
    status: Optional[TaskStatus] = None
    priority: Optional[Priority] = None
    due_date: Optional[datetime] = None
    project: Optional[str] = None


class TaskListResponse(BaseModel):
    """Response model for task list with filtering."""
    tasks: list[Task]
    count: int
