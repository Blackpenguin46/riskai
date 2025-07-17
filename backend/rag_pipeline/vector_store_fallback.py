"""
Vector Store Fallback Implementation

Provides a fallback vector store implementation when ChromaDB is not available.
Uses FAISS or simple in-memory storage for development.
"""

import os
import json
import pickle
import logging
from typing import List, Dict, Any, Optional, Tuple
from pathlib import Path
import numpy as np

logger = logging.getLogger(__name__)

class FallbackVectorStore:
    """Simple vector store implementation for development"""
    
    def __init__(self, persist_directory: str = "vectordb_fallback"):
        self.persist_directory = Path(persist_directory)
        self.persist_directory.mkdir(exist_ok=True)
        
        self.vectors = []
        self.documents = []
        self.metadatas = []
        self.dimension = None
        
        # Try to load existing data
        self._load_data()
    
    def add_documents(self, documents: List[str], embeddings: List[List[float]], metadatas: List[Dict] = None):
        """Add documents with their embeddings"""
        
        if metadatas is None:
            metadatas = [{"source": f"doc_{i}"} for i in range(len(documents))]
        
        self.documents.extend(documents)
        self.vectors.extend(embeddings)
        self.metadatas.extend(metadatas)
        
        if self.dimension is None and embeddings:
            self.dimension = len(embeddings[0])
        
        self._save_data()
        logger.info(f"Added {len(documents)} documents to fallback vector store")
    
    def similarity_search(self, query_embedding: List[float], k: int = 4) -> List[Dict[str, Any]]:
        """Search for similar documents"""
        
        if not self.vectors:
            return []
        
        # Convert to numpy for easier computation
        query_vec = np.array(query_embedding)
        stored_vecs = np.array(self.vectors)
        
        # Calculate cosine similarity
        similarities = np.dot(stored_vecs, query_vec) / (
            np.linalg.norm(stored_vecs, axis=1) * np.linalg.norm(query_vec)
        )
        
        # Get top k results
        top_indices = np.argsort(similarities)[-k:][::-1]
        
        results = []
        for idx in top_indices:
            if idx < len(self.documents):
                results.append({
                    "document": self.documents[idx],
                    "metadata": self.metadatas[idx],
                    "similarity": float(similarities[idx])
                })
        
        return results
    
    def _save_data(self):
        """Save data to disk"""
        try:
            data = {
                "vectors": self.vectors,
                "documents": self.documents,
                "metadatas": self.metadatas,
                "dimension": self.dimension
            }
            
            with open(self.persist_directory / "data.pkl", "wb") as f:
                pickle.dump(data, f)
                
        except Exception as e:
            logger.error(f"Error saving vector store data: {e}")
    
    def _load_data(self):
        """Load data from disk"""
        try:
            data_file = self.persist_directory / "data.pkl"
            if data_file.exists():
                with open(data_file, "rb") as f:
                    data = pickle.load(f)
                
                self.vectors = data.get("vectors", [])
                self.documents = data.get("documents", [])
                self.metadatas = data.get("metadatas", [])
                self.dimension = data.get("dimension")
                
                logger.info(f"Loaded {len(self.documents)} documents from fallback store")
                
        except Exception as e:
            logger.error(f"Error loading vector store data: {e}")

class SimpleEmbedder:
    """Simple embedding fallback using sentence transformers"""
    
    def __init__(self):
        self.model = None
        self._initialize_model()
    
    def _initialize_model(self):
        """Initialize the embedding model"""
        try:
            from sentence_transformers import SentenceTransformer
            self.model = SentenceTransformer('all-MiniLM-L6-v2')
            logger.info("Initialized SentenceTransformer model")
        except Exception as e:
            logger.error(f"Error initializing embedding model: {e}")
            self.model = None
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Embed a list of documents"""
        if self.model is None:
            # Return dummy embeddings if model not available
            return [[0.0] * 384 for _ in texts]
        
        try:
            embeddings = self.model.encode(texts)
            return embeddings.tolist()
        except Exception as e:
            logger.error(f"Error embedding documents: {e}")
            return [[0.0] * 384 for _ in texts]
    
    def embed_query(self, text: str) -> List[float]:
        """Embed a single query"""
        if self.model is None:
            return [0.0] * 384
        
        try:
            embedding = self.model.encode([text])
            return embedding[0].tolist()
        except Exception as e:
            logger.error(f"Error embedding query: {e}")
            return [0.0] * 384

def get_vector_store(persist_directory: str = "vectordb_fallback") -> FallbackVectorStore:
    """Get vector store instance"""
    return FallbackVectorStore(persist_directory)

def get_embedder() -> SimpleEmbedder:
    """Get embedder instance"""
    return SimpleEmbedder()

# Test function
def test_fallback_system():
    """Test the fallback system"""
    
    embedder = get_embedder()
    vector_store = get_vector_store()
    
    # Test documents
    documents = [
        "This is a test document about cybersecurity",
        "Risk assessment is important for organizations",
        "Machine learning can help with threat detection"
    ]
    
    # Generate embeddings
    embeddings = embedder.embed_documents(documents)
    
    # Add to vector store
    vector_store.add_documents(documents, embeddings)
    
    # Test search
    query = "cybersecurity risk"
    query_embedding = embedder.embed_query(query)
    results = vector_store.similarity_search(query_embedding, k=2)
    
    print(f"Query: {query}")
    print(f"Results: {len(results)}")
    for i, result in enumerate(results):
        print(f"  {i+1}. {result['document'][:50]}... (similarity: {result['similarity']:.3f})")

if __name__ == "__main__":
    test_fallback_system()