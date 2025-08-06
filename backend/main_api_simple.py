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

# Assessment questions endpoint
@app.get("/api/assessment/enterprise/questions")
def get_assessment_questions():
    """Get enterprise assessment questions"""
    return {
        "sections": [
            {
                "id": "governance",
                "name": "Governance & Risk Management",
                "questions": [
                    {
                        "id": "gov_001",
                        "text": "What is your current cybersecurity governance maturity level?",
                        "type": "scale",
                        "scale_min": 1,
                        "scale_max": 10
                    }
                ]
            },
            {
                "id": "access_control", 
                "name": "Access Control & Identity",
                "questions": [
                    {
                        "id": "access_001",
                        "text": "What percentage of your users have multi-factor authentication enabled?",
                        "type": "percentage"
                    }
                ]
            }
        ],
        "total_questions": 2,
        "estimated_time": "5 minutes"
    }

# Submit assessment endpoint
@app.post("/api/assessment/enterprise/submit")
def submit_assessment(data: Dict[str, Any]):
    """Submit assessment answers"""
    logger.info(f"Received assessment submission: {data}")
    
    # Mock scoring response
    return {
        "assessment_id": f"assessment_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
        "overall_score": 75.5,
        "risk_level": "Medium Risk",
        "sections": [
            {
                "name": "Governance & Risk Management",
                "score": 80.0,
                "status": "Good"
            },
            {
                "name": "Access Control & Identity", 
                "score": 71.0,
                "status": "Needs Improvement"
            }
        ],
        "recommendations": [
            "Implement comprehensive security awareness training",
            "Establish regular vulnerability assessments",
            "Develop incident response procedures"
        ],
        "ai_feedback": "Based on your responses, your organization shows good governance practices but needs improvement in access control. Focus on implementing MFA across all systems and conducting regular security training.",
        "timestamp": datetime.utcnow().isoformat()
    }

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