"""
Custom exception classes for error handling.
"""
from starlette.exceptions import HTTPException
from fastapi import HTTPException as FastAPIHTTPException


class BackendError(FastAPIHTTPException):
    """Base exception for backend errors."""
    def __init__(self, detail: str, status_code: int = 400):
        super().__init__(status_code=status_code, detail=detail)


class ResourceNotFoundError(BackendError):
    """Raised when a resource is not found."""
    def __init__(self, resource: str):
        super().__init__(f"{resource} not found", status_code=404)


class ValidationError(BackendError):
    """Raised when validation fails."""
    def __init__(self, message: str):
        super().__init__(message)


class StorageError(BackendError):
    """Raised when storage operations fail."""
    def __init__(self, message: str):
        super().__init__(f"Storage error: {message}", status_code=500)


class ConflictError(BackendError):
    """Raised when there's a conflict (e.g., duplicate resource)."""
    def __init__(self, resource: str):
        super().__init__(f"{resource} already exists", status_code=409)


class InvalidJSONError(StorageError):
    """Raised when JSON file is corrupted and cannot be repaired."""
    def __init__(self, filepath: str):
        super().__init__(f"Invalid JSON in file {filepath}")


class FileLockError(BackendError):
    """Raised when file locking fails."""
    def __init__(self, filepath: str):
        super().__init__(f"Could not acquire lock for {filepath}", status_code=503)
