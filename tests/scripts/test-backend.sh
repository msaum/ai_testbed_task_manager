#!/bin/bash
# Backend test runner script

set -e

echo "=================================="
echo "Running Backend Tests"
echo "=================================="

# Navigate to backend directory
cd /app

# Run pytest with coverage
pytest /app/tests \
    -v \
    --cov=app \
    --cov-report=term \
    --cov-report=html:/app/test-results/coverage.html \
    --cov-report=xml:/app/test-results/coverage.xml \
    --junitxml=/app/test-results/junit.xml \
    --tb=short

# Check if tests passed
if [ $? -eq 0 ]; then
    echo "Backend tests passed!"
    exit 0
else
    echo "Backend tests failed!"
    exit 1
fi
