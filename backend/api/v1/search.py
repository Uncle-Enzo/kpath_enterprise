"""
Search API endpoints for KPATH Enterprise.

Provides semantic search capabilities via REST API.
"""

from fastapi import APIRouter, Depends, HTTPException, BackgroundTasks, Query
from sqlalchemy.orm import Session
from typing import List, Optional, Dict, Any
import logging
import time
from datetime import datetime

from backend.core.database import get_db
from backend.core.auth import (
    get_current_user, get_current_user_flexible, 
    oauth2_scheme, api_key_header
)
from backend.schemas.search import (
    SearchRequest, SearchResponse, SearchResultSchema,
    SearchStatusResponse, IndexRebuildRequest, SearchFeedbackRequest
)
from backend.models.models import User, SearchQuery as SearchQueryLog
from backend.services.search_manager import get_search_manager
from backend.services.search.search_service import SearchQuery

logger = logging.getLogger(__name__)
router = APIRouter(tags=["search"])


@router.post("/search", response_model=SearchResponse)
async def search_services(
    request: SearchRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_flexible)
):
    """
    Perform semantic search for services.
    
    This endpoint uses AI-powered semantic search to find services that match your query.
    The search understands natural language and can find conceptually similar services.
    
    ### Features:
    - **Semantic Understanding**: Finds services based on meaning, not just keywords
    - **Domain Filtering**: Optionally filter results by business domains
    - **Capability Filtering**: Optionally filter by service capabilities
    - **Relevance Scoring**: Results are ranked by semantic similarity (0-1)
    
    ### Example Queries:
    - `"customer data management"` - Find services related to customer data
    - `"send notifications"` - Find services that can send notifications
    - `"financial reporting"` - Find finance-related services
    
    ### Filtering:
    - **domains**: Case-insensitive exact match on service domains
    - **capabilities**: Partial match on capability descriptions
    
    Returns a list of services ranked by relevance score.
    """
    try:
        start_time = time.time()
        search_manager = get_search_manager()
        
        if not search_manager.is_initialized:
            raise HTTPException(
                status_code=503,
                detail="Search service not initialized"
            )
        
        # Create search query
        query = SearchQuery(
            text=request.query,
            user_id=current_user.id,
            limit=request.limit,
            min_score=request.min_score,
            domains=request.domains,
            capabilities=request.capabilities
        )
        
        # Perform search
        results = search_manager.search(query, db)
        
        # Calculate search time
        search_time_ms = int((time.time() - start_time) * 1000)
        
        # Log API key usage if applicable
        if hasattr(current_user, 'api_key_info') and current_user.api_key_info:
            try:
                from api_key_manager_fixed import APIKeyManager
                api_manager = APIKeyManager(db)
                api_manager.log_api_request(
                    api_key_id=current_user.api_key_info['key_id'],
                    endpoint="/api/v1/search/search",
                    method="POST",
                    status_code=200,
                    response_time_ms=search_time_ms
                )
            except Exception as log_error:
                logger.warning(f"Failed to log API key request: {log_error}")
        
        # Log search query for analytics
        try:
            search_log = SearchQueryLog(
                query=request.query,
                user_id=current_user.id if current_user else None,
                results_count=len(results),
                response_time_ms=search_time_ms,
                timestamp=datetime.utcnow()
            )
            db.add(search_log)
            db.commit()
        except Exception as log_error:
            logger.warning(f"Failed to log search query: {log_error}")
            # Don't fail the search if logging fails
        
        # Convert to response format
        search_results = [
            SearchResultSchema(
                service_id=result.service_id,
                score=result.score,
                rank=result.rank,
                service=result.service_data,
                distance=result.distance
            )
            for result in results
        ]
        
        # Log search for analytics
        logger.info(f"Search by user {current_user.id}: '{request.query}' -> {len(results)} results in {search_time_ms}ms")
        
        return SearchResponse(
            query=request.query,
            results=search_results,
            total_results=len(search_results),
            search_time_ms=search_time_ms,
            user_id=current_user.id
        )
        
    except Exception as e:
        # Log failed API key request
        if hasattr(current_user, 'api_key_info') and current_user.api_key_info:
            try:
                from api_key_manager_fixed import APIKeyManager
                api_manager = APIKeyManager(db)
                api_manager.log_api_request(
                    api_key_id=current_user.api_key_info['key_id'],
                    endpoint="/api/v1/search/search",
                    method="POST",
                    status_code=500,
                    response_time_ms=int((time.time() - start_time) * 1000) if 'start_time' in locals() else 0
                )
            except:
                pass
        
        logger.error(f"Search error: {e}")
        raise HTTPException(status_code=500, detail="Search failed")


