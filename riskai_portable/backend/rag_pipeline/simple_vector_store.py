"""
Simple Vector Store Implementation

Pure Python implementation that doesn't require any compiled dependencies.
Works with any Python version and provides basic vector similarity search.
"""

import json
import pickle
import math
import os
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
import logging

logger = logging.getLogger(__name__)

class SimpleVectorStore:
    """Simple vector store using pure Python"""
    
    def __init__(self, persist_directory: str = "vectordb_simple"):
        self.persist_directory = Path(persist_directory)
        self.persist_directory.mkdir(exist_ok=True)
        
        self.documents = []
        self.embeddings = []
        self.metadatas = []
        
        # Load existing data
        self._load_data()
    
    def add_texts(self, texts: List[str], metadatas: Optional[List[Dict]] = None) -> List[str]:
        """Add texts to the vector store"""
        
        if metadatas is None:
            metadatas = [{"source": f"doc_{i}"} for i in range(len(texts))]
        
        # Generate simple embeddings using TF-IDF like approach
        embeddings = self._generate_simple_embeddings(texts)
        
        # Store
        self.documents.extend(texts)
        self.embeddings.extend(embeddings)
        self.metadatas.extend(metadatas)
        
        # Save
        self._save_data()
        
        logger.info(f"Added {len(texts)} texts to simple vector store")
        return [f"doc_{i}" for i in range(len(texts))]
    
    def similarity_search(self, query: str, k: int = 4) -> List[Dict[str, Any]]:
        """Search for similar documents"""
        
        if not self.documents:
            return []
        
        # Generate query embedding
        query_embedding = self._generate_simple_embeddings([query])[0]
        
        # Calculate similarities
        similarities = []
        for i, doc_embedding in enumerate(self.embeddings):
            similarity = self._cosine_similarity(query_embedding, doc_embedding)
            similarities.append((i, similarity))
        
        # Sort by similarity
        similarities.sort(key=lambda x: x[1], reverse=True)
        
        # Return top k results
        results = []
        for i, similarity in similarities[:k]:
            if i < len(self.documents):
                results.append({
                    "page_content": self.documents[i],
                    "metadata": self.metadatas[i],
                    "similarity": similarity
                })
        
        return results
    
    def _generate_simple_embeddings(self, texts: List[str]) -> List[List[float]]:
        """Generate simple embeddings using word frequency"""
        
        embeddings = []
        
        for text in texts:
            # Simple word-based embedding
            words = text.lower().split()
            
            # Create a fixed-size embedding based on common words
            embedding = [0.0] * 100  # 100-dimensional embedding
            
            # Hash words to dimensions
            for word in words:
                if len(word) > 2:  # Skip very short words
                    hash_val = hash(word) % 100
                    embedding[hash_val] += 1.0
            
            # Normalize
            norm = math.sqrt(sum(x * x for x in embedding))
            if norm > 0:
                embedding = [x / norm for x in embedding]
            
            embeddings.append(embedding)
        
        return embeddings
    
    def _cosine_similarity(self, vec1: List[float], vec2: List[float]) -> float:
        """Calculate cosine similarity between two vectors"""
        
        if len(vec1) != len(vec2):
            return 0.0
        
        dot_product = sum(a * b for a, b in zip(vec1, vec2))
        norm1 = math.sqrt(sum(a * a for a in vec1))
        norm2 = math.sqrt(sum(b * b for b in vec2))
        
        if norm1 == 0 or norm2 == 0:
            return 0.0
        
        return dot_product / (norm1 * norm2)
    
    def _save_data(self):
        """Save data to disk"""
        try:
            data = {
                "documents": self.documents,
                "embeddings": self.embeddings,
                "metadatas": self.metadatas
            }
            
            with open(self.persist_directory / "data.json", "w") as f:
                json.dump(data, f, indent=2)
                
        except Exception as e:
            logger.error(f"Error saving vector store data: {e}")
    
    def _load_data(self):
        """Load data from disk"""
        try:
            data_file = self.persist_directory / "data.json"
            if data_file.exists():
                with open(data_file, "r") as f:
                    data = json.load(f)
                
                self.documents = data.get("documents", [])
                self.embeddings = data.get("embeddings", [])
                self.metadatas = data.get("metadatas", [])
                
                logger.info(f"Loaded {len(self.documents)} documents from simple store")
                
        except Exception as e:
            logger.error(f"Error loading vector store data: {e}")
            # Initialize empty
            self.documents = []
            self.embeddings = []
            self.metadatas = []

class SimpleLangChainVectorStore:
    """LangChain-compatible wrapper for SimpleVectorStore"""
    
    def __init__(self, persist_directory: str = "vectordb_simple"):
        self.store = SimpleVectorStore(persist_directory)
    
    def add_documents(self, documents):
        """Add documents to the store"""
        texts = []
        metadatas = []
        
        for doc in documents:
            if hasattr(doc, 'page_content'):
                texts.append(doc.page_content)
            else:
                texts.append(str(doc))
            
            if hasattr(doc, 'metadata'):
                metadatas.append(doc.metadata)
            else:
                metadatas.append({"source": "unknown"})
        
        return self.store.add_texts(texts, metadatas)
    
    def similarity_search(self, query: str, k: int = 4):
        """Search for similar documents"""
        
        results = self.store.similarity_search(query, k)
        
        # Convert to LangChain Document-like objects
        documents = []
        for result in results:
            # Create a simple object with the required attributes
            doc = type('Document', (), {
                'page_content': result['page_content'],
                'metadata': result['metadata']
            })()
            documents.append(doc)
        
        return documents

def create_simple_vector_store(persist_directory: str = "vectordb_simple") -> SimpleLangChainVectorStore:
    """Create a simple vector store instance"""
    return SimpleLangChainVectorStore(persist_directory)

# Test function
def test_simple_vector_store():
    """Test the simple vector store"""
    
    store = create_simple_vector_store()
    
    # Test documents
    class MockDocument:
        def __init__(self, content, metadata=None):
            self.page_content = content
            self.metadata = metadata or {}
    
    documents = [
        MockDocument("This is a document about cybersecurity risks", {"source": "doc1"}),
        MockDocument("Risk assessment is important for organizations", {"source": "doc2"}),
        MockDocument("Machine learning helps with threat detection", {"source": "doc3"})
    ]
    
    # Add documents
    store.add_documents(documents)
    
    # Test search
    results = store.similarity_search("cybersecurity threat", k=2)
    
    print(f"Found {len(results)} results:")
    for i, doc in enumerate(results):
        print(f"  {i+1}. {doc.page_content[:50]}... (source: {doc.metadata.get('source', 'unknown')})")

if __name__ == "__main__":
    test_simple_vector_store()