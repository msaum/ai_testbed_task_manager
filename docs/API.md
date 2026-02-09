# Local Task Manager API Documentation

**Document Version:** 1.0.0
**Last Updated:** 2026-02-09
**Base URL:** `/api/v1`

---

## Table of Contents

- [Overview](#overview)
- [Authentication](#authentication)
- [Data Models](#data-models)
- [API Endpoints](#api-endpoints)
- [Error Handling](#error-handling)
- [Examples](#examples)
- [Swagger UI](#swagger-ui)

---

## Overview

The Local Task Manager API provides RESTful endpoints for managing tasks, projects, and application settings. All data is persisted to JSON files on disk.

**Features:**
- Full CRUD operations for tasks and projects
- Task filtering by status, priority, and project
- Thread-safe atomic writes for data integrity
- Automatic JSON repair on corruption

---

## Authentication

**No authentication required.**

This is a single-user application designed for local or private network use. No authentication or authorization is implemented.

---

## Data Models

### Task

Represents a task in the task manager.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| id | string | Yes (auto-generated) | Unique identifier (UUID) |
| title | string | Yes | Task title (min 1 character) |
| notes | string | No | Additional notes or description |
| status | string | No | "active" or "completed" (default: "active") |
| priority | string | No | "low", "medium", or "high" (default: "medium") |
| due_date | string (ISO8601) | No | Due date and time |
| project | string | No | Project name (default: "Inbox") |
| created_at | string (ISO8601) | Yes (auto-generated) | Creation timestamp |
| updated_at | string (ISO8601) | Yes (auto-generated) | Last update timestamp |

**Example Task:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "title": "Complete project",
  "notes": "Finish the API design",
  "status": "active",
  "priority": "high",
  "due_date": "2026-02-15T23:59:59Z",
  "project": "Work",
  "created_at": "2026-02-09T10:00:00Z",
  "updated_at": "2026-02-09T10:00:00Z"
}
```

### Project

Represents a project for organizing tasks.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| name | string | Yes | Project name (min 1 character) |
| created_at | string (ISO8601) | Yes (auto-generated) | Creation timestamp |

**Example Project:**
```json
{
  "name": "Personal",
  "created_at": "2026-02-09T10:00:00Z"
}
```

### Settings

Application settings for UI preferences.

| Field | Type | Required | Description |
|-------|------|----------|-------------|
| theme | string | No | "light" or "dark" (default: "light") |
| sort_order | string | No | "priority", "due_date", or "created" (default: "created") |

**Example Settings:**
```json
{
  "theme": "dark",
  "sort_order": "priority"
}
```

---

## API Endpoints

### Tasks API

#### GET /api/v1/tasks

List all tasks with optional filtering.

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| status | string | Filter by status (active/completed) |
| priority | string | Filter by priority (low/medium/high) |
| project | string | Filter by project name |

**Responses:**

| Status | Description |
|--------|-------------|
| 200 | Success - Returns list of tasks |

**Example Request:**
```bash
# Get all tasks
curl http://localhost:8000/api/v1/tasks

# Get active tasks
curl http://localhost:8000/api/v1/tasks?status=active

# Get high priority tasks in 'Work' project
curl http://localhost:8000/api/v1/tasks?priority=high&project=Work
```

**Example Response:**
```json
{
  "tasks": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "title": "Complete project",
      "notes": "Finish the API design",
      "status": "active",
      "priority": "high",
      "due_date": "2026-02-15T23:59:59Z",
      "project": "Work",
      "created_at": "2026-02-09T10:00:00Z",
      "updated_at": "2026-02-09T10:00:00Z"
    }
  ],
  "count": 1
}
```

#### GET /api/v1/tasks/{task_id}

Get a specific task by ID.

**Path Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| task_id | string | The unique identifier of the task |

**Responses:**

| Status | Description |
|--------|-------------|
| 200 | Success - Returns task details |
| 404 | Not found - Task does not exist |

**Example Request:**
```bash
curl http://localhost:8000/api/v1/tasks/550e8400-e29b-41d4-a716-446655440000
```

**Example Response:**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "title": "Complete project",
  "notes": "Finish the API design",
  "status": "active",
  "priority": "high",
  "due_date": "2026-02-15T23:59:59Z",
  "project": "Work",
  "created_at": "2026-02-09T10:00:00Z",
  "updated_at": "2026-02-09T10:00:00Z"
}
```

#### POST /api/v1/tasks

Create a new task.

**Request Body:**
```json
{
  "title": "Complete project",
  "notes": "Finish the API design",
  "priority": "high",
  "due_date": "2026-02-15T23:59:59Z",
  "project": "Work"
}
```

**Responses:**

| Status | Description |
|--------|-------------|
| 201 | Created - Returns the created task |
| 400 | Bad request - Invalid task data |

**Example Request:**
```bash
curl -X POST http://localhost:8000/api/v1/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Complete project",
    "notes": "Finish the API design",
    "priority": "high",
    "due_date": "2026-02-15T23:59:59Z",
    "project": "Work"
  }'
```

**Example Response:**
```json
{
  "id": "a1b2c3d4-e5f6-7890-abcd-ef1234567890",
  "title": "Complete project",
  "notes": "Finish the API design",
  "status": "active",
  "priority": "high",
  "due_date": "2026-02-15T23:59:59Z",
  "project": "Work",
  "created_at": "2026-02-09T14:30:00Z",
  "updated_at": "2026-02-09T14:30:00Z"
}
```

#### PUT /api/v1/tasks/{task_id}

Update an existing task.

**Path Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| task_id | string | The unique identifier of the task |

**Request Body:** (All fields are optional)

```json
{
  "title": "Updated task title",
  "notes": "Updated notes",
  "status": "completed",
  "priority": "low",
  "due_date": "2026-03-01T00:00:00Z",
  "project": "Personal"
}
```

**Responses:**

| Status | Description |
|--------|-------------|
| 200 | Success - Returns the updated task |
| 404 | Not found - Task does not exist |
| 400 | Bad request - Invalid update data |

**Example Request:**
```bash
curl -X PUT http://localhost:8000/api/v1/tasks/a1b2c3d4-e5f6-7890-abcd-ef1234567890 \
  -H "Content-Type: application/json" \
  -d '{
    "status": "completed"
  }'
```

#### PATCH /api/v1/tasks/{task_id}/status

Update only the status of a task.

**Path Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| task_id | string | The unique identifier of the task |

**Query Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| status | string | New status value ("active" or "completed") |

**Responses:**

| Status | Description |
|--------|-------------|
| 200 | Success - Returns the updated task |
| 404 | Not found - Task does not exist |
| 400 | Bad request - Invalid status value |

**Example Request:**
```bash
curl -X PATCH "http://localhost:8000/api/v1/tasks/a1b2c3d4-e5f6-7890-abcd-ef1234567890/status?status=completed"
```

#### DELETE /api/v1/tasks/{task_id}

Delete a task.

**Path Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| task_id | string | The unique identifier of the task |

**Responses:**

| Status | Description |
|--------|-------------|
| 204 | Success - Task deleted |
| 404 | Not found - Task does not exist |

**Example Request:**
```bash
curl -X DELETE http://localhost:8000/api/v1/tasks/a1b2c3d4-e5f6-7890-abcd-ef1234567890
```

---

### Projects API

#### GET /api/v1/projects

List all projects.

**Responses:**

| Status | Description |
|--------|-------------|
| 200 | Success - Returns list of projects |

**Example Request:**
```bash
curl http://localhost:8000/api/v1/projects
```

**Example Response:**
```json
[
  {
    "name": "Work",
    "created_at": "2026-02-09T10:00:00Z"
  },
  {
    "name": "Personal",
    "created_at": "2026-02-09T11:00:00Z"
  }
]
```

#### GET /api/v1/projects/{project_name}

Get a specific project by name.

**Path Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| project_name | string | The name of the project |

**Responses:**

| Status | Description |
|--------|-------------|
| 200 | Success - Returns project details |
| 404 | Not found - Project does not exist |

**Example Request:**
```bash
curl http://localhost:8000/api/v1/projects/Work
```

**Example Response:**
```json
{
  "name": "Work",
  "created_at": "2026-02-09T10:00:00Z"
}
```

#### POST /api/v1/projects

Create a new project.

**Request Body:**
```json
{
  "name": "New Project"
}
```

**Responses:**

| Status | Description |
|--------|-------------|
| 201 | Created - Returns the created project |
| 409 | Conflict - Project already exists |
| 400 | Bad request - Invalid project data |

**Example Request:**
```bash
curl -X POST http://localhost:8000/api/v1/projects \
  -H "Content-Type: application/json" \
  -d '{
    "name": "New Project"
  }'
```

#### DELETE /api/v1/projects/{project_name}

Delete a project.

**Path Parameters:**

| Parameter | Type | Description |
|-----------|------|-------------|
| project_name | string | The name of the project |

**Responses:**

| Status | Description |
|--------|-------------|
| 204 | Success - Project deleted |
| 404 | Not found - Project does not exist |

**Example Request:**
```bash
curl -X DELETE http://localhost:8000/api/v1/projects/New%20Project
```

---

### Settings API

#### GET /api/v1/settings

Get all current settings.

**Responses:**

| Status | Description |
|--------|-------------|
| 200 | Success - Returns current settings |

**Example Request:**
```bash
curl http://localhost:8000/api/v1/settings
```

**Example Response:**
```json
{
  "theme": "dark",
  "sort_order": "priority"
}
```

#### PUT /api/v1/settings

Update all settings.

**Request Body:**
```json
{
  "theme": "dark",
  "sort_order": "due_date"
}
```

**Responses:**

| Status | Description |
|--------|-------------|
| 200 | Success - Returns updated settings |
| 400 | Bad request - Invalid settings data |

**Example Request:**
```bash
curl -X PUT http://localhost:8000/api/v1/settings \
  -H "Content-Type: application/json" \
  -d '{
    "theme": "dark"
  }'
```

#### PATCH /api/v1/settings

Partially update settings.

**Request Body:** (All fields are optional)

```json
{
  "theme": "dark"
}
```

**Responses:**

| Status | Description |
|--------|-------------|
| 200 | Success - Returns updated settings |
| 400 | Bad request - Invalid settings data |

**Example Request:**
```bash
curl -X PATCH http://localhost:8000/api/v1/settings \
  -H "Content-Type: application/json" \
  -d '{
    "sort_order": "priority"
  }'
```

---

## Error Handling

The API uses standard HTTP status codes:

| Status | Description |
|--------|-------------|
| 200 | OK |
| 201 | Created |
| 204 | No Content |
| 400 | Bad Request - Invalid parameters or data |
| 404 | Not Found - Resource does not exist |
| 409 | Conflict - Resource already exists |
| 500 | Internal Server Error |

**Error Response Format:**
```json
{
  "detail": "Error message describing what went wrong"
}
```

**Common Error Responses:**

| Status | Error Message | Description |
|--------|---------------|-------------|
| 400 | "Title is required" | Missing required field |
| 400 | "Invalid status. Must be one of: active, completed" | Invalid status value |
| 404 | "Task not found" | Task ID doesn't exist |
| 404 | "Project not found" | Project name doesn't exist |
| 409 | "Project 'Name' already exists" | Duplicate project |

---

## Examples

### Complete Workflow Example

Here's a complete example of using the API to manage tasks:

```bash
# 1. Get current settings
curl http://localhost:8000/api/v1/settings

# 2. Create a project
curl -X POST http://localhost:8000/api/v1/projects \
  -H "Content-Type: application/json" \
  -d '{"name": "Personal"}'

# 3. Create a task
curl -X POST http://localhost:8000/api/v1/tasks \
  -H "Content-Type: application/json" \
  -d '{
    "title": "Buy groceries",
    "notes": "Milk, bread, eggs",
    "priority": "medium",
    "due_date": "2026-02-15T18:00:00Z",
    "project": "Personal"
  }'

# 4. List all tasks
curl http://localhost:8000/api/v1/tasks

# 5. Update task status to complete
curl -X PATCH "http://localhost:8000/api/v1/tasks/{task-id}/status?status=completed"

# 6. List only completed tasks
curl "http://localhost:8000/api/v1/tasks?status=completed"

# 7. Delete a project
curl -X DELETE http://localhost:8000/api/v1/projects/Personal
```

### JavaScript/TypeScript Example

```typescript
// Task API client example
const API_BASE = 'http://localhost:8000/api/v1';

interface Task {
  id: string;
  title: string;
  notes: string;
  status: 'active' | 'completed';
  priority: 'low' | 'medium' | 'high';
  due_date: string | null;
  project: string;
  created_at: string;
  updated_at: string;
}

async function createTask(task: Partial<Task>): Promise<Task> {
  const response = await fetch(`${API_BASE}/tasks`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(task),
  });
  return await response.json();
}

async function listTasks(status?: string): Promise<{ tasks: Task[]; count: number }> {
  const url = status ? `${API_BASE}/tasks?status=${status}` : `${API_BASE}/tasks`;
  const response = await fetch(url);
  return await response.json();
}

async function updateTaskStatus(taskId: string, status: 'active' | 'completed'): Promise<Task> {
  const response = await fetch(`${API_BASE}/tasks/${taskId}/status?status=${status}`, {
    method: 'PATCH',
  });
  return await response.json();
}
```

---

## Swagger UI

The API includes automatic interactive documentation via Swagger UI.

**Access Documentation:**
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- OpenAPI JSON: http://localhost:8000/openapi.json

The Swagger UI allows you to:
- View all available endpoints
- Try out API requests directly from the browser
- View request/response schemas

---

## Data Storage

All data is persisted to JSON files in the `/data` directory:

| File | Description |
|------|-------------|
| `/data/tasks.json` | All tasks |
| `/data/projects.json` | All projects |
| `/data/settings.json` | Application settings |

**File Structure:**
```json
// tasks.json
{
  "tasks": [
    {
      "id": "...",
      "title": "...",
      ...
    }
  ]
}
```

**Data Safety Features:**
- Atomic writes using temp file + rename pattern
- File locking during writes to prevent corruption
- Automatic JSON repair on corruption
- Backup files created before writes

---

*End of API Documentation*