@router.get("/search", response_model=SearchResponse)
async def search_services_get(
    query: str = Query(..., description="Search query"),
    limit: int = Query(10, ge=1, le=100, description="Maximum number of results"),
    min_score: float = Query(0.0, ge=0.0, le=1.0, description="Minimum relevance score"),
    domains: Optional[List[str]] = Query(None, description="Filter by domains"),
    capabilities: Optional[List[str]] = Query(None, description="Filter by capabilities"),
    api_key: Optional[str] = Query(None, description="API key for authentication (alternative to X-API-Key header)"),
    db: Session = Depends(get_db),
    token: Optional[str] = Depends(oauth2_scheme),
    header_api_key: Optional[str] = Depends(api_key_header)
):
    """
    Perform semantic search for services (GET method).
    
    This endpoint is ideal for API key authentication as it accepts query parameters.
    
    ### Authentication Options:
    - **JWT Token**: Include in Authorization header as "Bearer {token}"
    - **API Key Header**: Include in X-API-Key header
    - **API Key Parameter**: Include as query parameter ?api_key=your_key
    
    ### Example:
    ```
    GET /api/v1/search?query=customer%20data&limit=10&api_key=kpe_your_api_key_here
    ```
    """
    
    # Handle authentication manually to support query parameter API key
    current_user = None
    
    # Try header API key first
    if header_api_key:
        from api_key_manager_fixed import APIKeyManager
        api_key_manager = APIKeyManager(db)
        key_info = api_key_manager.validate_api_key(header_api_key)
        if key_info:
            current_user = db.query(User).filter(User.id == key_info['user_id']).first()
            if current_user:
                current_user.api_key_info = key_info
    
    # Try query parameter API key if header didn't work
    if not current_user and api_key:
        from api_key_manager_fixed import APIKeyManager
        api_key_manager = APIKeyManager(db)
        key_info = api_key_manager.validate_api_key(api_key)
        if key_info:
            current_user = db.query(User).filter(User.id == key_info['user_id']).first()
            if current_user:
                current_user.api_key_info = key_info
    
    # Try JWT token if no API key worked
    if not current_user and token:
        try:
            from backend.core.auth import get_current_user
            current_user = await get_current_user(token, db)
        except:
            pass
    
    # If no authentication method worked, raise error
    if not current_user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Could not validate credentials",
            headers={"WWW-Authenticate": "Bearer"},
        )
    
    # Create request object from query parameters
    request = SearchRequest(
        query=query,
        limit=limit,
        min_score=min_score,
        domains=domains,
        capabilities=capabilities
    )
    
    # Use the same logic as POST endpoint
    response = await search_services(request, db, current_user)
    
    # Log API key usage for GET requests
    if hasattr(current_user, 'api_key_info') and current_user.api_key_info:
        try:
            from api_key_manager_fixed import APIKeyManager
            api_manager = APIKeyManager(db)
            api_manager.log_api_request(
                api_key_id=current_user.api_key_info['key_id'],
                endpoint="/api/v1/search/search",
                method="GET",
                status_code=200,
                response_time_ms=response.search_time_ms
            )
        except Exception as log_error:
            logger.warning(f"Failed to log API key request: {log_error}")
    
    return response


@router.get("/search/status", response_model=SearchStatusResponse)
async def get_search_status(
    current_user: User = Depends(get_current_user)
):
    """
    Get status information about the search service.
    """
    try:
        search_manager = get_search_manager()
        status = search_manager.get_status()
        
        return SearchStatusResponse(
            initialized=status['initialized'],
            index_built=status['index_built'],
            embedding_service=status['embedding_service'],
            search_service=status['search_service'],
            files=status['files']
        )
        
    except Exception as e:
        logger.error(f"Status error: {e}")
        raise HTTPException(status_code=500, detail="Failed to get search status")


