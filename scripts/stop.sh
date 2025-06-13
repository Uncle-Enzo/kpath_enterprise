#!/bin/bash
# Stop KPATH Enterprise API server

echo "🛑 Stopping KPATH Enterprise API server..."

# Function to kill processes on a specific port
kill_port() {
    local port=$1
    echo "Checking for processes on port $port..."
    
    # Find PIDs using the port
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        pids=$(lsof -ti:$port)
    else
        # Linux
        pids=$(lsof -ti:$port)
    fi
    
    if [ ! -z "$pids" ]; then
        echo "Found processes on port $port: $pids"
        for pid in $pids; do
            echo "Killing process $pid..."
            kill -9 $pid 2>/dev/null
            if [ $? -eq 0 ]; then
                echo "✅ Process $pid killed"
            else
                echo "⚠️  Could not kill process $pid (may require sudo)"
            fi
        done
    else
        echo "No processes found on port $port"
    fi
}

# Kill any Python processes running uvicorn
echo "Stopping any running uvicorn processes..."
pkill -f "uvicorn backend.main:app" 2>/dev/null
if [ $? -eq 0 ]; then
    echo "✅ Uvicorn processes stopped"
fi

pkill -f "python -m uvicorn" 2>/dev/null
if [ $? -eq 0 ]; then
    echo "✅ Python uvicorn processes stopped"
fi

# Kill processes on our default port
kill_port 8000

# Also check for common alternative ports
kill_port 8001
kill_port 8080

echo ""
echo "✅ KPATH Enterprise API server stopped"
