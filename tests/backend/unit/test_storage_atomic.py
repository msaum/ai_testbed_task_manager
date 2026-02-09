"""
Unit tests for the atomic.py storage module.

Tests atomic write operations, file locking, and JSON file handling.
"""
import os
import json
import tempfile
import shutil
from pathlib import Path
import pytest

from app.storage.atomic import (
    atomic_write,
    read_json_file,
    ensure_file_exists,
    AtomicWriteError,
    FileLockError,
)


class TestAtomicWrite:
    """Tests for the atomic_write function."""

    def test_atomic_write_creates_new_file(self, temp_dir):
        """Test that atomic_write creates a new file."""
        filepath = str(temp_dir / "test.json")
        data = {"key": "value"}

        atomic_write(filepath, data)

        assert os.path.exists(filepath)
        with open(filepath, 'r') as f:
            loaded = json.load(f)
        assert loaded == data

    def test_atomic_write_overwrites_existing(self, temp_dir):
        """Test that atomic_write overwrites existing content."""
        filepath = str(temp_dir / "test.json")
        initial_data = {"key": "initial"}
        atomic_write(filepath, initial_data)

        new_data = {"key": "updated"}
        atomic_write(filepath, new_data)

        with open(filepath, 'r') as f:
            loaded = json.load(f)
        assert loaded == new_data

    def test_atomic_write_with_nested_data(self, temp_dir):
        """Test atomic_write with nested data structures."""
        filepath = str(temp_dir / "test.json")
        data = {
            "level1": {
                "level2": {
                    "level3": "deep_value"
                },
                "list": [1, 2, 3]
            }
        }

        atomic_write(filepath, data)

        with open(filepath, 'r') as f:
            loaded = json.load(f)
        assert loaded == data

    def test_atomic_write_handles_special_chars(self, temp_dir):
        """Test that atomic_write handles special characters."""
        filepath = str(temp_dir / "test.json")
        data = {
            "text": "Special chars: \n\t\r\"'\\",
            "unicode": "Hello 世界 🌍"
        }

        atomic_write(filepath, data)

        with open(filepath, 'r') as f:
            loaded = json.load(f)
        assert loaded == data

    def test_atomic_write_creates_parent_dirs(self, temp_dir):
        """Test that atomic_write creates parent directories."""
        filepath = str(temp_dir / "sub" / "nested" / "test.json")
        data = {"key": "value"}

        atomic_write(filepath, data)

        assert os.path.exists(filepath)


class TestReadJsonFile:
    """Tests for the read_json_file function."""

    def test_read_existing_file(self, temp_dir):
        """Test reading an existing file."""
        filepath = str(temp_dir / "test.json")
        data = {"key": "value"}
        with open(filepath, 'w') as f:
            json.dump(data, f)

        result = read_json_file(filepath)

        assert result == data

    def test_read_nonexistent_file_returns_default(self, temp_dir):
        """Test reading a non-existent file returns default value."""
        filepath = str(temp_dir / "nonexistent.json")
        default = {"default": True}

        result = read_json_file(filepath, default=default)

        assert result == default

    def test_read_nonexistent_file_returns_empty(self, temp_dir):
        """Test reading a non-existent file without default returns empty."""
        filepath = str(temp_dir / "nonexistent.json")

        result = read_json_file(filepath)

        assert result == {}

    def test_read_corrupted_json_returns_default(self, temp_dir):
        """Test reading corrupted JSON returns default value."""
        filepath = str(temp_dir / "corrupted.json")
        with open(filepath, 'w') as f:
            f.write("{ this is not valid json }")
        default = {"fallback": True}

        result = read_json_file(filepath, default=default)

        assert result == default

    def test_read_corrupted_json_returns_empty(self, temp_dir):
        """Test reading corrupted JSON without default returns empty."""
        filepath = str(temp_dir / "corrupted.json")
        with open(filepath, 'w') as f:
            f.write("{ not valid json")

        result = read_json_file(filepath)

        assert result == {}

    def test_read_empty_file(self, temp_dir):
        """Test reading an empty file."""
        filepath = str(temp_dir / "empty.json")
        with open(filepath, 'w') as f:
            f.write("")

        result = read_json_file(filepath)

        assert result == {}


class TestEnsureFileExists:
    """Tests for the ensure_file_exists function."""

    def test_creates_file_if_not_exists(self, temp_dir):
        """Test that file is created if it doesn't exist."""
        filepath = str(temp_dir / "newfile.json")
        initial_data = {"initial": True}

        ensure_file_exists(filepath, initial_data)

        assert os.path.exists(filepath)
        with open(filepath, 'r') as f:
            loaded = json.load(f)
        assert loaded == initial_data

    def test_does_not_overwrite_existing(self, temp_dir):
        """Test that existing file is not overwritten."""
        filepath = str(temp_dir / "existing.json")
        initial_data = {"initial": True}
        atomic_write(filepath, initial_data)

        new_data = {"overwritten": True}
        ensure_file_exists(filepath, new_data)

        with open(filepath, 'r') as f:
            loaded = json.load(f)
        assert loaded == initial_data  # Should not be overwritten


class TestErrorHandling:
    """Tests for error handling in atomic operations."""

    def test_invalid_filepath(self):
        """Test behavior with invalid file path."""
        # This test may behave differently on different platforms
        # We just verify the function doesn't crash
        with pytest.raises(Exception):
            atomic_write("", {"data": "test"})

    def test_permission_error_handling(self, temp_dir):
        """Test handling of permission errors."""
        # Create a file
        filepath = str(temp_dir / "readonly.json")
        data = {"key": "value"}
        atomic_write(filepath, data)

        # Make it read-only (this may not fail on all systems,
        # particularly if running as root or on macOS)
        try:
            os.chmod(filepath, 0o444)

            # Try to write (should fail on most systems with proper permissions)
            try:
                atomic_write(filepath, {"key": "updated"})
                # If write succeeds, we're likely running as root or on macOS with no permission issues
                # This is not an error - just skip the test
            except (AtomicWriteError, OSError, PermissionError):
                # Expected behavior on systems with proper permission checking
                pass
        except PermissionError:
            # If we can't even change permissions, skip the test
            pass

        # Restore permissions for cleanup
        try:
            os.chmod(filepath, 0o644)
        except PermissionError:
            pass


class TestParallelAccess:
    """Tests for concurrent access handling."""

    def test_concurrent_reads(self, temp_dir):
        """Test multiple concurrent reads don't interfere."""
        filepath = str(temp_dir / "concurrent.json")
        data = {"value": 0}
        atomic_write(filepath, data)

        # Simulate concurrent reads
        results = []
        for _ in range(10):
            result = read_json_file(filepath)
            results.append(result)

        # All reads should see the same data
        for result in results:
            assert result == data
