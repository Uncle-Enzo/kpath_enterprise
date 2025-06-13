#!/bin/bash
# Wrapper script to run Python commands with the torch-env virtual environment

PYTHON_ENV="/Users/james/.pyenv/versions/3.10.13/envs/torch-env/bin/python"

if [ ! -f "$PYTHON_ENV" ]; then
    echo "Error: torch-env not found at $PYTHON_ENV"
    echo "Please ensure you have created the environment with:"
    echo "  pyenv virtualenv 3.10.13 torch-env"
    exit 1
fi

# Run the command with all arguments
$PYTHON_ENV "$@"
