#!/usr/bin/env python3
"""
Comprehensive Scoring API
Provides REST API access to all scoring functionality including weights, formulas, and methodology
"""

from fastapi import APIRouter, HTTPException, Query, Depends
from pydantic import BaseModel
from typing import Dict, List, Optional, Any
import logging
import time
from datetime import datetime

from scoring.scoring_engine import ScoringEngine, SECTION_WEIGHTS, RISK_LEVELS, QUESTION_WEIGHTS
from assessment.risk_categorization import RiskCategorizationEngine
from database.models import (
    get_session, Assessment, ScoringAuditLog, ScoringWeights, ScoringMethodology,
    AssessmentResult, IndustryBenchmarks
)

logger = logging.getLogger(__name__)
router = APIRouter()

# Pydantic Models
class ScoringRequest(BaseModel):
    assessment_id: int
    methodology: Optional[str] = "default"
    include_confidence: bool = True
    include_benchmarking: bool = False
    industry: Optional[str] = None
    company_size: Optional[str] = None

class QuestionScoringRequest(BaseModel):
    question_id: str
    question_type: str
    answer: Any
    question_options: Optional[List[str]] = None
    min_value: Optional[int] = None
    max_value: Optional[int] = None

class SectionScoringRequest(BaseModel):
    section_id: str
    responses: Dict[str, Any]
    questions_metadata: Optional[Dict[str, Any]] = None

class WeightUpdateRequest(BaseModel):
    weight_type: str  # section, question, category
    identifier: str  # section_id, question_id, etc.
    weight_value: float
    max_score: float
    description: Optional[str] = None

class MethodologyRequest(BaseModel):
    methodology_name: str
    description: str
    mathematical_formula: str
    implementation_notes: Optional[str] = None
    parameters: Optional[Dict[str, Any]] = None
    thresholds: Optional[Dict[str, Any]] = None

# --- Scoring Endpoints ---

@router.post("/scoring/calculate", tags=["Scoring"])
def calculate_assessment_score(request: ScoringRequest):
    """Calculate comprehensive assessment score with optional benchmarking"""
    start_time = time.time()
    
    try:
        # Get database session
        db = get_session()
        
        # Validate assessment exists
        assessment = db.query(Assessment).filter(Assessment.id == request.assessment_id).first()
        if not assessment:
            raise HTTPException(status_code=404, detail=f"Assessment {request.assessment_id} not found")
        
        # Calculate scores using scoring engine
        overall_result = ScoringEngine.score_assessment(request.assessment_id)
        
        # Add risk categorization if requested
        risk_assessment = None
        if request.include_confidence or request.include_benchmarking:
            risk_assessment = RiskCategorizationEngine.categorize_risk(
                score=overall_result.percentage,
                industry=request.industry if request.include_benchmarking else None,
                company_size=request.company_size if request.include_benchmarking else None
            )
        
        # Get historical scores for trend analysis
        historical_scores = []
        if request.include_confidence:
            historical_assessments = db.query(Assessment).filter(
                Assessment.company_id == assessment.company_id,
                Assessment.id < request.assessment_id,
                Assessment.overall_score.isnot(None)
            ).order_by(Assessment.created_at).all()
            
            historical_scores = [a.overall_score for a in historical_assessments if a.overall_score > 0]
        
        # Calculate completion rate
        total_questions = sum(s.total_questions for s in overall_result.section_breakdown)
        answered_questions = sum(s.questions_answered for s in overall_result.section_breakdown)
        completion_rate = answered_questions / total_questions if total_questions > 0 else 0
        
        # Perform risk categorization
        risk_assessment = RiskCategorizationEngine.categorize_risk(
            score=overall_result.percentage,
            industry=request.industry,
            company_size=request.company_size
        ) if request.include_benchmarking else None
        
        # Log operation
        execution_time = int((time.time() - start_time) * 1000)
        audit_log = ScoringAuditLog(
            operation_type="calculate",
            assessment_id=request.assessment_id,
            input_data=request.dict(),
            methodology_used=request.methodology,
            output_data={"overall_score": overall_result.percentage},
            execution_time_ms=execution_time,
            status="success"
        )
        db.add(audit_log)
        db.commit()
        db.close()
        
        # Prepare response
        response = {
            "assessment_id": request.assessment_id,
            "overall_score": overall_result.percentage,
            "risk_level": overall_result.risk_level,
            "risk_color": overall_result.risk_color,
            "execution_time_ms": execution_time,
            "methodology_used": request.methodology,
            "section_breakdown": [
                {
                    "section_id": s.section_id,
                    "section_name": s.section_name,
                    "score": s.percentage,
                    "risk_level": s.risk_level,
                    "weight": s.weight,
                    "questions_answered": s.questions_answered,
                    "total_questions": s.total_questions
                } for s in overall_result.section_breakdown
            ]
        }
        
        # Add risk categorization if available
        if risk_assessment:
            response["risk_categorization"] = {
                "confidence_interval": {
                    "lower_bound": risk_assessment.confidence_interval.lower_bound,
                    "upper_bound": risk_assessment.confidence_interval.upper_bound,
                    "confidence_level": risk_assessment.confidence_interval.confidence_level
                },
                "statistical_significance": risk_assessment.statistical_significance,
                "margin_of_error": risk_assessment.confidence_interval.margin_of_error,
                "industry": request.industry,
                "company_size": request.company_size,
                "industry_percentile": risk_assessment.industry_percentile if risk_assessment else None,
                "performance_vs_peers": risk_assessment.benchmark_comparison.performance_vs_peers if risk_assessment and risk_assessment.benchmark_comparison else None,
                "trend_analysis": risk_assessment.trend_analysis if risk_assessment else None,
                "recommendations": risk_assessment.recommendations
            }
        
        return response
        
    except Exception as e:
        logger.error(f"Error calculating assessment score: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to calculate assessment score: {str(e)}")

