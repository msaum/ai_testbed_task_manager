# Backend API Design Document

**Document Version:** 1.0
**Date:** 2026-02-09
**Project:** Local Task Manager

---

## 1. Technology Stack Decision

### Decision: Python with FastAPI

**Rationale:**

1. **Product Spec Preference:** FastAPI is listed as "(preferred)" in the Python options
2. **Type Hints:** Built-in type hints make the code self-documenting
3. **Async Support:** Native async/await for future extensibility
4. **Automatic Documentation:** OpenAPI/Swagger support via `/docs`
5. **Performance:** High performance comparable to Node.js/Go
6. **Simplicity:** Straightforward for CRUD operations

### Alternative Considered: Flask

Flask was considered but FastAPI was selected for:
- Better type safety with Pydantic models
- Automatic OpenAPI documentation
- Built-in async support
- More modern design patterns

---

## 2. Directory Structure

```
backend/
├── app/
│   ├── __init__.py
│   ├── main.py              # FastAPI app entry point
│   ├── config.py            # Configuration management
│   ├── models/              # Pydantic data models
│   │   ├── __init__.py
│   │   ├── task.py
│   │   ├── project.py
│   │   └── settings.py
│   ├── api/                 # API routes
│   │   ├── __init__.py
│   │   ├── v1.py            # API version 1 routes
│   │   └── dependencies.py  # Dependency injections
│   ├── storage/             # Data persistence layer
│   │   ├── __init__.py
│   │   ├── base.py          # Base storage interface
│   │   ├── json_file.py     # JSON file storage
│   │   └── atomic.py        # Atomic write utilities
│   ├── core/                # Core business logic
│   │   ├── __init__.py
│   │   ├── task_service.py
│   │   ├── project_service.py
│   │   └── settings_service.py
│   └── utils/               # Utility functions
│       ├── __init__.py
│       ├── errors.py        # Custom exceptions
│       └── helpers.py       # Helper functions
├── data/                    # Data directory (mounted volume)
│   ├── projects.json
│   ├── tasks.json
│   └── settings.json
├── requirements.txt
├── Dockerfile
└── README.md
```

---

## 3. Data Models

### 3.1 Task Model

```python
# app/models/task.py
from datetime import datetime
from uuid import uuid4
from typing import Optional, Literal
from pydantic import BaseModel, Field

Priority = Literal["low", "medium", "high"]
TaskStatus = Literal["active", "completed"]

class Task(BaseModel):
    id: str = Field(default_factory=lambda: str(uuid4()))
    title: str
    notes: str = ""
    status: TaskStatus = "active"
    priority: Priority = "medium"
    due_date: Optional[datetime] = None
    project: str = "Inbox"
    created_at: datetime = Field(default_factory=datetime.utcnow)
    updated_at: datetime = Field(default_factory=datetime.utcnow)

    def save(self) -> None:
        """Update updated_at timestamp."""
        self.updated_at = datetime.utcnow()
```

### 3.2 Project Model

```python
# app/models/project.py
from datetime import datetime
from pydantic import BaseModel

class Project(BaseModel):
    name: str
    created_at: datetime = Field(default_factory=datetime.utcnow)
```

### 3.3 Settings Model

```python
# app/models/settings.py
from pydantic import BaseModel

class Settings(BaseModel):
    theme: Literal["light", "dark"] = "light"
    sort_order: Literal["priority", "due_date", "created"] = "created"
```

---

## 4. API Specification

### Base URL

```
/api/v1
```

### 4.1 Tasks API

| Method | Endpoint | Description | Request Body | Response |
|--------|----------|-------------|--------------|----------|
| GET | `/api/v1/tasks` | List all tasks | - | List[Task] |
| POST | `/api/v1/tasks` | Create task | Task (without id/timestamps) | Task |
| PUT | `/api/v1/tasks/{id}` | Update task | Task (partial) | Task |
| DELETE | `/api/v1/tasks/{id}` | Delete task | - | 204 No Content |
| POST | `/api/v1/tasks/{id}/toggle` | Toggle completion | - | Task |

#### Query Parameters for GET /tasks

- `status`: Filter by status (active, completed)
- `project`: Filter by project name
- `sort_by`: Sort by (priority, due_date, created)
- `order`: Sort order (asc, desc)

