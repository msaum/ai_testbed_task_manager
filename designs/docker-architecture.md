# Docker Architecture Design Document

**Document Version:** 1.0
**Date:** 2026-02-09
**Project:** Local Task Manager

---

## 1. Overview

This document describes the Docker containerization strategy for the Local Task Manager application.

**Key Principles:**
- Single-user, offline-capable application
- State persistence via Docker volumes
- Clean separation between frontend and backend
- Simple development and production workflows

---

## 2. Architecture Diagram

```
┌─────────────────────────────────────────────────────────────────┐
│                         Docker Host                             │
│                                                                 │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │                   Docker Network (bridge)               │   │
│  │                                                         │   │
│  │  ┌─────────────────┐       ┌─────────────────────┐      │   │
│  │  │  Frontend       │       │  Backend            │      │   │
│  │  │  Container      │───────│  Container          │      │   │
│  │  │                 │ HTTP  │                     │      │   │
│  │  │  - React App    │ API   │  - FastAPI          │      │   │
│  │  │  - Nginx        │ ────> │  - /api/v1/*        │      │   │
│  │  │  - Port 80      │       │  - Data Service     │      │   │
│  │  └─────────────────┘       └─────────────────────┘      │   │
│  │         │                           │                   │   │
│  └─────────┼───────────────────────────┼───────────────────┘   │
│            │                           │                       │
│  ┌─────────▼───────────────────────────▼───────────────────┐   │
│  │                    Docker Volume                        │   │
│  │                  (taskmgr-data)                         │   │
│  │                                                         │   │
│  │  /data/                                                 │   │
│  │  ├── tasks.json          (Task data)                    │   │
│  │  ├── projects.json       (Project data)                 │   │
│  │  ├── settings.json       (UI settings)                  │   │
│  │  ├── tasks.json.bak      (Backup)                       │   │
│  │  └── ...                                                │   │
│  └─────────────────────────────────────────────────────────┘   │
│                                                                 │
└─────────────────────────────────────────────────────────────────┘

┌─────────────────────────────────────────────────────────────────┐
│                         Browser                                 │
│                                                                 │
│  http://localhost:5173                                          │
│     ↓ (HTML/CSS/JS from frontend container)                    │
│  http://localhost:8000/api/v1/*                                │
│     ↓ (JSON API from backend container)                        │
└─────────────────────────────────────────────────────────────────┘
```

---

## 3. Container Specifications

### 3.1 Frontend Container

| Property | Value |
|----------|-------|
| Base Image | nginx:alpine |
| Application Port | 80 |
| Mapped Port (host) | 5173 |
| Static Assets | /usr/share/nginx/html |
| Configuration | /etc/nginx/conf.d/default.conf |
| Build Context | ./frontend |
| Build File | Dockerfile |

#### Environment Variables

| Variable | Description | Required | Default |
|----------|-------------|----------|---------|
| API_URL | Backend API endpoint | Yes | http://backend:8000/api |

#### Dockerfile

```dockerfile
# frontend/Dockerfile
FROM node:20-alpine AS builder

WORKDIR /app

# Install dependencies
COPY package*.json ./
RUN npm ci --only=production && npm cache clean --force

# Copy source
COPY . .

# Build for production
RUN npm run build

# Production stage
FROM nginx:alpine

# Copy built assets
COPY --from=builder /app/dist /usr/share/nginx/html

# Copy nginx configuration
COPY nginx.conf /etc/nginx/conf.d/default.conf

# Expose port
EXPOSE 80

# Health check
HEALTHCHECK --interval=30s --timeout=3s --start-period=5s --retries=3 \
    CMD wget --no-verbose --tries=1 --spider http://localhost:80/ || exit 1

# Run nginx
CMD ["nginx", "-g", "daemon off;"]
```

#### Nginx Configuration

