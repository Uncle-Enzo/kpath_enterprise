"""
Base search service interface for KPATH Enterprise.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass
import numpy as np


@dataclass
class SearchResult:
    """
    Represents a search result from the semantic search service.
    """
    service_id: int
    score: float
    service_data: Dict[str, Any]
    distance: Optional[float] = None
    rank: Optional[int] = None


@dataclass
class SearchQuery:
    """
    Represents a search query with metadata.
    """
    text: str
    user_id: Optional[int] = None
    filters: Optional[Dict[str, Any]] = None
    limit: int = 10
    min_score: float = 0.0
    domains: Optional[List[str]] = None
    capabilities: Optional[List[str]] = None
    include_orchestration: bool = False
    search_mode: str = "agents_only"
    response_mode: str = "full"
    include_schemas: bool = True
    include_examples: bool = True
    field_filter: Optional[List[str]] = None


class SearchService(ABC):
    """
    Abstract base class for search services.
    
    Provides a common interface for different search implementations.
    """
    
    def __init__(self):
        """Initialize the search service."""
        self.is_initialized = False
    
    @abstractmethod
    def initialize(self) -> None:
        """
        Initialize the search service.
        
        This method should be called before using the search service.
        """
        pass
    
    @abstractmethod
    def build_index(self, embeddings: np.ndarray, service_ids: List[int]) -> None:
        """
        Build the search index from embeddings.
        
        Args:
            embeddings: Matrix of service embeddings (n_services x dimension)
            service_ids: List of service IDs corresponding to embeddings
        """
        pass
    
    @abstractmethod
    def search(self, query_embedding: np.ndarray, k: int = 10) -> List[Tuple[int, float]]:
        """
        Search for similar services using query embedding.
        
        Args:
            query_embedding: Query embedding vector
            k: Number of results to return
            
        Returns:
            List of tuples (service_id, score)
        """
        pass
    
    @abstractmethod
    def add_service(self, service_id: int, embedding: np.ndarray) -> None:
        """
        Add a new service to the search index.
        
        Args:
            service_id: Service ID
            embedding: Service embedding vector
        """
        pass
    
    @abstractmethod
    def remove_service(self, service_id: int) -> bool:
        """
        Remove a service from the search index.
        
        Args:
            service_id: Service ID to remove
            
        Returns:
            True if service was removed, False if not found
        """
        pass
    
    @abstractmethod
    def update_service(self, service_id: int, embedding: np.ndarray) -> bool:
        """
        Update a service's embedding in the search index.
        
        Args:
            service_id: Service ID
            embedding: New embedding vector
            
        Returns:
            True if service was updated, False if not found
        """
        pass
    
    @abstractmethod
    def save_index(self, filepath: str) -> None:
        """
        Save the search index to disk.
        
        Args:
            filepath: Path to save the index
        """
        pass
    
    @abstractmethod
    def load_index(self, filepath: str) -> None:
        """
        Load the search index from disk.
        
        Args:
            filepath: Path to load the index from
        """
        pass
    
    @abstractmethod
    def get_index_info(self) -> Dict[str, Any]:
        """
        Get information about the search index.
        
        Returns:
            Dictionary with index information
        """
        pass
    
    def semantic_search(self, query: SearchQuery, db_session) -> List[SearchResult]:
        """
        Perform semantic search with post-processing and filtering.
        
        Args:
            query: Search query object
            db_session: Database session for fetching service data
            
        Returns:
            List of search results
        """
        from backend.services.embedding import EmbeddingService
        from backend.models.models import Service
        
        if not self.is_initialized:
            raise RuntimeError("Search service must be initialized before use")
        
        # This method will be implemented by concrete classes
        # that have access to the embedding service
        raise NotImplementedError("Subclasses must implement semantic_search")