#### Example Requests

```bash
# List all tasks
GET /api/v1/tasks

# List active tasks in 'Work' project, sorted by priority
GET /api/v1/tasks?status=active&project=Work&sort_by=priority

# Create task
POST /api/v1/tasks
Content-Type: application/json
{
  "title": "Complete project",
  "notes": "Finish the API design",
  "priority": "high",
  "due_date": "2026-02-15T23:59:59Z",
  "project": "Work"
}

# Toggle task completion
POST /api/v1/tasks/{id}/toggle
```

### 4.2 Projects API

| Method | Endpoint | Description | Request Body | Response |
|--------|----------|-------------|--------------|----------|
| GET | `/api/v1/projects` | List all projects | - | List[Project] |
| POST | `/api/v1/projects` | Create project | Project (without created_at) | Project |
| DELETE | `/api/v1/projects/{name}` | Delete project | - | 204 No Content |

#### Example Requests

```bash
# List projects
GET /api/v1/projects

# Create project
POST /api/v1/projects
{
  "name": "Personal"
}

# Delete project
DELETE /api/v1/projects/Personal
```

### 4.3 Settings API

| Method | Endpoint | Description | Request Body | Response |
|--------|----------|-------------|--------------|----------|
| GET | `/api/v1/settings` | Get settings | - | Settings |
| PUT | `/api/v1/settings` | Update settings | Settings (partial) | Settings |

#### Example Requests

```bash
# Get settings
GET /api/v1/settings

# Update theme
PUT /api/v1/settings
{
  "theme": "dark"
}
```

---

## 5. Storage Layer Design

### 5.1 JSON File Structure

All files stored in `/data/` directory:

```json
// data/tasks.json
{
  "tasks": [
    {
      "id": "uuid-here",
      "title": "Task title",
      ...
    }
  ]
}

// data/projects.json
{
  "projects": [
    {
      "name": "Project name",
      "created_at": "2026-02-09T..."
    }
  ]
}

// data/settings.json
{
  "theme": "light",
  "sort_order": "priority"
}
```

### 5.2 Atomic Write Operations

**Implementation:** `/app/storage/atomic.py`

```python
import os
import fcntl
import json
from typing import Callable, Any
from contextlib import contextmanager

@contextmanager
def atomic_write(filepath: str, mode: str = 'w'):
    """
    Context manager for atomic file writes.
    Uses temp file + rename pattern with file locking.
    """
    temp_path = f"{filepath}.tmp"

    # Acquire exclusive lock
    with open(filepath, 'a+') as f:
        fcntl.flock(f.fileno(), fcntl.LOCK_EX)

        try:
            # Write to temp file
            with open(temp_path, mode) as temp_f:
                yield temp_f

            # Atomic rename
            os.rename(temp_path, filepath)

        finally:
            fcntl.flock(f.fileno(), fcntl.LOCK_UN)
            # Clean up temp file if it exists
            if os.path.exists(temp_path):
                os.remove(temp_path)
```

### 5.3 JSON File Storage Class

