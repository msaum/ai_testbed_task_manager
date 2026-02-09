# Frontend-Backend Integration Design Document

**Document Version:** 1.0
**Date:** 2026-02-09
**Project:** Local Task Manager

---

## 1. Overview

This document defines the integration contract between the frontend and backend components of the Local Task Manager application.

**Key Principles:**
- RESTful API design with JSON payloads
- Optimistic UI updates for responsive experience
- Graceful error handling and reconciliation
- Strong type safety across the boundary

---

## 2. Architecture Overview

```
┌───────────────────────────────────────────────────────────────────┐
│                         Browser                                   │
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐    │
│  │                     Frontend (React)                     │    │
│  │                                                          │    │
│  │  ┌──────────────┐    ┌──────────────┐    ┌─────────────┐ │    │
│  │  │  Components  │────│  State Management  ││  │  Utils  │ │    │
│  │  └──────────────┘    └────────────────────┘ └─────────────┘ │    │
│  │           │                     │                            │    │
│  │           ▼                     ▼                            │    │
│  │  ┌──────────────────────────────────────────────────────┐   │    │
│  │  │                 API Client (useApi)                  │   │    │
│  │  │  - Fetch wrapper                                     │   │    │
│  │  │  - Error handling                                    │   │    │
│  │  │  - Retry logic                                       │   │    │
│  │  └──────────────────────────────────────────────────────┘   │    │
│  └──────────────────────────────────────────────────────────────┘    │
│                           │                                           │
│                           ▼ HTTP/JSON                                 │
│  ┌──────────────────────────────────────────────────────────────┐   │
│  │                    Backend (FastAPI)                         │   │
│  │                                                              │   │
│  │  ┌────────────────────────────────────────────────────────┐ │   │
│  │  │  API Routes (/api/v1/*)                                │ │   │
│  │  │  - Validation                                          │ │   │
│  │  │  - Authentication (N/A - single user)                  │ │   │
│  │  └────────────────────────────────────────────────────────┘ │   │
│  │           │                                                     │   │
│  │           ▼                                                     │   │
│  │  ┌────────────────────────────────────────────────────────┐   │
│  │  │  Service Layer                                         │   │
│  │  │  - Business logic                                      │   │
│  │  │  - Validation                                          │   │
│  │  └────────────────────────────────────────────────────────┘   │
│  │           │                                                     │   │
│  │           ▼                                                     │   │
│  │  ┌────────────────────────────────────────────────────────┐   │
│  │  │  Storage Layer (JSON files)                            │   │
│  │  │  - Atomic writes                                       │   │
│  │  │  - File locking                                        │   │
│  │  └────────────────────────────────────────────────────────┘   │
│  └───────────────────────────────────────────────────────────────┘
│                           │
│                           ▼
│              ┌──────────────────────────────┐
│              │       /data/ directory       │
│              │  - tasks.json                │
│              │  - projects.json             │
│              │  - settings.json             │
│              └──────────────────────────────┘
```

---

## 3. API Contract

### 3.1 Base URL

```
/api/v1
```

### 3.2 Request Format

All requests use JSON content type:

```
Content-Type: application/json
```

### 3.3 Response Format

#### Success Response

```json
{
  "data": {...},
  "timestamp": "2026-02-09T12:00:00.000Z"
}
```

#### Error Response

```json
{
  "error": {
    "type": "ValidationError|ResourceNotFoundError|StorageError",
    "message": "Descriptive error message",
    "code": "VALIDATION_ERROR|NOT_FOUND|STORAGE_ERROR"
  }
}
```

#### List Response

```json
{
  "items": [...],
  "count": 5,
  "timestamp": "2026-02-09T12:00:00.000Z"
}
```

### 3.4 HTTP Status Codes

| Code | Description | Usage |
|------|-------------|-------|
| 200 | OK | Successful GET, PUT |
| 201 | Created | Successful POST |
| 204 | No Content | Successful DELETE |
| 400 | Bad Request | Invalid request body |
| 404 | Not Found | Resource doesn't exist |
| 409 | Conflict | Duplicate resource |
| 500 | Internal Server Error | Unexpected server error |

---

## 4. API Endpoints

### 4.1 Tasks Endpoints

#### GET /api/v1/tasks

**Purpose:** List all tasks with optional filtering.