@router.post("/scoring/question", tags=["Scoring"])
def score_individual_question(request: QuestionScoringRequest):
    """Score an individual question using mathematical rules"""
    try:
        question_score = ScoringEngine.score_question(
            question_id=request.question_id,
            question_type=request.question_type,
            answer=request.answer,
            question_options=request.question_options,
            min_value=request.min_value,
            max_value=request.max_value
        )
        
        return {
            "question_id": question_score.question_id,
            "raw_score": question_score.raw_score,
            "weighted_score": question_score.weighted_score,
            "max_score": question_score.max_score,
            "percentage": question_score.percentage
        }
        
    except Exception as e:
        logger.error(f"Error scoring question {request.question_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to score question: {str(e)}")

@router.post("/scoring/section", tags=["Scoring"])
def score_section(request: SectionScoringRequest):
    """Score a complete section"""
    try:
        # Convert responses to question scores
        question_scores = []
        for question_id, answer in request.responses.items():
            # Get question metadata if available
            question_metadata = request.questions_metadata.get(question_id, {}) if request.questions_metadata else {}
            
            question_score = ScoringEngine.score_question(
                question_id=question_id,
                question_type=question_metadata.get('type', 'text'),
                answer=answer,
                question_options=question_metadata.get('options'),
                min_value=question_metadata.get('min_value'),
                max_value=question_metadata.get('max_value')
            )
            question_scores.append(question_score)
        
        # Calculate section score
        section_result = ScoringEngine.calculate_section_score(request.section_id, question_scores)
        
        return {
            "section_id": section_result.section_id,
            "section_name": section_result.section_name,
            "raw_score": section_result.raw_score,
            "max_score": section_result.max_score,
            "percentage": section_result.percentage,
            "weight": section_result.weight,
            "risk_level": section_result.risk_level,
            "questions_answered": section_result.questions_answered,
            "total_questions": section_result.total_questions,
            "question_scores": [
                {
                    "question_id": qs.question_id,
                    "raw_score": qs.raw_score,
                    "percentage": qs.percentage
                } for qs in section_result.question_scores
            ]
        }
        
    except Exception as e:
        logger.error(f"Error scoring section {request.section_id}: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to score section: {str(e)}")

# --- Formula and Methodology Endpoints ---

@router.get("/scoring/formula", tags=["Scoring"])
def get_scoring_formula():
    """Get detailed scoring methodology and formulas"""
    return {
        "methodology": {
            "name": "RiskAI Mathematical Scoring System",
            "version": "1.0",
            "description": "Comprehensive risk assessment scoring using weighted mathematical formulas"
        },
        "formulas": {
            "section_score": "Section Score = Σ(Question Score × Question Weight) / Σ(Question Weights) × 100",
            "overall_score": "Overall Score = Σ(Section Score × Section Weight)",
            "confidence_interval": "CI = Score ± (1 - Completion Rate) × 10%"
        },
        "section_weights": SECTION_WEIGHTS,
        "risk_levels": {
            level: {
                "range": f"{data['min']}-{data['max']}",
                "label": data['label'],
                "color": data['color']
            } for level, data in RISK_LEVELS.items()
        },
        "weight_distribution": {
            "governance": "20% - Strategic foundation and risk management",
            "technical_controls": "40% - Asset management, data protection, access control, monitoring",
            "operational": "25% - Incident response, business continuity, awareness",
            "compliance": "15% - Regulatory compliance, emerging tech, third-party risk"
        }
    }

