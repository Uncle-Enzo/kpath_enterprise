#!/bin/bash
# Install KPATH Enterprise dependencies in torch-env

PYTHON_ENV="/Users/james/.pyenv/versions/3.10.13/envs/torch-env/bin/python"
PIP_ENV="/Users/james/.pyenv/versions/3.10.13/envs/torch-env/bin/pip"

if [ ! -f "$PYTHON_ENV" ]; then
    echo "Error: torch-env not found"
    exit 1
fi

cd /Users/james/claude_development/kpath_enterprise

echo "Installing dependencies in torch-env..."
$PIP_ENV install -r requirements.txt

echo "Installing ML dependencies..."
$PIP_ENV install sentence-transformers faiss-cpu torch numpy scikit-learn

echo "Done!"
