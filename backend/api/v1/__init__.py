"""
API v1 routes
"""
from fastapi import APIRouter

from backend.api.v1 import services, users, auth, health, search, api_keys, integration, agent_protocols, import_services

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
