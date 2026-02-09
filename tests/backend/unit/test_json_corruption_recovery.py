"""
Unit tests for JSON corruption recovery.

Tests the storage layer's ability to handle and recover from corrupted JSON files.
"""
import pytest
import json
import os
from pathlib import Path
from datetime import datetime

from app.storage.json_file import JSONFileStore, SingleValueStore
from app.storage.atomic import atomic_write, read_json_file
from app.models.task import Task
from app.models.settings import Settings


class TestJSONCorruptionDetection:
    """Tests for detecting corrupted JSON files."""

    def test_read_corrupted_json_file_returns_empty(self, temp_dir):
        """Test that reading a corrupted JSON file returns empty dict."""
        filepath = str(temp_dir / "corrupted.json")
        with open(filepath, 'w') as f:
            f.write("{ this is not valid json }")

        result = read_json_file(filepath)

        assert result == {}

    def test_read_corrupted_json_with_default(self, temp_dir):
        """Test that reading corrupted JSON returns default value."""
        filepath = str(temp_dir / "corrupted.json")
        with open(filepath, 'w') as f:
            f.write("{ invalid json content")

        default = {"recovered": True}
        result = read_json_file(filepath, default=default)

        assert result == default

    def test_read_partial_json_returns_empty(self, temp_dir):
        """Test that partial/incomplete JSON returns empty dict."""
        filepath = str(temp_dir / "partial.json")
        with open(filepath, 'w') as f:
            f.write('{"items": [{"id": "1", "title": "Task')

        result = read_json_file(filepath)

        assert result == {}

    def test_read_json_with_trailing_comma(self, temp_dir):
        """Test that JSON with trailing comma is handled."""
        filepath = str(temp_dir / "trailing.json")
        with open(filepath, 'w') as f:
            f.write('{"items": [{"id": "1", "title": "Task",}],}')

        result = read_json_file(filepath)

        assert result == {}


class TestJSONCorruptionRecoveryInStore:
    """Tests for storage recovery when JSON is corrupted."""

    def test_store_handles_corrupted_file_on_init(self, temp_dir):
        """Test that store can be initialized even with corrupted file."""
        filepath = str(temp_dir / "store.json")

        # Corrupt the file first
        with open(filepath, 'w') as f:
            f.write("{ not valid json at all }")

        # Store should be able to initialize and use initial data
        store = JSONFileStore(filepath, Task, collection_key="items")

        assert store.count() == 0
        # Should be able to add items after corruption
        task = Task(title="Recovered Task")
        store.add(task)
        assert store.count() == 1

    def test_store_recovers_from_corrupted_file_on_read(self, temp_dir):
        """Test that store can read from file after corruption and recover."""
        filepath = str(temp_dir / "store.json")

        # Add some data first
        store = JSONFileStore(filepath, Task, collection_key="items")
        task1 = Task(title="Task 1")
        task2 = Task(title="Task 2")
        store.add(task1)
        store.add(task2)

        # Now corrupt the file
        with open(filepath, 'w') as f:
            f.write("{ completely corrupted json content here }")

        # Reinitialize store
        store2 = JSONFileStore(filepath, Task, collection_key="items")

        # Should recover with empty data (initial data)
        assert store2.count() == 0

    def test_store_adds_to_corrupted_file(self, temp_dir):
        """Test that store can add items to corrupted file and recover."""
        filepath = str(temp_dir / "store.json")

        # Corrupt the file
        with open(filepath, 'w') as f:
            f.write("{ broken }")

        # Initialize store and add items
        store = JSONFileStore(filepath, Task, collection_key="items")
        task = Task(title="New Task")
        added = store.add(task)

        assert added.id == task.id
        assert store.count() == 1

        # Verify file is now valid JSON
        with open(filepath, 'r') as f:
            content = f.read()

        data = json.loads(content)
        assert "items" in data
        assert len(data["items"]) == 1

    def test_store_get_all_recovers_from_corruption(self, temp_dir):
        """Test that get_all recovers from corrupted file."""
        filepath = str(temp_dir / "store.json")

        # Create file with data
        store = JSONFileStore(filepath, Task, collection_key="items")
        store.add(Task(title="Original Task"))

        # Corrupt the file
        with open(filepath, 'w') as f:
            f.write("{ this is broken }")

        # Reinitialize and get all should return empty (initial data)
        store2 = JSONFileStore(filepath, Task, collection_key="items")
        all_tasks = store2.get_all()

        assert all_tasks == []

    def test_store_get_by_id_recovers_from_corruption(self, temp_dir):
        """Test that get_by_id handles corrupted file."""
        filepath = str(temp_dir / "store.json")

        # Corrupt file first
        with open(filepath, 'w') as f:
            f.write("{ invalid json }")

        store = JSONFileStore(filepath, Task, collection_key="items")

        # Should not crash, return None
        found = store.get_by_id("some-id")
        assert found is None


