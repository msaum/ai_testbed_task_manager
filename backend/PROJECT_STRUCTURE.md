# Backend Project Structure

## Overview

This document describes the project structure for the Local Task Manager backend implementation.

## Directory Structure

```
backend/
├── app/                      # Main application package
│   ├── __init__.py          # Package initialization and exports
│   ├── main.py              # FastAPI application entry point
│   │
│   ├── api/                 # API layer (routes/endpoints)
│   │   ├── __init__.py
│   │   └── routers/         # API routers
│   │       ├── __init__.py
│   │       ├── tasks.py     # Task CRUD endpoints
│   │       ├── projects.py  # Project CRUD endpoints
│   │       └── settings.py  # Settings management endpoints
│   │
│   ├── models/              # Pydantic data models
│   │   ├── __init__.py
│   │   ├── task.py          # Task, TaskCreate, TaskUpdate models
│   │   ├── project.py       # Project, ProjectCreate models
│   │   └── settings.py      # Settings model
│   │
│   ├── services/            # Business logic layer
│   │   ├── __init__.py
│   │   ├── tasks.py         # TaskService class
│   │   ├── projects.py      # ProjectService class
│   │   └── settings.py      # SettingsService class
│   │
│   ├── core/                # Core configuration and utilities
│   │   ├── __init__.py
│   │   └── config.py        # Application settings (Pydantic BaseSettings)
│   │
│   ├── storage/             # Data persistence layer
│   │   ├── __init__.py
│   │   ├── atomic.py        # Atomic write utilities with file locking
│   │   └── json_file.py     # Generic JSON file stores (JSONFileStore, SingleValueStore)
│   │
│   └── utils/               # Utility functions and helpers
│       ├── __init__.py
│       └── errors.py        # Custom exception classes
│
├── requirements.txt         # Python dependencies
├── .env.example             # Environment variables template
├── Dockerfile              # Docker image definition
├── docker-startup.sh       # Container startup script
└── .dockerignore           # Docker ignore patterns
```

## Module Organization

### app/main.py

The main application entry point that:
- Creates and configures the FastAPI application
- Adds CORS middleware
- Includes all API routers
- Defines health check and root endpoints

**Usage:**
```bash
# Run the application
python -m app.main

# Or using uvicorn
uvicorn app.main:app --reload
```

### app/core/config.py

Application configuration managed by Pydantic's `BaseSettings`:
- Loads configuration from `.env` file
- Provides type-safe access to environment variables
- Includes defaults for development

**Available settings:**
- `APP_NAME`, `APP_VERSION`, `APP_DESCRIPTION`
- `HOST`, `PORT`, `DEBUG`
- `ALLOWED_ORIGINS` (CORS)
- `STORAGE_DIR`

### app/api/routers/*.py

API routers define REST endpoints:
- `tasks.py`: `/api/v1/tasks` - Task management endpoints
- `projects.py`: `/api/v1/projects` - Project management endpoints
- `settings.py`: `/api/v1/settings` - Settings management endpoints

Each router follows FastAPI conventions with:
- GET endpoints for listing and retrieving resources
- POST for creating resources
- PUT/PATCH for updating resources
- DELETE for removing resources

### app/models/*.py

Pydantic models define data structures:
- **Task models**: Task, TaskCreate, TaskUpdate, TaskListResponse
- **Project models**: Project, ProjectCreate
- **Settings models**: Settings

Models include validation, default values, and JSON schema examples.

### app/services/*.py

Service classes contain business logic:
- `TaskService`: Task CRUD operations
- `ProjectService`: Project CRUD operations
- `SettingsService`: Settings management

Services use storage layer for persistence.

### app/storage/*.py

Storage layer provides data persistence:
- `atomic.py`: Atomic write utilities with file locking for concurrent access
- `json_file.py`: Generic JSON file stores (`JSONFileStore`, `SingleValueStore`)

Storage is transparent to services and models.

### app/utils/errors.py

Custom exception classes:
- `BackendError`: Base exception for backend errors
- `ResourceNotFoundError`: 404 errors
- `ValidationError`: 400 errors for invalid data
- `StorageError`: 500 errors for storage issues
- `ConflictError`: 409 errors for duplicates
- `InvalidJSONError`: Corrupted JSON file errors
- `FileLockError`: 503 errors for lock acquisition failures

## Running the Application

### Prerequisites

```bash
cd backend
pip install -r requirements.txt
```

### Development Mode

```bash
# Set up environment
cp .env.example .env
# Edit .env as needed

# Run with uvicorn (hot reload)
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# Or using Python
python -m app.main
```

The API will be available at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- Health check: http://localhost:8000/health

### Production Mode

```bash
# Build and run with Docker
docker build -t task-manager-backend .
docker run -p 8000:8000 task-manager-backend
```

## Adding New Features

### Adding a New API Endpoint

1. Create or update a model in `app/models/`
2. Add service methods in `app/services/`
3. Add router endpoints in `app/api/routers/`
4. Update `__init__.py` files to export new classes

### Adding New Storage

1. Create storage class in `app/storage/` or use existing `JSONFileStore`
2. Implement storage methods in service classes
3. Handle errors using custom exceptions from `app/utils/errors.py`

## API Endpoints Reference

### Tasks
- `GET /api/v1/tasks` - List all tasks
- `GET /api/v1/tasks/{task_id}` - Get task by ID
- `POST /api/v1/tasks` - Create a new task
- `PUT /api/v1/tasks/{task_id}` - Update a task
- `DELETE /api/v1/tasks/{task_id}` - Delete a task
- `PATCH /api/v1/tasks/{task_id}/status` - Update task status

### Projects
- `GET /api/v1/projects` - List all projects
- `GET /api/v1/projects/{project_name}` - Get project by name
- `POST /api/v1/projects` - Create a project
- `DELETE /api/v1/projects/{project_name}` - Delete a project

### Settings
- `GET /api/v1/settings` - Get all settings
- `PUT /api/v1/settings` - Update all settings
- `PATCH /api/v1/settings` - Partial update settings
