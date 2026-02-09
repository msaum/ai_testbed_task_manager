# Testing Strategy

This document describes the testing infrastructure for the Local Task Manager application.

## Overview

The application uses a comprehensive testing strategy with tests at multiple levels:

1. **Unit Tests** - Test individual components in isolation
2. **Integration Tests** - Test component interactions
3. **E2E Tests** - Test complete user flows and API behavior
4. **Performance Tests** - Verify response times and resource usage

## Test Directory Structure

```
tests/
├── backend/              # Backend tests (Python/pytest)
│   ├── unit/            # Unit tests
│   │   ├── test_storage_atomic.py      # Atomic write operations
│   │   ├── test_storage_json_file.py   # JSON file store
│   │   └── test_models.py              # Pydantic models
│   ├── integration/     # Integration tests
│   │   └── test_crud_operations.py     # Full CRUD operations
│   ├── fixtures/        # Test fixtures
│   ├── conftest.py      # Shared pytest fixtures
│   └── requirements.txt # Test dependencies
│
├── frontend/            # Frontend tests (Vitest/React Testing Library)
│   ├── unit/            # Unit tests
│   ├── integration/     # Integration tests
│   ├── fixtures/        # Test fixtures
│   └── mocks.ts         # Mock data and API functions
│
├── e2e/                 # End-to-end tests
│   ├── test_api.py              # API endpoint tests
│   ├── test_storage_persistence.py  # Data persistence tests
│   └── conftest.py              # Shared E2E fixtures
│
└── scripts/             # Test automation scripts
    ├── test-backend.sh       # Run backend tests
    ├── test-frontend.sh      # Run frontend tests
    └── run-all-tests.sh      # Run all tests
```

## Backend Testing (pytest)

### Running Tests

```bash
# Install test dependencies
cd backend
pip install -r tests/requirements.txt

# Run all tests
pytest tests/backend -v

# Run specific test file
pytest tests/backend/unit/test_models.py -v

# Run with coverage
pytest tests/backend -v --cov=app --cov-report=html

# Run with specific test patterns
pytest tests/backend -k "create" -v
```

### Key Test Files

#### `test_storage_atomic.py`
Tests for the atomic write operations:
- `test_atomic_write_creates_new_file` - Verifies file creation
- `test_atomic_write_overwrites_existing` - Verifies file updates
- `test_read_json_file` - Tests error handling for invalid JSON

#### `test_storage_json_file.py`
Tests for the JSON file storage layer:
- `test_store_creates_file_if_not_exists` - File initialization
- `test_add_item` / `test_get_all` - CRUD operations
- `test_update_item` / `test_delete_by_id` - Update and delete

#### `test_models.py`
Tests for Pydantic models:
- `test_create_task_with_required_fields` - Task creation
- `test_task_id_is_uuid` - ID generation
- `test_task_model_dump` - Serialization
- `test_task_model_dump_json` - JSON serialization

### Fixtures

Available fixtures are defined in `conftest.py`:

| Fixture | Description |
|---------|-------------|
| `temp_dir` | Temporary directory for test data |
| `test_data_dir` | Test data directory structure |
| `tasks_file` | Empty tasks.json file |
| `projects_file` | Empty projects.json file |
| `settings_file` | Empty settings.json file |
| `task_store` | Ready-to-use JSONFileStore for tasks |
| `project_store` | Ready-to-use JSONFileStore for projects |
| `settings_store` | SingleValueStore for settings |
| `sample_task` | Sample Task instance |
| `sample_project` | Sample Project instance |
| `sample_settings` | Sample Settings instance |
| `sample_tasks_data` | Pre-populated tasks data |
| `corrupted_json_file` | File with invalid JSON for error testing |

## Frontend Testing (Vitest)

### Running Tests

```bash
# Install dependencies
cd frontend
npm install

# Run tests
npm run test

# Run with coverage
npm run test:coverage

# Run tests in UI mode
npm run test:ui

# Run specific test file
npm run test -- src/components/Button.test.tsx
```

### Test Scripts

| Script | Description |
|--------|-------------|
| `npm run test` | Run all tests |
| `npm run test:coverage` | Run tests with coverage report |
| `npm run test:ui` | Run tests in browser UI |
| `npm run test:watch` | Watch mode for development |

### Key Test Files

#### `setup.ts`
Test environment setup:
- Mocks for `window.matchMedia`
- Mocks for `IntersectionObserver`
- Mocks for `ResizeObserver`
- Mocks for `localStorage`
- Console method mocking
- React Testing Library cleanup

