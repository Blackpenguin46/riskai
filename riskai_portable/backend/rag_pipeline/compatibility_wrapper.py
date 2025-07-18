"""
Compatibility wrapper for RAG pipeline components.

This module provides fallback implementations when complex dependencies
like ChromaDB or LangChain Community are not available.
"""

import logging
from typing import List, Dict, Any, Optional

logger = logging.getLogger(__name__)

# Try to import complex dependencies
try:
    from langchain_community.document_loaders import PyPDFLoader
    from langchain_chroma import Chroma
    COMPLEX_DEPS_AVAILABLE = True
    logger.info("Complex dependencies available")
except ImportError as e:
    logger.warning(f"Complex dependencies not available: {e}")
    COMPLEX_DEPS_AVAILABLE = False

# Import simple alternatives
from .loader_simple import load_documents as load_documents_simple
from .loader_simple import chunk_documents as chunk_documents_simple
from .simple_vector_store import create_simple_vector_store

def load_documents(data_dir: str):
    """Load documents with fallback support"""
    
    if COMPLEX_DEPS_AVAILABLE:
        try:
            # Try to use the original complex loader
            from .loader import load_documents as load_documents_complex
            return load_documents_complex(data_dir)
        except Exception as e:
            logger.warning(f"Complex loader failed: {e}, using simple loader")
    
    # Use simple loader
    return load_documents_simple(data_dir)

def chunk_documents(documents):
    """Chunk documents with fallback support"""
    
    if COMPLEX_DEPS_AVAILABLE:
        try:
            from .loader import chunk_documents as chunk_documents_complex
            return chunk_documents_complex(documents)
        except Exception as e:
            logger.warning(f"Complex chunking failed: {e}, using simple chunking")
    
    # Use simple chunking
    return chunk_documents_simple(documents)

def get_embedder():
    """Get embedder with fallback support"""
    
    if COMPLEX_DEPS_AVAILABLE:
        try:
            from .embedder import get_embedder as get_embedder_complex
            return get_embedder_complex()
        except Exception as e:
            logger.warning(f"Complex embedder failed: {e}, using simple embedder")
    
    # Use simple embedder
    return SimpleEmbedder()

def store_embeddings(chunks, embedder, persist_dir: str = "vectordb"):
    """Store embeddings with fallback support"""
    
    if COMPLEX_DEPS_AVAILABLE:
        try:
            from .store import store_embeddings as store_embeddings_complex
            return store_embeddings_complex(chunks, embedder, persist_dir)
        except Exception as e:
            logger.warning(f"Complex storage failed: {e}, using simple storage")
    
    # Use simple storage
    vector_store = create_simple_vector_store(persist_dir + "_simple")
    vector_store.add_documents(chunks)
    return vector_store

def load_existing_embeddings(embedder, persist_dir: str = "vectordb"):
    """Load existing embeddings with fallback support"""
    
    if COMPLEX_DEPS_AVAILABLE:
        try:
            from .store import load_existing_embeddings as load_existing_embeddings_complex
            return load_existing_embeddings_complex(embedder, persist_dir)
        except Exception as e:
            logger.warning(f"Complex loading failed: {e}, using simple loading")
    
    # Use simple loading
    vector_store = create_simple_vector_store(persist_dir + "_simple")
    return vector_store

def build_rag_chain(db):
    """Build RAG chain with fallback support"""
    
    if COMPLEX_DEPS_AVAILABLE:
        try:
            from .retriever import build_rag_chain as build_rag_chain_complex
            return build_rag_chain_complex(db)
        except Exception as e:
            logger.warning(f"Complex RAG chain failed: {e}, using simple chain")
    
    # Use simple RAG chain
    return SimpleRAGChain(db)

class SimpleEmbedder:
    """Simple embedder implementation using basic text processing"""
    
    def __init__(self):
        pass
    
    def embed_documents(self, texts: List[str]) -> List[List[float]]:
        """Generate simple embeddings for documents"""
        from .simple_vector_store import SimpleVectorStore
        store = SimpleVectorStore()
        return store._generate_simple_embeddings(texts)
    
    def embed_query(self, text: str) -> List[float]:
        """Generate simple embedding for a query"""
        return self.embed_documents([text])[0]

class SimpleRAGChain:
    """Simple RAG chain implementation"""
    
    def __init__(self, vector_store):
        self.vector_store = vector_store
    
    def run(self, query: str) -> Dict[str, Any]:
        """Run a query through the RAG chain"""
        
        try:
            # Get similar documents
            docs = self.vector_store.similarity_search(query, k=3)
            
            # Create context from documents
            context = "\n\n".join([doc.page_content for doc in docs])
            
            # Simple response generation
            response = self._generate_response(query, context)
            
            return {
                "result": response,
                "source_documents": docs
            }
            
        except Exception as e:
            logger.error(f"Error in simple RAG chain: {e}")
            return {
                "result": f"I understand you're asking about: {query}. This is a cybersecurity-related question. Based on the available information, I recommend following security best practices and conducting proper risk assessments.",
                "source_documents": []
            }
    
    def _generate_response(self, query: str, context: str) -> str:
        """Generate a simple response based on query and context"""
        
        # Simple template-based response
        if not context:
            return f"I understand you're asking about {query}. This appears to be a cybersecurity-related question. I recommend consulting security frameworks and conducting proper risk assessments."
        
        # Extract key information from context
        context_words = context.lower().split()
        query_words = query.lower().split()
        
        # Find relevant sentences
        sentences = context.split('.')
        relevant_sentences = []
        
        for sentence in sentences:
            sentence_words = sentence.lower().split()
            if any(word in sentence_words for word in query_words):
                relevant_sentences.append(sentence.strip())
        
        if relevant_sentences:
            response = f"Based on the available information: {' '.join(relevant_sentences[:2])}"
        else:
            response = f"Regarding {query}: {context[:200]}..."
        
        return response

# Test function
def test_compatibility():
    """Test the compatibility wrapper"""
    
    print("Testing compatibility wrapper...")
    
    # Test document loading
    docs = load_documents("data/")
    print(f"Loaded {len(docs)} documents")
    
    # Test chunking
    chunks = chunk_documents(docs)
    print(f"Created {len(chunks)} chunks")
    
    # Test embedder
    embedder = get_embedder()
    print(f"Got embedder: {type(embedder)}")
    
    # Test vector store
    vector_store = store_embeddings(chunks, embedder)
    print(f"Created vector store: {type(vector_store)}")
    
    # Test RAG chain
    rag_chain = build_rag_chain(vector_store)
    print(f"Created RAG chain: {type(rag_chain)}")
    
    # Test query
    result = rag_chain.run("What is cybersecurity risk assessment?")
    print(f"Query result: {result['result'][:100]}...")

if __name__ == "__main__":
    test_compatibility()