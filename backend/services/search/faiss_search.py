"""
FAISS-based search service for KPATH Enterprise.

This module provides high-performance vector similarity search using FAISS.
Note: FAISS installation may be required for full functionality.
"""

import numpy as np
from typing import List, Dict, Any, Optional, Tuple
import os
import pickle
import logging
from .search_service import SearchService, SearchResult, SearchQuery

logger = logging.getLogger(__name__)


class FAISSSearchService(SearchService):
    """
    FAISS-based search service implementation.
    
    Uses Facebook's FAISS library for efficient similarity search.
    Falls back to basic numpy cosine similarity if FAISS is not available.
    """
    
    def __init__(self, dimension: int = 384, use_gpu: bool = False):
        """
        Initialize FAISS search service.
        
        Args:
            dimension: Embedding vector dimension
            use_gpu: Whether to use GPU acceleration (if available)
        """
        super().__init__()
        self.dimension = dimension
        self.use_gpu = use_gpu
        self.service_ids = []
        self.embeddings = None
        self.index = None
        self.faiss_available = False
        
        # Try to import FAISS
        try:
            import faiss
            self.faiss = faiss
            self.faiss_available = True
            logger.info("FAISS library loaded successfully")
        except ImportError:
            logger.warning("FAISS not available, using fallback implementation")
            self.faiss = None
    
    def initialize(self) -> None:
        """
        Initialize the search service and create empty index.
        """
        if self.faiss_available:
            self._initialize_faiss()
        else:
            self._initialize_fallback()
        
        self.is_initialized = True
        logger.info(f"Search service initialized (FAISS: {self.faiss_available})")
    
    def _initialize_faiss(self) -> None:
        """Initialize FAISS index."""
        # Create flat L2 index for exact search
        self.index = self.faiss.IndexFlatL2(self.dimension)
        
        # Optionally move to GPU
        if self.use_gpu and self.faiss.get_num_gpus() > 0:
            res = self.faiss.StandardGpuResources()
            self.index = self.faiss.index_cpu_to_gpu(res, 0, self.index)
            logger.info("Using GPU acceleration for FAISS")
    
    def _initialize_fallback(self) -> None:
        """Initialize fallback numpy-based search."""
        self.embeddings = np.array([]).reshape(0, self.dimension)
        self.service_ids = []
    
    def build_index(self, embeddings: np.ndarray, service_ids: List[int]) -> None:
        """
        Build the search index from embeddings.
        
        Args:
            embeddings: Matrix of service embeddings (n_services x dimension)
            service_ids: List of service IDs corresponding to embeddings
        """
        if not self.is_initialized:
            self.initialize()
        
        if embeddings.shape[0] != len(service_ids):
            raise ValueError("Number of embeddings must match number of service IDs")
        
        if embeddings.shape[1] != self.dimension:
            raise ValueError(f"Embedding dimension {embeddings.shape[1]} doesn't match expected {self.dimension}")
        
        self.service_ids = service_ids.copy()
        
        if self.faiss_available:
            self._build_faiss_index(embeddings)
        else:
            self._build_fallback_index(embeddings)
        
        logger.info(f"Built search index with {len(service_ids)} services")
    
    def _build_faiss_index(self, embeddings: np.ndarray) -> None:
        """Build FAISS index from embeddings."""
        # Reset index
        self.index.reset()
        
        # Add embeddings to index
        embeddings_f32 = embeddings.astype(np.float32)
        self.index.add(embeddings_f32)
    
    def _build_fallback_index(self, embeddings: np.ndarray) -> None:
        """Build fallback numpy index."""
        self.embeddings = embeddings.astype(np.float32)
    
    def search(self, query_embedding: np.ndarray, k: int = 10) -> List[Tuple[int, float]]:
        """
        Search for similar services using query embedding.
        
        Args:
            query_embedding: Query embedding vector
            k: Number of results to return
            
        Returns:
            List of tuples (service_id, score)
        """
        if not self.is_initialized:
            raise RuntimeError("Search service not initialized")
        
        if len(self.service_ids) == 0:
            return []
        
        k = min(k, len(self.service_ids))  # Don't request more than available
        
        if self.faiss_available:
            return self._search_faiss(query_embedding, k)
        else:
            return self._search_fallback(query_embedding, k)
    
    def _search_faiss(self, query_embedding: np.ndarray, k: int) -> List[Tuple[int, float]]:
        """Search using FAISS index."""
        query = query_embedding.reshape(1, -1).astype(np.float32)
        
        # Search index
        distances, indices = self.index.search(query, k)
        
        # Convert to results
        results = []
        for i, (distance, idx) in enumerate(zip(distances[0], indices[0])):
            if idx >= 0 and idx < len(self.service_ids):  # Valid index
                service_id = self.service_ids[idx]
                # Convert L2 distance to similarity score (0-1, higher is better)
                score = 1.0 / (1.0 + distance)
                results.append((service_id, score))
        
        return results
    
    def _search_fallback(self, query_embedding: np.ndarray, k: int) -> List[Tuple[int, float]]:
        """Search using numpy cosine similarity."""
        if self.embeddings.shape[0] == 0:
            return []
        
        # Calculate cosine similarities
        query_norm = np.linalg.norm(query_embedding)
        if query_norm == 0:
            return [(self.service_ids[0], 0.0)]  # Return first service with 0 score
        
        # Normalize query
        query_normalized = query_embedding / query_norm
        
        # Normalize embeddings
        embedding_norms = np.linalg.norm(self.embeddings, axis=1)
        valid_indices = embedding_norms > 0
        
        if not np.any(valid_indices):
            return [(self.service_ids[0], 0.0)]
        
        embeddings_normalized = self.embeddings.copy()
        embeddings_normalized[valid_indices] = (
            self.embeddings[valid_indices] / embedding_norms[valid_indices, np.newaxis]
        )
        
        # Calculate cosine similarities
        similarities = np.dot(embeddings_normalized, query_normalized)
        
        # Get top k results
        top_indices = np.argsort(similarities)[::-1][:k]
        
        results = []
        for idx in top_indices:
            if valid_indices[idx]:
                service_id = self.service_ids[idx]
                score = max(0.0, similarities[idx])  # Ensure non-negative
                results.append((service_id, score))
        
        return results

    def add_service(self, service_id: int, embedding: np.ndarray) -> None:
        """
        Add a new service to the search index.
        
        Args:
            service_id: Service ID
            embedding: Service embedding vector
        """
        if not self.is_initialized:
            raise RuntimeError("Search service not initialized")
        
        if service_id in self.service_ids:
            logger.warning(f"Service {service_id} already exists, use update_service instead")
            return
        
        if self.faiss_available:
            self._add_service_faiss(service_id, embedding)
        else:
            self._add_service_fallback(service_id, embedding)
        
        logger.info(f"Added service {service_id} to search index")
    
    def _add_service_faiss(self, service_id: int, embedding: np.ndarray) -> None:
        """Add service to FAISS index."""
        embedding_f32 = embedding.reshape(1, -1).astype(np.float32)
        self.index.add(embedding_f32)
        self.service_ids.append(service_id)
    
    def _add_service_fallback(self, service_id: int, embedding: np.ndarray) -> None:
        """Add service to fallback index."""
        embedding_f32 = embedding.reshape(1, -1).astype(np.float32)
        self.embeddings = np.vstack([self.embeddings, embedding_f32])
        self.service_ids.append(service_id)
    
    def remove_service(self, service_id: int) -> bool:
        """
        Remove a service from the search index.
        
        Note: FAISS doesn't support efficient removal, so we rebuild the index.
        
        Args:
            service_id: Service ID to remove
            
        Returns:
            True if service was removed, False if not found
        """
        if service_id not in self.service_ids:
            return False
        
        idx = self.service_ids.index(service_id)
        
        # Remove from service IDs list
        self.service_ids.pop(idx)
        
        if self.faiss_available:
            self._remove_service_faiss(idx)
        else:
            self._remove_service_fallback(idx)
        
        logger.info(f"Removed service {service_id} from search index")
        return True
    
    def _remove_service_faiss(self, idx: int) -> None:
        """Remove service from FAISS index by rebuilding."""
        # FAISS doesn't support efficient removal, so we rebuild
        if hasattr(self, 'embeddings') and self.embeddings is not None:
            # If we have embeddings stored, use them
            embeddings = np.delete(self.embeddings, idx, axis=0)
            self._build_faiss_index(embeddings)
            self.embeddings = embeddings
        else:
            # We need to rebuild from database
            logger.warning("FAISS index rebuild required after removal")
    
    def _remove_service_fallback(self, idx: int) -> None:
        """Remove service from fallback index."""
        self.embeddings = np.delete(self.embeddings, idx, axis=0)
    
    def update_service(self, service_id: int, embedding: np.ndarray) -> bool:
        """
        Update a service's embedding in the search index.
        
        Args:
            service_id: Service ID
            embedding: New embedding vector
            
        Returns:
            True if service was updated, False if not found
        """
        if service_id not in self.service_ids:
            return False
        
        idx = self.service_ids.index(service_id)
        
        if self.faiss_available:
            self._update_service_faiss(idx, embedding)
        else:
            self._update_service_fallback(idx, embedding)
        
        logger.info(f"Updated service {service_id} in search index")
        return True
    
    def _update_service_faiss(self, idx: int, embedding: np.ndarray) -> None:
        """Update service in FAISS index by rebuilding."""
        # FAISS doesn't support efficient updates, so we rebuild
        if hasattr(self, 'embeddings') and self.embeddings is not None:
            self.embeddings[idx] = embedding.astype(np.float32)
            self._build_faiss_index(self.embeddings)
        else:
            logger.warning("FAISS index rebuild required after update")
    
    def _update_service_fallback(self, idx: int, embedding: np.ndarray) -> None:
        """Update service in fallback index."""
        self.embeddings[idx] = embedding.astype(np.float32)
    
    def save_index(self, filepath: str) -> None:
        """
        Save the search index to disk.
        
        Args:
            filepath: Path to save the index
        """
        if not self.is_initialized:
            raise RuntimeError("Search service not initialized")
        
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        index_data = {
            'service_ids': self.service_ids,
            'dimension': self.dimension,
            'faiss_available': self.faiss_available,
            'use_gpu': self.use_gpu
        }
        
        if self.faiss_available:
            # Save FAISS index
            faiss_filepath = filepath + '.faiss'
            self.faiss.write_index(self.index, faiss_filepath)
            index_data['faiss_filepath'] = faiss_filepath
        else:
            # Save embeddings
            index_data['embeddings'] = self.embeddings
        
        # Save metadata
        with open(filepath, 'wb') as f:
            pickle.dump(index_data, f)
        
        logger.info(f"Saved search index to {filepath}")
    
    def load_index(self, filepath: str) -> None:
        """
        Load the search index from disk.
        
        Args:
            filepath: Path to load the index from
        """
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Index file not found: {filepath}")
        
        # Load metadata
        with open(filepath, 'rb') as f:
            index_data = pickle.load(f)
        
        self.service_ids = index_data['service_ids']
        self.dimension = index_data['dimension']
        saved_faiss_available = index_data['faiss_available']
        
        if saved_faiss_available and self.faiss_available:
            # Load FAISS index
            faiss_filepath = index_data['faiss_filepath']
            if os.path.exists(faiss_filepath):
                self.index = self.faiss.read_index(faiss_filepath)
                if self.use_gpu and self.faiss.get_num_gpus() > 0:
                    res = self.faiss.StandardGpuResources()
                    self.index = self.faiss.index_cpu_to_gpu(res, 0, self.index)
            else:
                raise FileNotFoundError(f"FAISS index file not found: {faiss_filepath}")
        else:
            # Load embeddings for fallback
            self.embeddings = index_data.get('embeddings', np.array([]).reshape(0, self.dimension))
        
        self.is_initialized = True
        logger.info(f"Loaded search index from {filepath}")
    
    def get_index_info(self) -> Dict[str, Any]:
        """
        Get information about the search index.
        
        Returns:
            Dictionary with index information
        """
        info = {
            'initialized': self.is_initialized,
            'dimension': self.dimension,
            'num_services': len(self.service_ids),
            'faiss_available': self.faiss_available,
            'use_gpu': self.use_gpu
        }
        
        if self.faiss_available and self.is_initialized:
            info['index_type'] = type(self.index).__name__
            info['is_trained'] = self.index.is_trained
            info['ntotal'] = self.index.ntotal
        
        return info
    
    def _count_tools_by_type(self, tools: List[Dict[str, Any]]) -> Dict[str, int]:
        """
        Count tools by their apparent type based on tool names.
        
        Args:
            tools: List of tool dictionaries
            
        Returns:
            Dictionary with tool type counts
        """
        tool_types = {}
        
        for tool in tools:
            tool_name = tool.get('tool_name', '').lower()
            
            # Categorize based on common patterns
            if any(keyword in tool_name for keyword in ['get', 'fetch', 'retrieve', 'find', 'search', 'list']):
                tool_type = 'data_retrieval'
            elif any(keyword in tool_name for keyword in ['create', 'add', 'insert', 'post']):
                tool_type = 'data_creation'
            elif any(keyword in tool_name for keyword in ['update', 'modify', 'edit', 'patch', 'put']):
                tool_type = 'data_modification'
            elif any(keyword in tool_name for keyword in ['delete', 'remove', 'destroy']):
                tool_type = 'data_deletion'
            elif any(keyword in tool_name for keyword in ['process', 'execute', 'run', 'perform']):
                tool_type = 'processing'
            elif any(keyword in tool_name for keyword in ['validate', 'verify', 'check', 'test']):
                tool_type = 'validation'
            elif any(keyword in tool_name for keyword in ['send', 'notify', 'email', 'message']):
                tool_type = 'communication'
            else:
                tool_type = 'other'
            
            tool_types[tool_type] = tool_types.get(tool_type, 0) + 1
        
        return tool_types
    
    def semantic_search(self, query: SearchQuery, db_session, embedding_service) -> List[SearchResult]:
        """
        Perform semantic search with post-processing and filtering.
        
        Args:
            query: Search query object
            db_session: Database session for fetching service data
            embedding_service: Embedding service for query encoding
            
        Returns:
            List of search results
        """
        from backend.models.models import Service
        
        if not self.is_initialized:
            raise RuntimeError("Search service not initialized")
        
        # Generate query embedding
        query_embedding = embedding_service.embed_text(query.text)
        
        # Perform vector search
        raw_results = self.search(query_embedding, query.limit * 3)  # Get more for filtering
        
        if not raw_results:
            return []
        
        # Fetch service data
        results = []
        service_ids = [r[0] for r in raw_results]
        
        # Base query for active services
        services_query = db_session.query(Service).filter(
            Service.id.in_(service_ids),
            Service.status == 'active'
        )
        
        # Get all services first
        services = {s.id: s for s in services_query.all()}
        
        # Fetch tools data if orchestration is requested
        tools_by_service = {}
        if query.include_orchestration:
            from backend.models.models import Tool
            tools_query = db_session.query(Tool).filter(
                Tool.service_id.in_(service_ids)
            ).all()
            
            for tool in tools_query:
                if tool.service_id not in tools_by_service:
                    tools_by_service[tool.service_id] = []
                tools_by_service[tool.service_id].append({
                    'tool_name': tool.tool_name,
                    'description': tool.tool_description,
                    'input_schema': tool.input_schema,
                    'output_schema': tool.output_schema,
                    'example_calls': tool.example_calls,
                    'validation_rules': tool.validation_rules,
                    'error_handling': tool.error_handling,
                    'performance_metrics': tool.performance_metrics,
                    'rate_limit_config': tool.rate_limit_config,
                    'tool_version': tool.tool_version,
                    'is_active': tool.is_active,
                    'deprecation_date': tool.deprecation_date.isoformat() if tool.deprecation_date else None,
                    'deprecation_notice': tool.deprecation_notice,
                    'created_at': tool.created_at.isoformat() if tool.created_at else None,
                    'updated_at': tool.updated_at.isoformat() if tool.updated_at else None
                })
        
        # Build final results with filtering
        for rank, (service_id, score) in enumerate(raw_results):
            if service_id not in services:
                continue
            
            if score < query.min_score:
                continue
            
            service = services[service_id]
            
            # Apply domain filter
            if query.domains:
                service_domains = [d.domain.lower() for d in service.industries]
                query_domains = [d.lower() for d in query.domains]
                if not any(domain in service_domains for domain in query_domains):
                    continue
            
            # Apply capability filter
            if query.capabilities:
                service_capabilities = [c.capability_desc.lower() for c in service.capabilities]
                query_capabilities = [c.lower() for c in query.capabilities]
                # Check if any query capability is contained in service capabilities
                if not any(
                    any(query_cap in svc_cap for svc_cap in service_capabilities)
                    for query_cap in query_capabilities
                ):
                    continue
            
            service_data = {
                'id': service.id,
                'name': service.name,
                'description': service.description,
                'endpoint': service.endpoint,
                'version': service.version,
                'status': service.status,
                'tool_type': service.tool_type,
                'visibility': service.visibility,
                'interaction_modes': service.interaction_modes,
                'capabilities': [c.capability_desc for c in service.capabilities],
                'domains': [d.domain for d in service.industries],
                'tags': getattr(service, 'tags', []) or [],
                
                # Performance & SLA
                'default_timeout_ms': service.default_timeout_ms,
                'default_retry_policy': service.default_retry_policy,
                'success_criteria': service.success_criteria,
                
                # Integration Details (if available)
                'integration_details': {
                    'access_protocol': service.integration_details.access_protocol if service.integration_details else None,
                    'base_endpoint': service.integration_details.base_endpoint if service.integration_details else None,
                    'auth_method': service.integration_details.auth_method if service.integration_details else None,
                    'rate_limit_requests': service.integration_details.rate_limit_requests if service.integration_details else None,
                    'rate_limit_window_seconds': service.integration_details.rate_limit_window_seconds if service.integration_details else None,
                    'max_concurrent_requests': service.integration_details.max_concurrent_requests if service.integration_details else None,
                    'health_check_endpoint': service.integration_details.health_check_endpoint if service.integration_details else None,
                } if service.integration_details else None,
                
                # Agent Protocol Details (if available)
                'agent_protocol_details': {
                    'message_protocol': service.agent_protocols.message_protocol if service.agent_protocols else None,
                    'protocol_version': service.agent_protocols.protocol_version if service.agent_protocols else None,
                    'expected_input_format': service.agent_protocols.expected_input_format if service.agent_protocols else None,
                    'response_style': service.agent_protocols.response_style if service.agent_protocols else None,
                    'supports_streaming': service.agent_protocols.supports_streaming if service.agent_protocols else None,
                    'supports_async': service.agent_protocols.supports_async if service.agent_protocols else None,
                    'supports_batch': service.agent_protocols.supports_batch if service.agent_protocols else None,
                    'max_context_length': service.agent_protocols.max_context_length if service.agent_protocols else None,
                } if service.agent_protocols else None
            }
            
            # Add agent orchestration data if requested
            if query.include_orchestration:
                service_data.update({
                    # Agent Orchestration Details
                    'agent_protocol': service.agent_protocol,
                    'auth_type': service.auth_type,
                    'auth_config': service.auth_config,
                    'tool_recommendations': service.tool_recommendations,
                    'agent_capabilities': service.agent_capabilities,
                    'communication_patterns': service.communication_patterns,
                    'orchestration_metadata': service.orchestration_metadata,
                    
                    # Tools available for this service
                    'tools': tools_by_service.get(service_id, []),
                    
                    # Orchestration summary
                    'orchestration_summary': {
                        'total_tools': len(tools_by_service.get(service_id, [])),
                        'protocol_version': service.agent_protocol,
                        'authentication_required': service.auth_type is not None,
                        'supports_orchestration': service.agent_protocol is not None,
                        'tool_count_by_type': self._count_tools_by_type(tools_by_service.get(service_id, []))
                    }
                })
            
            result = SearchResult(
                service_id=service_id,
                score=score,
                service_data=service_data,
                rank=rank + 1
            )
            
            results.append(result)
            
            if len(results) >= query.limit:
                break
        
        return results
