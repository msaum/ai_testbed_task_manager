# Frontend Stack Design Document

**Document Version:** 1.0
**Date:** 2026-02-09
**Project:** Local Task Manager

---

## 1. Framework Selection

### Decision: React with TypeScript

**Rationale:**

1. **Product Spec Preference:** The product spec lists React as the first "allowed" framework with "(preferred)" notation.

2. **Ecosystem Maturity:** React has the most mature ecosystem for:
   - Component libraries and patterns
   - Type safety with TypeScript integration
   - Development tooling (React DevTools, Vite, etc.)

3. **Component-Based Architecture:** The three-panel layout (Sidebar, Main, Detail Drawer) maps naturally to React's component model.

4. **State Management:** React Hooks provide sufficient state management for this application without needing external libraries.

5. **Production Ready:** Create React App / Vite builds produce static assets suitable for nginx serving.

### Framework Configuration

```
Framework: React 18.x
Language: TypeScript 5.x
Build Tool: Vite (for development and production builds)
Styling: CSS Modules + CSS Variables (for theme support)
```

---

## 2. Component Structure

### Directory Structure

```
frontend/
├── src/
│   ├── components/
│   │   ├── common/
│   │   │   ├── Button.tsx
│   │   │   ├── IconButton.tsx
│   │   │   ├── Input.tsx
│   │   │   ├── Modal.tsx
│   │   │   ├── Select.tsx
│   │   │   └── ThemeToggle.tsx
│   │   ├── layout/
│   │   │   ├── Sidebar.tsx
│   │   │   ├── TaskList.tsx
│   │   │   ├── TaskItem.tsx
│   │   │   └── DetailDrawer.tsx
│   │   └── features/
│   │       ├── TaskEditor.tsx
│   │       ├── ProjectSelector.tsx
│   │       └── PriorityBadge.tsx
│   ├── hooks/
│   │   ├── useTasks.ts
│   │   ├── useProjects.ts
│   │   ├── useSettings.ts
│   │   └── useApi.ts
│   ├── types/
│   │   ├── task.ts
│   │   ├── project.ts
│   │   └── api.ts
│   ├── utils/
│   │   ├── date.ts
│   │   ├── filter.ts
│   │   └── sort.ts
│   ├── constants/
│   │   ├── themes.ts
│   │   └── priorities.ts
│   ├── App.tsx
│   ├── main.tsx
│   └── index.css
├── public/
│   └── index.html
├── vite.config.ts
├── tsconfig.json
└── Dockerfile
```

### Component Hierarchy

```
App
├── Sidebar (Project Selector)
│   ├── ProjectList
│   └── AddProjectButton
├── Main (Task Area)
│   ├── TaskFilterBar (Status, Project, Sort)
│   ├── TaskList
│   │   └── TaskItem (x N)
│   └── EmptyState (when no tasks)
└── DetailDrawer (Task Editor)
    ├── TaskEditor
    │   ├── TitleInput
    │   ├── NotesEditor
    │   ├── PrioritySelect
    │   ├── DueDateInput
    │   └── ProjectSelect
    └── DrawerActions (Save, Delete, Close)
```

---

## 3. State Management Approach

### Strategy: React Hooks with Local State

**Decision:** Use React Hooks (useState, useEffect, useReducer) for state management without external libraries like Redux or Zustand.

**Rationale:**

1. **Application Size:** This is a small-to-medium application with a single-user scope
2. **State Complexity:** The state graph is shallow (tasks, projects, settings, UI state)
3. **Performance:** For this scale, React's built-in state is performant
4. **Simplicity:** Fewer dependencies reduce complexity and potential conflicts

### State Organization

```typescript
// Top-level state in App.tsx
interface AppState {
  tasks: Task[];
  projects: Project[];
  settings: Settings;
  ui: {
    selectedTaskId: string | null;
    filter: {
      status: 'all' | 'active' | 'completed';
      project: string | null;
      sortBy: 'priority' | 'due_date' | 'created';
    };
    isDarkMode: boolean;
  };
}
```

### State Management Patterns

1. **Local Component State:** UI-specific state (modal open/close, form inputs)
2. **Context API:** Shared state across multiple components (tasks, projects, settings)
3. **Custom Hooks:** Business logic encapsulation (useTasks, useProjects, useSettings)

### State Flow

```
API Response → Context Provider → Components
    ↑                                    ↓
    └────── Optimistic Update ────────────┘
```

---

## 4. Styling Strategy

### CSS Modules + CSS Variables

**Decision:** Use CSS Modules for component-scoped styling and CSS Variables for theme management.

### Theme System

