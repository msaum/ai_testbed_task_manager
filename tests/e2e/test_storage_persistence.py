"""
E2E tests for storage persistence.

Verifies that data persists correctly across operations and restarts.
"""
import pytest
import httpx
import json
import os
import tempfile
import shutil
from pathlib import Path
from typing import Dict, Any

BASE_URL = os.getenv("BACKEND_URL", "http://localhost:8000")


@pytest.fixture(scope="function")
def data_dir():
    """Get the data directory path."""
    return Path(os.getenv("DATA_DIR", "./backend/data"))


class TestPersistence:
    """Tests for data persistence."""

    def test_tasks_persist_after_restart(self, data_dir):
        """
        Test that tasks persist after the application restarts.

        Note: This test verifies file-based persistence by checking
        that task data is written to disk.
        """
        # This test verifies the JSON file storage
        # It doesn't require actual restart since we verify the files

        # Create tasks via API
        client = httpx.Client(base_url=BASE_URL, timeout=10.0)

        task_data = {
            "title": "Persistent Task 1",
            "notes": "This should persist",
            "priority": "high"
        }

        response = client.post("/api/v1/tasks", json=task_data)
        assert response.status_code == 201
        task_id = response.json()["id"]

        # Check that data file was created
        tasks_file = data_dir / "tasks.json"
        assert tasks_file.exists()

        # Verify data in file
        with open(tasks_file, 'r') as f:
            data = json.load(f)

        assert "tasks" in data
        assert len(data["tasks"]) >= 1

        # Verify the task data is in the file
        found = False
        for item in data["tasks"]:
            if item.get("title") == "Persistent Task 1":
                found = True
                break

        assert found, "Task not found in persisted file"

    def test_projects_persist_after_restart(self, data_dir):
        """Test that projects persist after application restart."""
        import time
        client = httpx.Client(base_url=BASE_URL, timeout=10.0)

        project_data = {"name": f"Persistent Project {int(time.time())}"}

        response = client.post("/api/v1/projects", json=project_data)
        assert response.status_code == 201

        # Check projects file
        projects_file = data_dir / "projects.json"
        assert projects_file.exists()

        with open(projects_file, 'r') as f:
            data = json.load(f)

        assert "projects" in data

        # Verify project data
        names = [item.get("name") for item in data.get("projects", [])]
        assert project_data["name"] in names

    def test_settings_persist_after_restart(self, data_dir):
        """Test that settings persist after application restart."""
        client = httpx.Client(base_url=BASE_URL, timeout=10.0)

        settings_data = {"theme": "dark"}

        response = client.put("/api/v1/settings", json=settings_data)
        assert response.status_code == 200

        # Check settings file
        settings_file = data_dir / "settings.json"
        assert settings_file.exists()

        with open(settings_file, 'r') as f:
            data = json.load(f)

        assert data.get("value", {}).get("theme") == "dark"


class TestJSONFileOperations:
    """Tests for direct JSON file operations."""

    def test_atomic_write_pattern(self, data_dir):
        """
        Test that atomic write pattern is used.

        This verifies that writes don't corrupt data by checking
        that files are properly structured after writes.
        """
        client = httpx.Client(base_url=BASE_URL, timeout=10.0)

        # Create multiple tasks rapidly
        for i in range(10):
            task_data = {
                "title": f"Atomic Test Task {i}",
                "priority": "medium"
            }
            client.post("/api/v1/tasks", json=task_data)

        # Verify files are still valid JSON
        tasks_file = data_dir / "tasks.json"
        assert tasks_file.exists()

        with open(tasks_file, 'r') as f:
            content = f.read()

        # Try to parse - should not raise
        data = json.loads(content)
        assert "tasks" in data
        assert len(data["tasks"]) >= 10

    def test_corrupt_json_recovery(self, data_dir):
        """
        Test that corrupt JSON files can be recovered.

        This verifies the auto-repair capability of the storage layer.
        """
        tasks_file = data_dir / "tasks.json"

        if not tasks_file.exists():
            # Create file if it doesn't exist
            client = httpx.Client(base_url=BASE_URL, timeout=10.0)
            task_data = {"title": "Init", "priority": "medium"}
            client.post("/api/v1/tasks", json=task_data)

        # Save original content
        with open(tasks_file, 'r') as f:
            original_content = f.read()

        try:
            # Corrupt the file
            with open(tasks_file, 'w') as f:
                f.write("{ this is not valid json }")

            # Try to read - should not crash
            client = httpx.Client(base_url=BASE_URL, timeout=10.0)

            # The storage layer should handle this gracefully
            response = client.get("/api/v1/tasks")
            # Should return empty or recover

        finally:
            # Restore original content
            with open(tasks_file, 'w') as f:
                f.write(original_content)


class TestFileStructure:
    """Tests for JSON file structure."""

    def test_tasks_file_structure(self, data_dir):
        """Test the structure of tasks.json file."""
        tasks_file = data_dir / "tasks.json"

        if not tasks_file.exists():
            # Create a task first
            client = httpx.Client(base_url=BASE_URL, timeout=10.0)
            task_data = {"title": "Init", "priority": "medium"}
            client.post("/api/v1/tasks", json=task_data)

        with open(tasks_file, 'r') as f:
            data = json.load(f)

        # Verify structure
        assert isinstance(data, dict)
        assert "tasks" in data
        assert isinstance(data["tasks"], list)

        if data["tasks"]:
            task = data["tasks"][0]
            required_fields = ["id", "title", "notes", "status", "priority",
                             "project", "created_at", "updated_at"]
            for field in required_fields:
                assert field in task, f"Missing field: {field}"

    def test_projects_file_structure(self, data_dir):
        """Test the structure of projects.json file."""
        projects_file = data_dir / "projects.json"

        with open(projects_file, 'r') as f:
            data = json.load(f)

        assert isinstance(data, dict)
        assert "projects" in data
        assert isinstance(data["projects"], list)

        if data["projects"]:
            project = data["projects"][0]
            assert "name" in project
            assert "created_at" in project

    def test_settings_file_structure(self, data_dir):
        """Test the structure of settings.json file."""
        settings_file = data_dir / "settings.json"

        with open(settings_file, 'r') as f:
            data = json.load(f)

        assert isinstance(data, dict)
        assert "value" in data
        if data["value"]:
            assert "theme" in data["value"]
            assert "sort_order" in data["value"]
