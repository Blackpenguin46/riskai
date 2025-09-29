#!/usr/bin/env python3
"""
RiskAI Simple API for Docker Testing
Minimal version with essential endpoints only
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Optional, Any
import logging
from datetime import datetime
import os

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="RiskAI Platform",
    description="Enterprise cybersecurity risk assessment with AI-powered feedback",
    version="1.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Import chatbot router if available
try:
    from chatbot.chatbot_api import router as chatbot_router
    app.include_router(chatbot_router, prefix="/api")
    logger.info("Chatbot API loaded successfully")
except ImportError as e:
    logger.warning(f"Could not import chatbot_router: {e}")

# Import enterprise assessment router if available
try:
    from assessment.enterprise_assessment_api import router as enterprise_router
    app.include_router(enterprise_router, prefix="/api")
    logger.info("Enterprise assessment API loaded successfully")
except ImportError as e:
    logger.warning(f"Could not import enterprise_router: {e}")
    enterprise_router = None

# Initialize RAG pipeline for AI feedback
rag_initialized = False
try:
    from rag_pipeline.embedder import SimpleEmbedder
    from rag_pipeline.loader_simple import SimpleDocumentLoader
    from rag_pipeline.simple_vector_store import SimpleVectorStore

    logger.info("Initializing RAG pipeline...")

    # Initialize components
    embedder = SimpleEmbedder()
    vector_store = SimpleVectorStore(persist_directory="/app/vectordb")

    # Check if vector store is empty
    if vector_store.is_empty():
        logger.info("Vector store is empty, loading documents...")
        loader = SimpleDocumentLoader(data_dir="/app/data")
        documents = loader.load_documents()
        logger.info(f"Loaded {len(documents)} documents")

        # Add documents to vector store
        for doc in documents:
            embedding = embedder.embed(doc['content'])
            vector_store.add(
                id=doc['id'],
                embedding=embedding,
                metadata=doc['metadata'],
                content=doc['content']
            )
        vector_store.persist()
        logger.info("Documents indexed successfully")
    else:
        logger.info("Vector store already populated")

    rag_initialized = True
    logger.info("RAG pipeline initialized successfully")

except Exception as e:
    logger.warning(f"Could not initialize RAG pipeline: {e}")
    logger.warning("AI feedback will use fallback responses")

# Health check endpoint
@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "1.0.0"
    }

# System status endpoint
@app.get("/api/system/status")
def get_system_status():
    """Get system status"""
    return {
        "platform": "RiskAI",
        "version": "1.0.0",
        "features": {
            "120_question_assessment": True,
            "ai_chatbot": True,
            "docker_deployment": True
        },
        "timestamp": datetime.utcnow().isoformat()
    }

# Note: Enterprise assessment endpoints are now provided by enterprise_assessment_api router
# which includes the full 120-question assessment with dynamic scoring

# Company profile endpoints
@app.post("/api/company/profile")  
def save_company_profile(profile: Dict[str, Any]):
    """Save company profile"""
    logger.info(f"Saving company profile: {profile}")
    return {
        "status": "success",
        "message": "Company profile saved successfully"
    }

@app.get("/api/company/profile")
def get_company_profile():
    """Get company profile"""
    return {
        "name": "Sample Company",
        "industry": "healthcare",
        "size": "medium",
        "country": "US"
    }

if __name__ == "__main__":
    import uvicorn
    logger.info("Starting RiskAI Simple API...")
    uvicorn.run(app, host="0.0.0.0", port=8000)