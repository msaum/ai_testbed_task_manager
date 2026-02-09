"""
Unit tests for the json_file.py storage module.

Tests JSON file storage operations with Pydantic models.
"""
import pytest
import json
from pathlib import Path
from datetime import datetime

from app.storage.json_file import JSONFileStore, SingleValueStore
from app.models.task import Task, TaskCreate, TaskUpdate
from app.models.project import Project, ProjectCreate
from app.models.settings import Settings


class TestJSONFileStore:
    """Tests for the JSONFileStore class."""

    def test_store_creates_file_if_not_exists(self, temp_dir):
        """Test that store creates file with initial data if not exists."""
        filepath = str(temp_dir / "store.json")
        store = JSONFileStore(filepath, Task, collection_key="items")

        assert Path(filepath).exists()
        # File should have initial data
        with open(filepath, 'r') as f:
            data = json.load(f)
        assert "items" in data

    def test_add_item(self, temp_dir):
        """Test adding an item to the store."""
        filepath = str(temp_dir / "store.json")
        store = JSONFileStore(filepath, Task, collection_key="items")

        task = Task(title="Test Task", notes="Test notes")
        added = store.add(task)

        assert added.id == task.id
        assert store.count() == 1

    def test_add_item_duplicate_id_raises_error(self, temp_dir):
        """Test that adding duplicate ID raises StorageError."""
        filepath = str(temp_dir / "store.json")
        store = JSONFileStore(filepath, Task, collection_key="items")

        task1 = Task(title="Task 1")
        store.add(task1)

        task2 = Task(id=task1.id, title="Task 2")
        with pytest.raises(Exception):  # StorageError
            store.add(task2)

        assert store.count() == 1

    def test_get_all(self, temp_dir):
        """Test getting all items from store."""
        filepath = str(temp_dir / "store.json")
        store = JSONFileStore(filepath, Task, collection_key="items")

        # Add multiple items
        for i in range(5):
            store.add(Task(title=f"Task {i}"))

        all_tasks = store.get_all()

        assert len(all_tasks) == 5
        assert all(isinstance(task, Task) for task in all_tasks)

    def test_get_by_id(self, temp_dir):
        """Test getting an item by ID."""
        filepath = str(temp_dir / "store.json")
        store = JSONFileStore(filepath, Task, collection_key="items")

        task = Task(title="Found Task")
        store.add(task)

        found = store.get_by_id(task.id)

        assert found is not None
        assert found.id == task.id
        assert found.title == task.title

    def test_get_by_id_not_found(self, temp_dir):
        """Test getting non-existent item by ID."""
        filepath = str(temp_dir / "store.json")
        store = JSONFileStore(filepath, Task, collection_key="items")

        found = store.get_by_id("non-existent-id")

        assert found is None

    def test_get_by_field(self, temp_dir):
        """Test getting an item by field value."""
        filepath = str(temp_dir / "store.json")
        store = JSONFileStore(filepath, Task, collection_key="items")

        task = Task(title="Priority Task", priority="high")
        store.add(task)

        found = store.get_by_field("priority", "high")

        assert found is not None
        assert found.priority == "high"

    def test_get_by_field_not_found(self, temp_dir):
        """Test getting item by field value that doesn't match."""
        filepath = str(temp_dir / "store.json")
        store = JSONFileStore(filepath, Task, collection_key="items")

        store.add(Task(title="Task", priority="medium"))

        found = store.get_by_field("priority", "high")

        assert found is None

    def test_update_item(self, temp_dir):
        """Test updating an existing item."""
        filepath = str(temp_dir / "store.json")
        store = JSONFileStore(filepath, Task, collection_key="items")

        task = Task(title="Original Title")
        store.add(task)

        updated_task = Task(
            id=task.id,
            title="Updated Title",
            notes="New notes"
        )
        result = store.update(updated_task)

        assert result.title == "Updated Title"
        assert result.notes == "New notes"
        assert store.get_by_id(task.id).title == "Updated Title"

    def test_update_nonexistent_raises_error(self, temp_dir):
        """Test that updating non-existent item raises error."""
        filepath = str(temp_dir / "store.json")
        store = JSONFileStore(filepath, Task, collection_key="items")

        task = Task(id="non-existent", title="Fake Task")

        with pytest.raises(Exception):  # StorageError
            store.update(task)

    def test_delete_by_id(self, temp_dir):
        """Test deleting an item by ID."""
        filepath = str(temp_dir / "store.json")
        store = JSONFileStore(filepath, Task, collection_key="items")

        task = Task(title="To Delete")
        store.add(task)

        deleted = store.delete(task.id)

        assert deleted is True
        assert store.get_by_id(task.id) is None
        assert store.count() == 0

    def test_delete_nonexistent(self, temp_dir):
        """Test deleting non-existent item."""
        filepath = str(temp_dir / "store.json")
        store = JSONFileStore(filepath, Task, collection_key="items")

        deleted = store.delete("non-existent-id")

        assert deleted is False

    def test_delete_by_field(self, temp_dir):
        """Test deleting items by field value."""
        filepath = str(temp_dir / "store.json")
        store = JSONFileStore(filepath, Task, collection_key="items")

        store.add(Task(title="Task 1", priority="high"))
        store.add(Task(title="Task 2", priority="medium"))
        store.add(Task(title="Task 3", priority="high"))

        count = store.delete_by_field("priority", "high")

        assert count == 2
        assert store.count() == 1

    def test_clear(self, temp_dir):
        """Test clearing all items from store."""
        filepath = str(temp_dir / "store.json")
        store = JSONFileStore(filepath, Task, collection_key="items")

        for i in range(5):
            store.add(Task(title=f"Task {i}"))

        store.clear()

        assert store.count() == 0

    def test_count(self, temp_dir):
        """Test counting items in store."""
        filepath = str(temp_dir / "store.json")
        store = JSONFileStore(filepath, Task, collection_key="items")

        assert store.count() == 0

        store.add(Task(title="Task 1"))
        assert store.count() == 1

        store.add(Task(title="Task 2"))
        assert store.count() == 2


