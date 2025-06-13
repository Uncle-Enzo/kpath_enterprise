"""
TF-IDF based embedding service for KPATH Enterprise.

Provides a simple, fast embedding solution using TF-IDF vectorization.
Can be easily upgraded to transformer-based embeddings later.
"""

import numpy as np
from typing import List, Dict, Any
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import TruncatedSVD
import pickle
import os
from .embedding_service import EmbeddingService


class TFIDFEmbedder(EmbeddingService):
    """
    TF-IDF based embedding service with dimensionality reduction.
    
    Uses TfidfVectorizer + TruncatedSVD to create dense, fixed-size embeddings
    suitable for FAISS indexing.
    """
    
    def __init__(self, dimension: int = 384, max_features: int = 10000):
        """
        Initialize TF-IDF embedder.
        
        Args:
            dimension: Target embedding dimension
            max_features: Maximum number of TF-IDF features
        """
        super().__init__(dimension)
        self.max_features = max_features
        
        # Initialize components
        self.vectorizer = TfidfVectorizer(
            max_features=max_features,
            stop_words='english',
            ngram_range=(1, 2),  # Include bigrams
            min_df=1,  # Include all terms for small datasets
            max_df=1.0,  # Include all terms
            sublinear_tf=True,  # Use log scaling
            norm='l2'  # L2 normalization
        )
        
        self.svd = TruncatedSVD(
            n_components=min(dimension, max_features),
            random_state=42
        )
        
    def fit(self, texts: List[str]) -> None:
        """
        Fit the TF-IDF model and SVD on the provided texts.
        
        Args:
            texts: List of texts to fit the model on
        """
        if not texts:
            raise ValueError("Cannot fit on empty text list")
        
        # Fit TF-IDF vectorizer
        tfidf_matrix = self.vectorizer.fit_transform(texts)
        
        # Adjust SVD components based on actual features
        n_features = tfidf_matrix.shape[1]
        n_components = min(self.dimension, n_features, len(texts) - 1)
        
        if n_components <= 0:
            n_components = 1
        
        # Create SVD with appropriate number of components
        self.svd = TruncatedSVD(
            n_components=n_components,
            random_state=42
        )
        
        # Fit SVD for dimensionality reduction
        self.svd.fit(tfidf_matrix)
        
        # Update dimension to actual SVD components
        self.dimension = self.svd.n_components
        self.is_fitted = True
        
    def embed_text(self, text: str) -> np.ndarray:
        """
        Generate embedding for a single text.
        
        Args:
            text: Input text to embed
            
        Returns:
            Dense embedding vector
        """
        if not self.is_fitted:
            # Auto-fit with the current text if not fitted
            self.fit([text] if text else ["default"])
        
        # Transform to TF-IDF
        tfidf_vector = self.vectorizer.transform([text])
        
        # Reduce dimensions with SVD
        embedding = self.svd.transform(tfidf_vector)
        
        return embedding.flatten().astype(np.float32)
    
    def embed_texts(self, texts: List[str]) -> np.ndarray:
        """
        Generate embeddings for multiple texts.
        
        Args:
            texts: List of input texts to embed
            
        Returns:
            Matrix of embedding vectors (n_texts x dimension)
        """
        if not self.is_fitted:
            # Auto-fit with the provided texts
            self.fit(texts if texts else ["default"])
        
        if not texts:
            return np.array([]).reshape(0, self.dimension)
        
        # Transform to TF-IDF
        tfidf_matrix = self.vectorizer.transform(texts)
        
        # Reduce dimensions with SVD
        embeddings = self.svd.transform(tfidf_matrix)
        
        return embeddings.astype(np.float32)
    
    def save_model(self, filepath: str) -> None:
        """
        Save the fitted model to disk.
        
        Args:
            filepath: Path to save the model
        """
        if not self.is_fitted:
            raise RuntimeError("Cannot save unfitted model")
        
        model_data = {
            'vectorizer': self.vectorizer,
            'svd': self.svd,
            'dimension': self.dimension,
            'max_features': self.max_features,
            'is_fitted': self.is_fitted
        }
        
        os.makedirs(os.path.dirname(filepath), exist_ok=True)
        
        with open(filepath, 'wb') as f:
            pickle.dump(model_data, f)
    
    def load_model(self, filepath: str) -> None:
        """
        Load a fitted model from disk.
        
        Args:
            filepath: Path to load the model from
        """
        if not os.path.exists(filepath):
            raise FileNotFoundError(f"Model file not found: {filepath}")
        
        with open(filepath, 'rb') as f:
            model_data = pickle.load(f)
        
        self.vectorizer = model_data['vectorizer']
        self.svd = model_data['svd']
        self.dimension = model_data['dimension']
        self.max_features = model_data['max_features']
        self.is_fitted = model_data['is_fitted']
    
    def get_feature_names(self) -> List[str]:
        """
        Get the feature names from the TF-IDF vectorizer.
        
        Returns:
            List of feature names
        """
        if not self.is_fitted:
            raise RuntimeError("Model must be fitted before getting features")
        
        return self.vectorizer.get_feature_names_out().tolist()
    
    def get_model_info(self) -> Dict[str, Any]:
        """
        Get information about the fitted model.
        
        Returns:
            Dictionary with model information
        """
        if not self.is_fitted:
            return {'fitted': False}
        
        return {
            'fitted': True,
            'dimension': self.dimension,
            'max_features': self.max_features,
            'vocabulary_size': len(self.vectorizer.vocabulary_),
            'svd_components': self.svd.n_components,
            'svd_explained_variance_ratio': self.svd.explained_variance_ratio_.tolist()
        }