```css
/* CSS Variables for theming */
:root {
  --color-primary: #3b82f6;
  --color-text: #1f2937;
  --color-background: #ffffff;
  --color-border: #e5e7eb;
  --color-danger: #ef4444;
  --color-success: #10b981;
}

[data-theme="dark"] {
  --color-primary: #60a5fa;
  --color-text: #f3f4f6;
  --color-background: #111827;
  --color-border: #374151;
  --color-danger: #f87171;
  --color-success: #34d399;
}
```

### Styling Components

```typescript
// Component.tsx
import styles from './Component.module.css';

export function Component() {
  return <div className={styles.container}>...</div>;
}
```

---

## 5. API Communication

### Client Setup

- Use Fetch API (built-in to browsers)
- Create a centralized API client in `hooks/useApi.ts`
- Handle JSON serialization/deserialization
- Implement request/response interceptors for error handling

### API Client Pattern

```typescript
export class ApiClient {
  private baseUrl: string;

  constructor(baseUrl: string) {
    this.baseUrl = baseUrl;
  }

  async get<T>(endpoint: string): Promise<T> {
    const response = await fetch(`${this.baseUrl}${endpoint}`);
    return this.handleResponse(response);
  }

  async post<T>(endpoint: string, data: unknown): Promise<T> {
    const response = await fetch(`${this.baseUrl}${endpoint}`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(data),
    });
    return this.handleResponse(response);
  }

  // ... put, delete methods
}
```

---

## 6. Build and Deployment Configuration

### Vite Configuration

```typescript
// vite.config.ts
import { defineConfig } from 'vite';
import react from '@vitejs/plugin-react';

export default defineConfig({
  plugins: [react()],
  base: './', // For relative paths in Docker
  build: {
    outDir: 'dist',
    emptyOutDir: true,
    sourcemap: false, // Disabled for production
  },
  server: {
    port: 5173,
    proxy: {
      '/api': {
        target: 'http://localhost:8000',
        changeOrigin: true,
      },
    },
  },
});
```

### Docker Build Strategy

```dockerfile
# Build stage
FROM node:20-alpine AS builder
WORKDIR /app
COPY package*.json ./
RUN npm ci
COPY . .
RUN npm run build

# Production stage
FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf
EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

---

## 7. Development Environment

### Hot Reload

- Vite provides built-in HMR for instant feedback
- React Fast Refresh preserves component state

### Development Server

```bash
# Start dev server (proxies API to backend)
npm run dev

# Build for production
npm run build

# Preview production build
npm run preview
```

---

## 8. Performance Considerations

### Optimization Strategies

1. **Code Splitting:** Use React.lazy() for heavy components
2. **Memoization:** Use useMemo and useCallback for expensive operations
3. **Virtual Scrolling:** Consider react-window if task list becomes large
4. **Image Optimization:** Use SVG icons; inline critical CSS

### Bundle Size Targets

- Initial bundle: < 200KB (gzipped)
- Total vendor size: < 300KB (gzipped)

---

## 9. Testing Strategy

### Unit Testing

- Framework: Vitest (fast, Vite-native)
- Library: React Testing Library
- Mock: jsdom for browser-like environment

### Test Coverage

- Components: 80%+
- Hooks: 80%+
- Utilities: 90%+

### Test Files

```
src/
├── components/
│   └── __tests__/
│       ├── TaskList.test.tsx
│       └── TaskItem.test.tsx
├── hooks/
│   └── __tests__/
│       ├── useTasks.test.ts
│       └── useApi.test.ts
└── utils/
    └── __tests__/
        ├── sort.test.ts
        └── filter.test.ts
```

---

## 10. Accessibility

### Compliance Goals

- WCAG 2.1 Level A compliance
- Keyboard navigation support
- ARIA labels on interactive elements
- Proper focus management in modals

### Accessibility Features

1. Semantic HTML5 elements
2. Proper heading hierarchy
3. Focus traps in modals
4. Screen reader announcements for toast notifications
5. Keyboard shortcuts (e.g., Esc to close drawer)

---

## 11. Summary of Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Framework | React | Spec preference, ecosystem maturity |
| Language | TypeScript | Type safety, developer experience |
| Build Tool | Vite | Fast HMR, modern tooling |
| State Management | React Hooks | Sufficient for app scale |
| Styling | CSS Modules + Variables | Scoped styles + theming support |
| API Client | Fetch API | Built-in, no dependencies |
| Testing | Vitest + RTL | Fast, Vite-native |
| Icons | SVG | Inline, scalable, no requests |

---

## 12. Files and Directories to Create

```
frontend/
├── package.json
├── vite.config.ts
├── tsconfig.json
├── tsconfig.node.json
├── src/
│   ├── components/
│   │   ├── common/
│   │   ├── layout/
│   │   └── features/
│   ├── hooks/
│   ├── types/
│   ├── utils/
│   ├── constants/
│   ├── App.tsx
│   ├── main.tsx
│   └── index.css
├── public/
│   └── index.html
└── Dockerfile
```

---

*End of Frontend Stack Design Document*
