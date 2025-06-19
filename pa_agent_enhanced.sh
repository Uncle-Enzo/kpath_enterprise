#!/bin/bash
# Enhanced PA Agent launcher with agent-to-agent communication

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Project paths
PROJECT_ROOT="/Users/james/claude_development/kpath_enterprise"
PA_AGENT_DIR="$PROJECT_ROOT/agents/pa"
VENV_NAME="torch-env"

echo -e "${GREEN}🚀 Enhanced PA Agent Launcher${NC}"
echo "================================"

# Navigate to project root
cd "$PROJECT_ROOT" || exit 1

# Activate virtual environment
echo -e "${YELLOW}Activating virtual environment: $VENV_NAME${NC}"
if command -v pyenv &> /dev/null; then
    eval "$(pyenv init -)"
    pyenv activate "$VENV_NAME"
    if [ $? -eq 0 ]; then
        echo -e "${GREEN}✅ Virtual environment activated${NC}"
    else
        echo -e "${RED}❌ Failed to activate virtual environment${NC}"
        exit 1
    fi
else
    echo -e "${YELLOW}⚠️  pyenv not found, continuing without virtual environment${NC}"
fi

# Check if KPATH API is running
echo -e "${YELLOW}Checking KPATH API status...${NC}"
API_STATUS=$(curl -s -o /dev/null -w "%{http_code}" http://localhost:8000/api/v1/health)
if [ "$API_STATUS" = "200" ]; then
    echo -e "${GREEN}✅ KPATH API is running${NC}"
else
    echo -e "${RED}❌ KPATH API is not accessible (HTTP $API_STATUS)${NC}"
    echo -e "${YELLOW}Starting KPATH services...${NC}"
    ./restart.sh
    sleep 5
fi

# Check for OpenAI API key
if [ -z "$OPENAI_API_KEY" ]; then
    echo -e "${YELLOW}⚠️  OPENAI_API_KEY not set in environment${NC}"
    echo "You can set it with: export OPENAI_API_KEY='your-key-here'"
fi

# Launch Enhanced PA Agent
echo -e "${GREEN}Launching Enhanced PA Agent...${NC}"
echo "================================"

# Check if we have a query argument
if [ $# -eq 0 ]; then
    # Interactive mode
    echo -e "${GREEN}Starting in interactive mode...${NC}"
    python3 "$PA_AGENT_DIR/pa_agent_enhanced.py"
else
    # Single query mode
    QUERY="$*"
    echo -e "${GREEN}Processing query: \"$QUERY\"${NC}"
    python3 "$PA_AGENT_DIR/pa_agent_enhanced.py" "$QUERY"
fi
