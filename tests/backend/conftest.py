"""
Pytest configuration and shared fixtures for backend tests.

This module provides fixtures that are available across all backend tests.
"""
import os
import json
import tempfile
import shutil
from pathlib import Path
from typing import Generator, Dict, Any
from datetime import datetime
import pytest

# Add the backend directory to the path
import sys
sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))

from app.models.task import Task, TaskCreate, TaskUpdate
from app.models.project import Project, ProjectCreate
from app.models.settings import Settings
from app.storage.json_file import JSONFileStore, SingleValueStore
from app.storage.atomic import atomic_write, read_json_file, ensure_file_exists


# =============================================================================
# Temporary Directory Fixture
# =============================================================================

@pytest.fixture(scope="function")
def temp_dir() -> Generator[Path, None, None]:
    """
    Create a temporary directory for test data.

    This fixture creates a unique temporary directory for each test function
    and cleans it up after the test completes.
    """
    temp_path = tempfile.mkdtemp()
    try:
        yield Path(temp_path)
    finally:
        shutil.rmtree(temp_path, ignore_errors=True)


@pytest.fixture(scope="function")
def test_data_dir(temp_dir: Path) -> Generator[Path, None, None]:
    """
    Create a test data directory structure.

    Provides a /data subdirectory that mirrors the production data structure.
    """
    data_dir = temp_dir / "data"
    data_dir.mkdir(parents=True, exist_ok=True)
    yield data_dir


# =============================================================================
# JSON File Fixtures
# =============================================================================

@pytest.fixture(scope="function")
def tasks_file(test_data_dir: Path) -> Generator[str, None, None]:
    """
    Create a tasks.json file with initial data.

    Provides a file path to a tasks.json file that can be used in tests.
    """
    filepath = str(test_data_dir / "tasks.json")
    initial_data = {"items": []}
    ensure_file_exists(filepath, initial_data)
    yield filepath


@pytest.fixture(scope="function")
def projects_file(test_data_dir: Path) -> Generator[str, None, None]:
    """
    Create a projects.json file with initial data.
    """
    filepath = str(test_data_dir / "projects.json")
    initial_data = {"items": []}
    ensure_file_exists(filepath, initial_data)
    yield filepath


@pytest.fixture(scope="function")
def settings_file(test_data_dir: Path) -> Generator[str, None, None]:
    """
    Create a settings.json file with initial data.
    """
    filepath = str(test_data_dir / "settings.json")
    initial_data = {"value": None}
    ensure_file_exists(filepath, initial_data)
    yield filepath


# =============================================================================
# JSON File Store Fixtures
# =============================================================================

@pytest.fixture(scope="function")
def task_store(tasks_file: str) -> Generator[JSONFileStore[Task], None, None]:
    """
    Create a JSONFileStore for Task objects.

    Provides a ready-to-use store for testing task CRUD operations.
    """
    store = JSONFileStore[Task](tasks_file, Task, collection_key="items")
    yield store
    # Clean up after test
    store.clear()


@pytest.fixture(scope="function")
def project_store(projects_file: str) -> Generator[JSONFileStore[Project], None, None]:
    """
    Create a JSONFileStore for Project objects.
    """
    store = JSONFileStore[Project](projects_file, Project, collection_key="items")
    yield store
    store.clear()


@pytest.fixture(scope="function")
def settings_store(settings_file: str) -> Generator[SingleValueStore[Settings], None, None]:
    """
    Create a SingleValueStore for Settings.
    """
    store = SingleValueStore[Settings](settings_file, Settings)
    yield store


# =============================================================================
# Model Instance Fixtures
# =============================================================================

@pytest.fixture(scope="function")
def sample_task() -> Task:
    """
    Create a sample Task instance for testing.
    """
    return Task(
        title="Test Task",
        notes="This is a test task",
        priority="high",
        project="Inbox",
        due_date=datetime(2026, 2, 15, 23, 59, 59)
    )


@pytest.fixture(scope="function")
def sample_task_create() -> TaskCreate:
    """
    Create a sample TaskCreate instance.
    """
    return TaskCreate(
        title="Test Task",
        notes="Test notes",
        priority="medium",
        project="Work"
    )


