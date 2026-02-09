#!/bin/bash
# Docker startup script for Local Task Manager backend
# This script initializes JSON files before starting the FastAPI server

set -e

echo "Starting Local Task Manager backend..."

# Create data directory if it doesn't exist
mkdir -p /data

# Initialize JSON files if they don't exist
echo "Initializing JSON data files..."

# Create tasks.json if it doesn't exist
if [ ! -f /data/tasks.json ]; then
    echo '{"items": []}' > /data/tasks.json
    echo "Created /data/tasks.json"
fi

# Create projects.json if it doesn't exist
if [ ! -f /data/projects.json ]; then
    echo '{"items": [{"name": "Inbox", "created_at": "'$(date -u +%Y-%m-%dT%H:%M:%SZ)'"}]}' > /data/projects.json
    echo "Created /data/projects.json"
fi

# Create settings.json if it doesn't exist
if [ ! -f /data/settings.json ]; then
    echo '{"value": {"theme": "light", "sort_order": "created"}}' > /data/settings.json
    echo "Created /data/settings.json"
fi

echo "JSON files initialized successfully."
echo "Starting FastAPI server..."

# Start the FastAPI application
exec uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
