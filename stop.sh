#!/bin/bash
# Stop KPATH Enterprise - Backend API and Frontend

echo "🛑 Stopping KPATH Enterprise..."
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

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
        sleep 1
    else
        echo "No processes found on port $port"
    fi
}

# Kill backend processes
echo -e "\n${BLUE}Stopping Backend Processes...${NC}"
pkill -f "uvicorn backend.main:app" 2>/dev/null
pkill -f "python -m uvicorn" 2>/dev/null
pkill -f "uvicorn main:app" 2>/dev/null
kill_port 8000
kill_port 8001
kill_port 8080

# Kill frontend processes
echo -e "\n${BLUE}Stopping Frontend Processes...${NC}"
pkill -f "vite" 2>/dev/null
pkill -f "npm run dev" 2>/dev/null
pkill -f "node.*vite" 2>/dev/null
kill_port 5173
kill_port 5174

echo -e "\n${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${GREEN}✅ All KPATH Enterprise services stopped${NC}"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