@pytest.fixture(scope="function")
def sample_task_update() -> TaskUpdate:
    """
    Create a sample TaskUpdate instance.
    """
    return TaskUpdate(
        title="Updated Task Title",
        notes="Updated notes",
        status="completed"
    )


@pytest.fixture(scope="function")
def sample_project() -> Project:
    """
    Create a sample Project instance.
    """
    return Project(name="Test Project")


@pytest.fixture(scope="function")
def sample_project_create() -> ProjectCreate:
    """
    Create a sample ProjectCreate instance.
    """
    return ProjectCreate(name="New Project")


@pytest.fixture(scope="function")
def sample_settings() -> Settings:
    """
    Create a sample Settings instance.
    """
    return Settings(theme="dark", sort_order="priority")


# =============================================================================
# Test Data Fixtures
# =============================================================================

@pytest.fixture(scope="function")
def sample_tasks_data() -> Dict[str, Any]:
    """
    Provide sample tasks data in dictionary format.
    """
    return {
        "items": [
            {
                "id": "11111111-1111-1111-1111-111111111111",
                "title": "First Task",
                "notes": "First task notes",
                "status": "active",
                "priority": "high",
                "due_date": "2026-02-15T23:59:59",
                "project": "Work",
                "created_at": "2026-02-01T10:00:00",
                "updated_at": "2026-02-01T10:00:00"
            },
            {
                "id": "22222222-2222-2222-2222-222222222222",
                "title": "Second Task",
                "notes": "Second task notes",
                "status": "completed",
                "priority": "low",
                "due_date": None,
                "project": "Personal",
                "created_at": "2026-02-02T10:00:00",
                "updated_at": "2026-02-03T10:00:00"
            },
            {
                "id": "33333333-3333-3333-3333-333333333333",
                "title": "Third Task",
                "notes": "Third task notes",
                "status": "active",
                "priority": "medium",
                "due_date": "2026-02-20T23:59:59",
                "project": "Work",
                "created_at": "2026-02-03T10:00:00",
                "updated_at": "2026-02-03T10:00:00"
            }
        ]
    }


@pytest.fixture(scope="function")
def sample_projects_data() -> Dict[str, Any]:
    """
    Provide sample projects data in dictionary format.
    """
    return {
        "items": [
            {"name": "Work", "created_at": "2026-02-01T10:00:00"},
            {"name": "Personal", "created_at": "2026-02-01T10:00:00"},
            {"name": "Inbox", "created_at": "2026-02-01T10:00:00"}
        ]
    }


@pytest.fixture(scope="function")
def corrupted_json_file(temp_dir: Path) -> Generator[str, None, None]:
    """
    Create a file with invalid JSON content for testing error handling.
    """
    filepath = str(temp_dir / "corrupted.json")
    with open(filepath, 'w') as f:
        f.write("{ this is not valid json }")
    yield filepath


# =============================================================================
# File Locking Fixtures
# =============================================================================

@pytest.fixture(scope="function")
def lock_test_file(temp_dir: Path) -> Generator[str, None, None]:
    """
    Create a file for testing file locking behavior.
    """
    filepath = str(temp_dir / "lock_test.json")
    yield filepath


# =============================================================================
# API Test Fixtures
# =============================================================================

@pytest.fixture(scope="function")
def test_app():
    """
    Create a test FastAPI application instance.

    Note: This fixture imports from the main app module and creates
    a test client. It's provided for integration tests.
    """
    from fastapi.testclient import TestClient

    # Import and create app
    sys.path.insert(0, str(Path(__file__).parent.parent / "backend"))
    from app.main import create_application

    app = create_application()
    client = TestClient(app)
    yield client


# =============================================================================
# Clean State Fixture
# =============================================================================

@pytest.fixture(scope="function", autouse=True)
def clean_storage_state():
    """
    Automatically clean up storage state before each test.

    This ensures tests run in isolation and don't affect each other.
    """
    # Clear any temporary data before test
    yield
    # Cleanup after test is handled by temp_dir fixture
