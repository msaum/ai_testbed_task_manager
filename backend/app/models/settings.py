"""
Settings data model definition.
"""
from pydantic import BaseModel, Field


class Settings(BaseModel):
    """
    Application settings for UI preferences.
    """
    theme: str = Field(default="light", pattern="^(light|dark)$")
    sort_order: str = Field(default="created", pattern="^(priority|due_date|created)$")

    class Config:
        json_schema_extra = {
            "example": {
                "theme": "dark",
                "sort_order": "priority"
            }
        }
