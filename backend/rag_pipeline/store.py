# rag_pipeline/store.py
# ------------------
# Handles persisting and loading document embeddings using ChromaDB

import logging
import os
import shutil
from langchain_chroma import Chroma
from langchain.schema import Document
from rag_pipeline.loader import load_documents, chunk_documents

logger = logging.getLogger(__name__)


def store_embeddings(chunks: list[Document], embedder, persist_dir: str = "vectordb") -> Chroma:
    """
    Create a new Chroma vector store from document chunks and persist to disk.
    """
    db = Chroma.from_documents(
        documents=chunks,
        embedding=embedder,  # ✅ Use 'embedding' instead of 'embedding_function'
        persist_directory=persist_dir
    )
    # Note: Newer versions of Chroma auto-persist, no need to call persist()
    return db


def load_existing_embeddings(embedder, persist_dir: str = "vectordb") -> Chroma:
    """
    Load an existing Chroma vector store from disk. If loading fails (e.g., due to corrupted configuration),
    remove the existing store and rebuild from source documents.
    """
    try:
        return Chroma(
            persist_directory=persist_dir,
            embedding=embedder
        )
    except (KeyError, Exception) as e:
        logger.warning(f"Chroma collection load failed: {e}. Rebuilding vector store from source documents.")
        # Remove corrupted data files
        if os.path.isdir(persist_dir):
            for filename in os.listdir(persist_dir):
                filepath = os.path.join(persist_dir, filename)
                try:
                    if os.path.isfile(filepath):
                        os.remove(filepath)
                    elif os.path.isdir(filepath):
                        shutil.rmtree(filepath)
                except Exception as cleanup_error:
                    logger.warning(f"Failed to remove {filepath}: {cleanup_error}")
        # Rebuild from PDF source files
        docs_dir = os.getenv("PDF_DATA_DIR", "data/")
        docs = load_documents(docs_dir)
        if not docs:
            raise RuntimeError(f"No documents found in {docs_dir} to rebuild embeddings.")
        chunks = chunk_documents(docs)
        db = Chroma.from_documents(
            documents=chunks,
            embedding=embedder,
            persist_directory=persist_dir
        )
        # Note: Newer versions of Chroma auto-persist, no need to call persist()
        return db