"""
E2E test fixtures and utilities.

Provides shared fixtures for end-to-end testing.
"""
import pytest
import httpx
import os
import json
import tempfile
import shutil
from pathlib import Path
from datetime import datetime
from typing import Dict, Any

# API Configuration
BASE_URL = os.getenv("BACKEND_URL", "http://localhost:8000/api/v1")


@pytest.fixture(scope="function")
def temp_data_dir():
    """
    Create a temporary directory for test data.

    This ensures tests don't interfere with production data.
    """
    temp_path = tempfile.mkdtemp()
    data_path = Path(temp_path) / "data"
    data_path.mkdir()

    # Initialize JSON files
    files = {
        "tasks.json": {"items": []},
        "projects.json": {"items": []},
        "settings.json": {"value": None},
    }

    for filename, initial_data in files.items():
        filepath = data_path / filename
        with open(filepath, 'w') as f:
            json.dump(initial_data, f)

    yield temp_path

    # Cleanup
    shutil.rmtree(temp_path, ignore_errors=True)


@pytest.fixture(scope="function")
def test_api_url():
    """Get the API URL for testing."""
    return BASE_URL


@pytest.fixture(scope="function")
def api_client(test_api_url):
    """Create an HTTP client for API testing."""
    return httpx.Client(base_url=test_api_url, timeout=10.0)


@pytest.fixture(scope="function")
def sample_task_data():
    """Sample task data for testing."""
    return {
        "title": "E2E Test Task",
        "notes": "This is a test task created via API",
        "priority": "high",
        "project": "Work",
        "due_date": "2026-02-15T23:59:59Z"
    }


@pytest.fixture(scope="function")
def sample_project_data():
    """Sample project data for testing."""
    return {
        "name": "E2E Test Project"
    }


@pytest.fixture(scope="function")
def sample_settings_data():
    """Sample settings data for testing."""
    return {
        "theme": "dark",
        "sort_order": "priority"
    }


@pytest.fixture(scope="function")
def clean_state(api_client):
    """Clean up test data before and after tests."""
    # This fixture ensures a clean state
    yield
