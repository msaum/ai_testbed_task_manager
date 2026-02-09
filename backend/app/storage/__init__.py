"""
Storage layer package.

Provides data persistence using JSON file storage with atomic writes.
"""
from app.storage.atomic import (
    atomic_write,
    read_json_file,
    ensure_file_exists,
    AtomicWriteError,
    FileLockError,
    StorageError,
)
from app.storage.json_file import JSONFileStore, SingleValueStore

__all__ = [
    "atomic_write",
    "read_json_file",
    "ensure_file_exists",
    "AtomicWriteError",
    "FileLockError",
    "StorageError",
    "JSONFileStore",
    "SingleValueStore",
]
