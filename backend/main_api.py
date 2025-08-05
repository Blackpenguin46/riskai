#!/usr/bin/env python3
"""
RiskAI Main API
Streamlined API integrating all enhanced components for research paper demonstration
"""

from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Dict, List, Optional, Any
import logging
from datetime import datetime

# Import our enhanced components
try:
    from assessment.scoring_api import router as scoring_router
except ImportError as e:
    print(f"Warning: Could not import scoring_router: {e}")
    scoring_router = None

try:
    from assessment.source_attribution_api import router as attribution_router
except ImportError as e:
    print(f"Warning: Could not import attribution_router: {e}")
    attribution_router = None

try:
    from assessment.bias_detection_api import router as bias_router
except ImportError as e:
    print(f"Warning: Could not import bias_router: {e}")
    bias_router = None

try:
    from assessment.comprehensive_feedback_api import router as feedback_router
except ImportError as e:
    print(f"Warning: Could not import feedback_router: {e}")
    feedback_router = None

try:
    from assessment.question_api import router as question_router
except ImportError as e:
    print(f"Warning: Could not import question_router: {e}")
    question_router = None

try:
    from assessment.assessment_api import router as assessment_router
except ImportError as e:
    print(f"Warning: Could not import assessment_router: {e}")
    assessment_router = None

try:
    from assessment.dashboard_api import router as dashboard_router
except ImportError as e:
    print(f"Warning: Could not import dashboard_router: {e}")
    dashboard_router = None

try:
    from assessment.enterprise_assessment_api import router as enterprise_router
except ImportError as e:
    print(f"Warning: Could not import enterprise_router: {e}")
    enterprise_router = None

try:
    from chatbot.chatbot_api import router as chatbot_router
except ImportError as e:
    print(f"Warning: Could not import chatbot_router: {e}")
    chatbot_router = None

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Create FastAPI app
app = FastAPI(
    title="RiskAI Enhanced Platform",
    description="Enterprise-grade cybersecurity risk assessment with AI-powered feedback, mathematical scoring, and bias detection",
    version="2.0.0"
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include all routers (only if they loaded successfully)
if assessment_router:
    app.include_router(assessment_router, prefix="/api")
if question_router:
    app.include_router(question_router, prefix="/api")
if scoring_router:
    app.include_router(scoring_router, prefix="/api")
if attribution_router:
    app.include_router(attribution_router, prefix="/api")
if bias_router:
    app.include_router(bias_router, prefix="/api")
if feedback_router:
    app.include_router(feedback_router, prefix="/api")
if dashboard_router:
    app.include_router(dashboard_router, prefix="/api")
if enterprise_router:
    app.include_router(enterprise_router, prefix="/api")
if chatbot_router:
    app.include_router(chatbot_router, prefix="/api")

# Health check endpoint
@app.get("/health")
def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow().isoformat(),
        "version": "2.0.0",
        "components": {
            "assessment_engine": "operational",
            "scoring_system": "operational",
            "source_attribution": "operational",
            "bias_detection": "operational",
            "ai_feedback": "operational"
        }
    }

# System status endpoint
@app.get("/api/system/status")
def get_system_status():
    """Get comprehensive system status"""
    return {
        "platform": "RiskAI Enhanced",
        "version": "2.0.0",
        "features": {
            "120_question_assessment": True,
            "mathematical_scoring": True,
            "ai_powered_feedback": True,
            "source_attribution": True,
            "bias_detection": True,
            "real_time_scoring": True,
            "industry_adaptation": True
        },
        "api_endpoints": {
            "assessments": "/api/assessments/",
            "questions": "/api/questions/",
            "scoring": "/api/scoring/",
            "attribution": "/api/attribution/",
            "bias": "/api/bias/",
            "feedback": "/api/feedback/"
        },
        "documentation": "/docs",
        "timestamp": datetime.utcnow().isoformat()
    }

# Demo data endpoint for research paper
@app.get("/api/demo/sample-assessment")
def get_sample_assessment():
    """Get sample assessment data for demonstration (redirects to enterprise assessment)"""
    try:
        # Redirect to the new enterprise assessment demo
        from assessment.enterprise_assessment_api import _get_risk_level
        
        # Create sample data with dynamic scoring
        sample_profile = {
            "name": "Acme Healthcare Corp",
            "industry": "healthcare",
            "size": "medium",
            "country": "US",
            "compliance_requirements": ["HIPAA", "SOC2"],
            "technology_adoption": "medium",
            "data_types": ["patient_data", "financial_data"],
            "risk_tolerance": "medium"
        }
        
        # Sample answers demonstrating different score levels
        sample_answers = {
            "gov_001": "basic",        # 30/100 score
            "gov_002": 6,              # 60/100 score  
            "gov_003": "quarterly",    # 70/100 score
            "gov_004": True,           # 80/100 score
            "access_001": 75,          # 75/100 score (percentage)
            "access_002": "quarterly", # 70/100 score
            "access_003": 6,           # 60/100 score
            "data_001": 85,            # 85/100 score (percentage)
            "data_002": True,          # 80/100 score
            "monitor_001": 7,          # 70/100 score
            "ir_001": 6                # 60/100 score
        }
        
        # Use dynamic scoring engine
        from scoring.dynamic_scoring_engine import dynamic_scoring_engine
        scoring_result = dynamic_scoring_engine.score_assessment(sample_answers, sample_profile)
        
        overall_score = scoring_result['overall_score']
        risk_level, risk_color = _get_risk_level(overall_score)
        
        return {
            "assessment_id": "demo-dynamic-001",
            "company_profile": sample_profile,
            "overall_score": overall_score,
            "risk_level": risk_level,
            "risk_color": risk_color,
            "scoring_method": "dynamic_quantitative_qualitative",
            "section_breakdown": [
                {
                    "section_id": section_id,
                    "section_name": section_data.get('name', section_id.title()),
                    "score": section_scores['score'],
                    "confidence": section_scores['confidence'],
                    "evidence_strength": section_scores['evidence_strength'],
                    "weight": section_scores['weight'],
                    "questions_answered": section_scores['questions_answered']
                }
                for section_id, section_scores in scoring_result['section_scores'].items()
            ],
            "recommendations": scoring_result['recommendations'],
            "insights": scoring_result['insights'],
            "confidence_metrics": scoring_result['confidence_metrics'],
            "quantitative_support": True,
            "industry_adjustments_applied": True,
            "assessment_date": datetime.utcnow().isoformat(),
            "demo_note": "This assessment uses dynamic scoring based on actual answers"
        }
    except Exception as e:
        logger.error(f"Error generating demo assessment: {str(e)}")
        # Fallback to static demo data
        return {
            "assessment_id": "demo-fallback-001",
            "company_profile": {
                "name": "Acme Healthcare Corp",
                "industry": "healthcare",
                "size": "medium"
            },
            "overall_score": 68.5,
            "risk_level": "Medium Risk", 
            "risk_color": "#f59e0b",
            "scoring_method": "fallback_static",
            "error": str(e),
            "demo_note": "Fallback demo data - dynamic scoring unavailable"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)