```python
# app/storage/json_file.py
import json
from pathlib import Path
from typing import Generic, TypeVar, List, Optional
from app.storage.atomic import atomic_write
from app.utils.errors import StorageError

T = TypeVar('T')

class JSONFileStore(Generic[T]):
    """Generic JSON file storage with atomic writes."""

    def __init__(self, filepath: str, model_class: type):
        self.filepath = filepath
        self.model_class = model_class
        self._ensure_file_exists()

    def _ensure_file_exists(self):
        """Create file with empty structure if it doesn't exist."""
        if not Path(self.filepath).exists():
            self._write_data({})

    def _read_data(self) -> dict:
        """Read and parse JSON file."""
        try:
            with open(self.filepath, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            raise StorageError(f"Invalid JSON in {self.filepath}")
        except FileNotFoundError:
            return {}

    def _write_data(self, data: dict):
        """Write data atomically."""
        with atomic_write(self.filepath) as f:
            json.dump(data, f, indent=2, default=str)

    def get_all(self) -> List[T]:
        """Get all items."""
        data = self._read_data()
        items = data.get('items', [])
        return [self.model_class(**item) for item in items]

    def get_by_id(self, item_id: str) -> Optional[T]:
        """Get item by ID."""
        for item in self.get_all():
            if item.id == item_id:
                return item
        return None

    def add(self, item: T) -> T:
        """Add a new item."""
        data = self._read_data()
        items = data.get('items', [])

        # Check for duplicate ID
        for existing in items:
            if existing.get('id') == item.id:
                raise StorageError(f"Item with ID {item.id} already exists")

        items.append(item.model_dump())
        data['items'] = items
        self._write_data(data)
        return item

    def update(self, item: T) -> T:
        """Update an existing item."""
        data = self._read_data()
        items = data.get('items', [])

        for i, existing in enumerate(items):
            if existing.get('id') == item.id:
                items[i] = item.model_dump()
                data['items'] = items
                self._write_data(data)
                return item

        raise StorageError(f"Item with ID {item.id} not found")

    def delete(self, item_id: str) -> bool:
        """Delete an item by ID."""
        data = self._read_data()
        items = data.get('items', [])

        original_len = len(items)
        items = [i for i in items if i.get('id') != item_id]
        data['items'] = items

        if len(items) < original_len:
            self._write_data(data)
            return True
        return False
```

---

## 6. Service Layer Design

### 6.1 Task Service

```python
# app/core/task_service.py
from typing import List, Optional, Literal
from app.models.task import Task, Priority, TaskStatus
from app.storage.json_file import JSONFileStore

class TaskService:
    def __init__(self, store: JSONFileStore[Task]):
        self.store = store

    def list_tasks(
        self,
        status: Optional[TaskStatus] = None,
        project: Optional[str] = None,
        sort_by: Literal["priority", "due_date", "created"] = "created"
    ) -> List[Task]:
        """List tasks with optional filtering and sorting."""
        tasks = self.store.get_all()

        # Filter
        if status:
            tasks = [t for t in tasks if t.status == status]
        if project:
            tasks = [t for t in tasks if t.project == project]

        # Sort
        priority_order = {"high": 0, "medium": 1, "low": 2}

        if sort_by == "priority":
            tasks.sort(key=lambda t: priority_order.get(t.priority, 99))
        elif sort_by == "due_date":
            tasks.sort(key=lambda t: t.due_date or datetime.max)
        elif sort_by == "created":
            tasks.sort(key=lambda t: t.created_at, reverse=True)

        return tasks

    def get_task(self, task_id: str) -> Optional[Task]:
        """Get a task by ID."""
        return self.store.get_by_id(task_id)

    def create_task(self, title: str, **kwargs) -> Task:
        """Create a new task."""
        task = Task(title=title, **kwargs)
        return self.store.add(task)

    def update_task(self, task_id: str, **kwargs) -> Task:
        """Update an existing task."""
        task = self.store.get_by_id(task_id)
        if not task:
            raise ResourceNotFoundError(f"Task {task_id} not found")

        for key, value in kwargs.items():
            if hasattr(task, key):
                setattr(task, key, value)

        task.save()
        return self.store.update(task)

    def delete_task(self, task_id: str) -> bool:
        """Delete a task."""
        return self.store.delete(task_id)

    def toggle_task(self, task_id: str) -> Task:
        """Toggle task completion status."""
        task = self.store.get_by_id(task_id)
        if not task:
            raise ResourceNotFoundError(f"Task {task_id} not found")

        task.status = "completed" if task.status == "active" else "active"
        task.save()
        return self.store.update(task)
```

### 6.2 Project Service

```python
# app/core/project_service.py
from app.models.project import Project
from app.storage.json_file import JSONFileStore
from app.utils.errors import StorageError

class ProjectService:
    def __init__(self, store: JSONFileStore[Project]):
        self.store = store

    def list_projects(self) -> List[Project]:
        """List all projects."""
        return self.store.get_all()

    def create_project(self, name: str) -> Project:
        """Create a new project."""
        projects = self.store.get_all()

        # Check for duplicate name
        for project in projects:
            if project.name == name:
                raise StorageError(f"Project '{name}' already exists")

        project = Project(name=name)
        return self.store.add(project)

    def delete_project(self, name: str) -> bool:
        """Delete a project."""
        project = None
        projects = self.store.get_all()

        for p in projects:
            if p.name == name:
                project = p
                break

        if not project:
            return False

        # Check if any tasks use this project
        from app.core.task_service import TaskService
        # (TaskService would be injected or created)

        return self.store.delete_by(lambda p: p.name == name)
```

