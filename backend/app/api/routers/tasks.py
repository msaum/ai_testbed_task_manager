"""
Task API routes.

Provides CRUD endpoints for task management operations.
"""
from typing import List
from fastapi import APIRouter, HTTPException, status
from fastapi.responses import Response

from app.models.task import Task, TaskCreate, TaskUpdate, TaskListResponse
from app.services.tasks import TaskService
from app.utils.errors import ResourceNotFoundError, ValidationError

router = APIRouter()

# Service instance
task_service = TaskService()


@router.get("", response_model=TaskListResponse, summary="List all tasks")
async def list_tasks(
    status: str = None,
    priority: str = None,
    project: str = None,
):
    """
    Retrieve all tasks with optional filtering.

    Args:
        status: Filter by task status (active/completed)
        priority: Filter by priority (low/medium/high)
        project: Filter by project name

    Returns:
        List of tasks matching the filters
    """
    tasks = task_service.get_all(
        status=status,
        priority=priority,
        project=project
    )
    return TaskListResponse(tasks=tasks, count=len(tasks))


@router.get("/{task_id}", response_model=Task, summary="Get a task by ID")
async def get_task(task_id: str):
    """
    Retrieve a specific task by its ID.

    Args:
        task_id: The unique identifier of the task

    Returns:
        The task details

    Raises:
        404: If the task is not found
    """
    try:
        task = task_service.get_by_id(task_id)
        if not task:
            raise ResourceNotFoundError("Task")
        return task
    except ResourceNotFoundError:
        raise HTTPException(status_code=404, detail="Task not found")


@router.post("", response_model=Task, status_code=status.HTTP_201_CREATED, summary="Create a new task")
async def create_task(task_data: TaskCreate):
    """
    Create a new task.

    Args:
        task_data: Task creation data (title, notes, priority, due_date, project)

    Returns:
        The created task with its ID
    """
    try:
        task = task_service.create(task_data)
        return task
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))


@router.put("/{task_id}", response_model=Task, summary="Update a task")
async def update_task(task_id: str, task_data: TaskUpdate):
    """
    Update an existing task.

    Args:
        task_id: The unique identifier of the task
        task_data: Task update data (any combination of update fields)

    Returns:
        The updated task

    Raises:
        404: If the task is not found
    """
    try:
        task = task_service.get_by_id(task_id)
        if not task:
            raise ResourceNotFoundError("Task")

        updated_task = task_service.update(task_id, task_data)
        return updated_task
    except ResourceNotFoundError:
        raise HTTPException(status_code=404, detail="Task not found")


@router.delete("/{task_id}", status_code=status.HTTP_204_NO_CONTENT, summary="Delete a task")
async def delete_task(task_id: str):
    """
    Delete a task by its ID.

    Args:
        task_id: The unique identifier of the task

    Raises:
        404: If the task is not found
    """
    try:
        task = task_service.get_by_id(task_id)
        if not task:
            raise ResourceNotFoundError("Task")

        task_service.delete(task_id)
        return Response(status_code=status.HTTP_204_NO_CONTENT)
    except ResourceNotFoundError:
        raise HTTPException(status_code=404, detail="Task not found")


@router.patch("/{task_id}/status", response_model=Task, summary="Update task status")
async def update_task_status(task_id: str, status: str):
    """
    Update only the status of a task.

    Args:
        task_id: The unique identifier of the task
        status: New status value (active/completed)

    Returns:
        The updated task

    Raises:
        404: If the task is not found
        400: If the status value is invalid
    """
    valid_statuses = ["active", "completed"]
    if status not in valid_statuses:
        raise HTTPException(status_code=400, detail=f"Invalid status. Must be one of: {', '.join(valid_statuses)}")

    try:
        task = task_service.get_by_id(task_id)
        if not task:
            raise ResourceNotFoundError("Task")

        updated_task = task_service.update_status(task_id, status)
        return updated_task
    except ResourceNotFoundError:
        raise HTTPException(status_code=404, detail="Task not found")