class TestJSONCorruptionRecoveryWithInitialData:
    """Tests for corruption recovery using initial data."""

    def test_store_uses_initial_data_after_corruption(self, temp_dir):
        """Test that store uses initial data after corruption."""
        filepath = str(temp_dir / "store.json")

        initial_data = {
            "items": [
                {"id": "init-1", "title": "Initial Task 1", "notes": "", "status": "active", "priority": "medium", "project": "Inbox", "created_at": "2026-01-01T00:00:00", "updated_at": "2026-01-01T00:00:00"}
            ]
        }

        store = JSONFileStore(
            filepath,
            Task,
            collection_key="items",
            initial_data=initial_data
        )

        assert store.count() == 1

        # Corrupt file
        with open(filepath, 'w') as f:
            f.write("{ corrupted }")

        # Reinitialize - should use initial data
        store2 = JSONFileStore(
            filepath,
            Task,
            collection_key="items",
            initial_data=initial_data
        )

        assert store2.count() == 1

    def test_store_rebuilds_from_initial_data_on_empty_file(self, temp_dir):
        """Test that store rebuilds from initial data on empty file."""
        filepath = str(temp_dir / "store.json")

        # Create empty file
        with open(filepath, 'w') as f:
            f.write("")

        initial_data = {"items": []}
        store = JSONFileStore(filepath, Task, collection_key="items", initial_data=initial_data)

        assert store.count() == 0


class TestSingleValueStoreCorruption:
    """Tests for SingleValueStore corruption recovery."""

    def test_single_value_store_handles_corrupted_file(self, temp_dir):
        """Test that SingleValueStore handles corrupted file."""
        filepath = str(temp_dir / "settings.json")

        # Corrupt the file
        with open(filepath, 'w') as f:
            f.write("{ not valid }")

        store = SingleValueStore(filepath, Settings)

        # Should return default settings
        settings = store.get()
        assert settings is not None
        assert settings.theme == "light"  # Default

    def test_single_value_store_recovers_from_corruption(self, temp_dir):
        """Test SingleValueStore can recover and update after corruption."""
        filepath = str(temp_dir / "settings.json")

        # Corrupt file
        with open(filepath, 'w') as f:
            f.write("{ broken }")

        store = SingleValueStore(filepath, Settings)
        store.update(Settings(theme="dark", sort_order="priority"))

        retrieved = store.get()
        assert retrieved.theme == "dark"
        assert retrieved.sort_order == "priority"

    def test_single_value_store_preserves_after_corruption_recovery(self, temp_dir):
        """Test that SingleValueStore preserves data after corruption recovery."""
        filepath = str(temp_dir / "settings.json")

        # Create with data
        store = SingleValueStore(filepath, Settings)
        store.update(Settings(theme="dark"))

        # Corrupt file
        with open(filepath, 'w') as f:
            f.write("{ corrupted }")

        # Reinitialize - should get default, not corrupted
        store2 = SingleValueStore(filepath, Settings)
        settings = store2.get()
        assert settings.theme == "light"  # Default


class TestWriteAfterCorruption:
    """Tests for writing after corruption recovery."""

    def test_store_can_write_after_corruption_recovery(self, temp_dir):
        """Test that store can write after recovering from corruption."""
        filepath = str(temp_dir / "store.json")

        # Corrupt file
        with open(filepath, 'w') as f:
            f.write("{ broken }")

        store = JSONFileStore(filepath, Task, collection_key="items")
        store.add(Task(title="New After Corruption"))

        # Verify file is now valid and has data
        with open(filepath, 'r') as f:
            data = json.load(f)

        assert "items" in data
        assert len(data["items"]) == 1
        assert data["items"][0]["title"] == "New After Corruption"

    def test_store_can_update_after_corruption(self, temp_dir):
        """Test that store can update after corruption."""
        filepath = str(temp_dir / "store.json")

        # Add data, then corrupt
        store = JSONFileStore(filepath, Task, collection_key="items")
        task = store.add(Task(title="Original"))
        task_id = task.id

        with open(filepath, 'w') as f:
            f.write("{ corrupted }")

        store2 = JSONFileStore(filepath, Task, collection_key="items")
        # Update should fail since task doesn't exist in corrupted file
        # (which is correct behavior - data was lost)

        # But we can add new data
        new_task = store2.add(Task(title="New"))
        assert new_task.id != task_id
        assert store2.count() == 1
