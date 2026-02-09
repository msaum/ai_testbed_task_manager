#!/bin/bash
# Comprehensive test runner script

set -e

echo "=========================================="
echo "Local Task Manager - Test Suite Runner"
echo "=========================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Track overall status
OVERALL_STATUS=0

# Function to run a test command and report status
run_tests() {
    local name=$1
    local cmd=$2
    local status_file=$3

    echo -e "${YELLOW}Running ${name}...${NC}"

    if $cmd; then
        echo -e "${GREEN}${name} passed!${NC}"
        echo "PASSED" > "${status_file}"
        return 0
    else
        echo -e "${RED}${name} failed!${NC}"
        echo "FAILED" > "${status_file}"
        return 1
    fi
}

# Check if running in Docker
if [ -f "/.dockerenv" ]; then
    echo "Running inside Docker container"
    APP_DIR="/app"
else
    echo "Running locally"
    APP_DIR="$(pwd)"
fi

echo ""

# Run backend tests
echo "----------------------------------------"
echo "Backend Tests"
echo "----------------------------------------"
cd "${APP_DIR}/backend"

if [ -f "requirements.txt" ]; then
    pip install -q -r requirements.txt 2>/dev/null || true
fi

if pytest tests/backend -v --tb=short; then
    echo -e "${GREEN}Backend tests passed!${NC}"
    BACKEND_STATUS=0
else
    echo -e "${RED}Backend tests failed!${NC}"
    BACKEND_STATUS=1
    OVERALL_STATUS=1
fi

echo ""

# Run frontend tests
echo "----------------------------------------"
echo "Frontend Tests"
echo "----------------------------------------"
cd "${APP_DIR}/frontend"

if [ ! -d "node_modules" ]; then
    echo "Installing frontend dependencies..."
    npm ci
fi

if npm run test -- --run; then
    echo -e "${GREEN}Frontend tests passed!${NC}"
    FRONTEND_STATUS=0
else
    echo -e "${RED}Frontend tests failed!${NC}"
    FRONTEND_STATUS=1
    OVERALL_STATUS=1
fi

echo ""

# Run E2E tests
echo "----------------------------------------"
echo "End-to-End Tests"
echo "----------------------------------------"

# Start backend server for E2E tests
echo "Starting backend server..."
cd "${APP_DIR}/backend"

# Check if backend is running
if [ -f "/.dockerenv" ]; then
    # Inside Docker - assume backend is already running or start it
    if command -v uvicorn &> /dev/null; then
        uvicorn app.main:app --host 0.0.0.0 --port 8000 &
        sleep 2
    fi
else
    # Locally
    if command -v uvicorn &> /dev/null; then
        uvicorn app.main:app --host 127.0.0.1 --port 8000 &
        BACKEND_PID=$!
        sleep 2
    fi
fi

# Wait for backend to be ready
echo "Waiting for backend to be ready..."
for i in {1..10}; do
    if curl -s http://localhost:8000/health > /dev/null 2>&1; then
        echo "Backend is ready!"
        break
    fi
    if [ $i -eq 10 ]; then
        echo -e "${RED}Backend not responding!${NC}"
        OVERALL_STATUS=1
    fi
    sleep 1
done

# Run E2E tests
cd "${APP_DIR}"
if pytest tests/e2e -v --tb=short; then
    echo -e "${GREEN}E2E tests passed!${NC}"
else
    echo -e "${RED}E2E tests failed!${NC}"
    OVERALL_STATUS=1
fi

# Cleanup
if [ -n "$BACKEND_PID" ]; then
    kill $BACKEND_PID 2>/dev/null || true
fi

echo ""
echo "=========================================="
echo "Test Suite Summary"
echo "=========================================="
echo ""

if [ $OVERALL_STATUS -eq 0 ]; then
    echo -e "${GREEN}All tests passed!${NC}"
    exit 0
else
    echo -e "${RED}Some tests failed!${NC}"
    exit 1
fi
