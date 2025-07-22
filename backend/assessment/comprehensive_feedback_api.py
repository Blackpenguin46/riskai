#!/usr/bin/env python3
"""
Comprehensive Feedback API
Integrates AI recommendations, source attribution, and bias detection into unified feedback endpoints
"""

from fastapi import APIRouter, HTTPException, Query, Depends
from pydantic import BaseModel
from typing import Dict, List, Optional, Any
import logging
from datetime import datetime
import asyncio

from assessment.ai_feedback_engine import ai_feedback_engine
from assessment.source_attribution import source_attributor
from assessment.bias_detection import bias_detector
from database.models import get_session, Assessment, LLMRecommendation, RecommendationSource, BiasMonitoring

logger = logging.getLogger(__name__)
router = APIRouter()

# Pydantic Models
class ComprehensiveFeedbackRequest(BaseModel):
    assessment_id: int
    include_source_attribution: bool = True
    include_bias_analysis: bool = True
    include_confidence_metrics: bool = True
    industry_context: Optional[str] = None
    company_size: Optional[str] = None

class RecommendationWithMetadata(BaseModel):
    recommendation_id: str
    category: str  # immediate, short_term, strategic
    text: str
    confidence_score: float
    implementation_difficulty: str
    expected_impact: str
    timeframe: str
    
    # Source attribution
    primary_sources: Optional[List[Dict[str, Any]]] = None
    supporting_sources: Optional[List[Dict[str, Any]]] = None
    source_confidence: Optional[float] = None
    
    # Bias analysis
    bias_score: Optional[float] = None
    fairness_metrics: Optional[Dict[str, float]] = None
    bias_warnings: Optional[List[str]] = None
    
    # Additional metadata
    frameworks_referenced: Optional[List[str]] = None
    review_required: Optional[bool] = None

class ComprehensiveFeedbackResponse(BaseModel):
    assessment_id: int
    overall_assessment: Dict[str, Any]
    recommendations: List[RecommendationWithMetadata]
    methodology: Dict[str, Any]
    quality_metrics: Dict[str, Any]
    generated_at: str

class FeedbackQualityRequest(BaseModel):
    recommendation_id: str
    user_rating: int  # 1-5 scale
    feedback_text: Optional[str] = None
    implementation_status: Optional[str] = None

class BulkFeedbackRequest(BaseModel):
    assessment_ids: List[int]
    include_comparisons: bool = True

# --- Comprehensive Feedback Endpoints ---

