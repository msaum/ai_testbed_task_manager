"""
Unit tests for data models (task, project, settings).

Tests model creation, validation, and serialization.
"""
import pytest
from datetime import datetime
from pydantic import ValidationError

from app.models.task import Task, TaskCreate, TaskUpdate, Priority, TaskStatus
from app.models.project import Project, ProjectCreate
from app.models.settings import Settings


class TestTaskModel:
    """Tests for the Task model."""

    def test_create_task_with_required_fields(self):
        """Test creating a task with required fields only."""
        task = Task(title="Test Task")

        assert task.id is not None  # UUID generated
        assert task.title == "Test Task"
        assert task.notes == ""
        assert task.status == "active"  # Default
        assert task.priority == "medium"  # Default
        assert task.due_date is None
        assert task.project == "Inbox"  # Default
        assert task.created_at is not None
        assert task.updated_at is not None

    def test_create_task_with_all_fields(self):
        """Test creating a task with all fields specified."""
        due_date = datetime(2026, 2, 15, 23, 59, 59)
        task = Task(
            title="Complete Project",
            notes="Finish the API design",
            status="active",
            priority="high",
            due_date=due_date,
            project="Work"
        )

        assert task.title == "Complete Project"
        assert task.notes == "Finish the API design"
        assert task.status == "active"
        assert task.priority == "high"
        assert task.due_date == due_date
        assert task.project == "Work"

    def test_task_id_is_uuid(self):
        """Test that task ID is a valid UUID."""
        task = Task(title="Test Task")

        assert len(task.id) == 36  # UUID format
        assert task.id.count("-") == 4

    def test_task_unique_ids(self):
        """Test that each task gets a unique ID."""
        task1 = Task(title="Task 1")
        task2 = Task(title="Task 2")

        assert task1.id != task2.id

    def test_task_model_dump(self):
        """Test Pydantic model_dump method."""
        task = Task(title="Test Task")

        dumped = task.model_dump()

        assert "id" in dumped
        assert "title" in dumped
        assert "created_at" in dumped
        assert isinstance(dumped["created_at"], datetime)

    def test_task_model_dump_json(self):
        """Test Pydantic model_dump_json method."""
        task = Task(title="Test Task")

        json_str = task.model_dump_json()

        assert '"id"' in json_str
        assert '"title"' in json_str
        assert 'Test Task' in json_str

    def test_task_updated_at_on_save(self):
        """Test that updated_at is set on save."""
        task = Task(title="Test Task")
        initial_updated_at = task.updated_at

        # Wait a tiny bit to ensure different timestamp
        import time
        time.sleep(0.01)

        task.save()

        assert task.updated_at >= initial_updated_at

    def test_title_empty_string_raises_error(self):
        """Test that empty title raises validation error."""
        with pytest.raises(ValidationError):
            Task(title="")


class TestTaskCreateModel:
    """Tests for the TaskCreate model."""

    def test_create_with_required_fields(self):
        """Test creating TaskCreate with required fields."""
        task_create = TaskCreate(title="New Task")

        assert task_create.title == "New Task"
        assert task_create.notes == ""
        assert task_create.priority == "medium"
        assert task_create.project == "Inbox"

    def test_create_with_all_fields(self):
        """Test creating TaskCreate with all fields."""
        due_date = datetime(2026, 2, 15)
        task_create = TaskCreate(
            title="New Task",
            notes="Task notes",
            priority="high",
            due_date=due_date,
            project="Work"
        )

        assert task_create.title == "New Task"
        assert task_create.notes == "Task notes"
        assert task_create.priority == "high"
        assert task_create.due_date == due_date
        assert task_create.project == "Work"

    def test_title_empty_raises_error(self):
        """Test that empty title raises validation error."""
        with pytest.raises(ValidationError):
            TaskCreate(title="")


class TestTaskUpdateModel:
    """Tests for the TaskUpdate model."""

    def test_update_all_optional(self):
        """Test that all TaskUpdate fields are optional."""
        task_update = TaskUpdate()

        assert task_update.title is None
        assert task_update.notes is None
        assert task_update.status is None
        assert task_update.priority is None
        assert task_update.due_date is None
        assert task_update.project is None

    def test_update_partial_fields(self):
        """Test updating partial fields."""
        task_update = TaskUpdate(
            title="Updated Title",
            status="completed"
        )

        assert task_update.title == "Updated Title"
        assert task_update.status == "completed"
        assert task_update.notes is None

    def test_update_empty_title_allowed(self):
        """Test that empty title is allowed for update."""
        # Empty string should fail validation
        with pytest.raises(ValidationError):
            TaskUpdate(title="")


class TestProjectModel:
    """Tests for the Project model."""

    def test_create_with_required_fields(self):
        """Test creating a project with required fields."""
        project = Project(name="Test Project")

        assert project.name == "Test Project"
        assert project.created_at is not None

    def test_project_name_empty_raises_error(self):
        """Test that empty name raises validation error."""
        with pytest.raises(ValidationError):
            Project(name="")


class TestProjectCreateModel:
    """Tests for the ProjectCreate model."""

    def test_create_with_required_fields(self):
        """Test creating ProjectCreate with required fields."""
        project_create = ProjectCreate(name="New Project")

        assert project_create.name == "New Project"

    def test_name_empty_raises_error(self):
        """Test that empty name raises validation error."""
        with pytest.raises(ValidationError):
            ProjectCreate(name="")


class TestSettingsModel:
    """Tests for the Settings model."""

    def test_default_settings(self):
        """Test default settings values."""
        settings = Settings()

        assert settings.theme == "light"
        assert settings.sort_order == "created"

    def test_theme_light(self):
        """Test theme set to light."""
        settings = Settings(theme="light")
        assert settings.theme == "light"

    def test_theme_dark(self):
        """Test theme set to dark."""
        settings = Settings(theme="dark")
        assert settings.theme == "dark"

    def test_theme_invalid_raises_error(self):
        """Test that invalid theme raises validation error."""
        with pytest.raises(ValidationError):
            Settings(theme="invalid")

    def test_sort_order_priority(self):
        """Test sort_order set to priority."""
        settings = Settings(sort_order="priority")
        assert settings.sort_order == "priority"

    def test_sort_order_due_date(self):
        """Test sort_order set to due_date."""
        settings = Settings(sort_order="due_date")
        assert settings.sort_order == "due_date"

    def test_sort_order_created(self):
        """Test sort_order set to created."""
        settings = Settings(sort_order="created")
        assert settings.sort_order == "created"

    def test_sort_order_invalid_raises_error(self):
        """Test that invalid sort_order raises validation error."""
        with pytest.raises(ValidationError):
            Settings(sort_order="invalid")

    def test_full_settings(self):
        """Test creating settings with all fields."""
        settings = Settings(theme="dark", sort_order="priority")

        assert settings.theme == "dark"
        assert settings.sort_order == "priority"


class TestModelConfig:
    """Tests for model configuration."""

    def test_task_config_example(self):
        """Test that Task has proper config example."""
        task = Task(title="Test")

        schema = task.model_json_schema()

        assert "properties" in schema
        assert "id" in schema["properties"]
        assert "title" in schema["properties"]

    def test_project_config_example(self):
        """Test that Project has proper config example."""
        project = Project(name="Test")

        schema = project.model_json_schema()

        assert "properties" in schema
        assert "name" in schema["properties"]

    def test_settings_config_example(self):
        """Test that Settings has proper config example."""
        settings = Settings()

        schema = settings.model_json_schema()

        assert "properties" in schema
        assert "theme" in schema["properties"]
        assert "sort_order" in schema["properties"]
