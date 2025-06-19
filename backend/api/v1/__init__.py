"""
API v1 routes
"""
from fastapi import APIRouter

from backend.api.v1 import services, users, auth, health, search, api_keys, integration, agent_protocols, import_services, analytics, orchestration, agents

api_router = APIRouter()

# Include routers
api_router.include_router(auth.router, prefix="/auth", tags=["authentication"])
api_router.include_router(services.router, prefix="/services", tags=["services"])
api_router.include_router(users.router, prefix="/users", tags=["users"])
api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(search.router, prefix="/search", tags=["search"])
api_router.include_router(api_keys.router, prefix="/api-keys", tags=["api-keys"])
api_router.include_router(integration.router, tags=["integration"])
api_router.include_router(agent_protocols.router, tags=["agent-protocols"])
api_router.include_router(import_services.router, prefix="/import", tags=["import"])
api_router.include_router(analytics.router, prefix="/analytics", tags=["analytics"])
api_router.include_router(orchestration.router, prefix="/orchestration", tags=["orchestration"])
api_router.include_router(agents.agent_router, tags=["agents"])

# Import and include the enhanced Shoes Agent router
try:
    import sys
    import os
    # Add the project root to Python path
    project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), '../../..'))
    if project_root not in sys.path:
        sys.path.insert(0, project_root)
    
    from agents.shoes.api_enhanced import router as shoes_router
    api_router.include_router(shoes_router, tags=["shoes-agent"])
    print("✅ Enhanced Shoes Agent router loaded successfully")
except ImportError as e:
    print(f"⚠️  Could not load enhanced Shoes Agent router: {e}")
    # Fall back to placeholder agents router
    pass
