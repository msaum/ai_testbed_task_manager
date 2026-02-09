"""
Integration tests for data persistence across container restarts.

Tests that verify data persists correctly when the application
is restarted (simulating container restart).
"""
import pytest
import json
import os
import shutil
import tempfile
from pathlib import Path
from datetime import datetime

from app.models.task import Task
from app.models.project import Project
from app.models.settings import Settings
from app.storage.json_file import JSONFileStore, SingleValueStore


class TestTaskPersistenceAcrossRestart:
    """Tests for task persistence across restart."""

    def test_tasks_persist_after_restart(self, temp_dir):
        """Test that tasks persist after simulated restart."""
        tasks_file = str(temp_dir / "tasks.json")

        # First "run" - create tasks
        store1 = JSONFileStore(tasks_file, Task, collection_key="items")
        task1 = store1.add(Task(title="Task 1", notes="Persistent task 1", priority="high"))
        store1.add(Task(title="Task 2", notes="Persistent task 2", priority="medium"))
        store1.add(Task(title="Task 3", notes="Persistent task 3", priority="low"))

        assert store1.count() == 3

        # Simulate restart by deleting old store references
        del store1

        # Second "run" - create new store instance
        store2 = JSONFileStore(tasks_file, Task, collection_key="items")

        # Verify tasks persist
        assert store2.count() == 3

        # Verify specific task by ID
        retrieved = store2.get_by_id(task1.id)
        assert retrieved is not None
        assert retrieved.title == "Task 1"

    def test_tasks_persist_with_all_fields(self, temp_dir):
        """Test that all task fields persist after restart."""
        tasks_file = str(temp_dir / "tasks.json")

        # First run - create task with all fields
        store1 = JSONFileStore(tasks_file, Task, collection_key="items")
        original_task = Task(
            title="Complete Project",
            notes="Finish the API design",
            status="pending",
            priority="high",
            project="Work",
            due_date=datetime(2026, 2, 15, 23, 59, 59)
        )
        created = store1.add(original_task)

        # Restart
        del store1
        store2 = JSONFileStore(tasks_file, Task, collection_key="items")

        # Verify all fields persist
        retrieved = store2.get_by_id(created.id)
        assert retrieved is not None
        assert retrieved.title == "Complete Project"
        assert retrieved.notes == "Finish the API design"
        assert retrieved.status == "pending"
        assert retrieved.priority == "high"
        assert retrieved.project == "Work"
        assert retrieved.due_date is not None
        assert retrieved.due_date.strftime("%Y-%m-%d") == "2026-02-15"

    def test_completed_tasks_remain_completed_after_restart(self, temp_dir):
        """Test that completed tasks remain completed after restart."""
        tasks_file = str(temp_dir / "tasks.json")

        store1 = JSONFileStore(tasks_file, Task, collection_key="items")
        task1 = Task(title="Completed Task", status="completed")
        task2 = Task(title="Pending Task", status="pending")
        store1.add(task1)
        store1.add(task2)

        # Restart
        del store1
        store2 = JSONFileStore(tasks_file, Task, collection_key="items")

        completed = [t for t in store2.get_all() if t.status == "completed"]
        pending = [t for t in store2.get_all() if t.status == "pending"]

        assert len(completed) == 1
        assert len(pending) == 1


class TestProjectPersistenceAcrossRestart:
    """Tests for project persistence across restart."""

    def test_projects_persist_after_restart(self, temp_dir):
        """Test that projects persist after simulated restart."""
        projects_file = str(temp_dir / "projects.json")

        # First run - create projects
        store1 = JSONFileStore(projects_file, Project, collection_key="items")
        store1.add(Project(name="Work"))
        store1.add(Project(name="Personal"))
        store1.add(Project(name="Inbox"))

        assert store1.count() == 3

        # Restart
        del store1
        store2 = JSONFileStore(projects_file, Project, collection_key="items")

        assert store2.count() == 3
        names = [p.name for p in store2.get_all()]
        assert "Work" in names
        assert "Personal" in names
        assert "Inbox" in names

    def test_project_names_case_preserved(self, temp_dir):
        """Test that project name casing is preserved."""
        projects_file = str(temp_dir / "projects.json")

        store1 = JSONFileStore(projects_file, Project, collection_key="items")
        store1.add(Project(name="MyImportantProject"))
        store1.add(Project(name="another-project"))

        del store1
        store2 = JSONFileStore(projects_file, Project, collection_key="items")

        names = [p.name for p in store2.get_all()]
        assert "MyImportantProject" in names
        assert "another-project" in names


