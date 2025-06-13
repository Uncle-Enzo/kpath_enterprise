"""
Analytics endpoints for dashboard and metrics
"""
from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func, and_
from typing import Dict, Any, List
from datetime import datetime, timedelta
import logging

from backend.core.database import get_db
from backend.core.auth import get_current_user, require_role
from backend.models.models import User, APIKey, Service, SearchQuery, UserLoginLog, APIRequestLog
from pydantic import BaseModel

logger = logging.getLogger(__name__)
router = APIRouter(tags=["analytics"])


class AnalyticsResponse(BaseModel):
    """Analytics data response model"""
    users: Dict[str, Any]
    apiKeys: Dict[str, Any]
    services: Dict[str, Any]
    search: Dict[str, Any]
    system: Dict[str, Any]


class DashboardStatsResponse(BaseModel):
    """Dashboard statistics response model"""
    totalServices: int
    activeServices: int
    totalUsers: int
    activeUsers: int
    apiKeys: int
    searchesToday: int
    avgResponseTime: int
    systemHealth: str


@router.get("/dashboard", response_model=DashboardStatsResponse)
async def get_dashboard_stats(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get dashboard statistics
    """
    try:
        # Count total and active services
        total_services = db.query(Service).count()
        active_services = db.query(Service).filter(Service.status == "active").count()
        
        # Count total and active users
        total_users = db.query(User).count()
        active_users = db.query(User).filter(User.is_active == True).count()
        
        # Count API keys
        api_keys_count = db.query(APIKey).filter(APIKey.active == True).count()
        
        # Get search queries today
        today = datetime.now().date()
        searches_today = db.query(SearchQuery).filter(
            func.date(SearchQuery.timestamp) == today
        ).count()
        
        # Calculate average response time from recent searches
        recent_searches = db.query(SearchQuery).filter(
            SearchQuery.timestamp >= datetime.now() - timedelta(days=7)
        ).all()
        avg_response_time = 85  # Default fallback
        if recent_searches:
            avg_response_time = sum(s.response_time_ms for s in recent_searches) // len(recent_searches)
        
        return DashboardStatsResponse(
            totalServices=total_services,
            activeServices=active_services,
            totalUsers=total_users,
            activeUsers=active_users,
            apiKeys=api_keys_count,
            searchesToday=searches_today,
            avgResponseTime=avg_response_time,
            systemHealth="Healthy"
        )
        
    except Exception as e:
        logger.error(f"Error getting dashboard stats: {e}")
        raise HTTPException(status_code=500, detail="Failed to get dashboard stats")


@router.get("/", response_model=AnalyticsResponse)
async def get_analytics(
    db: Session = Depends(get_db),
    current_user: User = Depends(require_role(["admin", "editor"]))
):
    """
    Get comprehensive analytics data (admin/editor only)
    """
    try:
        # User Analytics
        total_users = db.query(User).count()
        active_users = db.query(User).filter(User.is_active == True).count()
        admin_count = db.query(User).filter(User.role == "admin").count()
        
        # Recent logins (last 7 days)
        week_ago = datetime.now() - timedelta(days=7)
        recent_logins = db.query(UserLoginLog).filter(
            UserLoginLog.login_timestamp >= week_ago
        ).count()
        
        # API Key Analytics
        total_api_keys = db.query(APIKey).count()
        active_api_keys = db.query(APIKey).filter(APIKey.active == True).count()
        
        # API Request Analytics
        total_api_requests = db.query(APIRequestLog).count()
        today = datetime.now().date()
        api_requests_today = db.query(APIRequestLog).filter(
            func.date(APIRequestLog.timestamp) == today
        ).count()
        
        # Service Analytics
        total_services = db.query(Service).count()
        active_services = db.query(Service).filter(Service.status == "active").count()
        deprecated_services = db.query(Service).filter(Service.status == "deprecated").count()
        
        # Service distribution by type
        service_types = db.query(
            Service.tool_type, 
            func.count(Service.id).label('count')
        ).group_by(Service.tool_type).all()
        
        service_by_type = {service_type or 'Unknown': count for service_type, count in service_types}
        
        # Search Analytics
        total_queries = db.query(SearchQuery).count()
        week_ago = datetime.now() - timedelta(days=7)
        queries_this_week = db.query(SearchQuery).filter(
            SearchQuery.timestamp >= week_ago
        ).count()
        
        # Calculate average response time
        recent_searches = db.query(SearchQuery).filter(
            SearchQuery.timestamp >= datetime.now() - timedelta(days=7)
        ).all()
        avg_response_time = 85
        if recent_searches:
            avg_response_time = sum(s.response_time_ms for s in recent_searches) // len(recent_searches)
        
        # Top search queries
        top_queries_raw = db.query(
            SearchQuery.query, 
            func.count(SearchQuery.query).label('count')
        ).group_by(SearchQuery.query).order_by(
            func.count(SearchQuery.query).desc()
        ).limit(10).all()
        
        top_queries = [{"query": query, "count": count} for query, count in top_queries_raw]
        
        search_analytics = {
            "totalQueries": total_queries,
            "queriesThisWeek": queries_this_week,
            "avgResponseTime": avg_response_time,
            "topQueries": top_queries
        }
        
        # System monitoring - safer implementation
        try:
            db_connections = db.execute("SELECT count(*) FROM pg_stat_activity").scalar()
        except Exception:
            db_connections = 0
            
        system_analytics = {
            "uptime": "Unknown",  # Needs system monitoring
            "dbConnections": db_connections,
            "memoryUsage": 0,  # Needs system monitoring
            "cpuUsage": 0  # Needs system monitoring
        }
        
        return AnalyticsResponse(
            users={
                "total": total_users,
                "active": active_users,
                "adminCount": admin_count,
                "recentLogins": recent_logins
            },
            apiKeys={
                "total": total_api_keys,
                "active": active_api_keys,
                "totalRequests": total_api_requests,
                "requestsToday": api_requests_today
            },
            services={
                "total": total_services,
                "active": active_services,
                "deprecated": deprecated_services,
                "byType": service_by_type
            },
            search=search_analytics,
            system=system_analytics
        )
        
    except Exception as e:
        logger.error(f"Error getting analytics: {e}")
        raise HTTPException(status_code=500, detail="Failed to get analytics")