```nginx
# frontend/nginx.conf
server {
    listen 80;
    server_name localhost;
    root /usr/share/nginx/html;
    index index.html;

    # Gzip compression
    gzip on;
    gzip_types text/plain text/css application/json application/javascript text/xml application/xml;

    # Cache static assets
    location ~* \.(js|css|png|jpg|jpeg|gif|ico|svg|woff|woff2)$ {
        expires 1y;
        add_header Cache-Control "public, immutable";
    }

    # Handle SPA routing
    location / {
        try_files $uri $uri/ /index.html;
    }

    # API proxy (for dev mode)
    location /api/ {
        proxy_pass $API_URL;
        proxy_http_version 1.1;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
```

### 3.2 Backend Container

| Property | Value |
|----------|-------|
| Base Image | python:3.11-slim |
| Application Port | 8000 |
| Mapped Port (host) | 8000 |
| Application Directory | /app |
| Data Directory | /data |
| User | root (for file operations) |
| Build Context | ./backend |
| Build File | Dockerfile |

#### Dockerfile

```dockerfile
# backend/Dockerfile
FROM python:3.11-slim

# Set environment variables
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Create working directory
WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Create data directory
RUN mkdir -p /data && chmod 777 /data

# Copy application code
COPY app ./app

# Expose port
EXPOSE 8000

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8000/docs || exit 1

# Run the application
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

---

## 4. Docker Compose Configuration

```yaml
# docker-compose.yml
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
      - PYTHONUNBUFFERED=1
      - LOG_LEVEL=INFO

  frontend:
    build: ./frontend
    container_name: taskmgr-frontend
    ports:
      - "5173:80"
    environment:
      - API_URL=http://backend:8000/api
    depends_on:
      - backend
    restart: unless-stopped

volumes:
  taskmgr-data:
    name: taskmgr-data
    driver: local
```

---

## 5. Volume Management

### 5.1 Data Directory Structure

```
/volumes/taskmgr-data/
├── tasks.json              # All tasks (primary data)
├── tasks.json.bak          # Backup of tasks.json
├── tasks.json.tmp          # Temporary file during writes
├── projects.json           # All projects
├── projects.json.bak
├── projects.json.tmp
├── settings.json           # User settings
├── settings.json.bak
└── settings.json.tmp
```

### 5.2 Volume Permissions

```bash
# Create named volume
docker volume create taskmgr-data

# Inspect volume
docker volume inspect taskmgr-data

# Remove volume (deletes all data!)
docker volume rm taskmgr-data
```

---

## 6. Development vs Production

### 6.1 Development Mode

```yaml
# docker-compose.dev.yml
version: "3.9"

services:
  backend:
    build: ./backend
    container_name: taskmgr-backend
    ports:
      - "8000:8000"
    volumes:
      - taskmgr-data:/data
      - ./backend:/app:ro  # Read-only code mount
    environment:
      - PYTHONUNBUFFERED=1
      - LOG_LEVEL=DEBUG
    command: >
      sh -c "pip install watchdog &&
             watchfiles --interval 1 'uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload' app"

  frontend:
    build: ./frontend
    container_name: taskmgr-frontend
    ports:
      - "5173:80"
    environment:
      - API_URL=http://localhost:8000/api
    volumes:
      - ./frontend:/app:ro
      - /app/node_modules
    command: >
      sh -c "npm install --save-dev @types/node &&
             npm run dev -- --host 0.0.0.0 --port 5173"
```

### 6.2 Local Development (Outside Docker)

For faster iteration during development:

```bash
# Backend development
cd backend
pip install -r requirements.txt
uvicorn app.main:app --reload

# Frontend development
cd frontend
npm install
npm run dev
```

---

## 7. Build and Deployment

### 7.1 Build Process

```bash
# Build all images
docker compose build

# Build single service
docker compose build backend
docker compose build frontend
```

### 7.2 Run Process

```bash
# Start all services
docker compose up -d

# Start with rebuild
docker compose up -d --build

# View logs
docker compose logs -f