class TestSettingsPersistenceAcrossRestart:
    """Tests for settings persistence across restart."""

    def test_settings_persist_after_restart(self, temp_dir):
        """Test that settings persist after simulated restart."""
        settings_file = str(temp_dir / "settings.json")

        # First run - update settings
        store1 = SingleValueStore(settings_file, Settings)
        store1.update(Settings(theme="dark", sort_order="priority"))

        # Restart
        del store1
        store2 = SingleValueStore(settings_file, Settings)

        settings = store2.get()
        assert settings.theme == "dark"
        assert settings.sort_order == "priority"

    def test_default_settings_when_no_file(self, temp_dir):
        """Test that default settings are returned when no file exists."""
        settings_file = str(temp_dir / "settings.json")

        # Ensure file doesn't exist
        path = Path(settings_file)
        if path.exists():
            path.unlink()

        store = SingleValueStore(settings_file, Settings)
        settings = store.get()

        assert settings.theme == "light"  # Default
        assert settings.sort_order == "created"  # Default

    def test_settings_can_be_updated_after_restart(self, temp_dir):
        """Test that settings can be updated after restart."""
        settings_file = str(temp_dir / "settings.json")

        # First run - set initial value
        store1 = SingleValueStore(settings_file, Settings)
        store1.update(Settings(theme="dark"))

        # Restart
        del store1
        store2 = SingleValueStore(settings_file, Settings)

        # Verify initial value persisted
        assert store2.get().theme == "dark"

        # Update after restart
        store2.update(Settings(theme="light"))

        # Restart again
        del store2
        store3 = SingleValueStore(settings_file, Settings)

        assert store3.get().theme == "light"


class TestCombinedPersistence:
    """Tests for combined persistence of tasks, projects, and settings."""

    def test_all_entities_persist_together(self, temp_dir):
        """Test that all entities persist together after restart."""
        tasks_file = str(temp_dir / "tasks.json")
        projects_file = str(temp_dir / "projects.json")
        settings_file = str(temp_dir / "settings.json")

        # First run
        task_store1 = JSONFileStore(tasks_file, Task, collection_key="items")
        project_store1 = JSONFileStore(projects_file, Project, collection_key="items")
        settings_store1 = SingleValueStore(settings_file, Settings)

        # Add data
        task_store1.add(Task(title="Task 1", project="Work"))
        project_store1.add(Project(name="Work"))
        settings_store1.update(Settings(theme="dark"))

        # Restart
        del task_store1, project_store1, settings_store1

        # Second run
        task_store2 = JSONFileStore(tasks_file, Task, collection_key="items")
        project_store2 = JSONFileStore(projects_file, Project, collection_key="items")
        settings_store2 = SingleValueStore(settings_file, Settings)

        # Verify all data persisted
        assert task_store2.count() == 1
        assert project_store2.count() == 1
        assert settings_store2.get().theme == "dark"

    def test_cross_entity_relationships_preserved(self, temp_dir):
        """Test that task-project relationships are preserved."""
        tasks_file = str(temp_dir / "tasks.json")
        projects_file = str(temp_dir / "projects.json")

        # First run
        task_store1 = JSONFileStore(tasks_file, Task, collection_key="items")
        project_store1 = JSONFileStore(projects_file, Project, collection_key="items")

        project_store1.add(Project(name="Work"))
        project_store1.add(Project(name="Personal"))
        task_store1.add(Task(title="Work Task 1", project="Work"))
        task_store1.add(Task(title="Work Task 2", project="Work"))
        task_store1.add(Task(title="Personal Task", project="Personal"))

        # Restart
        del task_store1, project_store1

        # Second run
        task_store2 = JSONFileStore(tasks_file, Task, collection_key="items")
        project_store2 = JSONFileStore(projects_file, Project, collection_key="items")

        # Verify project relationship
        work_tasks = [t for t in task_store2.get_all() if t.project == "Work"]
        personal_tasks = [t for t in task_store2.get_all() if t.project == "Personal"]

        assert len(work_tasks) == 2
        assert len(personal_tasks) == 1
        assert project_store2.count() == 2