#### `mocks.ts`
Reusable test mocks:
- `mockTasks` - Sample task data
- `mockProjects` - Sample project data
- `mockSettings` - Sample settings data
- `mockApi` - Mock API functions (get, post, put, delete)

#### `components.test.tsx`
Unit tests for basic components:
- Button rendering and interactions
- Form components
- Input field handling
- Checkbox toggles
- Select dropdowns
- Textarea handling
- Conditional content

#### `integration.test.tsx`
Integration tests:
- App structure rendering
- Task list display
- Task filtering
- Loading states
- Empty states
- Task creation forms

### Testing Library Components

| Function | Purpose |
|----------|---------|
| `render()` | Render component to document |
| `screen.getByText()` | Find elements by text |
| `screen.getByRole()` | Find elements by role |
| `screen.getByPlaceholderText()` | Find inputs by placeholder |
| `fireEvent.change()` | Simulate input changes |
| `fireEvent.click()` | Simulate clicks |
| `userEvent.type()` | Simulate typing |
| `userEvent.selectOptions()` | Simulate dropdown selection |

## E2E Testing

### Running E2E Tests

```bash
# Start the backend server first
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000

# In another terminal
pytest tests/e2e -v
```

### Running with Docker

```bash
# Build and run test environment
docker-compose -f docker-compose.test.yml up --build

# Run all tests
docker-compose -f docker-compose.test.yml run backend-test

# Run E2E tests
docker-compose -f docker-compose.test.yml run integration-test
```

### Key Test Files

#### `test_api.py`
API endpoint tests:
- `TestHealth` - Health check endpoint
- `TestRoot` - Root API information
- `TestTasks` - Full task CRUD lifecycle
- `TestProjects` - Project management
- `TestSettings` - Settings management
- `TestErrorHandling` - Error response codes
- `TestPerformance` - Response time verification

#### `test_storage_persistence.py`
Data persistence tests:
- `TestPersistence` - Data survives restart
- `TestJSONFileOperations` - File operations
- `TestFileStructure` - JSON file structure verification

## CI/CD Integration

### GitHub Actions Example

```yaml
name: Test Suite

on:
  push:
    branches: [main]
  pull_request:
    branches: [main]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      # Backend tests
      - name: Setup Python
        uses: actions/setup-python@v4
        with:
          python-version: '3.11'
      - name: Install backend dependencies
        run: pip install -r tests/requirements.txt
      - name: Run backend tests
        run: pytest tests/backend -v --cov=app

      # Frontend tests
      - name: Setup Node.js
        uses: actions/setup-node@v3
        with:
          node-version: '20'
      - name: Install frontend dependencies
        run: cd frontend && npm install
      - name: Run frontend tests
        run: cd frontend && npm run test:coverage

      # Upload coverage reports
      - name: Upload coverage reports
        uses: actions/upload-artifact@v3
        with:
          name: coverage
          path: tests/backend/htmlcov/
```

## Coverage Reporting

### Backend Coverage

```bash
# Generate HTML coverage report
pytest tests/backend -v --cov=app --cov-report=html

# View report
open tests/backend/htmlcov/index.html
```

### Frontend Coverage

```bash
# Generate coverage
npm run test:coverage

# View report
open coverage/index.html
```

## Test Data Cleanup

All tests use temporary directories that are automatically cleaned up:

- Backend tests use `tempfile.mkdtemp()` for isolated data
- Frontend tests use Jest's automatic cleanup
- E2E tests use fixtures that clean up after each test

## Best Practices

1. **Test Naming**: Use descriptive names that explain what is being tested
   ```python
   def test_create_task_with_invalid_data_returns_error(self):
       ...
   ```

2. **Isolation**: Each test should be independent and not rely on others
3. **Cleanup**: Always clean up resources in fixtures using `yield` + cleanup
4. **Mocks**: Use mocks for external dependencies (API calls, file I/O)
5. **Assertions**: Use specific assertions rather than generic ones
6. **Coverage**: Aim for at least 80% code coverage

## Troubleshooting

### Backend Tests

**Issue**: `ModuleNotFoundError: No module named 'app'`
```bash
# Ensure you're in the backend directory
cd backend
# Run with PYTHONPATH set
PYTHONPATH=. pytest tests/backend -v
```

### Frontend Tests

**Issue**: `TypeError: Cannot read property 'matchMedia' of undefined`
```bash
# Ensure setup.ts is loaded
# Check vite.config.ts has setupFiles configured
```

**Issue**: Tests timeout
```bash
# Increase timeout
npm run test -- --testTimeout=30000
```

## Related Documentation

- [README.md](README.md) - Project overview
- [AGENTS.md](AGENTS.md) - Development guidelines
