"""
Task service layer.

Provides business logic for task management operations.
"""
from typing import List, Optional

from app.models.task import Task, TaskCreate, TaskUpdate, TaskListResponse
from app.storage.json_file import JSONFileStore
from app.utils.errors import ResourceNotFoundError, ValidationError


class TaskService:
    """
    Service class for managing tasks.

    Handles CRUD operations and business logic for tasks,
    using JSON file storage backend.
    """

    def __init__(self, storage_path: str = "./data/tasks.json"):
        """
        Initialize the TaskService.

        Args:
            storage_path: Path to the tasks storage file
        """
        self._store = JSONFileStore[Task](
            filepath=storage_path,
            model_class=Task,
            collection_key="tasks",
            initial_data={"tasks": []}
        )

    def get_all(self, status: str = None, priority: str = None, project: str = None) -> List[Task]:
        """
        Get all tasks with optional filtering.

        Args:
            status: Filter by task status
            priority: Filter by priority
            project: Filter by project name

        Returns:
            List of matching tasks
        """
        tasks = self._store.get_all()

        if status:
            # Map frontend status to backend status
            status_map = {
                'pending': 'pending',
                'in_progress': 'in_progress',
                'completed': 'completed'
            }
            backend_status = status_map.get(status, status)
            tasks = [t for t in tasks if t.status == backend_status]
        if priority:
            tasks = [t for t in tasks if t.priority == priority]
        if project:
            tasks = [t for t in tasks if t.project == project]

        return tasks

    def get_by_id(self, task_id: str) -> Optional[Task]:
        """
        Get a task by its ID.

        Args:
            task_id: The unique identifier of the task

        Returns:
            The task if found, None otherwise
        """
        return self._store.get_by_id(task_id)

    def create(self, task_data: TaskCreate) -> Task:
        """
        Create a new task.

        Args:
            task_data: Task creation data

        Returns:
            The created task

        Raises:
            ValidationError: If the task data is invalid
        """
        task = Task(**task_data.model_dump())
        task.save()
        return self._store.add(task)

    def update(self, task_id: str, task_data: TaskUpdate) -> Task:
        """
        Update an existing task.

        Args:
            task_id: The unique identifier of the task
            task_data: Task update data

        Returns:
            The updated task

        Raises:
            ResourceNotFoundError: If the task is not found
        """
        existing = self._store.get_by_id(task_id)
        if not existing:
            raise ResourceNotFoundError("Task")

        # Build update dict from non-None values
        update_data = task_data.model_dump(exclude_unset=True)
        updated_data = existing.model_dump()
        updated_data.update(update_data)

        updated_task = Task(**updated_data)
        updated_task.save()
        return self._store.update(updated_task)

    def delete(self, task_id: str) -> bool:
        """
        Delete a task by its ID.

        Args:
            task_id: The unique identifier of the task

        Returns:
            True if task was deleted, False if not found
        """
        return self._store.delete(task_id)

    def update_status(self, task_id: str, status: str) -> Task:
        """
        Update only the status of a task.

        Args:
            task_id: The unique identifier of the task
            status: New status value

        Returns:
            The updated task

        Raises:
            ResourceNotFoundError: If the task is not found
        """
        task = self.get_by_id(task_id)
        if not task:
            raise ResourceNotFoundError("Task")

        task.status = status
        task.save()
        return self._store.update(task)
