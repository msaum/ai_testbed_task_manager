# Local Task Manager

A lightweight, single-user task management web application designed for local or private network use. The application runs entirely inside Docker containers and persists all state to JSON files on disk.

## Features

- **Task Management**: Create, edit, delete, and track tasks with priorities and due dates
- **Project Organization**: Organize tasks into custom projects
- **Light/Dark Mode**: Toggle between light and dark themes
- **Multi-View Filters**: Filter tasks by status, priority, and project
- **JSON Persistence**: All data stored in human-readable JSON files
- **Docker Ready**: Single command deployment with Docker Compose
- **No Authentication**: Simple, single-user design for local use

---

## Quick Start

### Prerequisites

- Docker (version 20.10 or later)
- Docker Compose (version 2.0 or later)

### Running with Docker Compose

1. **Create the docker-compose.yml file** in your project root:

```yaml
version: "3.9"

services:
  backend:
    build: ./backend
    container_name: taskmgr-backend
    ports:
      - "8000:8000"
    volumes:
      - taskmgr-data:/data
    restart: unless-stopped

  frontend:
    build: ./frontend
    container_name: taskmgr-frontend
    ports:
      - "5173:80"
    environment:
      - API_URL=http://backend:8000/api/v1
    depends_on:
      - backend
    restart: unless-stopped

volumes:
  taskmgr-data:
```

2. **Build and start the containers:**

```bash
docker compose up --build
```

3. **Access the application:**

- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Documentation: http://localhost:8000/docs

4. **Stop the application:**

```bash
docker compose down
```

---

## Local Development Setup

### Backend (FastAPI/Python)

#### Prerequisites

- Python 3.11 or later
- pip (Python package manager)

#### Setup Steps

1. **Clone or navigate to the backend directory:**

```bash
cd /Users/msaum/ai_testbed_task_manager/backend
```

2. **Create a virtual environment:**

```bash
python -m venv venv
source venv/bin/activate
```

3. **Install dependencies:**

```bash
pip install -r requirements.txt
```

4. **Create a `.env` file:**

```bash
cp .env.example .env
```

Edit `.env` to configure:

```env
APP_NAME="Local Task Manager"
APP_VERSION="1.0.0"
APP_DESCRIPTION="A local task management system"
HOST=0.0.0.0
PORT=8000
DEBUG=true
ALLOWED_ORIGINS=http://localhost:5173
STORAGE_DIR=./data
```

5. **Create the data directory:**

```bash
mkdir -p data
```

6. **Run the development server:**

```bash
python -m uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

The backend will be available at http://localhost:8000

#### Running Tests

```bash
pytest
```

### Frontend (React/TypeScript/Vite)

#### Prerequisites

- Node.js 18 or later
- npm or pnpm

#### Setup Steps

1. **Navigate to the frontend directory:**

```bash
cd /Users/msaum/ai_testbed_task_manager/frontend
```

2. **Install dependencies:**

```bash
npm install
# or
pnpm install
```

3. **Run the development server:**

```bash
npm run dev
# or
pnpm dev
```

The frontend will be available at http://localhost:5173

4. **Build for production:**

```bash
npm run build
```

---

## Docker Setup

### Backend Dockerfile

```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Create data directory
RUN mkdir -p /data

# Copy application code
COPY app ./app

# Expose port
EXPOSE 8000

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

### Frontend Dockerfile

```dockerfile
FROM node:18-alpine AS builder

WORKDIR /app

# Copy package files
COPY package*.json ./

# Install dependencies
RUN npm install

# Copy source code
COPY . .

# Build the application
RUN npm run build

# Production stage
FROM nginx:alpine

# Copy built assets
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80

CMD ["nginx", "-g", "daemon off;"]
```

### Docker Compose Configuration

```yaml
version: "3.9"

services:
  backend:
    build: ./backend
    container_name: taskmgr-backend
    ports:
      - "8000:8000"
    volumes:
      - taskmgr-data:/data
    restart: unless-stopped
    environment:
      - DEBUG=true

  frontend:
    build: ./frontend
    container_name: taskmgr-frontend
    ports:
      - "5173:80"
    environment:
      - API_URL=http://localhost:8000/api/v1
    depends_on:
      - backend
    restart: unless-stopped

volumes:
  taskmgr-data:
```

---

## Project Structure

```
ai_testbed_task_manager/
├── backend/                          # FastAPI backend
│   ├── app/
│   │   ├── api/                      # API routes
│   │   │   └── routers/
│   │   │       ├── tasks.py
│   │   │       ├── projects.py
│   │   │       └── settings.py
│   │   ├── core/                     # Core business logic
│   │   │   └── config.py
│   │   ├── models/                   # Pydantic data models
│   │   │   ├── task.py
│   │   │   ├── project.py
│   │   │   └── settings.py
│   │   ├── services/                 # Service layer
│   │   │   ├── tasks.py
│   │   │   ├── projects.py
│   │   │   └── settings.py
│   │   ├── storage/                  # Data persistence layer
│   │   │   ├── atomic.py
│   │   │   └── json_file.py
│   │   ├── utils/                    # Utilities
│   │   │   ├── errors.py
│   │   │   └── helpers.py
│   │   ├── main.py                   # FastAPI app entry point
│   │   └── __init__.py
│   ├── data/                         # Data directory
│   │   ├── tasks.json
│   │   ├── projects.json
│   │   └── settings.json
│   ├── Dockerfile
│   ├── .env.example
│   ├── .dockerignore
│   ├── requirements.txt
│   └── README.md
│
├── frontend/                         # React frontend
│   ├── src/
│   │   ├── components/               # React components
│   │   ├── pages/                    # Page components
│   │   ├── layout/                   # Layout components
│   │   ├── types/                    # TypeScript types
│   │   ├── hooks/                    # Custom hooks
│   │   ├── constants/                # Constants
│   │   ├── utils/                    # Utility functions
│   │   ├── App.tsx
│   │   ├── main.tsx
│   │   └── index.css
│   ├── public/                       # Static assets
│   ├── Dockerfile
│   ├── nginx.conf
│   ├── package.json
│   ├── tsconfig.json
│   ├── vite.config.ts
│   └── README.md
│
├── docs/                             # Documentation
│   └── API.md
│
├── designs/                          # Design documents
│   ├── backend-api.md
│   ├── docker-architecture.md
│   ├── frontend-stack.md
│   └── integration.md
│
├── docker-compose.yml
├── README.md
└── .gitignore
```

