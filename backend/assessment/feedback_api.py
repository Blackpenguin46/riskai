"""
API endpoints for AI-powered assessment feedback
Integrates with the 120-question assessment and RAG pipeline
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, List, Any, Optional
import logging
from datetime import datetime

from .ai_feedback_engine import (
    ai_feedback_engine, 
    AssessmentContext, 
    FeedbackResult,
    AIRecommendation
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/assessment/feedback", tags=["AI Feedback"])

class AssessmentFeedbackRequest(BaseModel):
    """Request model for generating AI feedback"""
    overall_score: float
    risk_level: str
    section_scores: Dict[str, Dict[str, Any]]
    responses: Dict[str, Dict[str, Any]]
    completion_rate: float

class RecommendationResponse(BaseModel):
    """Response model for AI recommendations"""
    category: str
    priority: int
    title: str
    description: str
    implementation_steps: List[str]
    frameworks_referenced: List[str]
    confidence_score: float
    sources: List[str]
    estimated_impact: str
    estimated_effort: str
    timeline: str

class FeedbackResponse(BaseModel):
    """Response model for complete AI feedback"""
    overall_assessment: str
    risk_summary: str
    immediate_actions: List[RecommendationResponse]
    short_term_improvements: List[RecommendationResponse]
    strategic_initiatives: List[RecommendationResponse]
    emerging_tech_focus: List[str]
    confidence_metrics: Dict[str, float]
    sources_used: List[str]
    generation_timestamp: str

@router.post("/generate", response_model=FeedbackResponse)
async def generate_ai_feedback(request: AssessmentFeedbackRequest):
    """
    Generate comprehensive AI-powered feedback based on assessment results
    Uses local LLM and RAG pipeline with cybersecurity knowledge base
    """
    try:
        logger.info(f"Generating AI feedback for assessment with score: {request.overall_score}")
        
        # Identify critical and high-risk sections
        critical_sections = []
        high_risk_sections = []
        
        for section_id, section_data in request.section_scores.items():
            percentage = section_data.get('percentage', 0)
            if percentage < 40:
                critical_sections.append(section_id)
            elif percentage < 60:
                high_risk_sections.append(section_id)
        
        # Create assessment context
        assessment_context = AssessmentContext(
            overall_score=request.overall_score,
            risk_level=request.risk_level,
            section_scores=request.section_scores,
            responses=request.responses,
            completion_rate=request.completion_rate,
            critical_sections=critical_sections,
            high_risk_sections=high_risk_sections
        )
        
        # Generate AI feedback
        feedback_result = ai_feedback_engine.generate_comprehensive_feedback(assessment_context)
        
        # Convert to response format
        def convert_recommendation(rec: AIRecommendation) -> RecommendationResponse:
            return RecommendationResponse(
                category=rec.category,
                priority=rec.priority,
                title=rec.title,
                description=rec.description,
                implementation_steps=rec.implementation_steps,
                frameworks_referenced=rec.frameworks_referenced,
                confidence_score=rec.confidence_score,
                sources=rec.sources,
                estimated_impact=rec.estimated_impact,
                estimated_effort=rec.estimated_effort,
                timeline=rec.timeline
            )
        
        response = FeedbackResponse(
            overall_assessment=feedback_result.overall_assessment,
            risk_summary=feedback_result.risk_summary,
            immediate_actions=[convert_recommendation(rec) for rec in feedback_result.immediate_actions],
            short_term_improvements=[convert_recommendation(rec) for rec in feedback_result.short_term_improvements],
            strategic_initiatives=[convert_recommendation(rec) for rec in feedback_result.strategic_initiatives],
            emerging_tech_focus=feedback_result.emerging_tech_focus,
            confidence_metrics=feedback_result.confidence_metrics,
            sources_used=feedback_result.sources_used,
            generation_timestamp=feedback_result.generation_timestamp.isoformat()
        )
        
        logger.info(f"Successfully generated AI feedback with {len(response.immediate_actions)} immediate actions")
        return response
        
    except Exception as e:
        logger.error(f"Error generating AI feedback: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to generate AI feedback: {str(e)}"
        )

@router.get("/health")
async def check_feedback_health():
    """Check the health of the AI feedback system"""
    try:
        # Check if RAG pipeline is available
        rag_available = ai_feedback_engine.qa_chain is not None
        
        return {
            "status": "healthy",
            "rag_pipeline_available": rag_available,
            "local_llm_model": "tiiuae/falcon-rw-1b",
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Health check failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")

@router.post("/reload-knowledge")
async def reload_knowledge_base():
    """Reload the RAG knowledge base from PDF documents"""
    try:
        logger.info("Reloading AI feedback knowledge base...")
        
        # Reinitialize the RAG pipeline
        ai_feedback_engine.initialize_rag_pipeline()
        
        return {
            "status": "success",
            "message": "Knowledge base reloaded successfully",
            "rag_available": ai_feedback_engine.qa_chain is not None,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error reloading knowledge base: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to reload knowledge base: {str(e)}"
        )

@router.get("/knowledge-sources")
async def get_knowledge_sources():
    """Get information about available knowledge sources"""
    try:
        import os
        
        data_dir = "data/"
        pdf_files = []
        
        if os.path.exists(data_dir):
            for file in os.listdir(data_dir):
                if file.endswith('.pdf'):
                    pdf_files.append(file)
        
        return {
            "total_pdf_sources": len(pdf_files),
            "pdf_files": pdf_files[:20],  # Return first 20 for brevity
            "rag_pipeline_status": "available" if ai_feedback_engine.qa_chain else "unavailable",
            "knowledge_domains": [
                "Cybersecurity Risk Management",
                "IT Governance",
                "Compliance Frameworks",
                "Emerging Technology Security",
                "NIST Standards",
                "ISO 27001",
                "Risk Assessment Methodologies"
            ]
        }
    except Exception as e:
        logger.error(f"Error getting knowledge sources: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to get knowledge sources: {str(e)}"
        )