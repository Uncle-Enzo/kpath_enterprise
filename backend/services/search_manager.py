"""
Search manager for KPATH Enterprise.

Coordinates between embedding services and search services to provide
a unified semantic search interface.
"""

import os
import logging
from typing import List, Optional, Dict, Any
from sqlalchemy.orm import Session

from .search.search_service import SearchService, SearchResult, SearchQuery
from .search.faiss_search import FAISSSearchService
from .embedding.embedding_service import EmbeddingService
from .embedding import create_best_embedder
from backend.core.config import get_settings

logger = logging.getLogger(__name__)
settings = get_settings()


class SearchManager:
    """
    Manages semantic search functionality for KPATH Enterprise.
    
    Coordinates between embedding generation and vector search to provide
    end-to-end semantic search capabilities.
    """
    
    def __init__(self, 
                 embedding_service: Optional[EmbeddingService] = None,
                 search_service: Optional[SearchService] = None):
        """
        Initialize search manager.
        
        Args:
            embedding_service: Custom embedding service (optional)
            search_service: Custom search service (optional)
        """
        # Initialize embedding service first to get actual dimension
        self.embedding_service = embedding_service or create_best_embedder(dimension=384)
        
        # Get the actual dimension from the embedding service
        # For TF-IDF, this will be determined after fitting
        dimension = getattr(self.embedding_service, 'dimension', 384)
        
        # Initialize search service with the correct dimension
        self.search_service = search_service or FAISSSearchService(dimension=dimension)
        
        # State tracking
        self.is_initialized = False
        self.index_built = False
        self.tool_index_built = False
        
        # File paths for persistence
        self.model_path = "data/models/embedding_model.pkl"
        self.index_path = "data/indexes/search_index.pkl"
        self.tool_index_path = "data/indexes/tool_search_index.pkl"
        
        # Tool index storage
        self.tool_embeddings = None
        self.tool_ids = []
        self.tool_service_map = {}  # Maps tool_id to service_id
        
        # Create directories
        os.makedirs(os.path.dirname(self.model_path), exist_ok=True)
        os.makedirs(os.path.dirname(self.index_path), exist_ok=True)
        
        # Try to load existing model and index on initialization
        if self._load_existing_model_and_index():
            self.is_initialized = True
            self.index_built = True
            logger.info("Loaded existing model and index on initialization")
    
    def initialize(self, db: Session, force_rebuild: bool = False) -> None:
        """
        Initialize the search manager and build indexes.
        
        Args:
            db: Database session
            force_rebuild: Whether to force rebuild of indexes
        """
        logger.info("Initializing search manager...")
        
        # Initialize search service
        self.search_service.initialize()
        
        # Try to load existing model and index
        if not force_rebuild:
            if self._load_existing_model_and_index():
                self.is_initialized = True
                self.index_built = True
                logger.info("Loaded existing model and index")
                return
        
        # Build new model and index
        self._build_from_database(db)
        
        # Build tool index
        self._build_tool_index(db)
        
        # Save for future use
        self._save_model_and_index()
        
        self.is_initialized = True
        self.index_built = True
        logger.info("Search manager initialized successfully")
    
    def _load_existing_model_and_index(self) -> bool:
        """
        Try to load existing model and index files.
        
        Returns:
            True if both loaded successfully, False otherwise
        """
        try:
            # Load embedding model
            if os.path.exists(self.model_path):
                if hasattr(self.embedding_service, 'load_model'):
                    self.embedding_service.load_model(self.model_path)
                    logger.info("Loaded embedding model")
                else:
                    logger.warning("Embedding service doesn't support loading")
                    return False
            else:
                logger.info("No existing embedding model found")
                return False
            
            # Load search index
            if os.path.exists(self.index_path):
                self.search_service.load_index(self.index_path)
                logger.info("Loaded search index")
            else:
                logger.info("No existing search index found")
                return False
            
            return True
            
        except Exception as e:
            logger.error(f"Failed to load existing model/index: {e}")
            return False
    
    def _build_from_database(self, db: Session) -> None:
        """
        Build embedding model and search index from database.
        
        Args:
            db: Database session
        """
        logger.info("Building model and index from database...")
        
        # Get embeddings and service IDs from database
        embeddings, service_ids = self.embedding_service.embed_services_from_db(db)
        
        if len(service_ids) == 0:
            logger.warning("No services found in database")
            return
        
        # Update search service dimension if needed
        if embeddings.shape[1] != self.search_service.dimension:
            logger.info(f"Updating search service dimension from {self.search_service.dimension} to {embeddings.shape[1]}")
            self.search_service.dimension = embeddings.shape[1]
            
            # Re-initialize search service with correct dimension
            if hasattr(self.search_service, 'faiss_available') and self.search_service.faiss_available:
                self.search_service._initialize_faiss()
            else:
                self.search_service._initialize_fallback()
        
        # Build search index
        self.search_service.build_index(embeddings, service_ids)
        
        logger.info(f"Built index with {len(service_ids)} services, dimension {embeddings.shape[1]}")
    
    def _build_tool_index(self, db: Session) -> None:
        """
        Build tool embeddings and index from database.
        
        Args:
            db: Database session
        """
        from backend.models.models import Tool, Service
        
        logger.info("Building tool index from database...")
        
        # Get all tools with their services
        tools = db.query(Tool).join(Service).filter(Service.status == 'active').all()
        
        if not tools:
            logger.warning("No tools found in database")
            return
        
        # Create tool embeddings
        tool_texts = []
        self.tool_ids = []
        self.tool_service_map = {}
        
        for tool in tools:
            # Create rich text representation for better searchability
            tool_text_parts = [
                f"Tool: {tool.tool_name}",
                f"Purpose: {tool.tool_description}",
                f"Service: {tool.service.name}"
            ]
            
            # Add input/output information
            if tool.input_schema:
                props = tool.input_schema.get('properties', {})
                if props:
                    tool_text_parts.append(f"Inputs: {', '.join(props.keys())}")
            
            if tool.output_schema:
                props = tool.output_schema.get('properties', {})
                if props:
                    tool_text_parts.append(f"Outputs: {', '.join(props.keys())}")
            
            # Add example usage if available
            if tool.example_calls:
                if isinstance(tool.example_calls, dict):
                    tool_text_parts.append(f"Examples: {', '.join(tool.example_calls.keys())}")
                elif isinstance(tool.example_calls, list):
                    tool_text_parts.append(f"Examples: {len(tool.example_calls)} available")
            
            tool_text = " ".join(tool_text_parts)
            tool_texts.append(tool_text)
            self.tool_ids.append(tool.id)
            self.tool_service_map[tool.id] = tool.service_id
        
        # Generate tool embeddings
        if tool_texts:
            self.tool_embeddings = self.embedding_service.embed_texts(tool_texts)
            logger.info(f"Built tool index with {len(self.tool_ids)} tools")
            self.tool_index_built = True
        else:
            logger.warning("No tool texts to embed")
    
    def _save_model_and_index(self) -> None:
        """Save embedding model and search index to disk."""
        try:
            # Save embedding model
            if hasattr(self.embedding_service, 'save_model'):
                self.embedding_service.save_model(self.model_path)
                logger.info("Saved embedding model")
            
            # Save search index
            self.search_service.save_index(self.index_path)
            logger.info("Saved search index")
            
        except Exception as e:
            logger.error(f"Failed to save model/index: {e}")
    
    def search(self, query: SearchQuery, db: Session) -> List[SearchResult]:
        """
        Perform semantic search based on the search mode.
        
        Args:
            query: Search query with mode
            db: Database session
            
        Returns:
            List of search results
        """
        logger.info(f"Search called with query: {query.text}, mode: {query.search_mode}")
        
        if query.search_mode == "tools_only":
            return self.search_tools(query, db)
        elif query.search_mode == "agents_and_tools":
            return self.search_agents_and_tools(query, db)
        elif query.search_mode == "workflows":
            return self.search_workflows(query, db)
        elif query.search_mode == "capabilities":
            return self.search_capabilities(query, db)
        else:  # Default to agents_only
            return self.search_agents(query, db)
    
    def search_agents(self, query: SearchQuery, db: Session) -> List[SearchResult]:
        """
        Perform traditional agent/service search (original implementation).
        
        Args:
            query: Search query
            db: Database session
            
        Returns:
            List of search results
        """
        logger.info(f"Search called with query: {query.text}")
        logger.info(f"Search manager state - initialized: {self.is_initialized}, index_built: {self.index_built}")
        
        if not self.is_initialized:
            logger.error("Search manager not initialized")
            raise RuntimeError("Search manager not initialized")
        
        if not self.index_built:
            logger.warning("No search index available")
            return []
        
        try:
            # Perform search using the search service
            results = self.search_service.semantic_search(query, db, self.embedding_service)
            logger.info(f"Search returned {len(results)} results")
            return results
        except Exception as e:
            logger.error(f"Search error in search manager: {e}", exc_info=True)
            raise

    def search_tools(self, query: SearchQuery, db: Session) -> List[SearchResult]:
        """
        Search for tools and return full connectivity information with tool recommendations.
        
        Args:
            query: Search query
            db: Database session
            
        Returns:
            List of search results with full service connectivity data and recommended tools
        """
        from backend.models.models import Tool, Service
        import numpy as np
        
        logger.info(f"Searching tools with query: {query.text}")
        
        # Check if tool index is built
        if not self.tool_index_built or self.tool_embeddings is None:
            logger.warning("Tool index not built, building now...")
            self._build_tool_index(db)
            if not self.tool_index_built:
                logger.error("Failed to build tool index")
                return []
        
        # Generate query embedding
        try:
            query_embedding = self.embedding_service.embed_query(query.text)
        except AttributeError as e:
            logger.error(f"embed_query not found, trying embed_text: {e}")
            query_embedding = self.embedding_service.embed_text(query.text)
        
        # Calculate similarities with pre-built tool embeddings
        try:
            similarities = self.embedding_service.calculate_similarities(query_embedding, self.tool_embeddings)
        except AttributeError as e:
            logger.error(f"calculate_similarities not found, computing manually: {e}")
            # Compute similarities manually
            similarities = []
            for tool_embedding in self.tool_embeddings:
                sim = self.embedding_service.similarity(query_embedding, tool_embedding)
                similarities.append(sim)
            similarities = np.array(similarities)
        
        # Sort by similarity and filter by min_score
        tool_scores = list(zip(self.tool_ids, similarities))
        tool_scores.sort(key=lambda x: x[1], reverse=True)
        
        # Get tools and their services from database
        results = []
        for idx, (tool_id, score) in enumerate(tool_scores):
            if score < query.min_score:
                continue
            if len(results) >= query.limit:
                break
            
            # Get tool with service data
            tool = db.query(Tool).filter(Tool.id == tool_id).first()
            if not tool:
                continue
                
            service = tool.service
            
            # Get full service data including connectivity information
            service_data = {
                'id': service.id,
                'name': service.name,
                'description': service.description,
                'endpoint': service.endpoint,
                'version': service.version,
                'status': service.status,
                'tool_type': service.tool_type,
                'visibility': service.visibility,
                'interaction_modes': service.interaction_modes if service.interaction_modes else [],
                'capabilities': [cap.capability_desc for cap in service.capabilities] if service.capabilities else [],
                'domains': [domain.domain for domain in service.industries] if service.industries else [],
                'tags': [],  # Tags not currently in model
                'default_timeout_ms': service.default_timeout_ms,
                'default_retry_policy': service.default_retry_policy,
                'success_criteria': service.success_criteria,
                'integration_details': self._serialize_integration_details(service.integration_details),
                'agent_protocol_details': self._serialize_agent_protocols(service.agent_protocols)
            }
            
            # Add orchestration data if the service has it
            if hasattr(service, 'agent_protocol') and service.agent_protocol:
                service_data['agent_protocol'] = service.agent_protocol
                service_data['auth_type'] = service.auth_type
                service_data['tool_recommendations'] = service.tool_recommendations
                service_data['agent_capabilities'] = service.agent_capabilities
                service_data['communication_patterns'] = service.communication_patterns
                service_data['orchestration_metadata'] = service.orchestration_metadata
            
            # Create SearchResult with full connectivity data
            result = SearchResult(
                service_id=service.id,
                score=float(score),
                rank=idx + 1,
                service_data=service_data,
                distance=1.0 - score
            )
            
            # Add recommended tool data
            setattr(result, 'entity_type', 'service_with_tool')
            setattr(result, 'recommended_tool', {
                'tool_id': tool.id,
                'tool_name': tool.tool_name,
                'tool_description': tool.tool_description,
                'input_schema': tool.input_schema,
                'output_schema': tool.output_schema,
                'example_calls': tool.example_calls,
                'recommendation_score': float(score),
                'recommendation_reason': f"Best match for '{query.text}' based on tool capabilities"
            })
            
            results.append(result)
        
        logger.info(f"Tool search returned {len(results)} results with connectivity information")
        return results

    def search_agents_and_tools(self, query: SearchQuery, db: Session) -> List[SearchResult]:
        """
        Search both agents and tools, returning mixed results.
        
        Args:
            query: Search query
            db: Database session
            
        Returns:
            List of mixed search results
        """
        logger.info(f"Searching agents and tools with query: {query.text}")
        
        # Get agent results
        agent_results = self.search_agents(query, db)
        
        # Get tool results with adjusted limit to account for agents
        tool_query = SearchQuery(
            text=query.text,
            user_id=query.user_id,
            limit=query.limit,
            min_score=query.min_score,
            search_mode="tools_only"
        )
        tool_results = self.search_tools(tool_query, db)
        
        # Merge and re-rank results by score
        all_results = agent_results + tool_results
        all_results.sort(key=lambda x: x.score, reverse=True)
        
        # Re-assign ranks and limit
        final_results = []
        for idx, result in enumerate(all_results[:query.limit]):
            result.rank = idx + 1
            final_results.append(result)
        
        logger.info(f"Mixed search returned {len(final_results)} results")
        return final_results

    def search_workflows(self, query: SearchQuery, db: Session) -> List[SearchResult]:
        """
        Search for workflows based on invocation patterns.
        
        Args:
            query: Search query
            db: Database session
            
        Returns:
            List of workflow search results
        """
        from backend.models.models import InvocationLog, Service, Tool
        from sqlalchemy import func
        
        logger.info(f"Searching workflows with query: {query.text}")
        
        # Find common invocation patterns
        # Group by initiator and target to find common workflows
        workflow_patterns = db.query(
            InvocationLog.initiator_agent_id,
            InvocationLog.target_agent_id,
            InvocationLog.tool_id,
            func.count(InvocationLog.id).label('invocation_count')
        ).filter(
            InvocationLog.success == True
        ).group_by(
            InvocationLog.initiator_agent_id,
            InvocationLog.target_agent_id,
            InvocationLog.tool_id
        ).having(
            func.count(InvocationLog.id) > 1  # At least 2 invocations
        ).all()
        
        # Create workflow descriptions
        workflows = []
        for pattern in workflow_patterns:
            initiator = db.query(Service).filter(Service.id == pattern.initiator_agent_id).first()
            target = db.query(Service).filter(Service.id == pattern.target_agent_id).first()
            tool = db.query(Tool).filter(Tool.id == pattern.tool_id).first()
            
            if initiator and target and tool:
                workflow_desc = f"{initiator.name} calls {target.name} using {tool.tool_name}"
                workflows.append({
                    'description': workflow_desc,
                    'initiator_id': initiator.id,
                    'target_id': target.id,
                    'tool_id': tool.id,
                    'count': pattern.invocation_count
                })
        
        # Generate embeddings for workflows
        if not workflows:
            return []
            
        workflow_texts = [w['description'] for w in workflows]
        query_embedding = self.embedding_service.embed_query(query.text)
        workflow_embeddings = self.embedding_service.embed_batch(workflow_texts)
        similarities = self.embedding_service.calculate_similarities(query_embedding, workflow_embeddings)
        
        # Create results
        results = []
        for idx, (workflow, score) in enumerate(sorted(zip(workflows, similarities), 
                                                      key=lambda x: x[1], reverse=True)):
            if score < query.min_score:
                continue
            if len(results) >= query.limit:
                break
            
            result = SearchResult(
                service_id=workflow['initiator_id'],  # Use initiator as primary service
                score=float(score),
                rank=idx + 1,
                service_data={
                    'id': workflow['initiator_id'],
                    'name': workflow['description'],
                    'type': 'workflow'
                },
                distance=1.0 - score
            )
            
            setattr(result, 'entity_type', 'workflow')
            setattr(result, 'workflow_data', {
                'initiator_id': workflow['initiator_id'],
                'target_id': workflow['target_id'],
                'tool_id': workflow['tool_id'],
                'invocation_count': workflow['count'],
                'description': workflow['description']
            })
            
            results.append(result)
        
        logger.info(f"Workflow search returned {len(results)} results")
        return results

    def search_capabilities(self, query: SearchQuery, db: Session) -> List[SearchResult]:
        """
        Search by capabilities across all services and tools.
        
        Args:
            query: Search query
            db: Database session
            
        Returns:
            List of capability-based search results
        """
        from backend.models.models import Service, ServiceCapability, Tool
        
        logger.info(f"Searching capabilities with query: {query.text}")
        
        # Get all capabilities with their services
        capabilities = db.query(ServiceCapability).join(Service).filter(
            Service.status == 'active'
        ).all()
        
        # Get all tools for capability matching
        tools = db.query(Tool).join(Service).filter(Service.status == 'active').all()
        
        # Create combined capability list
        capability_items = []
        
        # Add service capabilities
        for cap in capabilities:
            capability_items.append({
                'text': f"{cap.capability_name} {cap.capability_desc}",
                'type': 'service_capability',
                'service_id': cap.service_id,
                'capability': cap
            })
        
        # Add tool capabilities
        for tool in tools:
            tool_cap_text = f"{tool.tool_name} {tool.tool_description}"
            capability_items.append({
                'text': tool_cap_text,
                'type': 'tool_capability',
                'service_id': tool.service_id,
                'tool': tool
            })
        
        if not capability_items:
            return []
        
        # Generate embeddings
        cap_texts = [item['text'] for item in capability_items]
        query_embedding = self.embedding_service.embed_query(query.text)
        cap_embeddings = self.embedding_service.embed_batch(cap_texts)
        similarities = self.embedding_service.calculate_similarities(query_embedding, cap_embeddings)
        
        # Create results
        results = []
        seen_services = set()  # To avoid duplicate services
        
        for idx, (item, score) in enumerate(sorted(zip(capability_items, similarities), 
                                                  key=lambda x: x[1], reverse=True)):
            if score < query.min_score:
                continue
            if len(results) >= query.limit:
                break
            
            service_id = item['service_id']
            if service_id in seen_services:
                continue  # Skip if we already have this service
            seen_services.add(service_id)
            
            # Get service data
            service = db.query(Service).filter(Service.id == service_id).first()
            if not service:
                continue
            
            result = SearchResult(
                service_id=service_id,
                score=float(score),
                rank=len(results) + 1,
                service_data={
                    'id': service.id,
                    'name': service.name,
                    'description': service.description,
                    'status': service.status
                },
                distance=1.0 - score
            )
            
            setattr(result, 'entity_type', 'capability')
            setattr(result, 'capability_data', {
                'matched_type': item['type'],
                'matched_text': item['text']
            })
            
            results.append(result)
        
        logger.info(f"Capability search returned {len(results)} results")
        return results

    def get_status(self) -> Dict[str, Any]:
        """
        Get status information about the search manager.
        
        Returns:
            Dictionary with status information
        """
        status = {
            'initialized': self.is_initialized,
            'index_built': self.index_built,
            'embedding_service': {
                'type': type(self.embedding_service).__name__,
                'fitted': getattr(self.embedding_service, 'is_fitted', False)
            },
            'search_service': {
                'type': type(self.search_service).__name__,
                'initialized': self.search_service.is_initialized
            }
        }
        
        # Add embedding service info
        if hasattr(self.embedding_service, 'get_model_info'):
            status['embedding_service'].update(self.embedding_service.get_model_info())
        
        # Add search service info
        if self.search_service.is_initialized:
            status['search_service'].update(self.search_service.get_index_info())
        
        # Add file status
        status['files'] = {
            'model_exists': os.path.exists(self.model_path),
            'index_exists': os.path.exists(self.index_path),
            'model_path': self.model_path,
            'index_path': self.index_path
        }
        
        return status

    def add_service(self, service_id: int, db: Session) -> bool:
        """
        Add a new service to the search index.
        
        Args:
            service_id: Service ID to add
            db: Database session
            
        Returns:
            True if added successfully
        """
        if not self.is_initialized:
            raise RuntimeError("Search manager not initialized")
        
        try:
            from backend.models.models import Service
            
            # Get service from database
            service = db.query(Service).filter(Service.id == service_id).first()
            if not service:
                logger.error(f"Service {service_id} not found")
                return False
            
            # Generate embedding
            service_data = {
                'name': service.name,
                'description': service.description,
                'capabilities': [cap.capability_desc for cap in service.capabilities],
                'domains': [domain.domain for domain in service.industries],
                'tags': getattr(service, 'tags', []) or []
            }
            
            embedding = self.embedding_service.embed_service(service_data)
            
            # Add to search index
            self.search_service.add_service(service_id, embedding)
            
            # Save updated index
            self._save_model_and_index()
            
            logger.info(f"Added service {service_id} to search index")
            return True
            
        except Exception as e:
            logger.error(f"Failed to add service {service_id}: {e}")
            return False
    
    def update_service(self, service_id: int, db: Session) -> bool:
        """
        Update a service in the search index.
        
        Args:
            service_id: Service ID to update
            db: Database session
            
        Returns:
            True if updated successfully
        """
        if not self.is_initialized:
            raise RuntimeError("Search manager not initialized")
        
        try:
            from backend.models.models import Service
            
            # Get service from database
            service = db.query(Service).filter(Service.id == service_id).first()
            if not service:
                logger.error(f"Service {service_id} not found")
                return False
            
            # Generate new embedding
            service_data = {
                'name': service.name,
                'description': service.description,
                'capabilities': [cap.capability_desc for cap in service.capabilities],
                'domains': [domain.domain for domain in service.industries],
                'tags': getattr(service, 'tags', []) or []
            }
            
            embedding = self.embedding_service.embed_service(service_data)
            
            # Update search index
            success = self.search_service.update_service(service_id, embedding)
            
            if success:
                # Save updated index
                self._save_model_and_index()
                logger.info(f"Updated service {service_id} in search index")
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to update service {service_id}: {e}")
            return False
    
    def remove_service(self, service_id: int) -> bool:
        """
        Remove a service from the search index.
        
        Args:
            service_id: Service ID to remove
            
        Returns:
            True if removed successfully
        """
        if not self.is_initialized:
            raise RuntimeError("Search manager not initialized")
        
        try:
            success = self.search_service.remove_service(service_id)
            
            if success:
                # Save updated index
                self._save_model_and_index()
                logger.info(f"Removed service {service_id} from search index")
            
            return success
            
        except Exception as e:
            logger.error(f"Failed to remove service {service_id}: {e}")
            return False
    
    def rebuild_index(self, db: Session) -> bool:
        """
        Rebuild the entire search index from database.
        
        Args:
            db: Database session
            
        Returns:
            True if rebuilt successfully
        """
        try:
            logger.info("Rebuilding search index...")
            
            # Rebuild from database
            self._build_from_database(db)
            
            # Rebuild tool index
            self._build_tool_index(db)
            
            # Save new index
            self._save_model_and_index()
            
            self.index_built = True
            logger.info("Search index rebuilt successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to rebuild index: {e}")
            return False

    def _serialize_integration_details(self, integration_details):
        """
        Serialize ServiceIntegrationDetails objects to dictionaries.
        
        Args:
            integration_details: SQLAlchemy relationship or list of ServiceIntegrationDetails
            
        Returns:
            Dictionary or list of dictionaries
        """
        if not integration_details:
            return None
            
        if hasattr(integration_details, '__iter__') and not isinstance(integration_details, (str, bytes)):
            # It's a list/collection
            return [self._serialize_single_integration_detail(detail) for detail in integration_details]
        else:
            # It's a single object
            return self._serialize_single_integration_detail(integration_details)
    
    def _serialize_single_integration_detail(self, detail):
        """Serialize a single ServiceIntegrationDetails object."""
        if not detail:
            return None
            
        return {
            'id': detail.id,
            'service_id': detail.service_id,
            'access_protocol': detail.access_protocol,
            'base_endpoint': detail.base_endpoint,
            'auth_method': detail.auth_method,
            'auth_config': detail.auth_config,
            'auth_endpoint': detail.auth_endpoint,
            'rate_limit_requests': detail.rate_limit_requests,
            'rate_limit_window_seconds': detail.rate_limit_window_seconds,
            'max_concurrent_requests': detail.max_concurrent_requests,
            'circuit_breaker_config': detail.circuit_breaker_config,
            'default_headers': detail.default_headers,
            'request_content_type': detail.request_content_type,
            'response_content_type': detail.response_content_type,
            'request_transform': detail.request_transform,
            'response_transform': detail.response_transform,
            'esb_type': detail.esb_type,
            'esb_service_name': detail.esb_service_name,
            'esb_routing_key': detail.esb_routing_key,
            'esb_operation': detail.esb_operation,
            'esb_adapter_type': detail.esb_adapter_type,
            'esb_namespace': detail.esb_namespace,
            'esb_version': detail.esb_version,
            'health_check_endpoint': detail.health_check_endpoint,
            'health_check_interval_seconds': detail.health_check_interval_seconds
        }
    
    def _serialize_agent_protocols(self, agent_protocols):
        """
        Serialize ServiceAgentProtocols objects to dictionaries.
        
        Args:
            agent_protocols: SQLAlchemy relationship or list of ServiceAgentProtocols
            
        Returns:
            Dictionary or list of dictionaries
        """
        if not agent_protocols:
            return None
            
        if hasattr(agent_protocols, '__iter__') and not isinstance(agent_protocols, (str, bytes)):
            # It's a list/collection
            return [self._serialize_single_agent_protocol(protocol) for protocol in agent_protocols]
        else:
            # It's a single object
            return self._serialize_single_agent_protocol(agent_protocols)
    
    def _serialize_single_agent_protocol(self, protocol):
        """Serialize a single ServiceAgentProtocols object."""
        if not protocol:
            return None
            
        return {
            'id': protocol.id,
            'service_id': protocol.service_id,
            'message_protocol': protocol.message_protocol,
            'protocol_version': protocol.protocol_version,
            'expected_input_format': protocol.expected_input_format,
            'response_style': protocol.response_style,
            'message_examples': protocol.message_examples,
            'tool_schema': protocol.tool_schema,
            'input_validation_rules': protocol.input_validation_rules,
            'output_parsing_rules': protocol.output_parsing_rules,
            'requires_session_state': protocol.requires_session_state,
            'max_context_length': protocol.max_context_length,
            'supported_languages': protocol.supported_languages,
            'supports_streaming': protocol.supports_streaming,
            'supports_async': protocol.supports_async,
            'supports_batch': protocol.supports_batch
        }


# Global search manager instance
_search_manager: Optional[SearchManager] = None


def get_search_manager() -> SearchManager:
    """
    Get the global search manager instance.
    
    Returns:
        SearchManager instance
    """
    global _search_manager
    
    if _search_manager is None:
        _search_manager = SearchManager()
    
    return _search_manager


def initialize_search(db: Session, force_rebuild: bool = False) -> None:
    """
    Initialize the global search manager.
    
    Args:
        db: Database session
        force_rebuild: Whether to force rebuild of indexes
    """
    search_manager = get_search_manager()
    search_manager.initialize(db, force_rebuild)


# Additional service operations are now part of the SearchManager class above