**Query Parameters:**
- `status`: `all` \| `active` \| `completed` (default: `all`)
- `project`: string (default: `null`)
- `sort_by`: `priority` \| `due_date` \| `created` (default: `created`)
- `order`: `asc` \| `desc` (default: `asc` for dates, `desc` for priority)

**Request:**
```http
GET /api/v1/tasks?status=active&sort_by=priority HTTP/1.1
Host: localhost:8000
```

**Response (200 OK):**
```json
{
  "items": [
    {
      "id": "550e8400-e29b-41d4-a716-446655440000",
      "title": "Complete project",
      "notes": "Finish the API design",
      "status": "active",
      "priority": "high",
      "due_date": "2026-02-15T23:59:59.000Z",
      "project": "Work",
      "created_at": "2026-02-09T10:00:00.000Z",
      "updated_at": "2026-02-09T11:00:00.000Z"
    }
  ],
  "count": 1,
  "timestamp": "2026-02-09T12:00:00.000Z"
}
```

#### POST /api/v1/tasks

**Purpose:** Create a new task.

**Request Body:**
```json
{
  "title": "Task title",
  "notes": "Optional notes",
  "priority": "low|medium|high",
  "due_date": "2026-02-15T23:59:59.000Z",
  "project": "Project name"
}
```

**Response (201 Created):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "title": "Task title",
  "notes": "Optional notes",
  "status": "active",
  "priority": "medium",
  "due_date": null,
  "project": "Inbox",
  "created_at": "2026-02-09T12:00:00.000Z",
  "updated_at": "2026-02-09T12:00:00.000Z"
}
```

**Validation Errors (400):**
```json
{
  "error": {
    "type": "ValidationError",
    "message": "Title is required",
    "code": "VALIDATION_ERROR"
  }
}
```

#### PUT /api/v1/tasks/{id}

**Purpose:** Update an existing task.

**Request Body (partial):**
```json
{
  "title": "Updated title",
  "status": "completed"
}
```

**Response (200 OK):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "title": "Updated title",
  "status": "completed",
  ...
}
```

#### DELETE /api/v1/tasks/{id}

**Purpose:** Delete a task.

**Response (204 No Content):**
```http
HTTP/1.1 204 No Content
```

#### POST /api/v1/tasks/{id}/toggle

**Purpose:** Toggle task completion status.

**Response (200 OK):**
```json
{
  "id": "550e8400-e29b-41d4-a716-446655440000",
  "title": "Task title",
  "status": "completed",
  ...
}
```

### 4.2 Projects Endpoints

#### GET /api/v1/projects

**Purpose:** List all projects.

**Response (200 OK):**
```json
{
  "items": [
    {
      "name": "Work",
      "created_at": "2026-02-09T10:00:00.000Z"
    }
  ],
  "count": 1,
  "timestamp": "2026-02-09T12:00:00.000Z"
}
```

#### POST /api/v1/projects

**Purpose:** Create a new project.

**Request Body:**
```json
{
  "name": "Project name"
}
```

**Response (201 Created):**
```json
{
  "name": "Project name",
  "created_at": "2026-02-09T12:00:00.000Z"
}
```

#### DELETE /api/v1/projects/{name}

**Purpose:** Delete a project. Tasks remain and become "Inbox".

**Response (204 No Content):**
```http
HTTP/1.1 204 No Content
```

### 4.3 Settings Endpoints

#### GET /api/v1/settings

**Purpose:** Get current user settings.

**Response (200 OK):**
```json
{
  "theme": "light",
  "sort_order": "created"
}
```

#### PUT /api/v1/settings

**Purpose:** Update user settings.

**Request Body (partial):**
```json
{
  "theme": "dark",
  "sort_order": "priority"
}
```

**Response (200 OK):**
```json
{
  "theme": "dark",
  "sort_order": "priority"
}
```

---

## 5. Frontend Integration Patterns

### 5.1 API Client Implementation

