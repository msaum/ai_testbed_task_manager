"""
JSON file storage implementation with auto-repair capabilities.

Provides generic storage for Pydantic models backed by JSON files.
"""
import json
from pathlib import Path
from typing import Generic, TypeVar, List, Optional, Callable, Any, Dict
from datetime import datetime

from app.storage.atomic import atomic_write, read_json_file, ensure_file_exists, StorageError
from app.utils.errors import ValidationError


T = TypeVar('T')


class JSONFileStore(Generic[T]):
    """
    Generic JSON file storage with atomic writes and auto-repair.

    Supports CRUD operations on collections of Pydantic models
    stored in JSON files with file locking and atomic writes.
    """

    def __init__(
        self,
        filepath: str,
        model_class: type,
        collection_key: str = "items",
        initial_data: Optional[Dict[str, Any]] = None
    ):
        """
        Initialize the JSON file store.

        Args:
            filepath: Path to the JSON file
            model_class: Pydantic model class for deserialization
            collection_key: Key in JSON object containing the list of items
            initial_data: Initial data to use if file doesn't exist
        """
        self.filepath = filepath
        self.model_class = model_class
        self.collection_key = collection_key
        self.initial_data = initial_data or {collection_key: []}

        # Auto-create file if it doesn't exist
        ensure_file_exists(filepath, self.initial_data)

    def _read_data(self) -> Dict[str, Any]:
        """Read and parse JSON file with repair on corruption."""
        try:
            return read_json_file(self.filepath, self.initial_data)
        except Exception:
            return self.initial_data

    def _write_data(self, data: Dict[str, Any]) -> None:
        """Write data atomically."""
        atomic_write(self.filepath, data)

    def _parse_items(self, data: List[Dict[str, Any]]) -> List[T]:
        """Parse raw dictionary items into model instances."""
        items = []
        if data is None:
            return items
        for item in data:
            try:
                # Handle legacy "active" status -> "pending"
                if isinstance(item, dict):
                    item = self._normalize_item(item)
                items.append(self.model_class(**item))
            except Exception as e:
                # Skip invalid items during read
                continue
        return items

    def _normalize_item(self, item: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize item data to match current schema."""
        if isinstance(item, dict) and item.get('status') == 'active':
            item = item.copy()
            item['status'] = 'pending'
        return item

    def get_all(self) -> List[T]:
        """Get all items from the store."""
        data = self._read_data()
        items = data.get(self.collection_key, [])
        return self._parse_items(items)

    def get_by_id(self, item_id: str) -> Optional[T]:
        """
        Get an item by its ID.

        Args:
            item_id: The unique identifier of the item

        Returns:
            The item if found, None otherwise
        """
        for item in self.get_all():
            if hasattr(item, 'id') and str(item.id) == str(item_id):
                return item
        return None

    def get_by_field(self, field: str, value: Any) -> Optional[T]:
        """
        Get an item by a specific field value.

        Args:
            field: The field name to search
            value: The value to match

        Returns:
            The first matching item, or None if not found
        """
        for item in self.get_all():
            # Handle both model instances and dicts
            if isinstance(item, dict):
                item_value = item.get(field)
            else:
                item_value = getattr(item, field, None)
            if item_value == value:
                return item
        return None

    def add(self, item: T) -> T:
        """
        Add a new item to the store.

        Args:
            item: The item to add (must have an 'id' attribute)

        Returns:
            The added item

        Raises:
            StorageError: If item with same ID already exists
        """
        data = self._read_data()
        items = data.get(self.collection_key, [])

        # Check for duplicate ID
        item_id = getattr(item, 'id', None)
        if item_id:
            for existing in items:
                # Handle both model instances and dicts
                if isinstance(existing, dict):
                    existing_id = existing.get('id')
                else:
                    existing_id = getattr(existing, 'id', None)
                if existing_id is not None and str(existing_id) == str(item_id):
                    raise StorageError(f"Item with ID {item_id} already exists")

        # Convert to dict and add
        items.append(self._item_to_dict(item))
        data[self.collection_key] = items
        self._write_data(data)
        return item

    def update(self, item: T) -> T:
        """
        Update an existing item.

        Args:
            item: The updated item

        Returns:
            The updated item

        Raises:
            StorageError: If item with this ID doesn't exist
        """
        data = self._read_data()
        items = data.get(self.collection_key, [])

        item_id = getattr(item, 'id', None)
        if not item_id:
            raise StorageError("Item must have an 'id' attribute")

        found = False
        for i, existing in enumerate(items):
            # Handle both model instances and dicts
            if isinstance(existing, dict):
                existing_id = existing.get('id')
            else:
                existing_id = getattr(existing, 'id', None)
            if existing_id is not None and str(existing_id) == str(item_id):
                items[i] = self._item_to_dict(item)
                found = True
                break

        if not found:
            raise StorageError(f"Item with ID {item_id} not found")

        data[self.collection_key] = items
        self._write_data(data)
        return item

    def delete(self, item_id: str) -> bool:
        """
        Delete an item by ID.

        Args:
            item_id: The ID of the item to delete

        Returns:
            True if item was deleted, False if not found
        """
        data = self._read_data()
        items = data.get(self.collection_key, [])

        original_len = len(items)
        filtered_items = []
        for item in items:
            # Handle both model instances and dicts
            if isinstance(item, dict):
                existing_id = item.get('id')
            else:
                existing_id = getattr(item, 'id', None)
            # Keep items where ID doesn't match
            if existing_id is None or str(existing_id) != str(item_id):
                filtered_items.append(item)
        data[self.collection_key] = filtered_items

        deleted = len(filtered_items) < original_len
        if deleted:
            self._write_data(data)

        return deleted

    def delete_by_field(self, field: str, value: Any) -> int:
        """
        Delete items matching a field value.

        Args:
            field: The field name to match
            value: The value to match

        Returns:
            Number of items deleted
        """
        data = self._read_data()
        items = data.get(self.collection_key, [])

        original_len = len(items)
        filtered_items = []
        for item in items:
            # Handle both model instances and dicts
            if isinstance(item, dict):
                existing_value = item.get(field)
            else:
                existing_value = getattr(item, field, None)
            # Keep items where field value doesn't match
            if existing_value != value:
                filtered_items.append(item)
        data[self.collection_key] = filtered_items

        deleted = len(filtered_items) < original_len
        count = original_len - len(filtered_items)

        if deleted:
            self._write_data(data)

        return count

    def count(self) -> int:
        """Return the total number of items in the store."""
        return len(self.get_all())

    def clear(self) -> None:
        """Remove all items from the store."""
        data = {self.collection_key: []}
        self._write_data(data)

    def _item_to_dict(self, item: T) -> Dict[str, Any]:
        """Convert a model instance to a dictionary."""
        if hasattr(item, 'model_dump'):
            return item.model_dump()
        elif hasattr(item, '__dict__'):
            return item.__dict__
        else:
            return dict(item)


class SingleValueStore(Generic[T]):
    """
    Storage for a single value (like settings).

    Uses a JSON object with a single 'value' key.
    """

    def __init__(self, filepath: str, model_class: type):
        self.filepath = filepath
        self.model_class = model_class
        self._ensure_file_exists()

    def _ensure_file_exists(self) -> None:
        """Create file with empty structure if it doesn't exist."""
        path = Path(self.filepath)
        if not path.exists():
            data = {"value": None}
            atomic_write(self.filepath, data)

    def _read_data(self) -> Dict[str, Any]:
        """Read and parse JSON file."""
        return read_json_file(self.filepath, {"value": None})

    def _write_data(self, data: Dict[str, Any]) -> None:
        """Write data atomically."""
        atomic_write(self.filepath, data)

    def get(self) -> Optional[T]:
        """Get the stored value."""
        data = self._read_data()
        value = data.get("value")

        if value is None:
            # Return default instance
            return self.model_class()

        try:
            return self.model_class(**value)
        except Exception:
            return self.model_class()

    def update(self, item: T) -> T:
        """
        Update the stored value.

        Args:
            item: The new value

        Returns:
            The updated value
        """
        data = {"value": self._item_to_dict(item)}
        self._write_data(data)
        return item

    def _item_to_dict(self, item: T) -> Dict[str, Any]:
        """Convert a model instance to a dictionary."""
        if hasattr(item, 'model_dump'):
            return item.model_dump()
        elif hasattr(item, '__dict__'):
            return item.__dict__
        else:
            return dict(item)
