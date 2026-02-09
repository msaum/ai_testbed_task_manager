# Docker Setup Guide

This guide provides detailed instructions for setting up and running Local Task Manager using Docker.

---

## Table of Contents

- [Prerequisites](#prerequisites)
- [Quick Start](#quick-start)
- [Docker Compose Configuration](#docker-compose-configuration)
- [Dockerfile Details](#dockerfile-details)
- [Data Persistence](#data-persistence)
- [Development vs Production](#development-vs-production)
- [Troubleshooting](#troubleshooting)

---

## Prerequisites

- Docker version 20.10 or later
- Docker Compose version 2.0 or later

Check your versions:

```bash
docker --version
docker compose version
```

---

## Quick Start

### Option 1: Using docker-compose.yml

1. **Create a `docker-compose.yml` file:**

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

2. **Build and start:**

```bash
docker compose up --build
```

3. **Access the application:**

- Frontend: http://localhost:5173
- Backend API: http://localhost:8000
- API Docs: http://localhost:8000/docs

---

## Docker Compose Configuration

### Backend Service

```yaml
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
    - APP_NAME="Local Task Manager"
    - APP_VERSION="1.0.0"
```

**Configuration Details:**

| Setting | Description |
|---------|-------------|
| `build: ./backend` | Build from the backend directory |
| `container_name` | Custom container name |
| `ports` | Map host port 8000 to container port 8000 |
| `volumes` | Mount named volume for data persistence |
| `restart: unless-stopped` | Restart unless explicitly stopped |
| `environment` | Application configuration |

### Frontend Service

```yaml
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
```

**Configuration Details:**

| Setting | Description |
|---------|-------------|
| `build: ./frontend` | Build from the frontend directory |
| `ports` | Map host port 5173 to container port 80 (nginx) |
| `environment` | Backend API URL for frontend |
| `depends_on` | Start backend before frontend |
| `restart: unless-stopped` | Restart unless explicitly stopped |

---

## Dockerfile Details

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

**Layer Breakdown:**

1. **Base Image:** `python:3.11-slim` - Minimal Python 3.11 image
2. **Working Directory:** Set to `/app`
3. **Dependencies:** Copy and install from requirements.txt
4. **Data Directory:** Create `/data` for persistence
5. **Application Code:** Copy the app directory
6. **Port:** Expose port 8000
7. **CMD:** Run uvicorn server

### Frontend Dockerfile

```dockerfile
# Build stage
FROM node:18-alpine AS builder

WORKDIR /app

COPY package*.json ./
RUN npm install
COPY . .
RUN npm run build

# Production stage
FROM nginx:alpine

COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/conf.d/default.conf

EXPOSE 80
CMD ["nginx", "-g", "daemon off;"]
```

**Build Stages:**

1. **Builder Stage:**
   - Install Node.js dependencies
   - Build the React application
   - Output to `/app/dist`

2. **Production Stage:**
   - Use lightweight nginx image
   - Copy built assets
   - Configure nginx
   - Serve static files

---

## Data Persistence

### Named Volumes

```yaml
volumes:
  taskmgr-data:
```

This creates a Docker-managed volume that persists across container restarts.

### Data Files

The `/data` directory in the backend container contains:

| File | Purpose |
|------|---------|
| `tasks.json` | All tasks |
| `projects.json` | All projects |
| `settings.json` | Application settings |

### Backup and Restore

**Backup:**

```bash
docker run --rm -v taskmgr-data:/data -v $(pwd):/backup \
  alpine tar czf /backup/data-backup.tar.gz /data
```

**Restore:**

```bash
# Stop containers
docker compose down

# Restore backup
docker run --rm -v taskmgr-data:/data -v $(pwd):/backup \
  alpine tar xzf /backup/data-backup.tar.gz -C /

# Start containers
docker compose up
```

---

## Development vs Production

### Development Mode

Use the `--reload` flag for automatic restarts:

```bash
docker compose up --build

# Or run backend manually with reload
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000", "--reload"]
```

### Production Mode

1. **Set DEBUG=false:**

```yaml
environment:
  - DEBUG=false
```

2. **Use gunicorn instead of uvicorn (optional):**

```dockerfile
RUN pip install gunicorn
CMD ["gunicorn", "app.main:app", "--bind", "0.0.0.0:8000", "--workers", "4"]
```

3. **Enable HTTPS (requires nginx configuration)**

---

## Troubleshooting

### Port Already in Use

**Error:** `Error starting userland proxy: listen tcp4 0.0.0.0:8000: bind: address already in use`

**Solution:**

```bash
# Check what's using the port
lsof -i :8000

# Kill the process or change the port
# In docker-compose.yml, change:
# - "8000:8000" to "- "8001:8000"
```

### Container Won't Start

**Check logs:**

```bash
docker compose logs backend
docker compose logs frontend

# Or for a specific container
docker logs taskmgr-backend
```

### Frontend Can't Connect to Backend

**Check environment variable:**

```bash
docker exec taskmgr-frontend printenv | grep API_URL
```

**Verify backend is running:**

```bash
docker ps | grep taskmgr-backend

# Test backend connectivity from frontend
docker exec taskmgr-frontend wget -qO- http://localhost:8000/api/v1/tasks
```

### Data Not Persisting

**Check volume:**

```bash
docker volume ls
docker volume inspect taskmgr-data

# Check data directory
docker exec taskmgr-backend ls -la /data
```

### JSON File Corruption

The application has auto-repair built-in. If files are corrupted:

```bash
# Stop containers
docker compose down

# Remove data volume
docker volume rm taskmgr-data

# Restart
docker compose up
```

### Build Failures

**Clear Docker cache:**

```bash
docker compose down
docker builder prune
docker compose up --build
```

---

## Performance Tuning

### Volume Mounting for Development

For development, mount the code directly:

```yaml
backend:
  volumes:
    - ./backend/app:/app/app
    - ./backend/data:/data
    - type: tmpfs
      target: /tmp
```

### Resource Limits

```yaml
backend:
  deploy:
    resources:
      limits:
        cpus: '1'
        memory: 512M
      reservations:
        cpus: '0.5'
        memory: 256M
```

---

## Multi-stage Builds

### Optimized Backend Dockerfile

```dockerfile
FROM python:3.11-slim AS builder

WORKDIR /build

COPY requirements.txt .
RUN pip install --user -r requirements.txt

FROM python:3.11-slim

WORKDIR /app

COPY --from=builder /root/.local /root/.local
ENV PATH=/root/.local/bin:$PATH

RUN mkdir -p /data
COPY app ./app

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## Security Considerations

1. **Don't expose ports to host** in production
2. **Use environment variables** for secrets
3. **Enable HTTPS** via reverse proxy
4. **Run as non-root** user (requires code changes)
5. **Scan images** for vulnerabilities

---

## AWS/ECS Deployment

For AWS ECS deployment, use the following task definition:

```json
{
  "containerDefinitions": [
    {
      "name": "taskmgr-backend",
      "image": "your-registry/taskmgr-backend:latest",
      "cpu": 256,
      "memory": 512,
      "portMappings": [
        {
          "containerPort": 8000,
          "hostPort": 8000
        }
      ],
      "environment": [
        {
          "name": "DEBUG",
          "value": "false"
        }
      ],
      "essential": true
    }
  ]
}
```

---

*End of Docker Setup Guide*
