#!/bin/bash
# Check status of KPATH Enterprise services

echo "📊 KPATH Enterprise Status"
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[0;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Function to check if a port is in use
check_port() {
    local port=$1
    local service=$2
    
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        pids=$(lsof -ti:$port 2>/dev/null)
    else
        # Linux
        pids=$(lsof -ti:$port 2>/dev/null)
    fi
    
    if [ ! -z "$pids" ]; then
        echo -e "${GREEN}✅ $service is running${NC} (port $port, PID: $pids)"
        return 0
    else
        echo -e "${RED}❌ $service is not running${NC} (port $port)"
        return 1
    fi
}

# Function to check service health
check_health() {
    local url=$1
    local service=$2
    
    if curl -s -f "$url" > /dev/null 2>&1; then
        echo -e "${GREEN}   ✓ $service endpoint is responding${NC}"
        return 0
    else
        echo -e "${RED}   ✗ $service endpoint is not responding${NC}"
        return 1
    fi
}

# Check Backend
echo -e "\n${BLUE}Backend API Server:${NC}"
if check_port 8000 "Backend"; then
    check_health "http://localhost:8000/health" "Health"
    check_health "http://localhost:8000/docs" "API Docs"
fi

# Check Frontend
echo -e "\n${BLUE}Frontend Development Server:${NC}"
if check_port 5173 "Frontend"; then
    check_health "http://localhost:5173" "Web UI"
fi

# Check Database
echo -e "\n${BLUE}PostgreSQL Database:${NC}"
# Try using the backend's database connection check
HEALTH_DATA=$(curl -s "http://localhost:8000/health" 2>/dev/null)
if [ ! -z "$HEALTH_DATA" ]; then
    DB_STATUS=$(echo "$HEALTH_DATA" | python3 -c "
import json, sys
try:
    data = json.load(sys.stdin)
    if data.get('components', {}).get('database') == 'healthy':
        print('healthy')
    else:
        print('unhealthy')
except:
    print('error')
" 2>/dev/null)
    
    if [[ "$DB_STATUS" == "healthy" ]]; then
        echo -e "${GREEN}✅ Database is accessible${NC}"
        # Get database info from .env for display
        if [ -f .env ]; then
            export $(grep DATABASE_URL .env | xargs)
            # Simple parse for display
            if [[ $DATABASE_URL =~ /([^/]+)$ ]]; then
                DB_NAME="${BASH_REMATCH[1]}"
                echo -e "${GREEN}   ✓ Connected to: $DB_NAME${NC}"
            fi
        fi
        # Try to get stats from the API
        AUTH_TOKEN=$(curl -s -X POST "http://localhost:8000/api/v1/auth/login" \
            -H "Content-Type: application/x-www-form-urlencoded" \
            -d "username=admin@kpath.ai&password=1234rt4rd" 2>/dev/null | \
            python3 -c "import json,sys; print(json.load(sys.stdin).get('access_token',''))" 2>/dev/null)
        
        if [ ! -z "$AUTH_TOKEN" ]; then
            # Get service count
            SERVICE_COUNT=$(curl -s "http://localhost:8000/api/v1/services" \
                -H "Authorization: Bearer $AUTH_TOKEN" 2>/dev/null | \
                python3 -c "import json,sys; d=json.load(sys.stdin); print(len(d) if isinstance(d,list) else d.get('total',0))" 2>/dev/null || echo "?")
            # Get user count if we're admin
            USER_COUNT=$(curl -s "http://localhost:8000/api/v1/users" \
                -H "Authorization: Bearer $AUTH_TOKEN" 2>/dev/null | \
                python3 -c "import json,sys; d=json.load(sys.stdin); print(len(d) if isinstance(d,list) else '?')" 2>/dev/null || echo "?")
            
            if [ "$SERVICE_COUNT" != "?" ] || [ "$USER_COUNT" != "?" ]; then
                echo -e "${GREEN}   ✓ Services: ${SERVICE_COUNT:-?}, Users: ${USER_COUNT:-?}${NC}"
            fi
        fi
    else
        echo -e "${YELLOW}⚠️  Database connection issue${NC} (status: $DB_STATUS)"
    fi
else
    # Backend not responding
    echo -e "${YELLOW}⚠️  Cannot verify database${NC} (backend API not responding)"
fi

# Check Redis (optional)
echo -e "\n${BLUE}Redis Cache (optional):${NC}"
if command -v docker &> /dev/null; then
    if [ $(docker ps -q -f name=redis 2>/dev/null) ]; then
        echo -e "${GREEN}✅ Redis container is running${NC}"
    else
        echo -e "${YELLOW}ℹ️  Redis is not running${NC} (not required for current phase)"
    fi
else
    echo -e "${YELLOW}ℹ️  Docker not installed${NC}"
fi

# Quick links
echo -e "\n${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
echo -e "${BLUE}Quick Links:${NC}"
echo "• Frontend:    http://localhost:5173"
echo "• Backend API: http://localhost:8000"
echo "• API Docs:    http://localhost:8000/docs"
echo "• Health:      http://localhost:8000/api/v1/health"
echo -e "${GREEN}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━${NC}"
