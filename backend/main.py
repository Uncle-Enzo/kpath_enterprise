"""
KPATH Enterprise API Server
"""
import uvicorn
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from backend.core.config import get_settings
from backend.core.database import SessionLocal
from backend.api.v1 import api_router
from backend.services.search_manager import get_search_manager

settings = get_settings()
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Manage application lifecycle - startup and shutdown
    """
    # Startup
    logger.info("Starting up KPATH Enterprise API...")
    
    # Initialize search service
    try:
        logger.info("Initializing search service...")
        search_manager = get_search_manager()
        db = SessionLocal()
        try:
            search_manager.initialize(db, force_rebuild=False)
            logger.info("Search service initialized successfully")
        finally:
            db.close()
    except Exception as e:
        logger.error(f"Failed to initialize search service: {e}")
        # Continue anyway - search will return errors but other endpoints will work
    
    yield
    
    # Shutdown
    logger.info("Shutting down KPATH Enterprise API...")


# Create FastAPI app
app = FastAPI(
    title="KPATH Enterprise API",
    description="""
## KPATH Enterprise - Microservices Discovery & Orchestration Platform

KPATH Enterprise provides semantic search capabilities for discovering and connecting microservices based on their capabilities.

### Key Features:
- **Semantic Search**: Find services using natural language queries with AI-powered understanding
- **Domain Filtering**: Filter services by business domains (Finance, Communication, etc.)
- **Capability Matching**: Search for services by their specific capabilities
- **Service Registry**: Comprehensive catalog of available microservices
- **Stateless Design**: All orchestration logic comes from external systems

### Authentication:
All endpoints (except health checks) require JWT authentication. Include the token in the Authorization header:
```
Authorization: Bearer <your-jwt-token>
```

### Search Examples:
- Find customer management services: `{"query": "customer management"}`
- Filter by domain: `{"query": "invoice", "domains": ["Finance"]}`
- Filter by capability: `{"query": "email", "capabilities": ["send"]}`
""",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_tags=[
        {"name": "auth", "description": "Authentication operations"},
        {"name": "search", "description": "Semantic search operations"},
        {"name": "services", "description": "Service registry management"},
        {"name": "users", "description": "User management"},
        {"name": "health", "description": "Health and status checks"},
    ],
    lifespan=lifespan  # Add the lifespan handler
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Configure appropriately for production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include API routes
app.include_router(api_router, prefix=settings.api_prefix)


@app.get("/")
async def root():
    """Root endpoint"""
    return {
        "name": "KPATH Enterprise API",
        "version": "0.1.0",
        "status": "operational"
    }


@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "components": {
            "api": "healthy",
            "database": "healthy",  # TODO: Add actual checks
            "faiss": "healthy",     # TODO: Add actual checks
            "cache": "healthy"      # TODO: Add actual checks
        }
    }


if __name__ == "__main__":
    uvicorn.run(
        "backend.main:app",
        host=settings.api_host,
        port=settings.api_port,
        reload=settings.reload,
        log_level=settings.log_level.lower()
    )
