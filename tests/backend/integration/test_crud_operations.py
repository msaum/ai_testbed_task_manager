"""
Integration tests for CRUD operations.

Tests end-to-end CRUD functionality using the JSON file storage layer.
"""
import pytest
from pathlib import Path
from datetime import datetime

from app.models.task import Task, TaskUpdate
from app.models.project import Project
from app.models.settings import Settings
from app.storage.json_file import JSONFileStore, SingleValueStore


class TestTaskCRUD:
    """Integration tests for Task CRUD operations."""

    def test_task_crud_lifecycle(self, temp_dir):
        """
        Test complete CRUD lifecycle for tasks.

        1. Create (add) a task
        2. Read (get) the task
        3. Update the task
        4. Delete the task
        """
        filepath = str(temp_dir / "tasks.json")
        store = JSONFileStore(filepath, Task, collection_key="items")

        # CREATE
        task = Task(
            title="Integration Test Task",
            notes="Testing CRUD operations",
            priority="high",
            project="Inbox"
        )
        created = store.add(task)
        assert created.id is not None
        assert store.count() == 1

        # READ - get_all
        all_tasks = store.get_all()
        assert len(all_tasks) == 1
        assert all_tasks[0].title == "Integration Test Task"

        # READ - get_by_id
        retrieved = store.get_by_id(created.id)
        assert retrieved is not None
        assert retrieved.title == "Integration Test Task"

        # UPDATE
        updated_task = Task(
            id=created.id,
            title="Updated Integration Test Task",
            notes="Updated notes",
            status="completed",
            priority="medium"
        )
        store.update(updated_task)

        verified = store.get_by_id(created.id)
        assert verified.title == "Updated Integration Test Task"
        assert verified.status == "completed"
        assert verified.priority == "medium"

        # DELETE
        deleted = store.delete(created.id)
        assert deleted is True
        assert store.count() == 0
        assert store.get_by_id(created.id) is None

    def test_task_bulk_operations(self, temp_dir):
        """Test bulk CRUD operations."""
        filepath = str(temp_dir / "tasks.json")
        store = JSONFileStore(filepath, Task, collection_key="items")

        # Create multiple tasks
        task_ids = []
        for i in range(10):
            task = Task(title=f"Task {i}", project=f"Project {i % 3}")
            created = store.add(task)
            task_ids.append(created.id)

        assert store.count() == 10

        # Read all
        all_tasks = store.get_all()
        assert len(all_tasks) == 10

        # Filter by project using get_by_field
        project_0_tasks = [t for t in all_tasks if t.project == "Project 0"]
        assert len(project_0_tasks) == 4  # Tasks 0, 3, 6, 9

        # Update multiple
        for task_id in task_ids[:5]:
            task = store.get_by_id(task_id)
            task.status = "completed"
            task.priority = "low"
            store.update(task)

        # Verify updates
        for task_id in task_ids[:5]:
            task = store.get_by_id(task_id)
            assert task.status == "completed"
            assert task.priority == "low"


class TestProjectCRUD:
    """Integration tests for Project CRUD operations."""

    def test_project_crud_lifecycle(self, temp_dir):
        """Test complete CRUD lifecycle for projects."""
        filepath = str(temp_dir / "projects.json")
        store = JSONFileStore(filepath, Project, collection_key="items")

        # CREATE
        project = Project(name="Integration Test Project")
        created = store.add(project)
        assert store.count() == 1

        # READ
        # Project uses name as identifier, not id
        retrieved = store.get_by_field("name", "Integration Test Project")
        assert retrieved is not None
        assert retrieved.name == "Integration Test Project"

        # UPDATE - Project uses name as identifier, so we need to
        # delete the old one and create a new one (or update by field)
        # Since we can't update by name directly, delete and recreate
        store.delete_by_field("name", "Integration Test Project")
        assert store.count() == 0

        # Create with new name
        updated_project = Project(name="Updated Project Name")
        store.add(updated_project)

        verified = store.get_by_field("name", "Updated Project Name")
        assert verified is not None

        # DELETE
        deleted = store.delete_by_field("name", "Updated Project Name")
        assert deleted == 1
        assert store.count() == 0