@router.get("/scoring/weights", tags=["Scoring"])
def get_scoring_weights():
    """Get current question and section weights"""
    db = get_session()
    try:
        # Get custom weights from database
        custom_weights = db.query(ScoringWeights).all()
        
        weights_data = {
            "section_weights": SECTION_WEIGHTS,
            "default_question_weights": QUESTION_WEIGHTS,
            "custom_weights": [
                {
                    "weight_type": w.weight_type,
                    "identifier": w.identifier,
                    "weight_value": w.weight_value,
                    "max_score": w.max_score,
                    "description": w.description,
                    "version": w.version
                } for w in custom_weights
            ]
        }
        
        return weights_data
        
    except Exception as e:
        logger.error(f"Error getting scoring weights: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get weights: {str(e)}")
    finally:
        db.close()

@router.post("/scoring/weights", tags=["Scoring"])
def update_scoring_weight(request: WeightUpdateRequest):
    """Update or create a scoring weight"""
    db = get_session()
    try:
        # Check if weight already exists
        existing_weight = db.query(ScoringWeights).filter(
            ScoringWeights.weight_type == request.weight_type,
            ScoringWeights.identifier == request.identifier
        ).first()
        
        if existing_weight:
            existing_weight.weight_value = request.weight_value
            existing_weight.max_score = request.max_score
            existing_weight.description = request.description
            existing_weight.updated_at = datetime.utcnow()
        else:
            new_weight = ScoringWeights(
                weight_type=request.weight_type,
                identifier=request.identifier,
                weight_value=request.weight_value,
                max_score=request.max_score,
                description=request.description
            )
            db.add(new_weight)
        
        db.commit()
        
        return {
            "message": "Weight updated successfully",
            "weight_type": request.weight_type,
            "identifier": request.identifier,
            "weight_value": request.weight_value
        }
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error updating scoring weight: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to update weight: {str(e)}")
    finally:
        db.close()

@router.get("/scoring/benchmarks/{industry}", tags=["Scoring"])
def get_industry_benchmarks(industry: str, company_size: Optional[str] = None):
    """Get industry-specific benchmarks"""
    db = get_session()
    try:
        query = db.query(IndustryBenchmarks).filter(IndustryBenchmarks.industry == industry)
        
        if company_size:
            query = query.filter(IndustryBenchmarks.company_size == company_size)
        
        benchmarks = query.all()
        
        if not benchmarks:
            return {
                "industry": industry,
                "company_size": company_size,
                "message": "No benchmark data available for this industry/size combination",
                "benchmarks": []
            }
        
        return {
            "industry": industry,
            "company_size": company_size,
            "benchmarks": [
                {
                    "average_score": b.average_score,
                    "standard_deviation": b.standard_deviation,
                    "sample_size": b.sample_size,
                    "percentiles": {
                        "10th": b.percentile_10,
                        "25th": b.percentile_25,
                        "50th": b.percentile_50,
                        "75th": b.percentile_75,
                        "90th": b.percentile_90
                    },
                    "data_source": b.data_source,
                    "data_date": b.data_date.isoformat(),
                    "data_quality_score": b.data_quality_score
                } for b in benchmarks
            ]
        }
        
    except Exception as e:
        logger.error(f"Error getting industry benchmarks: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get benchmarks: {str(e)}")
    finally:
        db.close()

@router.post("/scoring/methodology", tags=["Scoring"])
def create_scoring_methodology(request: MethodologyRequest):
    """Create or update a scoring methodology"""
    db = get_session()
    try:
        # Check if methodology already exists
        existing_methodology = db.query(ScoringMethodology).filter(
            ScoringMethodology.methodology_name == request.methodology_name
        ).first()
        
        if existing_methodology:
            existing_methodology.description = request.description
            existing_methodology.mathematical_formula = request.mathematical_formula
            existing_methodology.implementation_notes = request.implementation_notes
            existing_methodology.parameters = request.parameters
            existing_methodology.thresholds = request.thresholds
            existing_methodology.updated_at = datetime.utcnow()
        else:
            new_methodology = ScoringMethodology(
                methodology_name=request.methodology_name,
                description=request.description,
                mathematical_formula=request.mathematical_formula,
                implementation_notes=request.implementation_notes,
                parameters=request.parameters,
                thresholds=request.thresholds
            )
            db.add(new_methodology)
        
        db.commit()
        
        return {
            "message": "Methodology saved successfully",
            "methodology_name": request.methodology_name
        }
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error saving methodology: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to save methodology: {str(e)}")
    finally:
        db.close()