```typescript
// src/hooks/useApi.ts
import { useCallback } from 'react';

interface ApiResponse<T> {
  data?: T;
  items?: T[];
  error?: ApiError;
  timestamp: string;
}

interface ApiError {
  type: string;
  message: string;
  code: string;
}

export class ApiClient {
  private readonly baseUrl: string;

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl;
  }

  private async request<T>(endpoint: string, options?: RequestInit): Promise<T> {
    const url = `${this.baseUrl}${endpoint}`;
    const response = await fetch(url, {
      ...options,
      headers: {
        'Content-Type': 'application/json',
        ...options?.headers,
      },
    });

    if (!response.ok) {
      const errorData = await response.json().catch(() => ({}));
      throw new ApiErrorImpl(errorData.error);
    }

    const data = await response.json();
    return data;
  }

  async get<T>(endpoint: string): Promise<T> {
    return this.request<T>(endpoint);
  }

  async post<T>(endpoint: string, data: unknown): Promise<T> {
    return this.request<T>(endpoint, {
      method: 'POST',
      body: JSON.stringify(data),
    });
  }

  async put<T>(endpoint: string, data: unknown): Promise<T> {
    return this.request<T>(endpoint, {
      method: 'PUT',
      body: JSON.stringify(data),
    });
  }

  async delete(endpoint: string): Promise<void> {
    await this.request(endpoint, { method: 'DELETE' });
  }
}

export class ApiErrorImpl extends Error {
  constructor(public error: ApiError) {
    super(error.message);
    this.name = 'ApiError';
  }
}
```

### 5.2 Task Service Hook

```typescript
// src/hooks/useTasks.ts
import { useState, useCallback } from 'react';
import { ApiClient, ApiErrorImpl } from './useApi';
import type { Task, TaskStatus, Priority } from '../types/task';

interface UseTasksReturn {
  tasks: Task[];
  loading: boolean;
  error: Error | null;
  refresh: () => Promise<void>;
  createTask: (data: Partial<Task>) => Promise<Task>;
  updateTask: (id: string, data: Partial<Task>) => Promise<Task>;
  deleteTask: (id: string) => Promise<void>;
  toggleTask: (id: string) => Promise<void>;
  filterTasks: (filter: TaskFilter) => Task[];
}

export function useTasks(): UseTasksReturn {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<Error | null>(null);

  const apiClient = new ApiClient('/api');

  const refresh = useCallback(async () => {
    setLoading(true);
    setError(null);
    try {
      const response = await apiClient.get<{ items: Task[] }>('/tasks');
      setTasks(response.items || []);
    } catch (err) {
      setError(err as Error);
    } finally {
      setLoading(false);
    }
  }, [apiClient]);

  const createTask = useCallback(async (data: Partial<Task>) => {
    setLoading(true);
    setError(null);
    try {
      const newTask = await apiClient.post<Task>('/tasks', {
        title: data.title || '',
        notes: data.notes || '',
        priority: data.priority || 'medium',
        due_date: data.due_date?.toISOString() || null,
        project: data.project || 'Inbox',
      });
      setTasks(prev => [...prev, newTask]);
      return newTask;
    } catch (err) {
      setError(err as Error);
      throw err;
    } finally {
      setLoading(false);
    }
  }, [apiClient]);

  const updateTask = useCallback(async (id: string, data: Partial<Task>) => {
    setLoading(true);
    setError(null);
    try {
      const updatedTask = await apiClient.put<Task>(`/tasks/${id}`, data);
      setTasks(prev => prev.map(t => t.id === id ? updatedTask : t));
      return updatedTask;
    } catch (err) {
      setError(err as Error);
      throw err;
    } finally {
      setLoading(false);
    }
  }, [apiClient]);

  const deleteTask = useCallback(async (id: string) => {
    setLoading(true);
    setError(null);
    try {
      await apiClient.delete(`/tasks/${id}`);
      setTasks(prev => prev.filter(t => t.id !== id));
    } catch (err) {
      setError(err as Error);
      throw err;
    } finally {
      setLoading(false);
    }
  }, [apiClient]);

  const toggleTask = useCallback(async (id: string) => {
    setLoading(true);
    setError(null);
    try {
      const updatedTask = await apiClient.post<Task>(`/tasks/${id}/toggle`, {});
      setTasks(prev => prev.map(t => t.id === id ? updatedTask : t));
      return updatedTask;
    } catch (err) {
      setError(err as Error);
      throw err;
    } finally {
      setLoading(false);
    }
  }, [apiClient]);

  const filterTasks = useCallback((filter: TaskFilter) => {
    let filtered = [...tasks];

    if (filter.status !== 'all') {
      filtered = filtered.filter(t => t.status === filter.status);
    }

    if (filter.project) {
      filtered = filtered.filter(t => t.project === filter.project);
    }

    // Apply sorting
    const priorityOrder = { high: 0, medium: 1, low: 2 };

    if (filter.sortBy === 'priority') {
      filtered.sort((a, b) => priorityOrder[a.priority] - priorityOrder[b.priority]);
    } else if (filter.sortBy === 'due_date') {
      filtered.sort((a, b) => {
        const dateA = a.due_date ? new Date(a.due_date).getTime() : Infinity;
        const dateB = b.due_date ? new Date(b.due_date).getTime() : Infinity;
        return dateA - dateB;
      });
    } else if (filter.sortBy === 'created') {
      filtered.sort((a, b) => new Date(b.created_at).getTime() - new Date(a.created_at).getTime());
    }

    return filtered;
  }, [tasks]);

  return {
    tasks,
    loading,
    error,
    refresh,
    createTask,
    updateTask,
    deleteTask,
    toggleTask,
    filterTasks,
  };
}
```