@router.post("/search/rebuild")
async def rebuild_search_index(
    request: IndexRebuildRequest,
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Rebuild the search index from database.
    
    This is a potentially long-running operation that rebuilds the entire
    search index from the current database state.
    """
    # Check admin permissions
    if current_user.role != 'admin':
        raise HTTPException(
            status_code=403,
            detail="Admin access required"
        )
    
    def rebuild_task():
        """Background task to rebuild the index."""
        try:
            search_manager = get_search_manager()
            success = search_manager.rebuild_index(db)
            
            if success:
                logger.info(f"Index rebuilt by user {current_user.id}")
            else:
                logger.error(f"Index rebuild failed for user {current_user.id}")
                
        except Exception as e:
            logger.error(f"Index rebuild error: {e}")
    
    # Start rebuild in background
    background_tasks.add_task(rebuild_task)
    
    return {
        "message": "Index rebuild started",
        "status": "processing"
    }


@router.post("/search/initialize")
async def initialize_search_service(
    background_tasks: BackgroundTasks,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Initialize the search service.
    
    Sets up the embedding model and search index if not already initialized.
    """
    # Check admin permissions
    if current_user.role != 'admin':
        raise HTTPException(
            status_code=403,
            detail="Admin access required"
        )
    
    def initialize_task():
        """Background task to initialize search."""
        try:
            # Create a new DB session for the background task
            from backend.core.database import SessionLocal
            db_task = SessionLocal()
            try:
                from backend.services.search_manager import initialize_search
                initialize_search(db_task, force_rebuild=True)  # Force rebuild for now
                logger.info(f"Search service initialized by user {current_user.id}")
            finally:
                db_task.close()
            
        except Exception as e:
            logger.error(f"Search initialization error: {e}", exc_info=True)
    
    # Start initialization in background
    background_tasks.add_task(initialize_task)
    
    return {
        "message": "Search initialization started",
        "status": "processing"
    }


@router.get("/search/similar/{service_id}")
async def find_similar_services(
    service_id: int,
    limit: int = 10,
    min_score: float = 0.0,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Find services similar to a given service.
    
    Uses the target service's description and capabilities to find similar services.
    """
    try:
        from backend.models.models import Service
        
        # Get the target service
        service = db.query(Service).filter(Service.id == service_id).first()
        if not service:
            raise HTTPException(status_code=404, detail="Service not found")
        
        # Create query from service data
        query_parts = []
        if service.name:
            query_parts.append(service.name)
        if service.description:
            query_parts.append(service.description)
        
        # Add capabilities
        for capability in service.capabilities:
            query_parts.append(capability.name)
        
        query_text = " ".join(query_parts)
        
        # Create search query
        query = SearchQuery(
            text=query_text,
            user_id=current_user.id,
            limit=limit + 1,  # +1 to exclude the original service
            min_score=min_score
        )
        
        # Perform search
        search_manager = get_search_manager()
        results = search_manager.search(query, db)
        
        # Filter out the original service
        similar_results = [r for r in results if r.service_id != service_id][:limit]
        
        # Convert to response format
        search_results = [
            SearchResultSchema(
                service_id=result.service_id,
                score=result.score,
                rank=result.rank,
                service=result.service_data,
                distance=result.distance
            )
            for result in similar_results
        ]
        
        return {
            "target_service_id": service_id,
            "similar_services": search_results,
            "total_results": len(search_results)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Similar services error: {e}")
        raise HTTPException(status_code=500, detail="Failed to find similar services")


@router.delete("/search/service/{service_id}")
async def remove_service_from_index(
    service_id: int,
    current_user: User = Depends(get_current_user)
):
    """
    Remove a service from the search index.
    
    Used when a service is deleted or deactivated.
    """
    # Check admin permissions
    if current_user.role != 'admin':
        raise HTTPException(
            status_code=403,
            detail="Admin access required"
        )
    
    try:
        search_manager = get_search_manager()
        success = search_manager.remove_service(service_id)
        
        if success:
            return {"message": f"Service {service_id} removed from search index"}
        else:
            return {"message": f"Service {service_id} not found in search index"}
            
    except Exception as e:
        logger.error(f"Remove service error: {e}")
        raise HTTPException(status_code=500, detail="Failed to remove service from index")


@router.put("/search/service/{service_id}")
async def update_service_in_index(
    service_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Update a service's representation in the search index.
    
    Used when a service's details are modified.
    """
    # Check admin permissions
    if current_user.role != 'admin':
        raise HTTPException(
            status_code=403,
            detail="Admin access required"
        )
    
    try:
        search_manager = get_search_manager()
        success = search_manager.update_service(service_id, db)
        
        if success:
            return {"message": f"Service {service_id} updated in search index"}
        else:
            raise HTTPException(status_code=404, detail="Service not found")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Update service error: {e}")
        raise HTTPException(status_code=500, detail="Failed to update service in index")


@router.post("/search/service/{service_id}")
async def add_service_to_index(
    service_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Add a service to the search index.
    
    Used when a new service is created.
    """
    # Check admin permissions
    if current_user.role != 'admin':
        raise HTTPException(
            status_code=403,
            detail="Admin access required"
        )
    
    try:
        search_manager = get_search_manager()
        success = search_manager.add_service(service_id, db)
        
        if success:
            return {"message": f"Service {service_id} added to search index"}
        else:
            raise HTTPException(status_code=404, detail="Service not found")
            
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Add service error: {e}")
        raise HTTPException(status_code=500, detail="Failed to add service to index")



@router.post("/search/feedback")
async def submit_search_feedback(
    feedback: SearchFeedbackRequest,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user_flexible)
):
    """
    Submit feedback about search results.
    
    Records when users select or interact with search results to improve
    future ranking. This feedback is used to:
    
    - Track which services are most relevant for certain queries
    - Improve search ranking over time
    - Identify popular services
    
    ### Feedback Types:
    - **click**: User clicked on the result
    - **select**: User selected/used the service
    - **relevant**: User marked as relevant
    - **not_relevant**: User marked as not relevant
    """
    try:
        from backend.models.models import FeedbackLog
        import hashlib
        
        # Create query embedding hash for grouping similar queries
        query_hash = hashlib.md5(feedback.query.lower().strip().encode()).hexdigest()
        
        # Create feedback log entry
        feedback_log = FeedbackLog(
            query=feedback.query,
            query_embedding_hash=query_hash,
            selected_service_id=feedback.service_id,
            user_id=current_user.id,
            rank_position=feedback.rank,
            click_through=(feedback.feedback_type in ['click', 'select'])
        )
        
        db.add(feedback_log)
        db.commit()
        
        logger.info(f"Feedback recorded: User {current_user.id} {feedback.feedback_type} service {feedback.service_id} for query '{feedback.query}'")
        
        return {
            "message": "Feedback recorded successfully",
            "feedback_id": feedback_log.id
        }
        
    except Exception as e:
        logger.error(f"Feedback error: {e}")
        db.rollback()
        raise HTTPException(status_code=500, detail="Failed to record feedback")


@router.get("/search/feedback/stats")
async def get_feedback_stats(
    service_id: Optional[int] = None,
    limit: int = 10,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get feedback statistics for services.
    
    Returns aggregated feedback data to understand search performance.
    """
    try:
        from backend.models.models import FeedbackLog, Service
        from sqlalchemy import func
        
        # Base query
        query = db.query(
            FeedbackLog.selected_service_id,
            Service.name,
            func.count(FeedbackLog.id).label('total_clicks'),
            func.avg(FeedbackLog.rank_position).label('avg_rank'),
            func.count(func.distinct(FeedbackLog.user_id)).label('unique_users')
        ).join(
            Service, FeedbackLog.selected_service_id == Service.id
        ).group_by(
            FeedbackLog.selected_service_id, Service.name
        )
        
        # Filter by service if specified
        if service_id:
            query = query.filter(FeedbackLog.selected_service_id == service_id)
        
        # Order by total clicks and limit
        results = query.order_by(func.count(FeedbackLog.id).desc()).limit(limit).all()
        
        # Format results
        stats = []
        for result in results:
            stats.append({
                "service_id": result.selected_service_id,
                "service_name": result.name,
                "total_clicks": result.total_clicks,
                "average_rank": round(result.avg_rank, 2) if result.avg_rank else None,
                "unique_users": result.unique_users
            })
        
        return {
            "stats": stats,
            "total_services": len(stats)
        }
        
    except Exception as e:
        logger.error(f"Feedback stats error: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve feedback stats")


@router.get("/search/feedback/queries")
async def get_popular_queries(
    limit: int = 20,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    """
    Get most popular search queries.
    
    Returns the most frequently searched queries to understand user needs.
    """
    try:
        from backend.models.models import FeedbackLog
        from sqlalchemy import func
        
        # Get popular queries
        results = db.query(
            FeedbackLog.query,
            func.count(FeedbackLog.id).label('search_count'),
            func.count(func.distinct(FeedbackLog.user_id)).label('unique_users')
        ).group_by(
            FeedbackLog.query
        ).order_by(
            func.count(FeedbackLog.id).desc()
        ).limit(limit).all()
        
        # Format results
        queries = []
        for result in results:
            queries.append({
                "query": result.query,
                "search_count": result.search_count,
                "unique_users": result.unique_users
            })
        
        return {
            "popular_queries": queries,
            "total_queries": len(queries)
        }
        
    except Exception as e:
        logger.error(f"Popular queries error: {e}")
        raise HTTPException(status_code=500, detail="Failed to retrieve popular queries")