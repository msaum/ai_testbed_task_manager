import { useEffect, useState, useMemo } from 'react';
import { getTasks, deleteTask, updateTaskStatus } from '../../utils/api';
import type { Task, TaskStatus } from '../../types';

interface TaskListProps {
  selectedProject: string | null;
  onSelectTask?: (task: Task) => void;
}

export function TaskList({ selectedProject, onSelectTask }: TaskListProps) {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Filter states
  const [statusFilter, setStatusFilter] = useState<string>('all');
  const [priorityFilter, setPriorityFilter] = useState<string>('all');
  const [sortBy, setSortBy] = useState<string>('due_date');

  useEffect(() => {
    loadTasks();
  }, [selectedProject]);

  async function loadTasks() {
    try {
      setLoading(true);
      const response = await getTasks(
        statusFilter === 'all' ? undefined : statusFilter,
        priorityFilter === 'all' ? undefined : priorityFilter,
        selectedProject || undefined
      );
      setTasks(response.tasks);
    } catch (err) {
      console.error('Failed to load tasks:', err);
      setError('Failed to load tasks');
    } finally {
      setLoading(false);
    }
  }

  async function handleDelete(taskId: string, e: React.MouseEvent) {
    e.stopPropagation();
    if (confirm('Are you sure you want to delete this task?')) {
      try {
        await deleteTask(taskId);
        setTasks(tasks.filter((t) => t.id !== taskId));
      } catch (err) {
        console.error('Failed to delete task:', err);
        setError('Failed to delete task');
      }
    }
  }

  async function handleStatusChange(taskId: string, newStatus: TaskStatus, e: React.MouseEvent) {
    e.stopPropagation();
    try {
      const updatedTask = await updateTaskStatus(taskId, newStatus);
      setTasks(
        tasks.map((t) => (t.id === taskId ? { ...t, status: updatedTask.status } : t))
      );
    } catch (err) {
      console.error('Failed to update task status:', err);
      setError('Failed to update task status');
    }
  }

  const sortedAndFilteredTasks = useMemo(() => {
    let filtered = tasks;

    // Apply status filter
    if (statusFilter !== 'all') {
      filtered = filtered.filter((t) => t.status === statusFilter);
    }

    // Apply priority filter
    if (priorityFilter !== 'all') {
      filtered = filtered.filter((t) => t.priority === priorityFilter);
    }

    // Apply sorting
    const sorted = [...filtered].sort((a, b) => {
      switch (sortBy) {
        case 'priority':
          const priorityOrder = { high: 0, medium: 1, low: 2 };
          return priorityOrder[a.priority] - priorityOrder[b.priority];
        case 'due_date':
          if (!a.dueDate && !b.dueDate) return 0;
          if (!a.dueDate) return 1;
          if (!b.dueDate) return -1;
          return new Date(a.dueDate).getTime() - new Date(b.dueDate).getTime();
        case 'created':
          return new Date(b.createdAt).getTime() - new Date(a.createdAt).getTime();
        default:
          return 0;
      }
    });

    return sorted;
  }, [tasks, statusFilter, priorityFilter, sortBy]);

  const statusCount = useMemo(() => {
    return {
      all: tasks.length,
      pending: tasks.filter((t) => t.status === 'pending').length,
      in_progress: tasks.filter((t) => t.status === 'in_progress').length,
      completed: tasks.filter((t) => t.status === 'completed').length,
    };
  }, [tasks]);

  const priorityCount = useMemo(() => {
    return {
      all: tasks.length,
      high: tasks.filter((t) => t.priority === 'high').length,
      medium: tasks.filter((t) => t.priority === 'medium').length,
      low: tasks.filter((t) => t.priority === 'low').length,
    };
  }, [tasks]);

  const isOverdue = (dueDate?: string) => {
    if (!dueDate) return false;
    return new Date(dueDate) < new Date();
  };

  return (
    <>
      {/* Filters Bar */}
      <div className="filters-bar">
        <div className="filter-group">
          <label>Status</label>
          <select value={statusFilter} onChange={(e) => setStatusFilter(e.target.value)}>
            <option value="all">All ({statusCount.all})</option>
            <option value="pending">Pending ({statusCount.pending})</option>
            <option value="in_progress">In Progress ({statusCount.in_progress})</option>
            <option value="completed">Completed ({statusCount.completed})</option>
          </select>
        </div>

        <div className="filter-group">
          <label>Priority</label>
          <select
            value={priorityFilter}
            onChange={(e) => setPriorityFilter(e.target.value)}
          >
            <option value="all">All ({priorityCount.all})</option>
            <option value="high">High ({priorityCount.high})</option>
            <option value="medium">Medium ({priorityCount.medium})</option>
            <option value="low">Low ({priorityCount.low})</option>
          </select>
        </div>

        <div className="filter-group">
          <label>Sort By</label>
          <select value={sortBy} onChange={(e) => setSortBy(e.target.value)}>
            <option value="due_date">Due Date</option>
            <option value="priority">Priority</option>
            <option value="created">Created Date</option>
          </select>
        </div>
      </div>

      {/* Task List */}
      <div className="task-list">
        {loading && (
          <div className="loading-spinner">
            <div className="spinner"></div>
          </div>
        )}

        {error && (
          <div className="empty-state">
            <h3 className="text-error">Error</h3>
            <p>{error}</p>
          </div>
        )}

        {!loading && sortedAndFilteredTasks.length === 0 && (
          <div className="empty-state">
            <h3>No tasks found</h3>
            <p>
              {selectedProject
                ? `No tasks in "${selectedProject}"`
                : 'Create your first task to get started!'}
            </p>
          </div>
        )}

        {!loading &&
          sortedAndFilteredTasks.map((task) => (
            <div
              key={task.id}
              className={`task-card ${task.status === 'completed' ? 'completed' : ''}`}
              onClick={() => onSelectTask && onSelectTask(task)}
            >
              <div className="task-header">
                <h4
                  className={`task-title ${task.status === 'completed' ? 'completed' : ''}`}
                >
                  {task.title}
                </h4>
              </div>

              <div className="task-meta">
                <span
                  className={`priority-badge priority-${task.priority}`}
                >
                  {task.priority}
                </span>
                <span className="project-tag">Project: {task.project}</span>
                {task.dueDate && (
                  <span
                    className={`task-due-date ${isOverdue(task.dueDate) ? 'overdue' : ''}`}
                  >
                    {isOverdue(task.dueDate) ? 'Overdue: ' : 'Due: '}
                    {new Date(task.dueDate).toLocaleDateString()}
                  </span>
                )}
              </div>

              <div className="task-actions">
                <button
                  onClick={(e) => handleStatusChange(task.id, 'pending', e)}
                  disabled={task.status === 'pending'}
                  style={{
                    padding: '0.25rem 0.5rem',
                    cursor: task.status === 'pending' ? 'default' : 'pointer',
                    opacity: task.status === 'pending' ? 0.5 : 1,
                  }}
                  title="Mark as pending"
                >
                  Pending
                </button>
                <button
                  onClick={(e) => handleStatusChange(task.id, 'in_progress', e)}
                  disabled={task.status === 'in_progress'}
                  style={{
                    padding: '0.25rem 0.5rem',
                    cursor: task.status === 'in_progress' ? 'default' : 'pointer',
                    opacity: task.status === 'in_progress' ? 0.5 : 1,
                  }}
                  title="Mark as in progress"
                >
                  In Progress
                </button>
                <button
                  onClick={(e) => handleStatusChange(task.id, 'completed', e)}
                  disabled={task.status === 'completed'}
                  style={{
                    padding: '0.25rem 0.5rem',
                    cursor: task.status === 'completed' ? 'default' : 'pointer',
                    opacity: task.status === 'completed' ? 0.5 : 1,
                  }}
                  title="Mark as completed"
                >
                  Done
                </button>
                <button
                  onClick={(e) => handleDelete(task.id, e)}
                  style={{
                    padding: '0.25rem 0.5rem',
                    cursor: 'pointer',
                    marginLeft: 'auto',
                    background: 'var(--bg-tertiary)',
                    border: '1px solid var(--border)',
                    borderRadius: '4px',
                    color: 'var(--error)',
                  }}
                  title="Delete task"
                >
                  Delete
                </button>
              </div>
            </div>
          ))}
      </div>
    </>
  );
}

export default TaskList;
