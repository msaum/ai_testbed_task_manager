import type { ReactNode } from 'react';

interface LayoutProps {
  children: ReactNode;
}

export function Layout({ children }: LayoutProps) {
  return (
    <div className="layout">
      <header className="header">
        <nav className="nav">
          <div className="nav-logo">Task Manager</div>
          <div className="nav-links">
            <a href="/">Home</a>
          </div>
        </nav>
      </header>
      <main className="main-content">{children}</main>
      <footer className="footer">
        <p>Local Task Manager &copy; 2026</p>
      </footer>
    </div>
  );
}

export default Layout;
