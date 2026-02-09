"""
Integration tests for UI file change detection.

Tests that the storage layer properly detects and reflects changes
when files are modified externally (e.g., manual edits).
"""
import pytest
import json
import time
from pathlib import Path
from datetime import datetime

from app.models.task import Task
from app.models.project import Project
from app.models.settings import Settings
from app.storage.json_file import JSONFileStore, SingleValueStore


class TestFileChangeDetection:
    """Tests for detecting changes when files are modified."""

    def test_reload_after_external_file_change(self, temp_dir):
        """Test that store reflects changes when file is modified externally."""
        filepath = str(temp_dir / "tasks.json")

        # Create initial data via store
        store1 = JSONFileStore(filepath, Task, collection_key="items")
        store1.add(Task(title="Original Task"))

        # Simulate external file modification
        with open(filepath, 'w') as f:
            json.dump({
                "items": [
                    {
                        "id": "external-1",
                        "title": "External Task",
                        "notes": "",
                        "status": "active",
                        "priority": "medium",
                        "project": "Inbox",
                        "created_at": "2026-01-01T00:00:00",
                        "updated_at": "2026-01-01T00:00:00"
                    }
                ]
            }, f, indent=2)

        # Create new store instance - should see external changes
        store2 = JSONFileStore(filepath, Task, collection_key="items")
        tasks = store2.get_all()

        assert len(tasks) == 1
        assert tasks[0].title == "External Task"
        assert tasks[0].id == "external-1"

    def test_reload_after_multiple_external_changes(self, temp_dir):
        """Test that store reflects multiple external changes."""
        filepath = str(temp_dir / "tasks.json")

        # Create initial data
        store1 = JSONFileStore(filepath, Task, collection_key="items")
        store1.add(Task(title="Task 1"))

        # External change 1
        with open(filepath, 'w') as f:
            json.dump({
                "items": [{"id": "e1", "title": "External 1", "notes": "", "status": "active", "priority": "medium", "project": "Inbox", "created_at": "2026-01-01T00:00:00", "updated_at": "2026-01-01T00:00:00"}]
            }, f)

        store2 = JSONFileStore(filepath, Task, collection_key="items")
        assert store2.count() == 1

        # External change 2
        with open(filepath, 'w') as f:
            json.dump({
                "items": [
                    {"id": "e1", "title": "External 1 Updated", "notes": "", "status": "active", "priority": "medium", "project": "Inbox", "created_at": "2026-01-01T00:00:00", "updated_at": "2026-01-01T00:00:00"},
                    {"id": "e2", "title": "External 2", "notes": "", "status": "active", "priority": "medium", "project": "Inbox", "created_at": "2026-01-01T00:00:00", "updated_at": "2026-01-01T00:00:00"},
                    {"id": "e3", "title": "External 3", "notes": "", "status": "active", "priority": "medium", "project": "Inbox", "created_at": "2026-01-01T00:00:00", "updated_at": "2026-01-01T00:00:00"}
                ]
            }, f)

        store3 = JSONFileStore(filepath, Task, collection_key="items")
        assert store3.count() == 3
        titles = [t.title for t in store3.get_all()]
        assert "External 1 Updated" in titles
        assert "External 2" in titles
        assert "External 3" in titles