@router.get("/scoring/methodology/{methodology_name}", tags=["Scoring"])
def get_scoring_methodology(methodology_name: str):
    """Get a specific scoring methodology"""
    db = get_session()
    try:
        methodology = db.query(ScoringMethodology).filter(
            ScoringMethodology.methodology_name == methodology_name
        ).first()
        
        if not methodology:
            raise HTTPException(status_code=404, detail=f"Methodology '{methodology_name}' not found")
        
        return {
            "methodology_name": methodology.methodology_name,
            "version": methodology.version,
            "description": methodology.description,
            "mathematical_formula": methodology.mathematical_formula,
            "implementation_notes": methodology.implementation_notes,
            "parameters": methodology.parameters,
            "thresholds": methodology.thresholds,
            "created_at": methodology.created_at.isoformat(),
            "updated_at": methodology.updated_at.isoformat()
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting methodology: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get methodology: {str(e)}")
    finally:
        db.close()

@router.get("/scoring/audit/{assessment_id}", tags=["Scoring"])
def get_scoring_audit_log(assessment_id: int):
    """Get audit log for scoring operations on an assessment"""
    db = get_session()
    try:
        audit_logs = db.query(ScoringAuditLog).filter(
            ScoringAuditLog.assessment_id == assessment_id
        ).order_by(ScoringAuditLog.created_at.desc()).all()
        
        return {
            "assessment_id": assessment_id,
            "audit_logs": [
                {
                    "operation_type": log.operation_type,
                    "methodology_used": log.methodology_used,
                    "execution_time_ms": log.execution_time_ms,
                    "status": log.status,
                    "error_message": log.error_message,
                    "created_at": log.created_at.isoformat()
                } for log in audit_logs
            ]
        }
        
    except Exception as e:
        logger.error(f"Error getting audit log: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get audit log: {str(e)}")
    finally:
        db.close()

@router.post("/scoring/export", tags=["Scoring"])
def export_scoring_report(assessment_id: int, include_details: bool = True):
    """Generate detailed scoring report for export"""
    try:
        db = get_session()
        
        # Get assessment
        assessment = db.query(Assessment).filter(Assessment.id == assessment_id).first()
        if not assessment:
            raise HTTPException(status_code=404, detail=f"Assessment {assessment_id} not found")
        
        # Calculate scores
        overall_result = ScoringEngine.score_assessment(assessment_id)
        
        # Build export data
        export_data = {
            "assessment_info": {
                "id": assessment.id,
                "name": assessment.name,
                "description": assessment.description,
                "created_at": assessment.created_at.isoformat(),
                "completed_at": assessment.completed_at.isoformat() if assessment.completed_at else None
            },
            "scoring_summary": {
                "overall_score": overall_result.percentage,
                "risk_level": overall_result.risk_level,
                "risk_color": overall_result.risk_color,
                "confidence_interval": {
                    "lower": overall_result.confidence_interval[0],
                    "upper": overall_result.confidence_interval[1]
                }
            },
            "methodology": {
                "formulas": {
                    "section_score": "Section Score = Σ(Question Score × Question Weight) / Σ(Question Weights) × 100",
                    "overall_score": "Overall Score = Σ(Section Score × Section Weight)"
                },
                "section_weights": SECTION_WEIGHTS,
                "risk_thresholds": RISK_LEVELS
            }
        }
        
        if include_details:
            export_data["section_breakdown"] = [
                {
                    "section_id": s.section_id,
                    "section_name": s.section_name,
                    "score": s.percentage,
                    "risk_level": s.risk_level,
                    "weight": s.weight,
                    "questions_answered": s.questions_answered,
                    "total_questions": s.total_questions,
                    "question_scores": [
                        {
                            "question_id": qs.question_id,
                            "raw_score": qs.raw_score,
                            "percentage": qs.percentage
                        } for qs in s.question_scores
                    ]
                } for s in overall_result.section_breakdown
            ]
        
        db.close()
        return export_data
        
    except Exception as e:
        logger.error(f"Error exporting scoring report: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to export report: {str(e)}")