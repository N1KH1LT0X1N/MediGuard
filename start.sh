#!/bin/bash

# MediGuard AI - Startup Script
# This script starts both the backend and frontend servers

set -e  # Exit on error

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

echo -e "${BLUE}🚀 Starting MediGuard AI Project...${NC}\n"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo -e "${YELLOW}⚠️  Virtual environment not found. Creating one...${NC}"
    python3 -m venv venv
    echo -e "${GREEN}✓ Virtual environment created${NC}\n"
fi

# Check if frontend node_modules exists
if [ ! -d "frontend/node_modules" ]; then
    echo -e "${YELLOW}⚠️  Frontend dependencies not found. Installing...${NC}"
    cd frontend
    npm install
    cd ..
    echo -e "${GREEN}✓ Frontend dependencies installed${NC}\n"
fi

# Function to cleanup on exit
cleanup() {
    echo -e "\n${YELLOW}🛑 Shutting down servers...${NC}"
    kill $BACKEND_PID $FRONTEND_PID 2>/dev/null || true
    exit
}

trap cleanup SIGINT SIGTERM

# Start backend server
echo -e "${BLUE}📦 Starting Backend Server (FastAPI)...${NC}"
source venv/bin/activate
cd backend
python main.py &
BACKEND_PID=$!
cd ..
echo -e "${GREEN}✓ Backend started (PID: $BACKEND_PID)${NC}"
echo -e "   → http://localhost:8000${NC}"
echo -e "   → API Docs: http://localhost:8000/docs${NC}\n"

# Wait a moment for backend to start
sleep 2

# Start frontend server
echo -e "${BLUE}🎨 Starting Frontend Server (Vite)...${NC}"
cd frontend
npm run dev &
FRONTEND_PID=$!
cd ..
echo -e "${GREEN}✓ Frontend started (PID: $FRONTEND_PID)${NC}"
echo -e "   → http://localhost:5173${NC}\n"

echo -e "${GREEN}✅ Both servers are running!${NC}\n"
echo -e "${YELLOW}Press Ctrl+C to stop both servers${NC}\n"

# Wait for both processes
wait $BACKEND_PID $FRONTEND_PID

