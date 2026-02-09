"""
Project data model definition.
"""
from datetime import datetime
from pydantic import BaseModel, Field


class Project(BaseModel):
    """
    Represents a project for organizing tasks.
    """
    name: str = Field(..., min_length=1)
    created_at: datetime = Field(default_factory=datetime.utcnow)

    class Config:
        json_schema_extra = {
            "example": {
                "name": "Personal",
                "created_at": "2026-02-09T10:00:00Z"
            }
        }


class ProjectCreate(BaseModel):
    """Request model for creating a project."""
    name: str = Field(..., min_length=1)
