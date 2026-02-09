# Contributing to Local Task Manager

Thank you for your interest in contributing to the Local Task Manager project! This document provides guidelines for contributing to the project.

---

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Environment](#development-environment)
- [Running Tests](#running-tests)
- [Code Style](#code-style)
- [Pull Request Process](#pull-request-process)
- [Documentation](#documentation)

---

## Code of Conduct

This project and its community are intended to be a welcoming and respectful environment. We expect all contributors to:

- Use welcoming and inclusive language
- Be respectful of differing viewpoints and experiences
- Gracefully accept constructive criticism
- Focus on what is best for the community
- Show empathy towards other community members

---

## Getting Started

### 1. Fork the Repository

Fork the repository on GitHub to create your own copy.

### 2. Clone Your Fork

```bash
git clone https://github.com/YOUR_USERNAME/ai_testbed_task_manager.git
cd ai_testbed_task_manager
```

### 3. Add Upstream Remote

```bash
git remote add upstream https://github.com/original-owner/ai_testbed_task_manager.git
```

### 4. Create a Branch

```bash
git checkout -b feature/your-feature-name
# or
git checkout -b fix/your-fix-name
```

---

## Development Environment

### Backend Setup

1. Navigate to the backend directory:

```bash
cd backend
```

2. Create and activate a virtual environment:

```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:

```bash
pip install -r requirements.txt
pip install -r requirements-dev.txt  # If available
```

4. Create your `.env` file:

```bash
cp .env.example .env
```

5. Start the development server:

```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

### Frontend Setup

1. Navigate to the frontend directory:

```bash
cd frontend
```

2. Install dependencies:

```bash
npm install
# or
pnpm install
```

3. Start the development server:

```bash
npm run dev
# or
pnpm dev
```

---

## Running Tests

### Backend Tests

```bash
cd backend

# Run all tests
pytest

# Run specific test file
pytest tests/test_tasks.py

# Run with coverage
pytest --cov=app --cov-report=html

# Run with verbose output
pytest -v
```

### Frontend Tests

```bash
cd frontend

# Run all tests
npm test
# or
pnpm test

# Run tests in watch mode
npm test -- --watch
# or
pnpm test --watch

# Run with coverage
npm test -- --coverage
```

---

## Code Style

### Backend (Python)

We follow PEP 8 guidelines with some additional rules:

- Use type hints for all function signatures
- Use 4 spaces for indentation (no tabs)
- Limit lines to 79 characters
- Use snake_case for function and variable names
- Use PascalCase for class names
- Write docstrings for all public functions and classes

**Type Hint Examples:**

```python
from typing import List, Optional

def get_task(task_id: str) -> Optional[Task]:
    """Get a task by its ID."""
    pass

def list_tasks(status: Optional[str] = None) -> List[Task]:
    """List all tasks with optional filtering."""
    pass
```

**Docstring Format:**

```python
def create_task(title: str, notes: str = "") -> Task:
    """
    Create a new task.

    Args:
        title: The task title (required)
        notes: Additional notes or description

    Returns:
        The created task object

    Raises:
        ValidationError: If the task data is invalid
    """
    pass
```

### Frontend (TypeScript/React)

- Use TypeScript strict mode
- Follow ESLint rules (configured in `.eslintrc`)
- Use functional components with hooks
- Use PascalCase for component names
- Use camelCase for function and variable names
- Import components in alphabetical order

**React Component Example:**

```typescript
import React, { useState, useEffect } from 'react';

interface TaskProps {
  id: string;
  title: string;
  status: 'active' | 'completed';
  onToggle: (id: string) => void;
}

export const Task: React.FC<TaskProps> = ({ id, title, status, onToggle }) => {
  const [isCompleted, setIsCompleted] = useState(status);

  useEffect(() => {
    setIsCompleted(status);
  }, [status]);

  const handleToggle = () => {
    setIsCompleted(!isCompleted);
    onToggle(id);
  };

  return (
    <div className={`task ${isCompleted ? 'completed' : ''}`}>
      <button onClick={handleToggle}>
        {isCompleted ? 'Undo' : 'Complete'}
      </button>
      <span>{title}</span>
    </div>
  );
};
```

---

## Pull Request Process

### Before Submitting

1. **Update your branch:**

```bash
git fetch upstream
git checkout main
git merge upstream/main
git checkout feature/your-feature
git merge main
```

2. **Run tests:**

```bash
# Backend
cd backend
pytest

# Frontend
cd frontend
npm test
```

3. **Run linters:**

```bash
# Backend
cd backend
ruff check .
black . --check

# Frontend
cd frontend
npm run lint
npm run format:check
```

4. **Update documentation** if your changes affect the API or setup process.

### Submitting a Pull Request

1. Push your branch to your fork:

```bash
git push origin feature/your-feature
```

2. Open a Pull Request on GitHub

3. Fill in the PR template with:
   - A clear description of your changes
   - Any related issues
   - Testing steps

### PR Review Process

1. At least one maintainer must review your PR
2. Address any review comments
3. After approval, a maintainer will merge your PR

---

## Documentation

### API Documentation

API documentation is auto-generated from the FastAPI OpenAPI schema. To view:

```bash
# Start the backend
cd backend
python -m uvicorn app.main:app --reload

# Visit http://localhost:8000/docs
```

### Code Documentation

- Write docstrings for all public functions and classes
- Add inline comments for complex logic
- Update this CONTRIBUTING.md file if adding new development workflows

### README Updates

Update the main README.md if your changes affect:
- Installation instructions
- Configuration options
- Usage examples
- Troubleshooting information

---

## Questions?

If you have questions:

1. Check existing issues and discussions
2. Create a new issue with the "question" label
3. Join our community discussions

---

## Acknowledgments

Thank you for contributing! Your time and effort help make this project better for everyone.