@router.post("/feedback/comprehensive", tags=["AI Feedback"])
async def generate_comprehensive_feedback(request: ComprehensiveFeedbackRequest):
    """Generate comprehensive feedback with AI recommendations, source attribution, and bias analysis"""
    try:
        db = get_session()
        
        # Validate assessment exists
        assessment = db.query(Assessment).filter(Assessment.id == request.assessment_id).first()
        if not assessment:
            raise HTTPException(status_code=404, detail=f"Assessment {request.assessment_id} not found")
        
        # Generate AI recommendations
        logger.info(f"Generating AI recommendations for assessment {request.assessment_id}")
        ai_recommendations = await ai_feedback_engine.generate_comprehensive_feedback(
            assessment_id=request.assessment_id,
            industry_context=request.industry_context,
            company_size=request.company_size
        )
        
        # Process each recommendation with attribution and bias analysis
        processed_recommendations = []
        
        for rec in ai_recommendations.get('recommendations', []):
            recommendation_data = RecommendationWithMetadata(
                recommendation_id=f"rec_{datetime.now().strftime('%Y%m%d_%H%M%S')}_{len(processed_recommendations)}",
                category=rec.get('category', 'general'),
                text=rec.get('text', ''),
                confidence_score=rec.get('confidence', 0.8),
                implementation_difficulty=rec.get('difficulty', 'Medium'),
                expected_impact=rec.get('impact', 'Medium'),
                timeframe=rec.get('timeframe', '1-6 months')
            )
            
            # Add source attribution if requested
            if request.include_source_attribution:
                try:
                    attribution = source_attributor.attribute_recommendation(
                        recommendation_text=rec.get('text', ''),
                        section_id=rec.get('section_id'),
                        assessment_context={
                            'industry': request.industry_context,
                            'company_size': request.company_size
                        }
                    )
                    
                    recommendation_data.primary_sources = [
                        {
                            "framework": source.framework.value,
                            "control_id": source.control_id,
                            "control_title": source.control_title,
                            "relevance_score": source.relevance_score
                        } for source in attribution.primary_sources
                    ]
                    
                    recommendation_data.supporting_sources = [
                        {
                            "framework": source.framework.value,
                            "control_id": source.control_id,
                            "control_title": source.control_title,
                            "relevance_score": source.relevance_score
                        } for source in attribution.supporting_sources
                    ]
                    
                    recommendation_data.source_confidence = attribution.confidence_score
                    recommendation_data.frameworks_referenced = list(set(
                        source.framework.value for source in 
                        attribution.primary_sources + attribution.supporting_sources
                    ))
                    
                except Exception as e:
                    logger.warning(f"Source attribution failed for recommendation: {str(e)}")
            
            # Add bias analysis if requested
            if request.include_bias_analysis:
                try:
                    bias_analysis = bias_detector.analyze_bias(
                        recommendation_text=rec.get('text', ''),
                        context={
                            'industry': request.industry_context,
                            'company_size': request.company_size,
                            'section_id': rec.get('section_id')
                        }
                    )
                    
                    recommendation_data.bias_score = bias_analysis.overall_bias_score
                    recommendation_data.fairness_metrics = {
                        "demographic_parity": bias_analysis.fairness_metrics.demographic_parity,
                        "individual_fairness": bias_analysis.fairness_metrics.individual_fairness,
                        "group_fairness": bias_analysis.fairness_metrics.group_fairness,
                        "overall_fairness": bias_analysis.fairness_metrics.overall_fairness_score
                    }
                    
                    # Extract bias warnings
                    bias_warnings = []
                    for bias in bias_analysis.detected_biases:
                        if bias.severity.value in ['high', 'critical']:
                            bias_warnings.append(f"{bias.bias_type.value}: {bias.description}")
                    
                    recommendation_data.bias_warnings = bias_warnings
                    recommendation_data.review_required = bias_analysis.review_required
                    
                except Exception as e:
                    logger.warning(f"Bias analysis failed for recommendation: {str(e)}")
            
            processed_recommendations.append(recommendation_data)
        
        # Calculate overall quality metrics
        quality_metrics = {
            "total_recommendations": len(processed_recommendations),
            "high_confidence_count": len([r for r in processed_recommendations if r.confidence_score > 0.8]),
            "source_attributed_count": len([r for r in processed_recommendations if r.primary_sources]),
            "bias_reviewed_count": len([r for r in processed_recommendations if r.bias_score is not None]),
            "review_required_count": len([r for r in processed_recommendations if r.review_required]),
            "average_confidence": sum(r.confidence_score for r in processed_recommendations) / len(processed_recommendations) if processed_recommendations else 0,
            "average_bias_score": sum(r.bias_score for r in processed_recommendations if r.bias_score is not None) / len([r for r in processed_recommendations if r.bias_score is not None]) if any(r.bias_score is not None for r in processed_recommendations) else 0
        }
        
        # Prepare methodology information
        methodology = {
            "ai_engine": "RiskAI Feedback Engine v1.0",
            "source_attribution": "Framework-based attribution system" if request.include_source_attribution else "Not included",
            "bias_detection": "Multi-dimensional bias analysis" if request.include_bias_analysis else "Not included",
            "confidence_calculation": "Bayesian confidence estimation" if request.include_confidence_metrics else "Not included",
            "generation_timestamp": datetime.utcnow().isoformat()
        }
        
        # Prepare overall assessment
        overall_assessment = {
            "assessment_score": assessment.overall_score if assessment.overall_score else 0,
            "risk_level": assessment.risk_level if assessment.risk_level else "Unknown",
            "completion_status": assessment.status,
            "industry_context": request.industry_context,
            "company_size": request.company_size,
            "total_questions": 120,  # Standard assessment length
            "recommendation_categories": {
                "immediate": len([r for r in processed_recommendations if r.category == 'immediate']),
                "short_term": len([r for r in processed_recommendations if r.category == 'short_term']),
                "strategic": len([r for r in processed_recommendations if r.category == 'strategic'])
            }
        }
        
        db.close()
        
        response = ComprehensiveFeedbackResponse(
            assessment_id=request.assessment_id,
            overall_assessment=overall_assessment,
            recommendations=processed_recommendations,
            methodology=methodology,
            quality_metrics=quality_metrics,
            generated_at=datetime.utcnow().isoformat()
        )
        
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating comprehensive feedback: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate feedback: {str(e)}")

