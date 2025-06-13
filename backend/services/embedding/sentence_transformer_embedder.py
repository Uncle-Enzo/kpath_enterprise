"""
Sentence-Transformers based embedding service for KPATH Enterprise.

Uses the all-MiniLM-L6-v2 model for high-quality semantic embeddings.
"""

import numpy as np
from typing import List, Dict, Any, Optional
import logging
import os
from .embedding_service import EmbeddingService

logger = logging.getLogger(__name__)


class SentenceTransformerEmbedder(EmbeddingService):
    """
    Sentence-Transformers based embedding service.
    
    Uses the all-MiniLM-L6-v2 model which provides excellent performance
    with 384-dimensional embeddings.
    """
    
    def __init__(self, model_name: str = "all-MiniLM-L6-v2", dimension: int = 384):
        """
        Initialize the sentence-transformers embedder.
        
        Args:
            model_name: Name of the sentence-transformers model
            dimension: Expected embedding dimension
        """
        super().__init__(dimension)
        self.model_name = model_name
        self.model = None
        self.sentence_transformers_available = False
        
        # Try to import sentence-transformers
        try:
            from sentence_transformers import SentenceTransformer
            self.SentenceTransformer = SentenceTransformer
            self.sentence_transformers_available = True
            logger.info("Sentence-transformers library loaded successfully")
        except ImportError as e:
            logger.warning(f"Sentence-transformers not available: {e}")
            self.SentenceTransformer = None
    
    def fit(self, texts: List[str]) -> None:
        """
        Load and initialize the sentence-transformers model.
        
        Args:
            texts: List of texts (not used for pre-trained models)
        """
        if not self.sentence_transformers_available:
            raise RuntimeError("Sentence-transformers library not available")
        
        try:
            logger.info(f"Loading sentence-transformers model: {self.model_name}")
            self.model = self.SentenceTransformer(self.model_name)
            
            # Verify the model's embedding dimension
            test_embedding = self.model.encode(["test"])
            actual_dimension = test_embedding.shape[1]
            
            if actual_dimension != self.dimension:
                logger.warning(f"Model dimension {actual_dimension} != expected {self.dimension}")
                self.dimension = actual_dimension
            
            self.is_fitted = True
            logger.info(f"Model loaded successfully with {self.dimension}D embeddings")
            
        except Exception as e:
            logger.error(f"Failed to load model {self.model_name}: {e}")
            raise RuntimeError(f"Failed to load sentence-transformers model: {e}")
    
    def embed_text(self, text: str) -> np.ndarray:
        """
        Generate embedding for a single text.
        
        Args:
            text: Input text to embed
            
        Returns:
            Embedding vector as numpy array
        """
        if not self.is_fitted:
            # Auto-fit on first use
            self.fit([])
        
        if not text or not text.strip():
            # Return zero vector for empty text
            return np.zeros(self.dimension, dtype=np.float32)
        
        try:
            embedding = self.model.encode([text], convert_to_numpy=True)
            return embedding[0].astype(np.float32)
        except Exception as e:
            logger.error(f"Failed to embed text: {e}")
            # Return zero vector on error
            return np.zeros(self.dimension, dtype=np.float32)
    
    def embed_texts(self, texts: List[str]) -> np.ndarray:
        """
        Generate embeddings for multiple texts.
        
        Args:
            texts: List of input texts to embed
            
        Returns:
            Matrix of embedding vectors (n_texts x dimension)
        """
        if not self.is_fitted:
            # Auto-fit on first use
            self.fit([])
        
        if not texts:
            return np.array([]).reshape(0, self.dimension)
        
        # Filter out empty texts and keep track of indices
        valid_texts = []
        valid_indices = []
        
        for i, text in enumerate(texts):
            if text and text.strip():
                valid_texts.append(text)
                valid_indices.append(i)
        
        # Initialize result matrix
        embeddings = np.zeros((len(texts), self.dimension), dtype=np.float32)
        
        if valid_texts:
            try:
                # Generate embeddings for valid texts
                valid_embeddings = self.model.encode(
                    valid_texts, 
                    convert_to_numpy=True,
                    show_progress_bar=len(valid_texts) > 10
                )
                
                # Place embeddings in correct positions
                for i, embedding in enumerate(valid_embeddings):
                    original_index = valid_indices[i]
                    embeddings[original_index] = embedding.astype(np.float32)
                    
            except Exception as e:
                logger.error(f"Failed to embed texts: {e}")
                # Return zero embeddings on error
        
        return embeddings
    
    def save_model(self, filepath: str) -> None:
        """
        Save the model configuration.
        
        Note: Sentence-transformers models are cached automatically.
        We just save the configuration.
        
        Args:
            filepath: Path to save the configuration
        """
        if not self.is_fitted:
            raise RuntimeError("Cannot save unfitted model")
        
        model_config = {
            'model_name': self.model_name,
            'dimension': self.dimension,
            'is_fitted': self.is_fitted,
            'sentence_transformers_available': self.sentence_transformers_available
        }
        
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        import pickle
        with open(filepath, 'wb') as f:
            pickle.dump(model_config, f)
        
        logger.info(f"Model configuration saved to {filepath}")
    
    def load_model(self, filepath: str) -> None:
        """
        Load the model configuration and reinitialize the model.
        
        Args:
            filepath: Path to load the configuration from
        """
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Model configuration not found: {filepath}")
        
        import pickle
        with open(filepath, 'rb') as f:
            model_config = pickle.load(f)
        
        self.model_name = model_config['model_name']
        self.dimension = model_config['dimension']
        
        # Reinitialize the model
        if self.sentence_transformers_available:
            self.fit([])
        else:
            logger.warning("Sentence-transformers not available, cannot load model")
        
        logger.info(f"Model configuration loaded from {filepath}")
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the model.
        
        Returns:
            Dictionary with model information
        """
        info = {
            'fitted': self.is_fitted,
            'model_name': self.model_name,
            'dimension': self.dimension,
            'sentence_transformers_available': self.sentence_transformers_available
        }
        
        if self.is_fitted and self.model is not None:
            # Add model-specific information
            try:
                info['max_seq_length'] = getattr(self.model, 'max_seq_length', 'unknown')
                info['device'] = str(self.model.device) if hasattr(self.model, 'device') else 'unknown'
            except Exception as e:
                logger.debug(f"Could not get model details: {e}")
        
        return info
    
    def is_available(self) -> bool:
        """
        Check if sentence-transformers is available.
        
        Returns:
            True if sentence-transformers can be used
        """
        return self.sentence_transformers_available


# Factory function to create the best available embedder
def create_best_embedder(dimension: int = 384) -> EmbeddingService:
    """
    Create the best available embedding service.
    
    Returns:
        EmbeddingService instance (sentence-transformers preferred, TF-IDF fallback)
    """
    # Try sentence-transformers first
    st_embedder = SentenceTransformerEmbedder(dimension=dimension)
    if st_embedder.is_available():
        logger.info("Using sentence-transformers embedder with all-MiniLM-L6-v2")
        return st_embedder
    
    # Fall back to TF-IDF
    logger.info("Sentence-transformers not available, using TF-IDF embedder")
    from .tfidf_embedder import TFIDFEmbedder
    return TFIDFEmbedder(dimension=dimension)