### 6.3 Settings Service

```python
# app/core/settings_service.py
from app.models.settings import Settings
from app.storage.json_file import JSONFileStore

class SettingsService:
    def __init__(self, store: JSONFileStore[Settings]):
        self.store = store

    def get_settings(self) -> Settings:
        """Get current settings."""
        settings_list = self.store.get_all()
        if settings_list:
            return settings_list[0]
        return Settings()

    def update_settings(self, **kwargs) -> Settings:
        """Update settings."""
        current = self.get_settings()

        for key, value in kwargs.items():
            if hasattr(current, key):
                setattr(current, key, value)

        # Store as single-item list
        self.store._write_data({"items": [current.model_dump()]})
        return current
```

---

## 7. Error Handling

### Custom Exceptions

```python
# app/utils/errors.py
from starlette.exceptions import HTTPException

class BackendError(HTTPException):
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
        super().__init__(f"Storage error: {message}")

class ConflictError(BackendError):
    """Raised when there's a conflict (e.g., duplicate)."""
    def __init__(self, resource: str):
        super().__init__(f"{resource} already exists", status_code=409)
```

### Error Response Format

```json
{
  "error": {
    "type": "ValidationError",
    "message": "Title is required",
    "code": "validation_error"
  }
}
```

---

## 8. Database Auto-Repair

### Implementation

```python
# app/core/repair.py
import json
from pathlib import Path
from datetime import datetime
from app.models.task import Task
from app.models.project import Project
from app.models.settings import Settings

class DataRepair:
    """Auto-repair functionality for corrupted JSON files."""

    @staticmethod
    def repair_json_file(filepath: str, backup_dir: str = "/data/backups"):
        """Attempt to repair a corrupted JSON file."""
        path = Path(filepath)

        if not path.exists():
            return None

        # Try to parse as JSON
        try:
            with open(filepath, 'r') as f:
                return json.load(f)
        except json.JSONDecodeError:
            pass

        # Try to extract valid JSON from partial content
        content = path.read_text()

        # Try to find last valid JSON object
        for i in range(len(content), 0, -1):
            try:
                candidate = content[:i]
                if candidate.strip().endswith('}'):
                    result = json.loads(candidate)
                    return result
            except json.JSONDecodeError:
                continue

        # If all else fails, restore from backup
        backup_path = Path(backup_dir) / f"{path.name}.bak"
        if backup_path.exists():
            content = backup_path.read_text()
            path.write_text(content)
            return json.loads(content)

        # Return empty structure
        return {}

    @staticmethod
    def auto_create_missing_files(data_dir: str):
        """Create missing JSON files with empty structures."""
        files = {
            "tasks.json": {"tasks": []},
            "projects.json": {"projects": []},
            "settings.json": {"items": [{"theme": "light", "sort_order": "created"}]}
        }

        for filename, default_data in files.items():
            filepath = Path(data_dir) / filename
            if not filepath.exists():
                filepath.write_text(json.dumps(default_data, indent=2))
```

---

## 9. API Route Implementation

### Main Application

```python
# app/main.py
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.api.v1 import router as api_router
from app.core.repair import DataRepair

app = FastAPI(
    title="Local Task Manager API",
    description="API for local task management with JSON persistence",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# CORS middleware for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # In production, specify allowed origins
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.on_event("startup")
async def startup_event():
    """Initialize data directory and repair corrupted files."""
    DataRepair.auto_create_missing_files("/data")

@app.get("/")
async def root():
    """Root endpoint with API information."""
    return {
        "name": "Local Task Manager API",
        "version": "1.0.0",
        "docs": "/docs",
        "status": "running"
    }

# Include API router
app.include_router(api_router, prefix="/api/v1")
```

### API Router

