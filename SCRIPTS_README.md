# KPATH Enterprise Service Management Scripts

This directory contains scripts to manage the KPATH Enterprise application.

## Quick Start

```bash
# Start both backend and frontend
./restart.sh

# Start in production mode
./restart.sh prod

# Stop all services
./stop.sh

# Check service status
./status.sh
```

## Scripts Overview

### restart.sh
Stops any running instances and starts both the backend API and frontend development server.

- **Development mode** (default): Includes hot reloading for both services
- **Production mode**: `./restart.sh prod` - Optimized for performance

Features:
- Automatically kills processes on ports 8000 (backend) and 5173 (frontend)
- Checks database connectivity before starting
- Installs frontend dependencies if needed
- Creates .env file for frontend if missing
- Waits for services to be ready before completing
- Shows colored output for better readability

### stop.sh
Gracefully stops all KPATH Enterprise services.

- Kills backend Python/uvicorn processes
- Kills frontend Node/Vite processes
- Cleans up any lingering processes on standard ports

### status.sh
Shows the current status of all services.

- Backend API server status and health
- Frontend development server status
- PostgreSQL database connectivity
- Redis cache status (optional)
- Quick links to all services

## Service URLs

Once running, access the services at:

- **Frontend**: http://localhost:5173
- **Backend API**: http://localhost:8000
- **API Documentation**: http://localhost:8000/docs
- **Health Check**: http://localhost:8000/api/v1/health

## Troubleshooting

If services fail to start:

1. Check that PostgreSQL is running
2. Ensure Python virtual environment is activated
3. Verify Node.js is installed for frontend
4. Check that ports 8000 and 5173 are available
5. Run `./status.sh` to see which services are having issues

For permission errors:
```bash
chmod +x restart.sh stop.sh status.sh
```
