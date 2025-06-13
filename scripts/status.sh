#!/bin/bash
# Check status of KPATH Enterprise API server

echo "📊 KPATH Enterprise API Server Status"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Function to check if port is in use
check_port() {
    local port=$1
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        lsof -i:$port > /dev/null 2>&1
    else
        # Linux
        lsof -i:$port > /dev/null 2>&1
    fi
    return $?
}

# Check if server is running on port 8000
if check_port 8000; then
    echo "✅ Server is RUNNING on port 8000"
    echo ""
    echo "Process details:"
    if [[ "$OSTYPE" == "darwin"* ]]; then
        lsof -i:8000 | grep LISTEN
    else
        lsof -i:8000 | grep LISTEN
    fi
    
    # Try to check health endpoint
    echo ""
    echo "Health check:"
    if command -v curl &> /dev/null; then
        response=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/api/v1/health/)
        if [ "$response" = "200" ]; then
            echo "✅ API is responding (HTTP $response)"
            curl -s http://localhost:8000/api/v1/health/ | python3 -m json.tool
        else
            echo "⚠️  API returned HTTP $response"
        fi
    else
        echo "ℹ️  Install curl to check API health"
    fi
else
    echo "❌ Server is NOT RUNNING on port 8000"
fi

# Check Redis status
echo ""
echo "Redis status:"
if command -v docker &> /dev/null; then
    if [ $(docker ps -q -f name=redis) ]; then
        echo "✅ Redis container is running"
    else
        echo "❌ Redis container is not running"
        echo "   Run: docker-compose up -d redis"
    fi
else
    echo "ℹ️  Docker not found - Redis status unknown"
fi

# Check for any uvicorn processes
echo ""
echo "Uvicorn processes:"
pgrep -fl uvicorn > /dev/null 2>&1
if [ $? -eq 0 ]; then
    pgrep -fl uvicorn
else
    echo "No uvicorn processes found"
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo "Commands:"
echo "  Start:   ./scripts/start_server.sh"
echo "  Stop:    ./scripts/stop.sh"
echo "  Restart: ./scripts/restart.sh"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
