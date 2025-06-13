"""
Health check endpoints
"""
from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.core.database import get_db, test_connection
from backend.schemas import HealthStatus

router = APIRouter(tags=["health"])


@router.get("/", response_model=HealthStatus)
async def health_check():
    """Basic health check endpoint"""
    # Test database connection
    db_healthy = test_connection()
    
    return {
        "status": "healthy" if db_healthy else "unhealthy",
        "components": {
            "api": "healthy",
            "database": "healthy" if db_healthy else "unhealthy",
            "faiss": "not_implemented",  # Will be implemented in Phase 2
            "cache": "not_implemented"    # Will be implemented in Phase 5
        },
        "version": "0.1.0"
    }


@router.get("/ready")
async def readiness_check(db: Session = Depends(get_db)):
    """Readiness check for Kubernetes"""
    try:
        # Simple query to verify database is ready
        db.execute("SELECT 1")
        return {"status": "ready"}
    except Exception as e:
        return {"status": "not_ready", "error": str(e)}


@router.get("/live")
async def liveness_check():
    """Liveness check for Kubernetes"""
    return {"status": "alive"}
