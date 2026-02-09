Below is a complete, reusable product specification you can hand to humans or AI coding agents.
It is intentionally precise and testable so multiple models can be evaluated against the same target.

⸻

Product Specification — Local Task Manager (Single-User, Containerized)

1. Overview

A lightweight, single-user task management web application designed for local or private network use.

The application runs entirely inside Docker containers and persists all state to JSON files on disk.
There is no authentication system, no multi-user concept, and no roles — the app represents one persistent workspace.

Primary goals:
	•	Deterministic behavior for testing AI coding systems
	•	Fully inspectable data (JSON files only)
	•	Easy reset and reproducible environment
	•	Minimal infrastructure dependencies
	•	Clear API boundary between front-end and back-end

⸻

2. Technology Requirements

Frontend

Must use a modern JS/TS framework:

Allowed:
	•	React (preferred)
	•	Vue
	•	Svelte

Required:
	•	Typescript
	•	Component-based architecture
	•	Fetch API for backend communication
	•	No external databases
	•	No server-side rendering required

Backend

Language: Python OR Lua

Recommended stacks:

Python options:
	•	FastAPI (preferred)
	•	Flask

Lua options:
	•	OpenResty
	•	Lapis

Backend responsibilities:
	•	CRUD operations
	•	File persistence
	•	Data validation
	•	API serving

Storage

All application state stored as JSON files:

/data/projects.json
/data/tasks.json
/data/settings.json

No database allowed.

⸻

3. Functional Requirements

3.1 Core Objects

Task

{
  "id": "uuid",
  "title": "string",
  "notes": "string",
  "status": "active | completed",
  "priority": "low | medium | high",
  "due_date": "ISO8601|null",
  "project": "string",
  "created_at": "ISO8601",
  "updated_at": "ISO8601"
}

Project

{
  "name": "string",
  "created_at": "ISO8601"
}

Settings

{
  "theme": "light | dark",
  "sort_order": "priority | due_date | created"
}


⸻

3.2 Features

Tasks

User can:
	•	Create task
	•	Edit task
	•	Delete task
	•	Mark complete / active
	•	Assign project
	•	Assign priority
	•	Assign due date
	•	Add notes

Views

Application must support:
	•	All Tasks
	•	Active Tasks
	•	Completed Tasks
	•	Filter by Project
	•	Sort by:
	•	Priority
	•	Due date
	•	Created date

Projects
	•	Create project
	•	Delete project
	•	Renaming allowed
	•	Deleting project does NOT delete tasks — tasks become “Inbox”

UI Preferences
	•	Light/Dark mode toggle
	•	Persisted in settings.json

⸻

4. Non-Functional Requirements

Requirement	Behavior
Single user	No accounts, no sessions
Offline capable	Works on localhost
Deterministic	Same JSON → same UI
Recoverable	Corrupt JSON auto-repair
Stateless containers	Data mounted via volume
Restart safe	App rebuild does not lose data


⸻

5. API Specification

Base URL: /api

⸻

Tasks

GET /api/tasks
Returns all tasks

POST /api/tasks
Create new task

PUT /api/tasks/{id}
Update task

DELETE /api/tasks/{id}
Delete task

POST /api/tasks/{id}/toggle
Toggle complete

⸻

Projects

GET /api/projects
List projects

POST /api/projects
Create project

DELETE /api/projects/{name}
Delete project

⸻

Settings

GET /api/settings
Read settings

PUT /api/settings
Update settings

⸻

6. File Persistence Rules
	•	Writes must be atomic
	•	Use temp file then rename
	•	Lock file during write
	•	On invalid JSON → restore last valid snapshot

Example:

tasks.json
tasks.json.bak
tasks.json.tmp


⸻

7. Frontend Behavior

Layout

Three panel layout:

Sidebar (Projects)
Main (Tasks)
Detail Drawer (Edit Task)

UX Rules
	•	Inline editing
	•	Keyboard shortcuts
	•	Optimistic updates
	•	Backend reconciliation on failure

⸻

8. Docker Architecture

Browser
   ↓
Frontend Container (Node build → static serve)
   ↓
Backend Container (API + JSON storage)
   ↓
Docker Volume (/data)


⸻

9. Dockerfile Requirements

Backend Container

Must:
	•	expose port 8000
	•	mount /data
	•	run production server
	•	auto-create missing JSON files

Frontend Container

Must:
	•	build static assets
	•	serve via nginx or dev server
	•	configurable API endpoint

⸻

10. docker-compose.yml

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
      - API_URL=http://backend:8000/api
    depends_on:
      - backend
    restart: unless-stopped

volumes:
  taskmgr-data:


⸻

11. Development Mode

Requirements:
	•	Hot reload frontend
	•	Backend auto-reload
	•	Shared mounted volume
	•	Debug logs enabled

⸻

12. Acceptance Criteria

Application is considered complete when:
	1.	Tasks persist after restart
	2.	Projects persist after restart
	3.	UI reflects file edits made manually
	4.	JSON corruption does not crash system
	5.	Docker compose up → fully working system
	6.	No authentication anywhere
	7.	Entire state exists only inside /data/*.json

⸻

13. Out of Scope
	•	Multi-user support
	•	Accounts
	•	Permissions
	•	Cloud sync
	•	Notifications
	•	Mobile native apps
	•	External databases
	•	OAuth
	•	Encryption

⸻

14. Deliverables

Required output structure:

/frontend
/backend
/docker-compose.yml
/README.md

System must run with:

docker compose up --build

And be accessible at:

http://localhost:5173


⸻

This spec is intentionally rigid so multiple implementations can be compared objectively.
