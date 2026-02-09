/**
 * Mock utilities for frontend tests.
 *
 * Provides reusable mocks for API calls, components, and services.
 */

// Mock API response types
export interface MockTask {
  id: string
  title: string
  notes: string
  status: 'active' | 'completed'
  priority: 'low' | 'medium' | 'high'
  due_date: string | null
  project: string
  created_at: string
  updated_at: string
}

export interface MockProject {
  name: string
  created_at: string
}

export interface MockSettings {
  theme: 'light' | 'dark'
  sort_order: 'priority' | 'due_date' | 'created'
}

// Mock API responses
export const mockTasks: MockTask[] = [
  {
    id: '11111111-1111-1111-1111-111111111111',
    title: 'Sample Task 1',
    notes: 'This is a sample task',
    status: 'active',
    priority: 'high',
    due_date: '2026-02-15T23:59:59Z',
    project: 'Work',
    created_at: '2026-02-01T10:00:00Z',
    updated_at: '2026-02-01T10:00:00Z',
  },
  {
    id: '22222222-2222-2222-2222-222222222222',
    title: 'Sample Task 2',
    notes: 'Another sample task',
    status: 'completed',
    priority: 'medium',
    due_date: null,
    project: 'Personal',
    created_at: '2026-02-02T10:00:00Z',
    updated_at: '2026-02-03T10:00:00Z',
  },
  {
    id: '33333333-3333-3333-3333-333333333333',
    title: 'Sample Task 3',
    notes: 'Third sample task',
    status: 'active',
    priority: 'low',
    due_date: '2026-02-20T23:59:59Z',
    project: 'Work',
    created_at: '2026-02-03T10:00:00Z',
    updated_at: '2026-02-03T10:00:00Z',
  },
]

export const mockProjects = [
  { name: 'Work', created_at: '2026-02-01T10:00:00Z' },
  { name: 'Personal', created_at: '2026-02-01T10:00:00Z' },
  { name: 'Inbox', created_at: '2026-02-01T10:00:00Z' },
]

export const mockSettings: MockSettings = {
  theme: 'light',
  sort_order: 'created',
}

// Mock API functions
export const mockApi = {
  tasks: {
    getAll: vi.fn().mockResolvedValue({ tasks: mockTasks, count: mockTasks.length }),
    getById: vi.fn().mockImplementation((id: string) => {
      const task = mockTasks.find((t) => t.id === id)
      return Promise.resolve(task || null)
    }),
    create: vi.fn().mockImplementation((taskData: Partial<MockTask>) => {
      const newTask: MockTask = {
        id: `new-${Date.now()}`,
        title: taskData.title || 'New Task',
        notes: taskData.notes || '',
        status: taskData.status || 'active',
        priority: taskData.priority || 'medium',
        due_date: taskData.due_date || null,
        project: taskData.project || 'Inbox',
        created_at: new Date().toISOString(),
        updated_at: new Date().toISOString(),
      }
      mockTasks.push(newTask)
      return Promise.resolve(newTask)
    }),
    update: vi.fn().mockImplementation((id: string, taskData: Partial<MockTask>) => {
      const index = mockTasks.findIndex((t) => t.id === id)
      if (index !== -1) {
        mockTasks[index] = { ...mockTasks[index], ...taskData, id }
        return Promise.resolve(mockTasks[index])
      }
      return Promise.resolve(null)
    }),
    delete: vi.fn().mockImplementation((id: string) => {
      const index = mockTasks.findIndex((t) => t.id === id)
      if (index !== -1) {
        mockTasks.splice(index, 1)
        return Promise.resolve(true)
      }
      return Promise.resolve(false)
    }),
    toggle: vi.fn().mockImplementation((id: string) => {
      const task = mockTasks.find((t) => t.id === id)
      if (task) {
        task.status = task.status === 'active' ? 'completed' : 'active'
        task.updated_at = new Date().toISOString()
        return Promise.resolve(task)
      }
      return Promise.resolve(null)
    }),
  },
  projects: {
    getAll: vi.fn().mockResolvedValue(mockProjects),
    create: vi.fn().mockImplementation((projectData: { name: string }) => {
      const newProject = {
        name: projectData.name,
        created_at: new Date().toISOString(),
      }
      return Promise.resolve(newProject)
    }),
    delete: vi.fn().mockImplementation((name: string) => {
      const index = mockProjects.findIndex((p) => p.name === name)
      if (index !== -1) {
        mockProjects.splice(index, 1)
        return Promise.resolve(true)
      }
      return Promise.resolve(false)
    }),
  },
  settings: {
    get: vi.fn().mockResolvedValue(mockSettings),
    update: vi.fn().mockImplementation((settings: Partial<MockSettings>) => {
      Object.assign(mockSettings, settings)
      return Promise.resolve(mockSettings)
    }),
  },
}

// Clear all mocks before each test
export const clearMocks = () => {
  vi.clearAllMocks()
}