@router.get("/feedback/{assessment_id}/summary", tags=["AI Feedback"])
def get_feedback_summary(assessment_id: int):
    """Get a summary of generated feedback for an assessment"""
    try:
        db = get_session()
        
        # Get assessment
        assessment = db.query(Assessment).filter(Assessment.id == assessment_id).first()
        if not assessment:
            raise HTTPException(status_code=404, detail="Assessment not found")
        
        # Get existing recommendations
        recommendations = db.query(LLMRecommendation).filter(
            LLMRecommendation.assessment_id == assessment_id
        ).all()
        
        # Get bias monitoring data
        bias_monitoring = db.query(BiasMonitoring).filter(
            BiasMonitoring.assessment_id == assessment_id
        ).first()
        
        db.close()
        
        summary = {
            "assessment_id": assessment_id,
            "assessment_status": assessment.status,
            "overall_score": assessment.overall_score,
            "risk_level": assessment.risk_level,
            "recommendations_count": len(recommendations),
            "recommendations_by_difficulty": {
                "Easy": len([r for r in recommendations if r.implementation_difficulty == "Easy"]),
                "Medium": len([r for r in recommendations if r.implementation_difficulty == "Medium"]),
                "Hard": len([r for r in recommendations if r.implementation_difficulty == "Hard"])
            },
            "average_confidence": sum(r.confidence_score for r in recommendations) / len(recommendations) if recommendations else 0,
            "bias_monitoring_active": bias_monitoring is not None,
            "last_updated": max(r.generation_timestamp for r in recommendations).isoformat() if recommendations else None
        }
        
        return summary
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting feedback summary: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get summary: {str(e)}")

@router.post("/feedback/quality/rate", tags=["AI Feedback"])
def rate_feedback_quality(request: FeedbackQualityRequest):
    """Rate the quality of a recommendation"""
    try:
        db = get_session()
        
        # Find the recommendation
        recommendation = db.query(LLMRecommendation).filter(
            LLMRecommendation.id == request.recommendation_id
        ).first()
        
        if not recommendation:
            raise HTTPException(status_code=404, detail="Recommendation not found")
        
        # Update recommendation with user feedback
        recommendation.user_rating = request.user_rating
        recommendation.user_feedback = request.feedback_text
        recommendation.implementation_status = request.implementation_status
        recommendation.feedback_timestamp = datetime.utcnow()
        
        db.commit()
        db.close()
        
        return {
            "message": "Feedback recorded successfully",
            "recommendation_id": request.recommendation_id,
            "rating": request.user_rating,
            "status": request.implementation_status
        }
        
    except HTTPException:
        raise
    except Exception as e:
        db.rollback()
        db.close()
        logger.error(f"Error rating feedback quality: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to rate feedback: {str(e)}")

@router.post("/feedback/bulk", tags=["AI Feedback"])
async def generate_bulk_feedback(request: BulkFeedbackRequest):
    """Generate feedback for multiple assessments"""
    try:
        results = []
        
        for assessment_id in request.assessment_ids:
            try:
                # Generate comprehensive feedback for each assessment
                feedback_request = ComprehensiveFeedbackRequest(
                    assessment_id=assessment_id,
                    include_source_attribution=True,
                    include_bias_analysis=True,
                    include_confidence_metrics=True
                )
                
                feedback_result = await generate_comprehensive_feedback(feedback_request)
                
                results.append({
                    "assessment_id": assessment_id,
                    "status": "success",
                    "recommendations_count": len(feedback_result.recommendations),
                    "quality_score": feedback_result.quality_metrics.get("average_confidence", 0),
                    "review_required": feedback_result.quality_metrics.get("review_required_count", 0) > 0
                })
                
            except Exception as e:
                results.append({
                    "assessment_id": assessment_id,
                    "status": "error",
                    "error_message": str(e)
                })
        
        # Generate comparison if requested
        comparison_data = None
        if request.include_comparisons and len(results) > 1:
            successful_results = [r for r in results if r["status"] == "success"]
            if len(successful_results) > 1:
                comparison_data = {
                    "average_recommendations": sum(r["recommendations_count"] for r in successful_results) / len(successful_results),
                    "average_quality": sum(r["quality_score"] for r in successful_results) / len(successful_results),
                    "high_quality_assessments": len([r for r in successful_results if r["quality_score"] > 0.8]),
                    "assessments_needing_review": len([r for r in successful_results if r["review_required"]])
                }
        
        return {
            "total_assessments": len(request.assessment_ids),
            "successful": len([r for r in results if r["status"] == "success"]),
            "failed": len([r for r in results if r["status"] == "error"]),
            "results": results,
            "comparison": comparison_data
        }
        
    except Exception as e:
        logger.error(f"Error generating bulk feedback: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate bulk feedback: {str(e)}")

