"""
Atomic write utilities for JSON file storage.

Implements atomic write pattern using temp file + rename with file locking.
"""
import os
import fcntl
import json
import tempfile
from pathlib import Path
from typing import Any, Dict, Optional
from datetime import datetime


class AtomicWriteError(Exception):
    """Raised when atomic write operations fail."""
    pass


class FileLockError(Exception):
    """Raised when file locking operations fail."""
    pass


class StorageError(Exception):
    """Raised when storage operations fail."""
    pass


def atomic_write(filepath: str, data: Dict[str, Any]) -> None:
    """
    Perform an atomic write to a JSON file.

    Uses temp file + rename pattern with file locking to ensure
    data integrity during concurrent writes.

    Args:
        filepath: Path to the target file
        data: Dictionary to write as JSON

    Raises:
        AtomicWriteError: If the write operation fails
        FileLockError: If file locking fails
    """
    path = Path(filepath)
    temp_path = None

    try:
        # Create temp file in the same directory for atomic rename
        dir_path = path.parent
        if not dir_path.exists():
            dir_path.mkdir(parents=True, exist_ok=True)

        # Create temp file
        fd, temp_path = tempfile.mkstemp(dir=str(dir_path), suffix='.tmp')
        os.close(fd)  # Close the file descriptor, we'll reopen with open()

        # Acquire exclusive lock
        lock_path = filepath + '.lock'
        lock_fd = open(lock_path, 'w')
        try:
            fcntl.flock(lock_fd.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            lock_fd.close()
            raise FileLockError(f"Could not acquire lock for {filepath}")

        try:
            # Write to temp file
            with open(temp_path, 'w') as f:
                json.dump(data, f, indent=2, default=str)
                # Ensure data is flushed to disk
                f.flush()
                os.fsync(f.fileno())

            # Atomic rename
            os.rename(temp_path, filepath)
            temp_path = None  # Mark as moved, don't clean up

        finally:
            # Release lock
            fcntl.flock(lock_fd.fileno(), fcntl.LOCK_UN)
            lock_fd.close()

            # Clean up temp file if it still exists
            if temp_path and os.path.exists(temp_path):
                try:
                    os.remove(temp_path)
                except OSError:
                    pass

            # Clean up lock file
            try:
                os.remove(lock_path)
            except OSError:
                pass

    except (IOError, OSError) as e:
        # Cleanup on failure
        if temp_path and os.path.exists(temp_path):
            try:
                os.remove(temp_path)
            except OSError:
                pass
        raise AtomicWriteError(f"Atomic write failed for {filepath}: {str(e)}")


def read_json_file(filepath: str, default: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
    """
    Read a JSON file with error handling.

    Args:
        filepath: Path to the JSON file
        default: Default value to return if file doesn't exist or is invalid

    Returns:
        Parsed JSON data or default value
    """
    path = Path(filepath)

    if not path.exists():
        return default if default is not None else {}

    try:
        with open(filepath, 'r') as f:
            return json.load(f)
    except json.JSONDecodeError:
        return default if default is not None else {}
    except IOError:
        return default if default is not None else {}


def ensure_file_exists(filepath: str, initial_data: Dict[str, Any]) -> None:
    """
    Ensure a JSON file exists, creating it with initial data if not.

    Args:
        filepath: Path to the file
        initial_data: Data to write if creating new file
    """
    path = Path(filepath)

    if not path.exists():
        atomic_write(filepath, initial_data)


def backup_file(filepath: str, backup_dir: str = "/data/backups") -> Optional[str]:
    """
    Create a backup of a JSON file.

    Args:
        filepath: Path to the file to backup
        backup_dir: Directory to store backups

    Returns:
        Path to the backup file, or None if backup failed
    """
    path = Path(filepath)
    backup_path = Path(backup_dir)

    if not path.exists():
        return None

    try:
        backup_path.mkdir(parents=True, exist_ok=True)
        timestamp = datetime.utcnow().strftime("%Y%m%d_%H%M%S")
        backup_filename = f"{path.name}.{timestamp}.bak"
        backup_file = backup_path / backup_filename

        with open(filepath, 'r') as src:
            content = src.read()

        with open(backup_file, 'w') as dst:
            dst.write(content)

        return str(backup_file)
    except (IOError, OSError):
        return None
