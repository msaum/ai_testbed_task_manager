import { useEffect, useState } from 'react';
import type { Task, TaskFormData } from '../../types';

interface TaskDetailDrawerProps {
  isOpen: boolean;
  task: Task | null;
  onClose: () => void;
  onSave: (taskData: TaskFormData) => Promise<void>;
  onDelete?: (taskId: string) => Promise<void>;
}

export function TaskDetailDrawer({
  isOpen,
  task,
  onClose,
  onSave,
  onDelete,
}: TaskDetailDrawerProps) {
  const [formData, setFormData] = useState<TaskFormData>({
    title: '',
    notes: '',
    status: 'pending',
    priority: 'medium',
    project: 'Inbox',
  });
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    if (task) {
      setFormData({
        title: task.title,
        notes: task.notes || '',
        status: task.status,
        priority: task.priority,
        dueDate: task.dueDate ? new Date(task.dueDate).toISOString().split('T')[0] : '',
        project: task.project,
      });
      setError(null);
    }
  }, [task]);

  function handleInputChange(
    field: keyof TaskFormData,
    value: string | boolean
  ) {
    setFormData((prev) => ({ ...prev, [field]: value }));
  }

  async function handleSubmit(e: React.FormEvent) {
    e.preventDefault();
    setLoading(true);
    setError(null);

    try {
      await onSave(formData);
      onClose();
    } catch (err) {
      console.error('Failed to save task:', err);
      setError('Failed to save task');
    } finally {
      setLoading(false);
    }
  }

  function handleDelete(e: React.MouseEvent) {
    e.preventDefault();
    if (task && onDelete && confirm('Are you sure you want to delete this task?')) {
      onDelete(task.id);
      onClose();
    }
  }

  if (!isOpen) return null;

  return (
    <>
      {/* Overlay */}
      <div
        className={`task-drawer-overlay ${isOpen ? 'open' : ''}`}
        onClick={onClose}
      />

      {/* Drawer */}
      <div className={`task-drawer ${isOpen ? 'open' : ''}`}>
        <div className="task-drawer-header">
          <h2>{task ? 'Edit Task' : 'Create Task'}</h2>
          <button className="task-drawer-close" onClick={onClose}>
            ×
          </button>
        </div>

        <div className="task-drawer-body">
          {error && <div className="text-error">{error}</div>}

          <form className="task-drawer-form" onSubmit={handleSubmit}>
            <div className="form-group">
              <label htmlFor="title">Title *</label>
              <input
                id="title"
                type="text"
                value={formData.title}
                onChange={(e) => handleInputChange('title', e.target.value)}
                placeholder="Task title"
                required
                minLength={1}
              />
            </div>

            <div className="form-group">
              <label htmlFor="notes">Notes</label>
              <textarea
                id="notes"
                value={formData.notes}
                onChange={(e) => handleInputChange('notes', e.target.value)}
                placeholder="Task description..."
              />
            </div>

            <div className="form-row">
              <div className="form-group">
                <label htmlFor="status">Status</label>
                <select
                  id="status"
                  value={formData.status}
                  onChange={(e) => handleInputChange('status', e.target.value)}
                >
                  <option value="pending">Pending</option>
                  <option value="in_progress">In Progress</option>
                  <option value="completed">Completed</option>
                </select>
              </div>

              <div className="form-group">
                <label htmlFor="priority">Priority</label>
                <select
                  id="priority"
                  value={formData.priority}
                  onChange={(e) => handleInputChange('priority', e.target.value)}
                >
                  <option value="low">Low</option>
                  <option value="medium">Medium</option>
                  <option value="high">High</option>
                </select>
              </div>
            </div>

            <div className="form-row">
              <div className="form-group">
                <label htmlFor="dueDate">Due Date</label>
                <input
                  id="dueDate"
                  type="date"
                  value={formData.dueDate || ''}
                  onChange={(e) => handleInputChange('dueDate', e.target.value)}
                />
              </div>

              <div className="form-group">
                <label htmlFor="project">Project</label>
                <input
                  id="project"
                  type="text"
                  value={formData.project}
                  onChange={(e) => handleInputChange('project', e.target.value)}
                  placeholder="Project name"
                />
              </div>
            </div>

            {task && (
              <div className="form-group">
                <label>Task ID</label>
                <input
                  type="text"
                  value={task.id}
                  disabled
                  style={{ opacity: 0.7, cursor: 'not-allowed' }}
                />
              </div>
            )}
          </form>
        </div>

        <div className="task-drawer-footer">
          {task && onDelete && (
            <button
              onClick={handleDelete}
              style={{
                padding: '0.75rem 1.5rem',
                cursor: 'pointer',
                background: 'var(--bg-tertiary)',
                border: '1px solid var(--error)',
                borderRadius: '6px',
                color: 'var(--error)',
                marginRight: 'auto',
              }}
            >
              Delete
            </button>
          )}
          <button
            type="button"
            onClick={onClose}
            style={{
              padding: '0.75rem 1.5rem',
              cursor: 'pointer',
              background: 'var(--bg-tertiary)',
              border: '1px solid var(--border)',
              borderRadius: '6px',
              color: 'var(--text-primary)',
            }}
          >
            Cancel
          </button>
          <button
            type="submit"
            onClick={handleSubmit}
            disabled={loading || !formData.title}
            style={{
              padding: '0.75rem 1.5rem',
              cursor: loading || !formData.title ? 'not-allowed' : 'pointer',
              background: 'var(--accent)',
              border: '1px solid var(--accent)',
              borderRadius: '6px',
              color: 'white',
            }}
          >
            {loading ? 'Saving...' : 'Save Task'}
          </button>
        </div>
      </div>
    </>
  );
}

export default TaskDetailDrawer;
