import { BrowserRouter, Routes, Route } from 'react-router-dom';
import { Layout } from './components/layout/MainLayout';
import { ThemeProvider } from './contexts/ThemeContext';
import TaskList from './components/task/TaskList';
import TaskDetailDrawer from './components/task/TaskDetailDrawer';
import { useState } from 'react';
import { createTask, updateTask, deleteTask } from './utils/api';
import type { Task, TaskFormData } from './types';

function App() {
  const [selectedTask, setSelectedTask] = useState<Task | null>(null);
  const [isDrawerOpen, setIsDrawerOpen] = useState(false);
  const [isCreating, setIsCreating] = useState(false);
  const [selectedProject, setSelectedProject] = useState<string | null>(null);

  const handleCreateTask = () => {
    setSelectedTask(null);
    setIsCreating(true);
    setIsDrawerOpen(true);
  };

  const handleEditTask = (task: Task) => {
    setSelectedTask(task);
    setIsCreating(false);
    setIsDrawerOpen(true);
  };

  const handleCloseDrawer = () => {
    setIsDrawerOpen(false);
    setSelectedTask(null);
  };

  const handleSaveTask = async (taskData: TaskFormData) => {
    try {
      if (isCreating) {
        await createTask(taskData);
      } else if (selectedTask) {
        await updateTask(selectedTask.id, taskData);
      }
      // Refresh will happen automatically via TaskList re-render
    } catch (error) {
      console.error('Failed to save task:', error);
      throw error;
    }
  };

  const handleDeleteTask = async (taskId: string) => {
    try {
      await deleteTask(taskId);
    } catch (error) {
      console.error('Failed to delete task:', error);
      throw error;
    }
  };

  return (
    <ThemeProvider>
      <BrowserRouter>
        <Layout
          selectedProject={selectedProject}
          onSelectProject={setSelectedProject}
        >
          <Routes>
            <Route
              path="/"
              element={
                <MainView
                  selectedProject={selectedProject}
                  onEditTask={handleEditTask}
                  onCreateTask={handleCreateTask}
                />
              }
            />
          </Routes>
          <TaskDetailDrawer
            isOpen={isDrawerOpen}
            task={selectedTask}
            onClose={handleCloseDrawer}
            onSave={handleSaveTask}
            onDelete={handleDeleteTask}
          />
          <button
            className="add-task-btn"
            onClick={handleCreateTask}
            title="Create new task"
          >
            +
          </button>
        </Layout>
      </BrowserRouter>
    </ThemeProvider>
  );
}

interface MainViewProps {
  selectedProject: string | null;
  onEditTask: (task: Task) => void;
  onCreateTask: () => void;
}

function MainView({ selectedProject, onEditTask }: MainViewProps) {
  return <TaskList selectedProject={selectedProject} onSelectTask={onEditTask} />;
}

export default App;
