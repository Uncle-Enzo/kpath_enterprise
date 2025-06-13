#!/usr/bin/env python
"""
Test if torch-env has all required ML dependencies
"""

import sys
print(f"Python: {sys.version}")
print(f"Executable: {sys.executable}")
print("-" * 60)

# Test imports
modules = [
    ("torch", "PyTorch"),
    ("sentence_transformers", "Sentence Transformers"),
    ("faiss", "FAISS"),
    ("numpy", "NumPy"),
    ("sklearn", "Scikit-learn"),
]

for module_name, display_name in modules:
    try:
        module = __import__(module_name)
        version = getattr(module, "__version__", "unknown")
        print(f"✅ {display_name}: {version}")
    except ImportError as e:
        print(f"❌ {display_name}: Not installed ({e})")

print("-" * 60)

# Test sentence transformers functionality
try:
    from sentence_transformers import SentenceTransformer
    print("Testing SentenceTransformer model loading...")
    model = SentenceTransformer('all-MiniLM-L6-v2')
    print("✅ Model loaded successfully!")
    
    # Test encoding
    test_sentence = "This is a test sentence"
    embedding = model.encode(test_sentence)
    print(f"✅ Embedding generated: shape {embedding.shape}")
    
except Exception as e:
    print(f"❌ Error testing SentenceTransformer: {e}")
