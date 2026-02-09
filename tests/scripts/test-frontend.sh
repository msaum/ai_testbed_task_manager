#!/bin/bash
# Frontend test runner script

set -e

echo "=================================="
echo "Running Frontend Tests"
echo "=================================="

# Navigate to frontend directory
cd /app/frontend

# Install dependencies if not already installed
if [ ! -d "node_modules" ]; then
    echo "Installing dependencies..."
    npm ci
fi

# Run Vitest with coverage
npm run test -- \
    --run \
    --coverage \
    --reporter=dot \
    --reporter=html \
    --reporter=junit

# Check if tests passed
if [ $? -eq 0 ]; then
    echo "Frontend tests passed!"
    exit 0
else
    echo "Frontend tests failed!"
    exit 1
fi
