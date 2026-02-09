export type Priority = 'low' | 'medium' | 'high';
export type TaskStatus = 'pending' | 'in_progress' | 'completed';

export interface Task {
  id: string;
  title: string;
  notes: string;
  status: TaskStatus;
  priority: Priority;
  dueDate?: string;
  project: string;
  createdAt: string;
  updatedAt: string;
}

export interface TaskFormData {
  title: string;
  notes?: string;
  status?: TaskStatus;
  priority?: Priority;
  dueDate?: string;
  project?: string;
}

export interface Project {
  name: string;
  createdAt: string;
}

export interface Settings {
  theme: 'light' | 'dark';
  sortOrder: 'priority' | 'due_date' | 'created';
}

export interface ApiError {
  message: string;
  code?: string;
  details?: unknown;
}

export interface TaskListResponse {
  tasks: Task[];
  count: number;
}