---

## API Reference

### Base URL

```
/api/v1
```

### Endpoints

#### Tasks

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/tasks` | List all tasks |
| POST | `/api/v1/tasks` | Create a new task |
| GET | `/api/v1/tasks/{id}` | Get a task by ID |
| PUT | `/api/v1/tasks/{id}` | Update a task |
| PATCH | `/api/v1/tasks/{id}/status` | Update task status |
| DELETE | `/api/v1/tasks/{id}` | Delete a task |

#### Projects

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/projects` | List all projects |
| POST | `/api/v1/projects` | Create a project |
| DELETE | `/api/v1/projects/{name}` | Delete a project |

#### Settings

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/v1/settings` | Get all settings |
| PUT | `/api/v1/settings` | Update all settings |
| PATCH | `/api/v1/settings` | Partially update settings |

### API Documentation

Access interactive API documentation:

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc
- OpenAPI JSON: http://localhost:8000/openapi.json

---

## Configuration

### Environment Variables

**Backend (.env):**

| Variable | Default | Description |
|----------|---------|-------------|
| APP_NAME | "Local Task Manager" | Application name |
| APP_VERSION | "1.0.0" | Application version |
| APP_DESCRIPTION | "A local task management system" | App description |
| HOST | "0.0.0.0" | Server host |
| PORT | 8000 | Server port |
| DEBUG | false | Enable debug mode |
| ALLOWED_ORIGINS | "*" | CORS allowed origins |
| STORAGE_DIR | "./data" | Data storage directory |

### Frontend Configuration

Frontend reads the API URL from environment variables:

| Variable | Default | Description |
|----------|---------|-------------|
| API_URL | http://localhost:8000/api/v1 | Backend API URL |

---

## Data Persistence

All application state is stored as JSON files in the `/data` directory:

| File | Description |
|------|-------------|
| `tasks.json` | All tasks |
| `projects.json` | All projects |
| `settings.json` | Application settings |

### Data File Structure

**tasks.json:**
```json
{
  "tasks": [
    {
      "id": "uuid",
      "title": "Task title",
      "notes": "",
      "status": "active",
      "priority": "medium",
      "due_date": null,
      "project": "Inbox",
      "created_at": "2026-02-09T10:00:00Z",
      "updated_at": "2026-02-09T10:00:00Z"
    }
  ]
}
```

**projects.json:**
```json
{
  "projects": [
    {
      "name": "Project name",
      "created_at": "2026-02-09T10:00:00Z"
    }
  ]
}
```

**settings.json:**
```json
{
  "value": {
    "theme": "light",
    "sort_order": "created"
  }
}
```

---

## Contributing

### Development Workflow

1. **Fork the repository**

2. **Create a feature branch:**

```bash
git checkout -b feature/your-feature
```

3. **Make your changes**

4. **Run tests:**

```bash
# Backend
cd backend
pytest

# Frontend
cd frontend
npm test
```

5. **Run linters:**

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

6. **Commit your changes:**

```bash
git commit -m "Add your feature description"
```

7. **Push to your branch:**

```bash
git push origin feature/your-feature
```

8. **Open a Pull Request**

### Code Style

- **Backend:** Follow PEP 8 guidelines, use type hints
- **Frontend:** Follow ESLint rules, use TypeScript strict mode

### Testing

**Backend Tests:**
```bash
cd backend
pytest tests/
```

**Frontend Tests:**
```bash
cd frontend
npm test
```

---

## Troubleshooting

### Common Issues

**1. Port already in use**

If port 8000 is already in use:

```bash
# Change the port in .env
PORT=8001

# Or kill the process using the port
lsof -i :8000
kill -9 <PID>
```

**2. Data persistence issues**

If data is not persisting:

```bash
# Check that the volume is mounted correctly
docker inspect taskmgr-backend

# Ensure the data directory exists and is writable
ls -la /path/to/data
```

**3. Frontend can't connect to backend**

Verify the API_URL environment variable:

```bash
# Check frontend environment
docker exec taskmgr-frontend printenv | grep API_URL

# Ensure backend is running
docker ps | grep taskmgr-backend
```

**4. JSON file corruption**

The application has automatic repair built-in. If files are corrupted:

```bash
# Stop the containers
docker compose down

# Remove data (backup first if needed)
docker volume rm taskmgr-data

# Restart
docker compose up
```

---

## License

This project is provided as-is for educational and testing purposes.

---

## Acknowledgments

- Built with FastAPI for the backend
- Built with React and TypeScript for the frontend
- Uses Docker for containerization

---

*For API documentation, see [docs/API.md](docs/API.md)*
