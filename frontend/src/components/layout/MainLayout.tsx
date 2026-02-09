import type { ReactNode } from 'react';
import { ThemeToggle } from './ThemeToggle';
import { ProjectSidebar } from './ProjectSidebar';

interface LayoutProps {
  children: ReactNode;
  selectedProject: string | null;
  onSelectProject: (project: string | null) => void;
}

export function Layout({ children, selectedProject, onSelectProject }: LayoutProps) {
  return (
    <div className="layout">
      <header className="header">
        <nav className="nav">
          <div className="nav-logo">Task Manager</div>
          <div className="nav-controls">
            <ThemeToggle />
          </div>
        </nav>
      </header>
      <main className="main-content">
        <ProjectSidebar
          selectedProject={selectedProject}
          onSelectProject={onSelectProject}
        />
        <div className="task-area">{children}</div>
      </main>
      <footer className="footer">
        <p>Local Task Manager &copy; 2026</p>
      </footer>
    </div>
  );
}

export default Layout;
