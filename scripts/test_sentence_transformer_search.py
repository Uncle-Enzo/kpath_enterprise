#!/usr/bin/env python
"""
Test and verify Sentence Transformer is being used for search
"""
import sys
import os
sys.path.append('/Users/james/claude_development/kpath_enterprise')

# First, let's verify sentence_transformers is available
print("=" * 60)
print("Checking ML Dependencies...")
print("=" * 60)

try:
    import torch
    print(f"✅ PyTorch version: {torch.__version__}")
    print(f"   CUDA available: {torch.cuda.is_available()}")
    if torch.backends.mps.is_available():
        print(f"   MPS (Apple Silicon) available: True")
except ImportError as e:
    print(f"❌ PyTorch not installed: {e}")

try:
    import sentence_transformers
    print(f"✅ Sentence Transformers version: {sentence_transformers.__version__}")
except ImportError as e:
    print(f"❌ Sentence Transformers not installed: {e}")
    print("\nPlease install with:")
    print("  pip install sentence-transformers")
    sys.exit(1)

try:
    import faiss
    print(f"✅ FAISS available")
except ImportError:
    try:
        import faiss_cpu as faiss
        print(f"✅ FAISS-CPU available")
    except ImportError as e:
        print(f"❌ FAISS not installed: {e}")

print("\n" + "=" * 60)
print("Testing Sentence Transformer Model...")
print("=" * 60)

from sentence_transformers import SentenceTransformer

# Test loading the model
model_name = "all-MiniLM-L6-v2"
print(f"Loading model: {model_name}")
model = SentenceTransformer(model_name)
print(f"✅ Model loaded successfully!")
print(f"   Embedding dimension: {model.get_sentence_embedding_dimension()}")

# Test encoding
test_sentences = [
    "Customer data management system",
    "Financial reporting and analytics",
    "Email communication service"
]

print("\nTesting encoding...")
embeddings = model.encode(test_sentences)
print(f"✅ Encoded {len(test_sentences)} sentences")
print(f"   Embedding shape: {embeddings.shape}")
print(f"   First embedding sample: {embeddings[0][:5]}...")

print("\n" + "=" * 60)
print("Testing Search System Integration...")
print("=" * 60)

# Now test the actual search system
from backend.services.embedding.sentence_transformer_embedder import SentenceTransformerEmbedder
from backend.services.search_manager import initialize_search, get_search_manager
from backend.services.search.search_service import SearchQuery
from backend.core.database import SessionLocal

# Test the embedder directly
embedder = SentenceTransformerEmbedder()
print(f"Embedder available: {embedder.is_available()}")
print(f"Sentence transformers available: {embedder.sentence_transformers_available}")

if not embedder.is_available():
    print("❌ Sentence Transformer embedder not available!")
    print("   This means the search system will fall back to TF-IDF")
else:
    print("✅ Sentence Transformer embedder is available!")

# Test search initialization
print("\nInitializing search system...")
db = SessionLocal()
try:
    # Force rebuild to ensure we're using the latest configuration
    initialize_search(db, force_rebuild=True)
    search_manager = get_search_manager()
    
    # Check what embedder is being used
    embedder_type = type(search_manager.embedding_service).__name__
    print(f"Search manager using: {embedder_type}")
    
    if embedder_type == "SentenceTransformerEmbedder":
        print("✅ Search system is using Sentence Transformers!")
    else:
        print(f"⚠️  Search system is using {embedder_type} instead of SentenceTransformerEmbedder")
    
    # Perform a test search
    print("\nPerforming test search...")
    query = SearchQuery(
        text="customer data analytics",
        limit=3,
        min_score=0.1
    )
    
    results = search_manager.search(query, db)
    print(f"Found {len(results)} results:")
    for i, result in enumerate(results, 1):
        print(f"  {i}. {result.service_data['name']} (Score: {result.score:.3f})")
        
except Exception as e:
    print(f"❌ Error during search test: {e}")
    import traceback
    traceback.print_exc()
finally:
    db.close()

print("\n" + "=" * 60)
print("Test completed!")
print("=" * 60)