@router.get("/feedback/analytics", tags=["AI Feedback"])
def get_feedback_analytics():
    """Get analytics about feedback system performance"""
    try:
        db = get_session()
        
        # Get recommendation statistics
        total_recommendations = db.query(LLMRecommendation).count() if hasattr(db.query(LLMRecommendation), 'count') else 0
        
        if total_recommendations > 0:
            recommendations = db.query(LLMRecommendation).all()
            
            # Calculate analytics
            avg_confidence = sum(r.confidence_score for r in recommendations if r.confidence_score) / len([r for r in recommendations if r.confidence_score])
            
            difficulty_distribution = {}
            for r in recommendations:
                diff = r.implementation_difficulty or "Unknown"
                difficulty_distribution[diff] = difficulty_distribution.get(diff, 0) + 1
            
            impact_distribution = {}
            for r in recommendations:
                impact = r.expected_impact or "Unknown"
                impact_distribution[impact] = impact_distribution.get(impact, 0) + 1
            
            # User ratings if available
            rated_recommendations = [r for r in recommendations if hasattr(r, 'user_rating') and r.user_rating]
            avg_user_rating = sum(r.user_rating for r in rated_recommendations) / len(rated_recommendations) if rated_recommendations else 0
        else:
            avg_confidence = 0
            difficulty_distribution = {}
            impact_distribution = {}
            avg_user_rating = 0
        
        # Get bias monitoring statistics
        total_bias_monitoring = db.query(BiasMonitoring).count() if hasattr(db.query(BiasMonitoring), 'count') else 0
        
        db.close()
        
        analytics = {
            "recommendation_statistics": {
                "total_recommendations": total_recommendations,
                "average_confidence": avg_confidence,
                "difficulty_distribution": difficulty_distribution,
                "impact_distribution": impact_distribution,
                "average_user_rating": avg_user_rating
            },
            "bias_monitoring": {
                "total_monitoring_sessions": total_bias_monitoring,
                "bias_detection_enabled": True
            },
            "source_attribution": {
                "frameworks_supported": len(source_attributor.framework_mappings),
                "attribution_enabled": True
            },
            "system_health": {
                "ai_engine_status": "operational",
                "bias_detector_status": "operational",
                "source_attributor_status": "operational"
            }
        }
        
        return analytics
        
    except Exception as e:
        logger.error(f"Error getting feedback analytics: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get analytics: {str(e)}")

@router.post("/feedback/export/{assessment_id}", tags=["AI Feedback"])
def export_feedback_report(assessment_id: int, format: str = Query("json", regex="^(json|pdf|csv)$")):
    """Export comprehensive feedback report in various formats"""
    try:
        db = get_session()
        
        # Get assessment and recommendations
        assessment = db.query(Assessment).filter(Assessment.id == assessment_id).first()
        if not assessment:
            raise HTTPException(status_code=404, detail="Assessment not found")
        
        recommendations = db.query(LLMRecommendation).filter(
            LLMRecommendation.assessment_id == assessment_id
        ).all()
        
        # Get source attributions
        sources = []
        for rec in recommendations:
            rec_sources = db.query(RecommendationSource).filter(
                RecommendationSource.recommendation_id == rec.id
            ).all()
            sources.extend(rec_sources)
        
        db.close()
        
        # Prepare export data
        export_data = {
            "assessment_info": {
                "id": assessment.id,
                "status": assessment.status,
                "overall_score": assessment.overall_score,
                "risk_level": assessment.risk_level,
                "created_at": assessment.created_at.isoformat(),
                "completed_at": assessment.completed_at.isoformat() if assessment.completed_at else None
            },
            "recommendations": [
                {
                    "id": rec.id,
                    "text": rec.recommendation_text,
                    "confidence": rec.confidence_score,
                    "difficulty": rec.implementation_difficulty,
                    "impact": rec.expected_impact,
                    "frameworks": rec.frameworks_referenced,
                    "generated_at": rec.generation_timestamp.isoformat()
                } for rec in recommendations
            ],
            "source_attributions": [
                {
                    "recommendation_id": src.recommendation_id,
                    "source_type": src.source_type,
                    "reference": src.reference,
                    "relevance_score": src.relevance_score
                } for src in sources
            ],
            "export_metadata": {
                "format": format,
                "generated_at": datetime.utcnow().isoformat(),
                "total_recommendations": len(recommendations),
                "total_sources": len(sources)
            }
        }
        
        if format == "json":
            return export_data
        elif format == "csv":
            # Convert to CSV format (simplified)
            csv_data = "ID,Text,Confidence,Difficulty,Impact,Generated At\n"
            for rec in export_data["recommendations"]:
                csv_data += f"{rec['id']},\"{rec['text']}\",{rec['confidence']},{rec['difficulty']},{rec['impact']},{rec['generated_at']}\n"
            
            return {"csv_data": csv_data}
        elif format == "pdf":
            # PDF generation would require additional libraries
            return {
                "message": "PDF export not yet implemented",
                "alternative": "Use JSON format and convert externally"
            }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error exporting feedback report: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to export report: {str(e)}")