#!/bin/bash
# Initialize Alembic migrations

echo "Initializing database migrations..."

cd /Users/james/claude_development/kpath_enterprise
source venv/bin/activate

# Create initial migration
echo "Creating initial migration..."
alembic revision --autogenerate -m "Initial migration"

echo "Migration created! To apply it, run:"
echo "alembic upgrade head"