class TestPersistenceFileFormat:
    """Tests for verifying file format after restart."""

    def test_tasks_file_structure_preserved(self, temp_dir):
        """Test that tasks file structure is preserved after restart."""
        tasks_file = str(temp_dir / "tasks.json")

        # First run
        store1 = JSONFileStore(tasks_file, Task, collection_key="items")
        store1.add(Task(title="Test Task"))

        # Restart
        del store1
        store2 = JSONFileStore(tasks_file, Task, collection_key="items")

        # Read raw file
        with open(tasks_file, 'r') as f:
            content = f.read()

        # Verify it's valid JSON
        data = json.loads(content)
        assert isinstance(data, dict)
        assert "items" in data
        assert isinstance(data["items"], list)

    def test_json_format_is_consistent(self, temp_dir):
        """Test that JSON format is consistent across restarts."""
        tasks_file = str(temp_dir / "tasks.json")

        # First run
        store1 = JSONFileStore(tasks_file, Task, collection_key="items")
        store1.add(Task(title="Task 1"))
        store1.add(Task(title="Task 2"))

        # Read raw content
        with open(tasks_file, 'r') as f:
            content1 = f.read()

        # Restart
        del store1
        store2 = JSONFileStore(tasks_file, Task, collection_key="items")

        # Read raw content again
        with open(tasks_file, 'r') as f:
            content2 = f.read()

        # Both should be valid JSON with same structure
        data1 = json.loads(content1)
        data2 = json.loads(content2)

        assert len(data1["items"]) == 2
        assert len(data2["items"]) == 2


class TestPersistenceAcrossMultipleRestarts:
    """Tests for persistence across multiple restarts."""

    def test_data_survives_three_restarts(self, temp_dir):
        """Test that data survives three consecutive restarts."""
        tasks_file = str(temp_dir / "tasks.json")

        # First run
        store1 = JSONFileStore(tasks_file, Task, collection_key="items")
        store1.add(Task(title="Task 1"))
        store1.add(Task(title="Task 2"))

        # Second run
        del store1
        store2 = JSONFileStore(tasks_file, Task, collection_key="items")
        store2.add(Task(title="Task 3"))
        store2.add(Task(title="Task 4"))

        # Third run
        del store2
        store3 = JSONFileStore(tasks_file, Task, collection_key="items")

        assert store3.count() == 4

        # Fourth run to verify
        del store3
        store4 = JSONFileStore(tasks_file, Task, collection_key="items")
        assert store4.count() == 4

    def test_data_survives_many_restarts(self, temp_dir):
        """Test that data survives many consecutive restarts."""
        tasks_file = str(temp_dir / "tasks.json")

        tasks_to_add = 20
        for i in range(tasks_to_add):
            store = JSONFileStore(tasks_file, Task, collection_key="items")
            store.add(Task(title=f"Task {i+1}"))
            del store

        # Final verification
        final_store = JSONFileStore(tasks_file, Task, collection_key="items")
        assert final_store.count() == tasks_to_add


class TestPersistenceWithConcurrentAccess:
    """Tests for persistence with concurrent access patterns."""

    def test_sequential_access_preserves_data(self, temp_dir):
        """Test that sequential access preserves data."""
        tasks_file = str(temp_dir / "tasks.json")

        # Access pattern: create, read, update, read, delete, read
        store1 = JSONFileStore(tasks_file, Task, collection_key="items")
        store1.add(Task(title="Task 1"))
        store1.add(Task(title="Task 2"))

        store2 = JSONFileStore(tasks_file, Task, collection_key="items")
        assert store2.count() == 2

        task = store2.get_by_id(store1.get_all()[0].id)
        task.status = "completed"
        store2.update(task)

        store3 = JSONFileStore(tasks_file, Task, collection_key="items")
        completed = [t for t in store3.get_all() if t.status == "completed"]
        assert len(completed) == 1