# View logs for specific service
docker compose logs -f backend
docker compose logs -f frontend
```

### 7.3 Stop Process

```bash
# Stop all services
docker compose down

# Stop and remove volumes
docker compose down -v
```

---

## 8. Security Considerations

### 8.1 Network Security

- Containers communicate over Docker's internal network
- API_URL uses container name resolution (backend)
- No external exposure of backend port (8000 not mapped to host)

### 8.2 Data Security

- All data persisted to Docker volumes
- Volume can be backed up independently:
  ```bash
  docker run --rm -v taskmgr-data:/data -v $(pwd):/backup \
    alpine tar czf /backup/backup.tar.gz /data
  ```

### 8.3 File System Security

- Backend runs as root (required for file operations)
- Data directory is world-writable (single-user assumption)
- In production multi-user scenarios, consider:
  - Running as non-root user
  - Restricting volume permissions
  - Using named volumes with specific permissions

---

## 9. Monitoring and Health Checks

### 9.1 Health Check Endpoints

```python
# Backend health check
@app.get("/health")
async def health_check():
    """Health check endpoint."""
    return {"status": "healthy"}

# Frontend health check
# Uses Nginx health check in Dockerfile
```

### 9.2 Docker Health Status

```bash
# Check container health
docker ps
docker inspect --format='{{.State.Health.Status}}' taskmgr-backend
docker inspect --format='{{.State.Health.Status}}' taskmgr-frontend
```

---

## 10. Troubleshooting

### 10.1 Common Issues

#### Issue: Container fails to start

```bash
# Check logs
docker compose logs backend
docker compose logs frontend

# Check container status
docker ps -a
```

#### Issue: Frontend cannot reach backend

```bash
# Verify containers are on same network
docker network inspect taskmgr_default

# Test network connectivity
docker exec taskmgr-frontend ping backend
docker exec taskmgr-frontend curl http://backend:8000/docs
```

#### Issue: Data not persisting

```bash
# Verify volume exists
docker volume ls

# Inspect volume
docker volume inspect taskmgr-data

# Check data directory
docker exec taskmgr-backend ls -la /data
```

### 10.2 Debug Commands

```bash
# Execute inside container
docker exec -it taskmgr-backend sh
docker exec -it taskmgr-frontend sh

# View running processes
docker top taskmgr-backend
docker top taskmgr-frontend
```

---

## 11. Backup and Recovery

### 11.1 Manual Backup

```bash
# Create backup
docker run --rm \
  -v taskmgr-data:/data:ro \
  -v $(pwd):/backup \
  alpine tar czf /backup/backup-$(date +%Y%m%d).tar.gz /data

# Restore backup
docker stop taskmgr-backend taskmgr-frontend
docker run --rm \
  -v taskmgr-data:/data \
  -v $(pwd):/backup \
  alpine tar xzf /backup/backup-YYYYMMDD.tar.gz -C /
docker start taskmgr-backend taskmgr-frontend
```

### 11.2 Automated Backup

```bash
#!/bin/bash
# backup.sh
BACKUP_DIR="/path/to/backups"
DATE=$(date +%Y%m%d_%H%M%S)

docker run --rm \
  -v taskmgr-data:/data:ro \
  -v $BACKUP_DIR:/backup \
  alpine tar czf /backup/backup-$DATE.tar.gz /data
```

---

## 12. Summary of Design Decisions

| Decision | Choice | Rationale |
|----------|--------|-----------|
| Frontend Image | nginx:alpine | Lightweight, production-ready static file server |
| Backend Image | python:3.11-slim | Minimal Python runtime for FastAPI |
| Data Storage | Docker named volume | Persistent, managed storage |
| Network | Default bridge | Internal container communication |
| Health Checks | Built-in HTTP checks | Automated container monitoring |
| Dev Mode | External mounts | Live code reload during development |
| Port Mapping | Frontend:5173, Backend:8000 | Standard ports for local development |

---

*End of Docker Architecture Design Document*
