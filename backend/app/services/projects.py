"""
Project service layer.

Provides business logic for project management operations.
"""
from typing import List, Optional

from app.models.project import Project, ProjectCreate
from app.storage.json_file import JSONFileStore


class ProjectService:
    """
    Service class for managing projects.

    Handles CRUD operations and business logic for projects,
    using JSON file storage backend.
    """

    def __init__(self, storage_path: str = "./data/projects.json"):
        """
        Initialize the ProjectService.

        Args:
            storage_path: Path to the projects storage file
        """
        self._store = JSONFileStore[Project](
            filepath=storage_path,
            model_class=Project,
            collection_key="projects",
            initial_data={"projects": []}
        )

    def get_all(self) -> List[Project]:
        """
        Get all projects.

        Returns:
            List of all projects
        """
        return self._store.get_all()

    def get_by_name(self, name: str) -> Optional[Project]:
        """
        Get a project by its name.

        Args:
            name: The name of the project

        Returns:
            The project if found, None otherwise
        """
        for project in self._store.get_all():
            if project.name == name:
                return project
        return None

    def create(self, project_data: ProjectCreate) -> Project:
        """
        Create a new project.

        Args:
            project_data: Project creation data

        Returns:
            The created project

        Raises:
            ValueError: If a project with the same name already exists
        """
        existing = self.get_by_name(project_data.name)
        if existing:
            raise ValueError(f"Project '{project_data.name}' already exists")

        project = Project(**project_data.model_dump())
        return self._store.add(project)

    def delete(self, name: str) -> bool:
        """
        Delete a project by its name.

        Args:
            name: The name of the project

        Returns:
            True if project was deleted, False if not found
        """
        project = self.get_by_name(name)
        if not project:
            return False

        # Use the store's delete_by_field method
        return self._store.delete_by_field("name", name) > 0
