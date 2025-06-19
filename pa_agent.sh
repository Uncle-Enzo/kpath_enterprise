#!/bin/bash
# Personal Assistant Agent Launcher
# Usage: ./pa_agent.sh [query]

cd /Users/james/claude_development/kpath_enterprise

# Activate the torch-env environment
eval "$(pyenv init -)"
pyenv activate torch-env

# Check if a query was provided as argument
if [ $# -eq 0 ]; then
    # Interactive mode
    python3 agents/pa/cli.py
else
    # Single query mode - join all arguments as the query
    python3 agents/pa/cli.py -q "$*"
fi
