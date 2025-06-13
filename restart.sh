#!/bin/bash
# Restart KPATH Enterprise - Backend API and Frontend

echo "🔄 Restarting KPATH Enterprise..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Get the directory where the script is located
SCRIPT_DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$SCRIPT_DIR"

# Function to kill processes on a specific port
kill_port() {
    local port=$1
    echo -e "${YELLOW}Checking for processes on port $port...${NC}"
    
    # Find PIDs using the port
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        pids=$(lsof -ti:$port 2>/dev/null)
    else
        # Linux
        pids=$(lsof -ti:$port 2>/dev/null)
    fi
    
    if [ ! -z "$pids" ]; then
        echo -e "${YELLOW}Found processes on port $port: $pids${NC}"
        for pid in $pids; do
            echo "Killing process $pid..."
            kill -9 $pid 2>/dev/null
            if [ $? -eq 0 ]; then
                echo -e "${GREEN}✅ Process $pid killed${NC}"
            else
                echo -e "${RED}⚠️  Could not kill process $pid (may require sudo)${NC}"
            fi
        done
        # Give it a moment to release the port
        sleep 2
    else
        echo "No processes found on port $port"
    fi
}

# Kill existing processes
echo -e "\n${BLUE}🛑 Stopping existing services...${NC}"

# Kill backend processes
echo -e "\n${YELLOW}Stopping backend processes...${NC}"
pkill -f "uvicorn backend.main:app" 2>/dev/null
pkill -f "python -m uvicorn" 2>/dev/null
kill_port 8000
kill_port 8001
kill_port 8080

# Kill frontend processes
echo -e "\n${YELLOW}Stopping frontend processes...${NC}"
pkill -f "vite" 2>/dev/null
pkill -f "npm run dev" 2>/dev/null
kill_port 5173
kill_port 5174

echo -e "${GREEN}✅ All processes stopped${NC}"

# Check if we should run in development or production mode
MODE=${1:-dev}

# Function to start backend
start_backend() {
    echo -e "\n${BLUE}🚀 Starting Backend API Server...${NC}"
    
    # Check for virtual environment
    if command -v pyenv &> /dev/null; then
        echo "Using pyenv environment: torch-env"
        eval "$(pyenv init -)"
        pyenv activate torch-env
    elif [ -d "venv" ]; then
        echo "Using local venv"
        source venv/bin/activate
    else
        echo -e "${RED}⚠️  Warning: No virtual environment found${NC}"
    fi
    
    # Check PostgreSQL connection
    echo "Checking database connection..."
    python -c "
import psycopg2
import os
from dotenv import load_dotenv
load_dotenv()
try:
    conn = psycopg2.connect(os.getenv('DATABASE_URL', 'postgresql://localhost/kpath_enterprise'))
    conn.close()
    print('✅ Database connection successful')
except Exception as e:
    print('❌ Database connection failed:', e)
    exit(1)
" || { echo -e "${RED}Please ensure PostgreSQL is running${NC}"; exit 1; }
    
    # Start backend
    cd backend
    export PYTHONPATH="$SCRIPT_DIR:$PYTHONPATH"
    if [ "$MODE" == "dev" ]; then
        python -m uvicorn main:app \
            --reload \
            --host 0.0.0.0 \
            --port 8000 \
            --log-level info \
            --reload-dir . \
            --reload-include "*.py" &
    else
        python -m uvicorn main:app \
            --host 0.0.0.0 \
            --port 8000 \
            --workers 4 \
            --log-level info &
    fi
    
    BACKEND_PID=$!
    cd ..
    
    # Wait for backend to start
    echo -n "Waiting for backend to start"
    for i in {1..30}; do
        if curl -s http://localhost:8000/health > /dev/null; then
            echo -e "\n${GREEN}✅ Backend started successfully${NC}"
            break
        fi
        echo -n "."
        sleep 1
    done
}

# Function to start frontend
start_frontend() {
    echo -e "\n${BLUE}🚀 Starting Frontend Development Server...${NC}"
    
    cd frontend-new
    
    # Check if node_modules exists
    if [ ! -d "node_modules" ]; then
        echo "Installing frontend dependencies..."
        npm install
    fi
    
    # Create .env if it doesn't exist
    if [ ! -f ".env" ]; then
        echo "Creating .env file..."
        echo "PUBLIC_API_URL=http://localhost:8000" > .env
    fi
    
    # Start frontend
    if [ "$MODE" == "dev" ]; then
        npm run dev &
    else
        npm run build && npm run preview &
    fi
    
    FRONTEND_PID=$!
    cd ..
    
    # Wait for frontend to start
    echo -n "Waiting for frontend to start"
    for i in {1..30}; do
        if curl -s http://localhost:5173 > /dev/null 2>&1; then
            echo -e "\n${GREEN}✅ Frontend started successfully${NC}"
            break
        fi
        echo -n "."
        sleep 1
    done
}

# Check for Redis (optional for caching phase)
check_redis() {
    if command -v docker &> /dev/null; then
        echo -e "\n${YELLOW}Checking Redis container...${NC}"
        if [ $(docker ps -q -f name=redis) ]; then
            echo -e "${GREEN}✅ Redis is running${NC}"
        else
            echo "Redis not running (optional for current phase)"
            # Uncomment when implementing caching phase:
            # docker-compose up -d redis
        fi
    fi
}

# Main execution
echo -e "\n${BLUE}Starting services in $MODE mode...${NC}"

# Start services in background
start_backend
start_frontend
check_redis

# Display access information
echo -e "\n${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}✅ KPATH Enterprise is running!${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo ""
echo -e "${BLUE}Frontend:${NC}     http://localhost:5173"
echo -e "${BLUE}Backend API:${NC}  http://localhost:8000"
echo -e "${BLUE}API Docs:${NC}     http://localhost:8000/docs"
echo -e "${BLUE}ReDoc:${NC}        http://localhost:8000/redoc"
echo -e "${BLUE}Health:${NC}       http://localhost:8000/api/v1/health"
echo ""
echo -e "${YELLOW}Press Ctrl+C to stop all services${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"

# Function to handle shutdown
shutdown() {
    echo -e "\n${YELLOW}Shutting down services...${NC}"
    
    # Kill backend
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null
    fi
    
    # Kill frontend
    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null
    fi
    
    # Clean up any remaining processes
    pkill -f "uvicorn" 2>/dev/null
    pkill -f "vite" 2>/dev/null
    
    echo -e "${GREEN}✅ All services stopped${NC}"
    exit 0
}

# Set up signal handler
trap shutdown SIGINT SIGTERM

# Keep script running and show logs
wait