class TestSingleValueStore:
    """Tests for the SingleValueStore class."""

    def test_store_creates_file_if_not_exists(self, temp_dir):
        """Test that store creates file if not exists."""
        filepath = str(temp_dir / "single.json")
        store = SingleValueStore(filepath, Settings)

        assert Path(filepath).exists()

    def test_get_returns_default_when_empty(self, temp_dir):
        """Test that get returns default instance when empty."""
        filepath = str(temp_dir / "single.json")
        store = SingleValueStore(filepath, Settings)

        settings = store.get()

        assert settings is not None
        assert settings.theme == "light"  # Default value

    def test_get_update(self, temp_dir):
        """Test get and update operations."""
        filepath = str(temp_dir / "single.json")
        store = SingleValueStore(filepath, Settings)

        settings = Settings(theme="dark", sort_order="priority")
        store.update(settings)

        retrieved = store.get()

        assert retrieved.theme == "dark"
        assert retrieved.sort_order == "priority"

    def test_update_preserves_other_values(self, temp_dir):
        """Test that update preserves unchanged values."""
        filepath = str(temp_dir / "single.json")
        store = SingleValueStore(filepath, Settings)

        settings = Settings(theme="dark", sort_order="priority")
        store.update(settings)

        # Update only theme
        new_settings = Settings(theme="light", sort_order=settings.sort_order)
        store.update(new_settings)

        retrieved = store.get()
        assert retrieved.theme == "light"
        assert retrieved.sort_order == "priority"


class TestPersistence:
    """Tests for data persistence across store instances."""

    def test_persistence_across_instances(self, temp_dir):
        """Test that data persists across store instances."""
        filepath = str(temp_dir / "persist.json")

        # First instance - add data
        store1 = JSONFileStore(filepath, Task, collection_key="items")
        task = Task(title="Persistent Task")
        store1.add(task)

        # Second instance - read data
        store2 = JSONFileStore(filepath, Task, collection_key="items")

        assert store2.count() == 1
        retrieved = store2.get_by_id(task.id)
        assert retrieved is not None
        assert retrieved.title == "Persistent Task"


class TestModelCompatibility:
    """Tests for compatibility with various model configurations."""

    def test_store_with_custom_collection_key(self, temp_dir):
        """Test store with custom collection key."""
        filepath = str(temp_dir / "custom.json")
        store = JSONFileStore(filepath, Task, collection_key="tasks")

        task = Task(title="Custom Key Task")
        store.add(task)

        # Verify data was written with custom key
        with open(filepath, 'r') as f:
            data = json.load(f)
        assert "tasks" in data
        assert "items" not in data

    def test_store_with_initial_data(self, temp_dir):
        """Test store with initial data."""
        filepath = str(temp_dir / "initial.json")
        initial = {
            "items": [
                {"id": "1", "title": "Initial Task", "notes": "", "status": "active",
                 "priority": "medium", "project": "Inbox"}
            ]
        }
        store = JSONFileStore(filepath, Task, collection_key="items", initial_data=initial)

        assert store.count() == 1
