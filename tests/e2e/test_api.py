"""
End-to-end tests for the API endpoints.

These tests verify the complete API behavior including:
- Health checks
- Task CRUD operations
- Project operations
- Settings operations
- Error handling
"""
import pytest
import httpx
from datetime import datetime
from typing import Dict, Any

BASE_URL = "http://localhost:8000"


@pytest.fixture(scope="module")
def client():
    """Create an HTTP client for API testing."""
    return httpx.Client(base_url=BASE_URL, timeout=10.0)


class TestHealth:
    """Tests for the health check endpoint."""

    def test_health_check(self, client: httpx.Client):
        """Test that the health endpoint returns healthy status."""
        response = client.get("/health")
        assert response.status_code == 200

        data = response.json()
        assert data["status"] == "healthy"
        assert "service" in data
        assert "version" in data


class TestRoot:
    """Tests for the root endpoint."""

    def test_root_endpoint(self, client: httpx.Client):
        """Test that the root endpoint returns API information."""
        response = client.get("/")
        assert response.status_code == 200

        data = response.json()
        assert "name" in data
        assert "version" in data
        assert "docs" in data


class TestTasks:
    """Tests for the tasks API endpoints."""

    def test_get_all_tasks_empty(self, client: httpx.Client):
        """Test getting tasks when none exist."""
        response = client.get("/api/v1/tasks")
        assert response.status_code == 200

        data = response.json()
        assert "tasks" in data
        assert "count" in data
        assert isinstance(data["tasks"], list)

    def test_create_task(self, client: httpx.Client):
        """Test creating a new task."""
        task_data = {
            "title": "E2E Test Task",
            "notes": "Testing API endpoints",
            "priority": "high",
            "project": "Inbox"
        }

        response = client.post("/api/v1/tasks", json=task_data)
        assert response.status_code == 201

        data = response.json()
        assert data["title"] == task_data["title"]
        assert data["notes"] == task_data["notes"]
        assert data["priority"] == "high"
        assert "id" in data
        assert data["status"] == "pending"

        return data["id"]

    def test_get_task_by_id(self, client: httpx.Client):
        """Test getting a specific task by ID."""
        # First create a task
        task_data = {"title": "Get By ID Test"}
        create_response = client.post("/api/v1/tasks", json=task_data)
        task_id = create_response.json()["id"]

        # Then retrieve it
        response = client.get(f"/api/v1/tasks/{task_id}")
        assert response.status_code == 200

        data = response.json()
        assert data["title"] == "Get By ID Test"
        assert data["id"] == task_id

    def test_update_task(self, client: httpx.Client):
        """Test updating an existing task."""
        # Create a task
        task_data = {"title": "Original Title"}
        create_response = client.post("/api/v1/tasks", json=task_data)
        task_id = create_response.json()["id"]

        # Update it
        update_data = {"title": "Updated Title", "status": "completed"}
        response = client.put(f"/api/v1/tasks/{task_id}", json=update_data)
        assert response.status_code == 200

        data = response.json()
        assert data["title"] == "Updated Title"
        assert data["status"] == "completed"

    def test_delete_task(self, client: httpx.Client):
        """Test deleting a task."""
        # Create a task
        task_data = {"title": "To Be Deleted"}
        create_response = client.post("/api/v1/tasks", json=task_data)
        task_id = create_response.json()["id"]

        # Delete it
        response = client.delete(f"/api/v1/tasks/{task_id}")
        assert response.status_code == 204

        # Verify it's gone
        get_response = client.get(f"/tasks/{task_id}")
        assert get_response.status_code == 404

    def test_toggle_task_status(self, client: httpx.Client):
        """Test toggling a task's completion status."""
        # Create a task
        task_data = {"title": "Toggle Test"}
        create_response = client.post("/api/v1/tasks", json=task_data)
        task_id = create_response.json()["id"]

        # Update to completed
        response = client.patch(f"/api/v1/tasks/{task_id}/status?status=completed")
        assert response.status_code == 200

        data = response.json()
        assert data["status"] == "completed"

        # Update back to pending (the valid status is "pending", not "active")
        response = client.patch(f"/api/v1/tasks/{task_id}/status?status=pending")
        assert response.status_code == 200
        assert response.json()["status"] == "pending"


class TestProjects:
    """Tests for the projects API endpoints."""

    def test_get_all_projects(self, client: httpx.Client):
        """Test getting all projects."""
        response = client.get("/api/v1/projects")
        assert response.status_code == 200

        data = response.json()
        assert isinstance(data, list)

    def test_create_project(self, client: httpx.Client):
        """Test creating a new project."""
        import time
        project_data = {"name": f"E2E Test Project {int(time.time())}"}

        response = client.post("/api/v1/projects", json=project_data)
        assert response.status_code == 201

        data = response.json()
        assert data["name"] == project_data["name"]
        assert "created_at" in data

    def test_delete_project(self, client: httpx.Client):
        """Test deleting a project."""
        import time
        # Create a project
        project_data = {"name": f"To Be Deleted {int(time.time())}"}
        create_response = client.post("/api/v1/projects", json=project_data)
        project_name = create_response.json()["name"]

        # Delete it
        response = client.delete(f"/api/v1/projects/{project_name}")
        assert response.status_code == 204


class TestSettings:
    """Tests for the settings API endpoints."""

    def test_get_settings(self, client: httpx.Client):
        """Test getting application settings."""
        response = client.get("/api/v1/settings")
        assert response.status_code == 200

        data = response.json()
        assert "theme" in data
        assert "sort_order" in data

    def test_update_settings(self, client: httpx.Client):
        """Test updating application settings."""
        update_data = {"theme": "dark", "sort_order": "priority"}

        response = client.put("/api/v1/settings", json=update_data)
        assert response.status_code == 200

        data = response.json()
        assert data["theme"] == "dark"
        assert data["sort_order"] == "priority"


class TestErrorHandling:
    """Tests for error handling."""

    def test_get_nonexistent_task(self, client: httpx.Client):
        """Test getting a non-existent task returns 404."""
        response = client.get("/api/v1/tasks/nonexistent-id")
        assert response.status_code == 404

    def test_delete_nonexistent_task(self, client: httpx.Client):
        """Test deleting a non-existent task returns 404."""
        response = client.delete("/api/v1/tasks/nonexistent-id")
        assert response.status_code == 404

    def test_create_task_with_invalid_data(self, client: httpx.Client):
        """Test creating a task with invalid data returns 422."""
        invalid_data = {"title": ""}  # Empty title is invalid

        response = client.post("/api/v1/tasks", json=invalid_data)
        # Should return 422 for validation error
        assert response.status_code == 422

    def test_update_nonexistent_task(self, client: httpx.Client):
        """Test updating a non-existent task returns 404."""
        update_data = {"title": "Updated"}
        response = client.put("/api/v1/tasks/nonexistent-id", json=update_data)
        assert response.status_code == 404


class TestPerformance:
    """Performance-related tests."""

    def test_response_time_reasonable(self, client: httpx.Client):
        """Test that API responses are reasonably fast."""
        import time

        start = time.time()
        response = client.get("/api/v1/tasks")
        end = time.time()

        elapsed = end - start
        # Should respond in less than 1 second
        assert elapsed < 1.0
