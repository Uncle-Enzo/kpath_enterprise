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
        
        # File paths for persistence
        self.model_path = "data/models/embedding_model.pkl"
        self.index_path = "data/indexes/search_index.pkl"
        
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
        Perform semantic search.
        
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
            
            # Save new index
            self._save_model_and_index()
            
            self.index_built = True
            logger.info("Search index rebuilt successfully")
            return True
            
        except Exception as e:
            logger.error(f"Failed to rebuild index: {e}")
            return False


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