```python
# app/api/v1.py
from fastapi import APIRouter, Depends, HTTPException
from app.core.task_service import TaskService
from app.core.project_service import ProjectService
from app.core.settings_service import SettingsService
from app.storage.json_file import JSONFileStore
from app.models.task import Task
from app.models.project import Project
from app.models.settings import Settings
from app.utils.errors import ResourceNotFoundError, ValidationError

router = APIRouter()

# Dependency factories
def get_task_store():
    return JSONFileStore[Task]("/data/tasks.json", Task)

def get_project_store():
    return JSONFileStore[Project]("/data/projects.json", Project)

def get_settings_store():
    return JSONFileStore[Settings]("/data/settings.json", Settings)

def get_task_service(store: JSONFileStore = Depends(get_task_store)):
    return TaskService(store)

def get_project_service(store: JSONFileStore = Depends(get_project_store)):
    return ProjectService(store)

def get_settings_service(store: JSONFileStore = Depends(get_settings_store)):
    return SettingsService(store)

# Tasks endpoints
@router.get("/tasks")
async def list_tasks(
    status: str = None,
    project: str = None,
    sort_by: str = "created",
    service: TaskService = Depends(get_task_service)
):
    return service.list_tasks(
        status=status if status != "all" else None,
        project=project if project else None,
        sort_by=sort_by
    )

@router.post("/tasks")
async def create_task(
    task_data: dict,
    service: TaskService = Depends(get_task_service)
):
    if "title" not in task_data or not task_data["title"]:
        raise ValidationError("Title is required")
    return service.create_task(**task_data)

@router.put("/tasks/{task_id}")
async def update_task(
    task_id: str,
    task_data: dict,
    service: TaskService = Depends(get_task_service)
):
    try:
        return service.update_task(task_id, **task_data)
    except ResourceNotFoundError:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")

@router.delete("/tasks/{task_id}")
async def delete_task(
    task_id: str,
    service: TaskService = Depends(get_task_service)
):
    try:
        service.delete_task(task_id)
        return {"status": "deleted"}
    except ResourceNotFoundError:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")

@router.post("/tasks/{task_id}/toggle")
async def toggle_task(
    task_id: str,
    service: TaskService = Depends(get_task_service)
):
    try:
        return service.toggle_task(task_id)
    except ResourceNotFoundError:
        raise HTTPException(status_code=404, detail=f"Task {task_id} not found")

# Projects endpoints
@router.get("/projects")
async def list_projects(
    service: ProjectService = Depends(get_project_service)
):
    return service.list_projects()

@router.post("/projects")
async def create_project(
    project_data: dict,
    service: ProjectService = Depends(get_project_service)
):
    if "name" not in project_data or not project_data["name"]:
        raise ValidationError("Project name is required")
    return service.create_project(project_data["name"])

@router.delete("/projects/{name}")
async def delete_project(
    name: str,
    service: ProjectService = Depends(get_project_service)
):
    deleted = service.delete_project(name)
    if not deleted:
        raise HTTPException(status_code=404, detail=f"Project '{name}' not found")
    return {"status": "deleted"}

# Settings endpoints
@router.get("/settings")
async def get_settings(
    service: SettingsService = Depends(get_settings_service)
):
    return service.get_settings()

@router.put("/settings")
async def update_settings(
    settings_data: dict,
    service: SettingsService = Depends(get_settings_service)
):
    return service.update_settings(**settings_data)
```

---

## 10. Docker Configuration

```dockerfile
# backend/Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Create data directory
RUN mkdir -p /data

# Copy application code
COPY app ./app

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

```yaml
# docker-compose.yml (partial)
services:
  backend:
    build: ./backend
    container_name: taskmgr-backend
    ports:
      - "8000:8000"
    volumes:
      - taskmgr-data:/data
    restart: unless-stopped
```

---

## 11. Summary of Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Backend Framework | FastAPI | Spec preference, type hints, async support |
| Data Persistence | JSON files in /data | Spec requirement for inspection |
| Storage Pattern | Atomic writes (temp + rename) | Spec requirement for safety |
| Error Handling | Custom exceptions + HTTPException | Clean separation of concerns |
| API Versioning | /api/v1 | Future-proofing |
| Data Models | Pydantic | Type safety, validation |
| File Structure | Layered (models, api, storage, core) | Separation of concerns |

---

*End of Backend API Design Document*