class TestUIReflectsManualEdits:
    """Tests for UI reflecting manual file edits."""

    def test_ui_shows_manually_added_tasks(self, temp_dir):
        """Test that manually added tasks appear in store."""
        filepath = str(temp_dir / "tasks.json")

        # Create initial file
        with open(filepath, 'w') as f:
            json.dump({
                "items": [
                    {
                        "id": "manual-1",
                        "title": "Manually Added Task",
                        "notes": "This was added manually",
                        "status": "active",
                        "priority": "high",
                        "project": "Inbox",
                        "created_at": "2026-01-01T00:00:00",
                        "updated_at": "2026-01-01T00:00:00"
                    }
                ]
            }, f, indent=2)

        # Create store - should see manually added task
        store = JSONFileStore(filepath, Task, collection_key="items")
        tasks = store.get_all()

        assert len(tasks) == 1
        assert tasks[0].title == "Manually Added Task"
        assert tasks[0].notes == "This was added manually"

    def test_ui_shows_manually_deleted_tasks(self, temp_dir):
        """Test that manually deleted tasks are not in store."""
        filepath = str(temp_dir / "tasks.json")

        # Create file with multiple tasks
        with open(filepath, 'w') as f:
            json.dump({
                "items": [
                    {"id": "t1", "title": "Task 1", "notes": "", "status": "pending", "priority": "medium", "project": "Inbox", "created_at": "2026-01-01T00:00:00", "updated_at": "2026-01-01T00:00:00"},
                    {"id": "t2", "title": "Task 2", "notes": "", "status": "pending", "priority": "medium", "project": "Inbox", "created_at": "2026-01-01T00:00:00", "updated_at": "2026-01-01T00:00:00"},
                    {"id": "t3", "title": "Task 3", "notes": "", "status": "pending", "priority": "medium", "project": "Inbox", "created_at": "2026-01-01T00:00:00", "updated_at": "2026-01-01T00:00:00"}
                ]
            }, f)

        store = JSONFileStore(filepath, Task, collection_key="items")

        # Verify 3 tasks
        assert store.count() == 3

        # Manually delete one task by rewriting file
        with open(filepath, 'w') as f:
            json.dump({
                "items": [
                    {"id": "t1", "title": "Task 1", "notes": "", "status": "pending", "priority": "medium", "project": "Inbox", "created_at": "2026-01-01T00:00:00", "updated_at": "2026-01-01T00:00:00"},
                    {"id": "t3", "title": "Task 3", "notes": "", "status": "pending", "priority": "medium", "project": "Inbox", "created_at": "2026-01-01T00:00:00", "updated_at": "2026-01-01T00:00:00"}
                ]
            }, f)

        # Create new store - should see 2 tasks
        store2 = JSONFileStore(filepath, Task, collection_key="items")
        assert store2.count() == 2

    def test_ui_shows_manually_updated_tasks(self, temp_dir):
        """Test that manually updated tasks reflect changes."""
        filepath = str(temp_dir / "tasks.json")

        # Create initial file
        with open(filepath, 'w') as f:
            json.dump({
                "items": [
                    {
                        "id": "updated-task",
                        "title": "Original Title",
                        "notes": "Original notes",
                        "status": "pending",
                        "priority": "medium",
                        "project": "Inbox",
                        "created_at": "2026-01-01T00:00:00",
                        "updated_at": "2026-01-01T00:00:00"
                    }
                ]
            }, f)

        store = JSONFileStore(filepath, Task, collection_key="items")
        tasks = store.get_all()
        assert tasks[0].title == "Original Title"
        assert tasks[0].status == "pending"

        # Manually update task
        with open(filepath, 'w') as f:
            json.dump({
                "items": [
                    {
                        "id": "updated-task",
                        "title": "Updated Title",
                        "notes": "Updated notes",
                        "status": "completed",
                        "priority": "high",
                        "project": "Work",
                        "created_at": "2026-01-01T00:00:00",
                        "updated_at": "2026-01-02T00:00:00"
                    }
                ]
            }, f)

        # Create new store - should see updated values
        store2 = JSONFileStore(filepath, Task, collection_key="items")
        tasks2 = store2.get_all()
        assert tasks2[0].title == "Updated Title"
        assert tasks2[0].status == "completed"
        assert tasks2[0].priority == "high"
        assert tasks2[0].project == "Work"


class TestStoreReloadBehavior:
    """Tests for store reload behavior on file changes."""

    def test_store_rereads_file_on_each_operation(self, temp_dir):
        """Test that store re-reads file on each operation (not cached)."""
        filepath = str(temp_dir / "tasks.json")

        # Create initial store and add task
        store = JSONFileStore(filepath, Task, collection_key="items")
        store.add(Task(title="Original"))

        # File changes are immediately reflected (store re-reads on each operation)
        with open(filepath, 'w') as f:
            json.dump({"items": []}, f)

        # Same instance sees new data since it re-reads file
        assert store.count() == 0

        # New instance also sees same data
        store2 = JSONFileStore(filepath, Task, collection_key="items")
        assert store2.count() == 0

    def test_concurrent_store_instances_see_latest(self, temp_dir):
        """Test that multiple store instances see latest file state."""
        filepath = str(temp_dir / "tasks.json")

        # Write initial data
        with open(filepath, 'w') as f:
            json.dump({"items": [{"id": "c1", "title": "Concurrent 1", "notes": "", "status": "active", "priority": "medium", "project": "Inbox", "created_at": "2026-01-01T00:00:00", "updated_at": "2026-01-01T00:00:00"}]}, f)

        # Create multiple store instances
        store1 = JSONFileStore(filepath, Task, collection_key="items")
        store2 = JSONFileStore(filepath, Task, collection_key="items")
        store3 = JSONFileStore(filepath, Task, collection_key="items")

        # All should see same data
        assert store1.count() == 1
        assert store2.count() == 1
        assert store3.count() == 1


