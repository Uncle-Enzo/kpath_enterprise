# KPATH Enterprise

A semantic search service for internal AI capabilities that helps AI personal assistants and agents discover which internal agents, tools, and services can fulfill natural language requests.

## Overview

KPATH Enterprise acts as a semantic discovery layer that integrates with Enterprise Service Buses (ESB) and Model Context Protocol (MCP) services. It uses FAISS for high-performance vector similarity search and provides a comprehensive admin interface for service management.

## Features

- 🔍 **Semantic Search**: Natural language queries to discover services
- 🚀 **High Performance**: FAISS-based vector search with caching
- 🔐 **Enterprise Security**: RBAC/ABAC policies with JWT authentication
- 📊 **Admin Dashboard**: Web UI for service management and monitoring
- 🔄 **Feedback Loop**: Continuous improvement through usage tracking
- 🏗️ **Flexible Deployment**: On-premises, cloud, or hybrid

## Quick Start

### Using Management Scripts (Recommended)

```bash
# Start both backend and frontend
./restart.sh

# Check service status
./status.sh

# Stop all services
./stop.sh
```

See [SCRIPTS_README.md](SCRIPTS_README.md) for detailed script documentation.

### Prerequisites

- Python 3.10.13 (managed via pyenv)
- PostgreSQL 14+
- Docker & Docker Compose
- Node.js 18+ (for frontend)
- pyenv and pyenv-virtualenv

### Installation

1. Clone the repository:
```bash
cd /Users/james/claude_development/kpath_enterprise
```

2. Set up the Python environment:
```bash
# Install Python 3.10.13 if not already installed
pyenv install 3.10.13

# Create and activate the virtual environment
pyenv virtualenv 3.10.13 torch-env
pyenv activate torch-env
```

3. Run the setup script:
```bash
./scripts/setup.sh
```

4. Copy and configure environment variables:
```bash
cp .env.example .env
# Edit .env with your settings
```

5. Start Redis:
```bash
docker-compose up -d redis
```

6. Run database migrations:
```bash
source venv/bin/activate
cd backend
alembic upgrade head
cd ..
```

6. Seed test data (optional):
```bash
python database/seed.py
```

7. Start the API server:
```bash
./scripts/restart.sh
```

### Server Management

Use the convenient management scripts:

```bash
# Start the server
./scripts/start_server.sh

# Stop the server
./scripts/stop.sh

# Restart the server (kills existing processes)
./scripts/restart.sh

# Check server status
./scripts/status.sh

# All-in-one management
./scripts/kpath [start|stop|restart|status|logs|test|db]
```

## Project Structure

```
kpath_enterprise/
├── backend/              # Python FastAPI application
│   ├── api/             # API endpoints
│   ├── core/            # Core configuration
│   ├── models/          # SQLAlchemy models
│   ├── schemas/         # Pydantic schemas
│   ├── services/        # Business logic
│   └── utils/           # Utilities
├── frontend/            # Svelte admin interface
├── database/            # Database scripts
│   ├── migrations/      # Alembic migrations
│   └── schema.sql       # Database schema
├── tests/              # Test suites
├── config/             # Configuration files
├── scripts/            # Utility scripts
└── docs/              # Documentation
```

## API Documentation

Once the server is running, access the interactive API documentation at:
- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## Development

### Running Tests

```bash
pytest tests/
```

### Code Formatting

```bash
black backend/
isort backend/
```

### Database Management

Access pgAdmin at http://localhost:5050 (if enabled in docker-compose.yml)
- Email: admin@kpath.local
- Password: admin

## Architecture

- **Backend**: FastAPI with async support
- **Database**: PostgreSQL with SQLAlchemy ORM
- **Vector Search**: FAISS for similarity search
- **Caching**: Redis for performance
- **Frontend**: SvelteKit for admin UI
- **Authentication**: JWT tokens

## License

Proprietary - KPATH Enterprise

## Support

For questions or issues, please refer to the project documentation in the `/docs` folder.
