"""
Project API routes.

Provides CRUD endpoints for project management operations.
"""
from typing import List
from fastapi import APIRouter, HTTPException, status

from app.models.project import Project, ProjectCreate
from app.services.projects import ProjectService
from app.utils.errors import ResourceNotFoundError

router = APIRouter()

# Service instance
project_service = ProjectService()


@router.get("", response_model=List[Project], summary="List all projects")
async def list_projects():
    """
    Retrieve all projects.

    Returns:
        List of all projects
    """
    return project_service.get_all()


@router.get("/{project_name}", response_model=Project, summary="Get a project by name")
async def get_project(project_name: str):
    """
    Retrieve a specific project by its name.

    Args:
        project_name: The name of the project

    Returns:
        The project details

    Raises:
        404: If the project is not found
    """
    try:
        project = project_service.get_by_name(project_name)
        if not project:
            raise ResourceNotFoundError("Project")
        return project
    except ResourceNotFoundError:
        raise HTTPException(status_code=404, detail="Project not found")


@router.post("", response_model=Project, status_code=status.HTTP_201_CREATED, summary="Create a new project")
async def create_project(project_data: ProjectCreate):
    """
    Create a new project.

    Args:
        project_data: Project creation data (name)

    Returns:
        The created project

    Raises:
        409: If a project with the same name already exists
    """
    try:
        project = project_service.create(project_data)
        return project
    except Exception as e:
        raise HTTPException(status_code=409, detail=str(e))


@router.delete("/{project_name}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete a project")
async def delete_project(project_name: str):
    """
    Delete a project by its name.

    Args:
        project_name: The name of the project

    Raises:
        404: If the project is not found
    """
    try:
        project = project_service.get_by_name(project_name)
        if not project:
            raise ResourceNotFoundError("Project")

        project_service.delete(project_name)
        return status.HTTP_204_NO_CONTENT
    except ResourceNotFoundError:
        raise HTTPException(status_code=404, detail="Project not found")