class TestSettingsCRUD:
    """Integration tests for Settings CRUD operations."""

    def test_settings_crud_lifecycle(self, temp_dir):
        """Test complete CRUD lifecycle for settings."""
        filepath = str(temp_dir / "settings.json")
        store = SingleValueStore(filepath, Settings)

        # CREATE/UPDATE
        settings = Settings(theme="dark", sort_order="priority")
        store.update(settings)

        # READ
        retrieved = store.get()
        assert retrieved.theme == "dark"
        assert retrieved.sort_order == "priority"

        # UPDATE
        updated_settings = Settings(theme="light", sort_order="created")
        store.update(updated_settings)

        verified = store.get()
        assert verified.theme == "light"
        assert verified.sort_order == "created"


class TestCrossEntityRelationships:
    """Tests for cross-entity relationships."""

    def test_task_project_relationship(self, temp_dir):
        """Test that tasks can reference projects."""
        filepath = str(temp_dir / "data.json")
        task_store = JSONFileStore(filepath, Task, collection_key="items")

        # Create tasks with different projects
        task_store.add(Task(title="Task 1", project="Work"))
        task_store.add(Task(title="Task 2", project="Work"))
        task_store.add(Task(title="Task 3", project="Personal"))

        # Filter by project
        work_tasks = [t for t in task_store.get_all() if t.project == "Work"]
        assert len(work_tasks) == 2

        personal_tasks = [t for t in task_store.get_all() if t.project == "Personal"]
        assert len(personal_tasks) == 1

    def test_task_priority_filtering(self, temp_dir):
        """Test filtering tasks by priority."""
        filepath = str(temp_dir / "data.json")
        task_store = JSONFileStore(filepath, Task, collection_key="items")

        task_store.add(Task(title="Low Priority", priority="low"))
        task_store.add(Task(title="Medium Priority", priority="medium"))
        task_store.add(Task(title="High Priority", priority="high"))
        task_store.add(Task(title="Another High", priority="high"))

        # Filter by priority
        high_priority = [t for t in task_store.get_all() if t.priority == "high"]
        assert len(high_priority) == 2


class TestDateOperations:
    """Tests for date-related operations."""

    def test_task_due_date(self, temp_dir):
        """Test task with due date."""
        filepath = str(temp_dir / "data.json")
        task_store = JSONFileStore(filepath, Task, collection_key="items")

        due_date = datetime(2026, 2, 15, 23, 59, 59)
        task = Task(title="Due Task", due_date=due_date)
        task_store.add(task)

        retrieved = task_store.get_by_id(task.id)
        assert retrieved.due_date is not None
        # Note: datetime comparison may have precision issues
        assert retrieved.due_date.strftime("%Y-%m-%d") == due_date.strftime("%Y-%m-%d")

    def test_task_sort_by_due_date(self, temp_dir):
        """Test sorting tasks by due date."""
        filepath = str(temp_dir / "data.json")
        task_store = JSONFileStore(filepath, Task, collection_key="items")

        from datetime import timedelta

        task1 = Task(title="First", due_date=datetime(2026, 2, 20))
        task2 = Task(title="Second", due_date=datetime(2026, 2, 10))
        task3 = Task(title="Third", due_date=datetime(2026, 2, 15))

        task_store.add(task1)
        task_store.add(task2)
        task_store.add(task3)

        # Sort by due date
        all_tasks = task_store.get_all()
        sorted_tasks = sorted(all_tasks, key=lambda t: t.due_date if t.due_date else datetime.max)

        assert sorted_tasks[0].title == "Second"
        assert sorted_tasks[1].title == "Third"
        assert sorted_tasks[2].title == "First"


class TestErrorHandling:
    """Tests for error handling in CRUD operations."""

    def test_add_duplicate_id_raises_error(self, temp_dir):
        """Test that adding duplicate ID raises an error."""
        filepath = str(temp_dir / "data.json")
        task_store = JSONFileStore(filepath, Task, collection_key="items")

        task1 = Task(title="First", id="same-id")
        task_store.add(task1)

        task2 = Task(title="Second", id="same-id")
        with pytest.raises(Exception):  # StorageError
            task_store.add(task2)

    def test_update_nonexistent_raises_error(self, temp_dir):
        """Test that updating non-existent task raises an error."""
        filepath = str(temp_dir / "data.json")
        task_store = JSONFileStore(filepath, Task, collection_key="items")

        fake_task = Task(title="Fake", id="nonexistent-id")
        with pytest.raises(Exception):  # StorageError
            task_store.update(fake_task)

    def test_delete_nonexistent_returns_false(self, temp_dir):
        """Test that deleting non-existent task returns False."""
        filepath = str(temp_dir / "data.json")
        task_store = JSONFileStore(filepath, Task, collection_key="items")

        deleted = task_store.delete("nonexistent-id")
        assert deleted is False
