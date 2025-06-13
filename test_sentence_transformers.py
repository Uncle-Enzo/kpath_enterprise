"""
Test sentence-transformers integration with all-MiniLM-L6-v2 model.
"""

import sys
import os
sys.path.append('/Users/james/claude_development/kpath_enterprise')

import numpy as np
from typing import List


def test_sentence_transformers():
    """Test sentence-transformers embedding service."""
    print("Testing Sentence-Transformers Integration...")
    print("=" * 50)
    
    try:
        from backend.services.embedding.sentence_transformer_embedder import SentenceTransformerEmbedder
        
        # Create embedder
        embedder = SentenceTransformerEmbedder(model_name="all-MiniLM-L6-v2")
        print(f"✓ Created SentenceTransformerEmbedder")
        print(f"  - Model: {embedder.model_name}")
        print(f"  - Expected dimension: {embedder.dimension}")
        print(f"  - Available: {embedder.is_available()}")
        
        if not embedder.is_available():
            print("✗ Sentence-transformers not available")
            return False
        
        # Test single text embedding
        test_text = "customer data management service"
        print(f"\nTesting single text: '{test_text}'")
        
        embedding = embedder.embed_text(test_text)
        print(f"✓ Generated embedding")
        print(f"  - Shape: {embedding.shape}")
        print(f"  - Type: {embedding.dtype}")
        print(f"  - Range: [{embedding.min():.3f}, {embedding.max():.3f}]")
        print(f"  - Norm: {np.linalg.norm(embedding):.3f}")
        
        # Test multiple texts
        test_texts = [
            "customer data management service",
            "user authentication API",
            "payment processing system",
            "file storage service",
            "email notification service"
        ]
        
        print(f"\nTesting {len(test_texts)} texts...")
        embeddings = embedder.embed_texts(test_texts)
        print(f"✓ Generated batch embeddings")
        print(f"  - Shape: {embeddings.shape}")
        print(f"  - Memory usage: ~{embeddings.nbytes / 1024:.1f} KB")
        
        # Test similarity
        print(f"\nTesting semantic similarity...")
        similarities = []
        for i, text1 in enumerate(test_texts):
            for j, text2 in enumerate(test_texts):
                if i < j:
                    emb1, emb2 = embeddings[i], embeddings[j]
                    similarity = embedder.similarity(emb1, emb2)
                    similarities.append((text1, text2, similarity))
        
        # Show most similar pairs
        similarities.sort(key=lambda x: x[2], reverse=True)
        print("Top 3 most similar pairs:")
        for text1, text2, sim in similarities[:3]:
            print(f"  {sim:.3f}: '{text1}' <-> '{text2}'")
        
        # Test model info
        info = embedder.get_model_info()
        print(f"\nModel Information:")
        for key, value in info.items():
            print(f"  - {key}: {value}")
        
        # Test service data embedding
        service_data = {
            'name': 'Customer API',
            'description': 'Manages customer data and profiles with CRUD operations',
            'capabilities': ['data_processing', 'api_integration', 'user_management'],
            'domains': ['crm', 'finance'],
            'tags': ['customer', 'data', 'api', 'rest']
        }
        
        print(f"\nTesting service data embedding...")
        service_embedding = embedder.embed_service(service_data)
        print(f"✓ Generated service embedding")
        print(f"  - Shape: {service_embedding.shape}")
        print(f"  - Norm: {np.linalg.norm(service_embedding):.3f}")
        
        return True
        
    except Exception as e:
        print(f"✗ Test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_best_embedder():
    """Test the factory function for best embedder."""
    print("\n" + "=" * 50)
    print("Testing Best Embedder Factory...")
    
    try:
        from backend.services.embedding import create_best_embedder
        
        embedder = create_best_embedder(dimension=384)
        print(f"✓ Created best available embedder")
        print(f"  - Type: {type(embedder).__name__}")
        
        # Test it works
        test_embedding = embedder.embed_text("test message")
        print(f"✓ Embedding test passed")
        print(f"  - Dimension: {test_embedding.shape[0]}")
        print(f"  - Non-zero: {np.count_nonzero(test_embedding)} / {len(test_embedding)}")
        
        return True
        
    except Exception as e:
        print(f"✗ Factory test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def test_faiss_integration():
    """Test FAISS integration with sentence-transformers."""
    print("\n" + "=" * 50)
    print("Testing FAISS + Sentence-Transformers Integration...")
    
    try:
        from backend.services.search.faiss_search import FAISSSearchService
        from backend.services.embedding import create_best_embedder
        
        # Create embedder
        embedder = create_best_embedder()
        
        # Create test data
        services = [
            "customer data management API",
            "user authentication service", 
            "payment processing system",
            "file storage and retrieval",
            "email notification service",
            "customer relationship management",
            "user profile management",
            "financial transaction processing"
        ]
        
        # Generate embeddings
        print(f"\nGenerating embeddings for {len(services)} services...")
        embeddings = embedder.embed_texts(services)
        service_ids = list(range(1, len(services) + 1))
        
        print(f"✓ Generated embeddings")
        print(f"  - Shape: {embeddings.shape}")
        print(f"  - Dimension: {embeddings.shape[1]}")
        
        # Create search service with correct dimension
        search_service = FAISSSearchService(dimension=embeddings.shape[1])
        
        # Initialize
        search_service.initialize()
        print(f"✓ Initialized search service")
        print(f"  - FAISS available: {search_service.faiss_available}")
        print(f"  - Dimension: {search_service.dimension}")
        
        # Build index
        search_service.build_index(embeddings, service_ids)
        print(f"✓ Built search index")
        
        # Test search
        query = "customer management system"
        query_embedding = embedder.embed_text(query)
        
        results = search_service.search(query_embedding, k=3)
        print(f"\nSearch results for: '{query}'")
        for i, (service_id, score) in enumerate(results):
            service_name = services[service_id - 1]
            print(f"  {i+1}. [{service_id}] {service_name} (score: {score:.3f})")
        
        # Test index info
        info = search_service.get_index_info()
        print(f"\nIndex Information:")
        for key, value in info.items():
            print(f"  - {key}: {value}")
        
        return True
        
    except Exception as e:
        print(f"✗ FAISS integration test failed: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all tests."""
    print("🔬 KPATH Enterprise - Sentence-Transformers Integration Tests")
    print("=" * 70)
    
    tests = [
        test_sentence_transformers,
        test_best_embedder, 
        test_faiss_integration
    ]
    
    passed = 0
    failed = 0
    
    for test_func in tests:
        try:
            if test_func():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"✗ Test {test_func.__name__} crashed: {e}")
            failed += 1
    
    print("\n" + "=" * 70)
    print(f"📊 RESULTS: {passed} passed, {failed} failed")
    
    if failed == 0:
        print("🎉 All tests passed! Sentence-transformers integration is working!")
        print("✨ Ready to use all-MiniLM-L6-v2 for high-quality semantic search!")
    else:
        print("❌ Some tests failed. Check the implementation.")
    
    print("=" * 70)
    return failed == 0


if __name__ == "__main__":
    main()