### 5.3 Optimistic Update Pattern

```typescript
// src/hooks/useTasks.ts (continuation)
const updateTaskOptimistic = useCallback(async (id: string, data: Partial<Task>) => {
  // Find original task for rollback
  const originalTask = tasks.find(t => t.id === id);

  if (!originalTask) {
    throw new Error('Task not found');
  }

  // Apply optimistic update
  const optimisticTask = { ...originalTask, ...data };
  setTasks(prev => prev.map(t => t.id === id ? optimisticTask : t));

  try {
    const updatedTask = await apiClient.put<Task>(`/tasks/${id}`, data);
    // Update is confirmed, keep optimistic state
    return updatedTask;
  } catch (err) {
    // Revert on error
    if (originalTask) {
      setTasks(prev => prev.map(t => t.id === id ? originalTask : t));
    }
    throw err;
  }
}, [tasks, apiClient]);
```

### 5.4 Error Handling Pattern

```typescript
// src/components/ErrorHandler.tsx
import { useEffect } from 'react';

interface ErrorHandlerProps {
  error: Error | null;
  onRetry?: () => void;
}

export function ErrorHandler({ error, onRetry }: ErrorHandlerProps) {
  useEffect(() => {
    if (error) {
      console.error('API Error:', error);

      // Check for specific error types
      if (error instanceof ApiErrorImpl) {
        switch (error.error.code) {
          case 'VALIDATION_ERROR':
            console.warn('Validation failed:', error.error.message);
            break;
          case 'NOT_FOUND':
            console.warn('Resource not found:', error.error.message);
            break;
        }
      }
    }
  }, [error]);

  if (!error) return null;

  return (
    <div className="error-handler">
      <p className="error-message">{error.message}</p>
      {onRetry && (
        <button onClick={onRetry} className="retry-button">
          Retry
        </button>
      )}
    </div>
  );
}
```

---

## 6. Data Sync Strategy

### 6.1 Initial Load

```typescript
// src/App.tsx
function App() {
  const { refresh, tasks, loading, error } = useTasks();

  useEffect(() => {
    // Load initial data on mount
    refresh();
  }, [refresh]);

  // ... rest of component
}
```

### 6.2 Real-time Updates (Polling)

For simple applications, polling is sufficient:

```typescript
// src/hooks/useTasks.ts
export function useTasksWithPolling(intervalMs: number = 5000) {
  const { tasks, refresh, ...rest } = useTasks();

  useEffect(() => {
    const interval = setInterval(() => {
      refresh();
    }, intervalMs);

    return () => clearInterval(interval);
  }, [refresh]);

  return { tasks, refresh, ...rest };
}
```

### 6.3 Conflict Resolution

**Strategy:** Last-write-wins with client-side reconciliation

```typescript
// Detect and resolve conflicts
function resolveConflict(localTask: Task, serverTask: Task): Task {
  // If server has newer updated_at, use server version
  if (new Date(serverTask.updated_at) > new Date(localTask.updated_at)) {
    return serverTask;
  }

  // Otherwise, keep local changes (merge)
  return {
    ...serverTask,
    ...localTask, // Local takes precedence for unsynced changes
  };
}
```

---

## 7. TypeScript Type Definitions

