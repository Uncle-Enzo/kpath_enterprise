#!/bin/bash
# Start the KPATH Enterprise API server

cd /Users/james/claude_development/kpath_enterprise

# Use the torch-env Python environment
PYTHON_ENV="/Users/james/.pyenv/versions/3.10.13/envs/torch-env/bin/python"

if [ ! -f "$PYTHON_ENV" ]; then
    echo "Error: torch-env not found at $PYTHON_ENV"
    echo "Please ensure you have created the environment with:"
    echo "  pyenv virtualenv 3.10.13 torch-env"
    exit 1
fi

echo "Starting KPATH Enterprise API server with torch-env..."
echo "API docs will be available at: http://localhost:8000/docs"
echo "Press Ctrl+C to stop"

$PYTHON_ENV -m uvicorn backend.main:app --reload --host 0.0.0.0 --port 8000
