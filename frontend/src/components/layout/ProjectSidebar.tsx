import { useEffect, useState } from 'react';
import { getProjects, deleteProject } from '../../utils/api';
import type { Project } from '../../types';

interface ProjectSidebarProps {
  selectedProject: string | null;
  onSelectProject: (project: string | null) => void;
}

export function ProjectSidebar({ selectedProject, onSelectProject }: ProjectSidebarProps) {
  const [projects, setProjects] = useState<Project[]>([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadProjects();
  }, []);

  async function loadProjects() {
    try {
      setLoading(true);
      const projects = await getProjects();
      setProjects(projects);
    } catch (err) {
      console.error('Failed to load projects:', err);
      setError('Failed to load projects');
    } finally {
      setLoading(false);
    }
  }

  async function handleDeleteProject(projectName: string, e: React.MouseEvent) {
    e.stopPropagation();
    if (confirm(`Are you sure you want to delete project "${projectName}"?`)) {
      try {
        await deleteProject(projectName);
        setProjects(projects.filter((p) => p.name !== projectName));
        if (selectedProject === projectName) {
          onSelectProject(null);
        }
      } catch (err) {
        console.error('Failed to delete project:', err);
        setError('Failed to delete project');
      }
    }
  }

  return (
    <aside className="sidebar">
      <div className="sidebar-section">
        <h3>Projects</h3>
        <ul className="project-list">
          <li
            className={selectedProject === null ? 'active' : ''}
            onClick={() => onSelectProject(null)}
          >
            <span>All Projects</span>
          </li>
          {loading && <li>Loading projects...</li>}
          {error && <li className="text-error">{error}</li>}
          {!loading &&
            projects.map((project) => (
              <li
                key={project.name}
                className={selectedProject === project.name ? 'active' : ''}
                onClick={() => onSelectProject(project.name)}
              >
                <span>{project.name}</span>
                <button
                  onClick={(e) => handleDeleteProject(project.name, e)}
                  className="delete-btn"
                  style={{
                    background: 'none',
                    border: 'none',
                    color: 'inherit',
                    cursor: 'pointer',
                    opacity: 0.5,
                    marginLeft: '0.5rem',
                    fontSize: '0.9rem',
                  }}
                  title="Delete project"
                >
                  ×
                </button>
              </li>
            ))}
        </ul>
      </div>

      <div className="sidebar-section">
        <h3>Quick Actions</h3>
        <button
          onClick={() => {
            onSelectProject(null);
          }}
          style={{
            width: '100%',
            padding: '0.5rem',
            marginBottom: '0.5rem',
            cursor: 'pointer',
            background: 'var(--bg-tertiary)',
            border: '1px solid var(--border)',
            borderRadius: '6px',
            color: 'var(--text-primary)',
          }}
        >
          Clear Filters
        </button>
      </div>
    </aside>
  );
}

export default ProjectSidebar;
