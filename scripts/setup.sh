#!/bin/bash
# KPATH Enterprise setup script

echo "Setting up KPATH Enterprise development environment..."

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install Poetry
echo "Installing Poetry..."
pip install --upgrade pip
pip install poetry

# Install dependencies
echo "Installing dependencies..."
poetry install

# Initialize Alembic
echo "Initializing Alembic for database migrations..."
cd backend
alembic init alembic
cd ..

# Create FAISS index directory
mkdir -p faiss_indexes

echo "Setup complete! To start developing:"
echo "1. source venv/bin/activate"
echo "2. docker-compose up -d redis"
echo "3. python backend/main.py"
