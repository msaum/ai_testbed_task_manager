import type { ApiError, Project, Settings, Task, TaskListResponse } from '../types';

const API_BASE_URL =
  import.meta.env.VITE_API_URL || 'http://localhost:8001/api/v1';

interface RequestOptions extends RequestInit {
  params?: Record<string, unknown>;
}

export async function apiRequest<T>(
  path: string,
  options?: RequestOptions
): Promise<T> {
  const url = `${API_BASE_URL}${path}`;
  const headers: HeadersInit = {
    'Content-Type': 'application/json',
    ...options?.headers,
  };

  const response = await fetch(url, {
    ...options,
    headers,
  });

  if (!response.ok) {
    const errorData = await response.json().catch(() => ({}));
    const error = new Error(
      errorData.message || `API error: ${response.statusText}`
    ) as ApiError;
    error.code = errorData.code || response.statusText;
    error.details = errorData;
    throw error;
  }

  return response.json() as Promise<T>;
}

export async function apiGet<T>(path: string): Promise<T> {
  return apiRequest<T>(path, { method: 'GET' });
}

export async function apiPost<T>(path: string, body: unknown): Promise<T> {
  return apiRequest<T>(path, {
    method: 'POST',
    body: JSON.stringify(body),
  });
}

export async function apiPut<T>(path: string, body: unknown): Promise<T> {
  return apiRequest<T>(path, {
    method: 'PUT',
    body: JSON.stringify(body),
  });
}

export async function apiDelete<T>(path: string): Promise<T> {
  return apiRequest<T>(path, { method: 'DELETE' });
}

// Task API functions
export async function getTasks(
  status?: string,
  priority?: string,
  project?: string
): Promise<TaskListResponse> {
  const params = new URLSearchParams();
  if (status) params.append('status', status);
  if (priority) params.append('priority', priority);
  if (project) params.append('project', project);
  const queryString = params.toString();
  const path = `/tasks${queryString ? `?${queryString}` : ''}`;
  return apiGet<TaskListResponse>(path);
}

export async function getTask(taskId: string): Promise<Task> {
  return apiGet<Task>(`/tasks/${taskId}`);
}

export async function createTask(taskData: {
  title: string;
  notes?: string;
  priority?: 'low' | 'medium' | 'high';
  dueDate?: string;
  project?: string;
}): Promise<Task> {
  return apiPost<Task>('/tasks', taskData);
}

export async function updateTask(
  taskId: string,
  taskData: {
    title?: string;
    notes?: string;
    status?: 'pending' | 'in_progress' | 'completed';
    priority?: 'low' | 'medium' | 'high';
    dueDate?: string;
    project?: string;
  }
): Promise<Task> {
  return apiPut<Task>(`/tasks/${taskId}`, taskData);
}

export async function deleteTask(taskId: string): Promise<void> {
  await apiDelete(`/tasks/${taskId}`);
}

export async function updateTaskStatus(
  taskId: string,
  status: 'pending' | 'in_progress' | 'completed'
): Promise<Task> {
  return apiPut<Task>(`/tasks/${taskId}/status`, { status });
}

// Project API functions
export async function getProjects(): Promise<Project[]> {
  return apiGet<Project[]>('/projects');
}

export async function createProject(name: string): Promise<Project> {
  return apiPost<Project>('/projects', { name });
}

export async function deleteProject(name: string): Promise<void> {
  await apiDelete(`/projects/${name}`);
}

// Settings API functions
export async function getSettings(): Promise<Settings> {
  return apiGet<Settings>('/settings');
}

export async function updateSettings(settings: Partial<Settings>): Promise<Settings> {
  return apiPatch<Settings>('/settings', settings);
}

async function apiPatch<T>(path: string, body: unknown): Promise<T> {
  return apiRequest<T>(path, {
    method: 'PATCH',
    body: JSON.stringify(body),
  });
}
