"""
Embedding services for KPATH Enterprise.

This module provides embedding generation services for semantic search.
Supports both sentence-transformers (preferred) and TF-IDF (fallback) embeddings.
"""

from .embedding_service import EmbeddingService
from .tfidf_embedder import TFIDFEmbedder
from .sentence_transformer_embedder import SentenceTransformerEmbedder, create_best_embedder

__all__ = ["EmbeddingService", "TFIDFEmbedder", "SentenceTransformerEmbedder", "create_best_embedder"]
