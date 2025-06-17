"""
Base embedding service interface for KPATH Enterprise.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Tuple
import numpy as np
from sqlalchemy.orm import Session


class EmbeddingService(ABC):
    """
    Abstract base class for embedding services.
    
    Provides a common interface for different embedding implementations
    (TF-IDF, transformer-based, etc.)
    """
    
    def __init__(self, dimension: int = 384):
        """
        Initialize the embedding service.
        
        Args:
            dimension: Embedding vector dimension
        """
        self.dimension = dimension
        self.is_fitted = False
    
    @abstractmethod
    def fit(self, texts: List[str]) -> None:
        """
        Fit the embedding model on a corpus of texts.
        
        Args:
            texts: List of texts to fit the model on
        """
        pass
    
    @abstractmethod
    def embed_text(self, text: str) -> np.ndarray:
        """
        Generate embedding for a single text.
        
        Args:
            text: Input text to embed
            
        Returns:
            Embedding vector as numpy array
        """
        pass
    
    @abstractmethod
    def embed_texts(self, texts: List[str]) -> np.ndarray:
        """
        Generate embeddings for multiple texts.
        
        Args:
            texts: List of input texts to embed
            
        Returns:
            Matrix of embedding vectors (n_texts x dimension)
        """
        pass
    
    def embed_service(self, service_data: Dict[str, Any]) -> np.ndarray:
        """
        Generate embedding for a service record.
        
        Combines service name, description, and capabilities into
        a single text for embedding.
        
        Args:
            service_data: Service data dictionary
            
        Returns:
            Service embedding vector
        """
        # Combine service fields into searchable text
        text_parts = []
        
        # Add service name (weighted more heavily)
        if service_data.get('name'):
            text_parts.extend([service_data['name']] * 3)  # Triple weight
        
        # Add description
        if service_data.get('description'):
            text_parts.append(service_data['description'])
        
        # Add capabilities
        if service_data.get('capabilities'):
            capabilities = service_data['capabilities']
            if isinstance(capabilities, list):
                text_parts.extend(capabilities)
            else:
                text_parts.append(str(capabilities))
        
        # Add tags if available
        if service_data.get('tags'):
            tags = service_data['tags']
            if isinstance(tags, list):
                text_parts.extend(tags)
            else:
                text_parts.append(str(tags))
        
        # Add domains
        if service_data.get('domains'):
            domains = service_data['domains']
            if isinstance(domains, list):
                text_parts.extend(domains)
            else:
                text_parts.append(str(domains))
        
        # Combine all parts
        combined_text = ' '.join(str(part) for part in text_parts if part)
        
        return self.embed_text(combined_text)
    
    def embed_services_from_db(self, db: Session) -> Tuple[np.ndarray, List[int]]:
        """
        Generate embeddings for all services in the database.
        
        Args:
            db: Database session
            
        Returns:
            Tuple of (embeddings matrix, service IDs list)
        """
        from backend.models.models import Service
        
        # Get all active services
        services = db.query(Service).filter(
            Service.status == 'active'
        ).all()
        
        if not services:
            return np.array([]), []
        
        # Convert services to embedding data
        service_texts = []
        service_ids = []
        
        for service in services:
            service_data = {
                'name': service.name,
                'description': service.description,
                'capabilities': [cap.capability_desc for cap in service.capabilities],
                'domains': [domain.domain for domain in service.industries],  # Note: using industries table for domains
                'tags': getattr(service, 'tags', []) or []  # Handle missing tags field
            }
            
            # Combine into searchable text
            text_parts = []
            if service_data['name']:
                text_parts.extend([service_data['name']] * 3)
            if service_data['description']:
                text_parts.append(service_data['description'])
            text_parts.extend(service_data['capabilities'])
            text_parts.extend(service_data['domains'])
            text_parts.extend(service_data['tags'])
            
            combined_text = ' '.join(str(part) for part in text_parts if part)
            service_texts.append(combined_text)
            service_ids.append(service.id)
        
        # Generate embeddings
        embeddings = self.embed_texts(service_texts)
        
        return embeddings, service_ids
    
    def similarity(self, embedding1: np.ndarray, embedding2: np.ndarray) -> float:
        """
        Calculate cosine similarity between two embeddings.
        
        Args:
            embedding1: First embedding vector
            embedding2: Second embedding vector
            
        Returns:
            Cosine similarity score (0-1)
        """
        # Normalize vectors
        norm1 = np.linalg.norm(embedding1)
        norm2 = np.linalg.norm(embedding2)
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        # Calculate cosine similarity
        similarity = np.dot(embedding1, embedding2) / (norm1 * norm2)
        
        # Ensure result is in [0, 1] range
        return max(0.0, min(1.0, (similarity + 1) / 2))
    
    def embed_tool(self, tool_data: Dict[str, Any]) -> np.ndarray:
        """
        Generate embedding for a tool record.
        
        Combines tool name, description, input/output schemas into
        a single text for embedding.
        
        Args:
            tool_data: Tool data dictionary
            
        Returns:
            Tool embedding vector
        """
        # Combine tool fields into searchable text
        text_parts = []
        
        # Add tool name (weighted more heavily)
        if tool_data.get('tool_name'):
            text_parts.extend([tool_data['tool_name']] * 3)  # Triple weight
        
        # Add description
        if tool_data.get('description'):
            text_parts.append(tool_data['description'])
        
        # Add input schema descriptions
        if tool_data.get('input_schema') and isinstance(tool_data['input_schema'], dict):
            schema = tool_data['input_schema']
            # Extract parameter names and descriptions
            if 'properties' in schema:
                for param, details in schema['properties'].items():
                    text_parts.append(param)
                    if isinstance(details, dict) and 'description' in details:
                        text_parts.append(details['description'])
        
        # Add output schema descriptions
        if tool_data.get('output_schema') and isinstance(tool_data['output_schema'], dict):
            schema = tool_data['output_schema']
            if 'properties' in schema:
                for param, details in schema['properties'].items():
                    text_parts.append(param)
                    if isinstance(details, dict) and 'description' in details:
                        text_parts.append(details['description'])
        
        # Add example call parameter names
        if tool_data.get('example_calls') and isinstance(tool_data['example_calls'], dict):
            for example_name, example_data in tool_data['example_calls'].items():
                text_parts.append(example_name)
                if isinstance(example_data, dict):
                    text_parts.extend(example_data.keys())
        
        # Combine all parts
        combined_text = ' '.join(str(part) for part in text_parts if part)
        
        return self.embed_text(combined_text)

    def embed_tools_from_db(self, db: Session) -> Tuple[np.ndarray, List[int]]:
        """
        Generate embeddings for all active tools in the database.
        
        Args:
            db: Database session
            
        Returns:
            Tuple of (embeddings matrix, tool IDs list)
        """
        from backend.models.models import Tool
        
        # Get all active tools
        tools = db.query(Tool).filter(
            Tool.is_active == True
        ).all()
        
        if not tools:
            return np.array([]), []
        
        # Convert tools to embedding data
        tool_texts = []
        tool_ids = []
        
        for tool in tools:
            tool_data = {
                'tool_name': tool.tool_name,
                'description': tool.tool_description,
                'input_schema': tool.input_schema,
                'output_schema': tool.output_schema,
                'example_calls': tool.example_calls
            }
            
            # Combine into searchable text
            text_parts = []
            if tool_data['tool_name']:
                text_parts.extend([tool_data['tool_name']] * 3)
            if tool_data['description']:
                text_parts.append(tool_data['description'])
            
            # Extract schema information
            for schema_type in ['input_schema', 'output_schema']:
                schema = tool_data.get(schema_type)
                if schema and isinstance(schema, dict) and 'properties' in schema:
                    for param, details in schema['properties'].items():
                        text_parts.append(param)
                        if isinstance(details, dict) and 'description' in details:
                            text_parts.append(details['description'])
            
            # Extract example call information
            examples = tool_data.get('example_calls')
            if examples and isinstance(examples, dict):
                for example_name, example_data in examples.items():
                    text_parts.append(example_name)
                    if isinstance(example_data, dict):
                        text_parts.extend(example_data.keys())
            
            combined_text = ' '.join(str(part) for part in text_parts if part)
            tool_texts.append(combined_text)
            tool_ids.append(tool.id)
        
        # Generate embeddings
        embeddings = self.embed_texts(tool_texts)
        
        return embeddings, tool_ids
        """
        Generate embedding for a search query.
        
        Args:
            query: Search query text
            
        Returns:
            Query embedding vector
        """
        return self.embed_text(query)
    
    def embed_batch(self, texts: List[str]) -> np.ndarray:
        """
        Generate embeddings for a batch of texts.
        
        Args:
            texts: List of texts to embed
            
        Returns:
            Matrix of embeddings
        """
        return self.embed_texts(texts)
    
    def calculate_similarities(self, query_embedding: np.ndarray, 
                             document_embeddings: np.ndarray) -> np.ndarray:
        """
        Calculate similarities between a query and multiple documents.
        
        Args:
            query_embedding: Query embedding vector
            document_embeddings: Matrix of document embeddings
            
        Returns:
            Array of similarity scores
        """
        if len(document_embeddings.shape) == 1:
            # Single document
            return np.array([self.similarity(query_embedding, document_embeddings)])
        
        # Multiple documents
        similarities = []
        for doc_embedding in document_embeddings:
            sim = self.similarity(query_embedding, doc_embedding)
            similarities.append(sim)
        
        return np.array(similarities)