class TestFileStructureChanges:
    """Tests for handling file structure changes."""

    def test_store_handles_missing_items_key(self, temp_dir):
        """Test that store handles missing items key gracefully."""
        filepath = str(temp_dir / "tasks.json")

        # File with missing items key
        with open(filepath, 'w') as f:
            json.dump({"other_key": "value"}, f)

        store = JSONFileStore(filepath, Task, collection_key="items")
        assert store.count() == 0

    def test_store_handles_items_as_none(self, temp_dir):
        """Test that store handles items being None."""
        filepath = str(temp_dir / "tasks.json")

        with open(filepath, 'w') as f:
            json.dump({"items": None}, f)

        store = JSONFileStore(filepath, Task, collection_key="items")
        # Should handle gracefully
        tasks = store.get_all()
        assert isinstance(tasks, list)

    def test_store_handles_empty_items(self, temp_dir):
        """Test that store handles empty items list."""
        filepath = str(temp_dir / "tasks.json")

        with open(filepath, 'w') as f:
            json.dump({"items": []}, f)

        store = JSONFileStore(filepath, Task, collection_key="items")
        assert store.count() == 0
        assert store.get_all() == []

    def test_store_handles_invalid_item_structure(self, temp_dir):
        """Test that store handles items with invalid structure."""
        filepath = str(temp_dir / "tasks.json")

        with open(filepath, 'w') as f:
            json.dump({
                "items": [
                    {"id": "valid", "title": "Valid Task", "notes": "", "status": "active", "priority": "medium", "project": "Inbox", "created_at": "2026-01-01T00:00:00", "updated_at": "2026-01-01T00:00:00"},
                    {"id": "invalid", "title": ""},  # Missing required fields
                    {"title": "Also Invalid"}  # Missing id
                ]
            }, f)

        store = JSONFileStore(filepath, Task, collection_key="items")
        # Valid items should be parsed, invalid ones skipped
        # The first item is explicitly valid, the third gets auto-generated UUID
        # The second item with empty title is invalid
        tasks = store.get_all()
        assert len(tasks) == 2
        valid_task = next((t for t in tasks if t.title == "Valid Task"), None)
        assert valid_task is not None


class TestProjectsFileChanges:
    """Tests for project file change detection."""

    def test_projects_reflect_external_changes(self, temp_dir):
        """Test that projects reflect external file changes."""
        filepath = str(temp_dir / "projects.json")

        # Manually create projects file
        with open(filepath, 'w') as f:
            json.dump({
                "items": [
                    {"name": "External Project 1", "created_at": "2026-01-01T00:00:00"},
                    {"name": "External Project 2", "created_at": "2026-01-01T00:00:00"}
                ]
            }, f)

        store = JSONFileStore(filepath, Project, collection_key="items")
        projects = store.get_all()

        assert len(projects) == 2
        assert projects[0].name == "External Project 1"
        assert projects[1].name == "External Project 2"

    def test_project_name_changes_reflected(self, temp_dir):
        """Test that project name changes are reflected."""
        filepath = str(temp_dir / "projects.json")

        with open(filepath, 'w') as f:
            json.dump({
                "items": [{"name": "Original Name", "created_at": "2026-01-01T00:00:00"}]
            }, f)

        store = JSONFileStore(filepath, Project, collection_key="items")
        assert store.get_by_field("name", "Original Name") is not None

        # Manually update project name
        with open(filepath, 'w') as f:
            json.dump({
                "items": [{"name": "Updated Name", "created_at": "2026-01-01T00:00:00"}]
            }, f)

        store2 = JSONFileStore(filepath, Project, collection_key="items")
        assert store2.get_by_field("name", "Original Name") is None
        assert store2.get_by_field("name", "Updated Name") is not None


class TestSettingsFileChanges:
    """Tests for settings file change detection."""

    def test_settings_reflect_external_changes(self, temp_dir):
        """Test that settings reflect external file changes."""
        filepath = str(temp_dir / "settings.json")

        # Manually update settings
        with open(filepath, 'w') as f:
            json.dump({
                "value": {"theme": "dark", "sort_order": "due_date"}
            }, f)

        store = SingleValueStore(filepath, Settings)
        settings = store.get()

        assert settings.theme == "dark"
        assert settings.sort_order == "due_date"