```typescript
// src/types/task.ts
export type Priority = 'low' | 'medium' | 'high';
export type TaskStatus = 'active' | 'completed';

export interface Task {
  id: string;
  title: string;
  notes: string;
  status: TaskStatus;
  priority: Priority;
  due_date: string | null;  // ISO8601 string
  project: string;
  created_at: string;  // ISO8601 string
  updated_at: string;  // ISO8601 string
}

// src/types/project.ts
export interface Project {
  name: string;
  created_at: string;  // ISO8601 string
}

// src/types/settings.ts
export interface Settings {
  theme: 'light' | 'dark';
  sort_order: 'priority' | 'due_date' | 'created';
}

// src/types/api.ts
export interface ApiResponse<T> {
  data?: T;
  items?: T[];
  error?: ApiError;
  timestamp: string;
}

export interface ApiError {
  type: string;
  message: string;
  code: string;
}
```

---

## 8. Environment Configuration

### 8.1 Frontend Environment Variables

```bash
# .env.development
VITE_API_URL=http://localhost:8000/api

# .env.production
VITE_API_URL=http://localhost:8000/api
```

### 8.2 Docker Environment

```yaml
# docker-compose.yml
services:
  frontend:
    environment:
      - API_URL=http://backend:8000/api
```

---

## 9. Testing the Integration

### 9.1 API Testing (pytest)

```python
# tests/test_api.py
import pytest
from httpx import AsyncClient
from app.main import app

@pytest.mark.asyncio
async def test_create_task():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.post("/api/v1/tasks", json={
            "title": "Test task",
            "priority": "high"
        })
        assert response.status_code == 201
        data = response.json()
        assert data["title"] == "Test task"
        assert data["status"] == "active"

@pytest.mark.asyncio
async def test_list_tasks():
    async with AsyncClient(app=app, base_url="http://test") as client:
        response = await client.get("/api/v1/tasks")
        assert response.status_code == 200
        data = response.json()
        assert "items" in data
        assert isinstance(data["items"], list)
```

### 9.2 Frontend Integration Testing

```typescript
// src/__tests__/TaskList.test.tsx
import { render, screen, waitFor } from '@testing-library/react';
import { TaskList } from '../components/layout/TaskList';
import { useTasks } from '../hooks/useTasks';

jest.mock('../hooks/useTasks');

describe('TaskList', () => {
  it('displays tasks when loaded', async () => {
    (useTasks as jest.Mock).mockReturnValue({
      tasks: [
        { id: '1', title: 'Task 1', status: 'active', ... },
        { id: '2', title: 'Task 2', status: 'active', ... }
      ],
      loading: false,
      error: null,
      refresh: jest.fn(),
      filterTasks: (f: any) => f
    });

    render(<TaskList />);

    expect(screen.getByText('Task 1')).toBeInTheDocument();
    expect(screen.getByText('Task 2')).toBeInTheDocument();
  });
});
```

---

## 10. Performance Considerations

### 10.1 Request Optimization

- **Batch requests:** Use when updating multiple tasks
- **Pagination:** Implement for large datasets (>100 items)
- **Caching:** Use browser caching headers

### 10.2 Response Optimization

```python
# Backend response optimization
from fastapi.responses import ORJSONResponse

@app.get("/api/v1/tasks", response_class=ORJSONResponse)
async def list_tasks(...):
    # ... query logic
    return ORJSONResponse(content={"items": tasks, "count": len(tasks)})
```

---

## 11. Security Considerations

### 11.1 CORS Configuration

```python
# Backend CORS middleware
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["GET", "POST", "PUT", "DELETE"],
    allow_headers=["*"],
)
```

### 11.2 Input Validation

```python
# Use Pydantic models for validation
from pydantic import BaseModel, Field

class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, max_length=200)
    notes: str = Field("", max_length=1000)
    priority: Literal["low", "medium", "high"] = "medium"
    due_date: Optional[datetime] = None
    project: str = Field("Inbox", max_length=100)
```

---

## 12. Summary of Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| API Versioning | /api/v1 | Future-proofing for breaking changes |
| Data Format | JSON | Universal format, human-readable |
| State Management | Optimistic updates | Responsive UX, graceful fallback |
| Error Handling | Structured error responses | Clear error communication |
| Type Safety | TypeScript interfaces | Compile-time validation |
| CORS | Permissive (local dev) | Simple single-user deployment |
| Sync Strategy | Polling + optimistic updates | Simple, effective for local app |

---

*End of Frontend-Backend Integration Design Document*
