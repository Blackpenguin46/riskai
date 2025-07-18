# rag_pipeline/store_compatible.py
# ------------------
# Handles persisting and loading document embeddings with ChromaDB fallback support

import logging
import os
import shutil
from typing import List, Union, Any
from langchain.schema import Document

logger = logging.getLogger(__name__)

# Try to import ChromaDB components
try:
    from langchain_chroma import Chroma
    CHROMADB_AVAILABLE = True
    logger.info("ChromaDB is available")
except ImportError as e:
    logger.warning(f"ChromaDB not available: {e}")
    CHROMADB_AVAILABLE = False
    Chroma = None

# Import fallback components
from .vector_store_fallback import FallbackVectorStore, get_embedder as get_fallback_embedder

def store_embeddings(chunks: List[Document], embedder, persist_dir: str = "vectordb") -> Union[Any, FallbackVectorStore]:
    """
    Create a new vector store from document chunks and persist to disk.
    Uses ChromaDB if available, otherwise falls back to simple vector store.
    """
    
    if CHROMADB_AVAILABLE and Chroma is not None:
        try:
            db = Chroma.from_documents(
                documents=chunks,
                embedding=embedder,
                persist_directory=persist_dir
            )
            db.persist()
            logger.info(f"Created ChromaDB vector store with {len(chunks)} documents")
            return db
        except Exception as e:
            logger.error(f"ChromaDB failed, falling back to simple store: {e}")
    
    # Fallback to simple vector store
    fallback_store = FallbackVectorStore(persist_dir + "_fallback")
    
    # Extract text content from Document objects
    texts = []
    metadatas = []
    for chunk in chunks:
        if hasattr(chunk, 'page_content'):
            texts.append(chunk.page_content)
        else:
            texts.append(str(chunk))
        
        if hasattr(chunk, 'metadata'):
            metadatas.append(chunk.metadata)
        else:
            metadatas.append({"source": "unknown"})
    
    # Generate embeddings using fallback embedder if main embedder fails
    try:
        if hasattr(embedder, 'embed_documents'):
            embeddings = embedder.embed_documents(texts)
        else:
            # Use fallback embedder
            fallback_embedder = get_fallback_embedder()
            embeddings = fallback_embedder.embed_documents(texts)
    except Exception as e:
        logger.error(f"Error generating embeddings: {e}")
        fallback_embedder = get_fallback_embedder()
        embeddings = fallback_embedder.embed_documents(texts)
    
    # Add to fallback store
    fallback_store.add_documents(texts, embeddings, metadatas)
    logger.info(f"Created fallback vector store with {len(texts)} documents")
    
    return fallback_store

def load_existing_embeddings(embedder, persist_dir: str = "vectordb") -> Union[Any, FallbackVectorStore]:
    """
    Load an existing vector store from disk. If loading fails, rebuild from source documents.
    """
    
    # Try ChromaDB first
    if CHROMADB_AVAILABLE and Chroma is not None:
        try:
            db = Chroma(
                persist_directory=persist_dir,
                embedding=embedder
            )
            logger.info("Loaded existing ChromaDB vector store")
            return db
        except Exception as e:
            logger.warning(f"ChromaDB load failed: {e}")
    
    # Try fallback store
    fallback_dir = persist_dir + "_fallback"
    try:
        fallback_store = FallbackVectorStore(fallback_dir)
        if fallback_store.documents:  # Check if it has data
            logger.info("Loaded existing fallback vector store")
            return fallback_store
    except Exception as e:
        logger.warning(f"Fallback store load failed: {e}")
    
    # Rebuild from source documents
    logger.info("Rebuilding vector store from source documents")
    
    try:
        from .loader import load_documents, chunk_documents
        
        docs_dir = os.getenv("PDF_DATA_DIR", "data/")
        docs = load_documents(docs_dir)
        
        if not docs:
            logger.warning(f"No documents found in {docs_dir}")
            # Return empty fallback store
            return FallbackVectorStore(fallback_dir)
        
        chunks = chunk_documents(docs)
        return store_embeddings(chunks, embedder, persist_dir)
        
    except Exception as e:
        logger.error(f"Failed to rebuild vector store: {e}")
        # Return empty fallback store as last resort
        return FallbackVectorStore(fallback_dir)

class VectorStoreWrapper:
    """Wrapper to provide consistent interface for both ChromaDB and fallback store"""
    
    def __init__(self, store):
        self.store = store
        self.is_chromadb = hasattr(store, 'similarity_search') and CHROMADB_AVAILABLE
        self.is_fallback = isinstance(store, FallbackVectorStore)
    
    def similarity_search(self, query: str, k: int = 4) -> List[Document]:
        """Search for similar documents"""
        
        if self.is_chromadb:
            # ChromaDB interface
            return self.store.similarity_search(query, k=k)
        
        elif self.is_fallback:
            # Fallback interface
            try:
                # Get embedder to encode query
                embedder = get_fallback_embedder()
                query_embedding = embedder.embed_query(query)
                
                results = self.store.similarity_search(query_embedding, k=k)
                
                # Convert to Document objects
                documents = []
                for result in results:
                    doc = Document(
                        page_content=result['document'],
                        metadata=result['metadata']
                    )
                    documents.append(doc)
                
                return documents
                
            except Exception as e:
                logger.error(f"Error in fallback similarity search: {e}")
                return []
        
        else:
            logger.error("Unknown vector store type")
            return []
    
    def add_documents(self, documents: List[Document]):
        """Add documents to the store"""
        
        if self.is_chromadb:
            self.store.add_documents(documents)
        
        elif self.is_fallback:
            # Convert documents to text and embeddings
            texts = [doc.page_content for doc in documents]
            metadatas = [doc.metadata for doc in documents]
            
            embedder = get_fallback_embedder()
            embeddings = embedder.embed_documents(texts)
            
            self.store.add_documents(texts, embeddings, metadatas)

def get_vector_store(persist_dir: str = "vectordb") -> VectorStoreWrapper:
    """Get a vector store instance wrapped for consistent interface"""
    
    # Try to get embedder
    try:
        from .embedder import get_embedder
        embedder = get_embedder()
    except Exception as e:
        logger.warning(f"Failed to get main embedder: {e}")
        embedder = get_fallback_embedder()
    
    # Load or create store
    store = load_existing_embeddings(embedder, persist_dir)
    return VectorStoreWrapper(store)