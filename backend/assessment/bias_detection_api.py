#!/usr/bin/env python3
"""
Bias Detection API
REST API endpoints for AI bias detection and mitigation functionality
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Dict, List, Optional, Any
import logging
from datetime import datetime

from assessment.bias_detection import bias_detector, BiasAnalysisResult, BiasDetection, FairnessMetrics, BiasType, SeverityLevel
from database.models import get_session, BiasMonitoring, BiasMetric

logger = logging.getLogger(__name__)
router = APIRouter()

# Pydantic Models
class BiasAnalysisRequest(BaseModel):
    recommendation_text: str
    context: Optional[Dict[str, Any]] = None
    historical_data: Optional[List[Dict[str, Any]]] = None

class BiasDetectionResponse(BaseModel):
    bias_type: str
    severity: str
    confidence: float
    description: str
    evidence: List[str]
    affected_groups: List[str]
    mitigation_suggestions: List[str]

class FairnessMetricsResponse(BaseModel):
    demographic_parity: float
    equalized_odds: float
    calibration: float
    individual_fairness: float
    group_fairness: float
    overall_fairness_score: float

class BiasAnalysisResponse(BaseModel):
    recommendation_id: str
    overall_bias_score: float
    detected_biases: List[BiasDetectionResponse]
    fairness_metrics: FairnessMetricsResponse
    transparency_score: float
    mitigation_actions: List[Dict[str, Any]]
    review_required: bool
    timestamp: str

class BulkBiasAnalysisRequest(BaseModel):
    recommendations: List[Dict[str, Any]]  # List of {text, context}

class BiasMonitoringRequest(BaseModel):
    assessment_id: int
    recommendation_ids: List[str]
    monitoring_period_days: Optional[int] = 30

# --- Bias Detection Endpoints ---

@router.post("/bias/analyze", tags=["Bias Detection"])
def analyze_recommendation_bias(request: BiasAnalysisRequest):
    """Analyze a single recommendation for bias and fairness issues"""
    try:
        # Perform bias analysis
        analysis_result = bias_detector.analyze_bias(
            recommendation_text=request.recommendation_text,
            context=request.context,
            historical_data=request.historical_data
        )
        
        # Convert to response format
        response = BiasAnalysisResponse(
            recommendation_id=analysis_result.recommendation_id,
            overall_bias_score=analysis_result.overall_bias_score,
            detected_biases=[
                BiasDetectionResponse(
                    bias_type=bias.bias_type.value,
                    severity=bias.severity.value,
                    confidence=bias.confidence,
                    description=bias.description,
                    evidence=bias.evidence,
                    affected_groups=bias.affected_groups,
                    mitigation_suggestions=bias.mitigation_suggestions
                ) for bias in analysis_result.detected_biases
            ],
            fairness_metrics=FairnessMetricsResponse(
                demographic_parity=analysis_result.fairness_metrics.demographic_parity,
                equalized_odds=analysis_result.fairness_metrics.equalized_odds,
                calibration=analysis_result.fairness_metrics.calibration,
                individual_fairness=analysis_result.fairness_metrics.individual_fairness,
                group_fairness=analysis_result.fairness_metrics.group_fairness,
                overall_fairness_score=analysis_result.fairness_metrics.overall_fairness_score
            ),
            transparency_score=analysis_result.transparency_score,
            mitigation_actions=analysis_result.mitigation_actions,
            review_required=analysis_result.review_required,
            timestamp=analysis_result.timestamp.isoformat()
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Error analyzing recommendation bias: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to analyze bias: {str(e)}")

@router.post("/bias/bulk-analyze", tags=["Bias Detection"])
def bulk_analyze_bias(request: BulkBiasAnalysisRequest):
    """Analyze multiple recommendations for bias"""
    try:
        results = []
        summary_stats = {
            "total_recommendations": len(request.recommendations),
            "high_bias_count": 0,
            "medium_bias_count": 0,
            "low_bias_count": 0,
            "review_required_count": 0,
            "common_bias_types": {},
            "average_fairness_score": 0.0
        }
        
        fairness_scores = []
        
        for rec_data in request.recommendations:
            analysis_result = bias_detector.analyze_bias(
                recommendation_text=rec_data.get('text', ''),
                context=rec_data.get('context'),
                historical_data=rec_data.get('historical_data')
            )
            
            # Categorize bias level
            if analysis_result.overall_bias_score > 0.7:
                summary_stats["high_bias_count"] += 1
            elif analysis_result.overall_bias_score > 0.4:
                summary_stats["medium_bias_count"] += 1
            else:
                summary_stats["low_bias_count"] += 1
            
            if analysis_result.review_required:
                summary_stats["review_required_count"] += 1
            
            # Track common bias types
            for bias in analysis_result.detected_biases:
                bias_type = bias.bias_type.value
                if bias_type not in summary_stats["common_bias_types"]:
                    summary_stats["common_bias_types"][bias_type] = 0
                summary_stats["common_bias_types"][bias_type] += 1
            
            fairness_scores.append(analysis_result.fairness_metrics.overall_fairness_score)
            
            results.append({
                "recommendation_text": rec_data.get('text', ''),
                "bias_analysis": {
                    "recommendation_id": analysis_result.recommendation_id,
                    "overall_bias_score": analysis_result.overall_bias_score,
                    "bias_count": len(analysis_result.detected_biases),
                    "fairness_score": analysis_result.fairness_metrics.overall_fairness_score,
                    "transparency_score": analysis_result.transparency_score,
                    "review_required": analysis_result.review_required
                }
            })
        
        # Calculate average fairness score
        if fairness_scores:
            summary_stats["average_fairness_score"] = sum(fairness_scores) / len(fairness_scores)
        
        return {
            "results": results,
            "summary": summary_stats
        }
        
    except Exception as e:
        logger.error(f"Error in bulk bias analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to analyze bulk bias: {str(e)}")

@router.get("/bias/patterns", tags=["Bias Detection"])
def get_bias_patterns():
    """Get information about bias detection patterns"""
    try:
        patterns_info = {}
        
        for bias_type, patterns in bias_detector.bias_patterns.items():
            patterns_info[bias_type.value] = {
                "description": f"Patterns for detecting {bias_type.value} bias",
                "pattern_count": len(patterns),
                "severity_levels": list(set(p["severity"].value for p in patterns))
            }
        
        return {
            "bias_types": patterns_info,
            "demographic_categories": list(bias_detector.demographic_terms.keys()),
            "fairness_thresholds": bias_detector.fairness_thresholds
        }
        
    except Exception as e:
        logger.error(f"Error getting bias patterns: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get patterns: {str(e)}")

@router.get("/bias/metrics/fairness", tags=["Bias Detection"])
def get_fairness_metrics_info():
    """Get information about fairness metrics"""
    try:
        metrics_info = {
            "demographic_parity": {
                "description": "Equal recommendation rates across demographic groups",
                "threshold": bias_detector.fairness_thresholds["demographic_parity"],
                "interpretation": "Higher values indicate less demographic bias"
            },
            "equalized_odds": {
                "description": "Equal true positive rates across groups",
                "threshold": bias_detector.fairness_thresholds["equalized_odds"],
                "interpretation": "Measures fairness in prediction accuracy"
            },
            "calibration": {
                "description": "Equal prediction accuracy across groups",
                "threshold": bias_detector.fairness_thresholds["calibration"],
                "interpretation": "Higher values indicate better calibration"
            },
            "individual_fairness": {
                "description": "Similar individuals receive similar recommendations",
                "threshold": bias_detector.fairness_thresholds["individual_fairness"],
                "interpretation": "Measures consistency in individual treatment"
            },
            "group_fairness": {
                "description": "Fair treatment of different groups",
                "threshold": bias_detector.fairness_thresholds["group_fairness"],
                "interpretation": "Higher values indicate better group fairness"
            }
        }
        
        return {
            "fairness_metrics": metrics_info,
            "overall_threshold": bias_detector.fairness_thresholds["overall_fairness"],
            "scoring_range": "0.0 (unfair) to 1.0 (completely fair)"
        }
        
    except Exception as e:
        logger.error(f"Error getting fairness metrics info: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get metrics info: {str(e)}")

@router.post("/bias/mitigation/suggest", tags=["Bias Detection"])
def suggest_bias_mitigation(
    recommendation_text: str,
    detected_biases: List[Dict[str, Any]]
):
    """Get specific mitigation suggestions for detected biases"""
    try:
        mitigation_suggestions = []
        
        for bias_data in detected_biases:
            bias_type_str = bias_data.get("bias_type", "")
            
            # Find matching bias type
            bias_type = None
            for bt in BiasType:
                if bt.value == bias_type_str:
                    bias_type = bt
                    break
            
            if bias_type:
                suggestions = bias_detector._generate_bias_mitigation(
                    bias_type, 
                    bias_data.get("evidence", [])
                )
                
                mitigation_suggestions.append({
                    "bias_type": bias_type_str,
                    "severity": bias_data.get("severity", "medium"),
                    "suggestions": suggestions,
                    "priority": bias_data.get("severity", "medium")
                })
        
        # Generate general mitigation strategies
        general_strategies = [
            "Use inclusive language that doesn't assume characteristics about users",
            "Provide multiple implementation approaches for different contexts",
            "Include disclaimers about the general nature of recommendations",
            "Encourage users to adapt recommendations to their specific situation",
            "Regularly review and update recommendations based on feedback"
        ]
        
        return {
            "specific_mitigations": mitigation_suggestions,
            "general_strategies": general_strategies,
            "implementation_tips": [
                "Test recommendations with diverse user groups",
                "Implement feedback mechanisms for bias reporting",
                "Regular bias audits of recommendation systems",
                "Training for content reviewers on bias detection"
            ]
        }
        
    except Exception as e:
        logger.error(f"Error suggesting bias mitigation: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to suggest mitigation: {str(e)}")

@router.post("/bias/monitoring/setup", tags=["Bias Detection"])
def setup_bias_monitoring(request: BiasMonitoringRequest):
    """Set up continuous bias monitoring for an assessment"""
    try:
        db = get_session()
        
        # Create bias monitoring record
        monitoring_record = BiasMonitoring(
            assessment_id=request.assessment_id,
            monitoring_start_date=datetime.utcnow(),
            monitoring_period_days=request.monitoring_period_days,
            recommendation_ids=request.recommendation_ids,
            status="active"
        )
        
        db.add(monitoring_record)
        db.commit()
        
        monitoring_id = monitoring_record.id
        db.close()
        
        return {
            "monitoring_id": monitoring_id,
            "message": "Bias monitoring setup successfully",
            "assessment_id": request.assessment_id,
            "recommendations_monitored": len(request.recommendation_ids),
            "monitoring_period_days": request.monitoring_period_days
        }
        
    except Exception as e:
        db.rollback()
        db.close()
        logger.error(f"Error setting up bias monitoring: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to setup monitoring: {str(e)}")

@router.get("/bias/monitoring/{monitoring_id}/status", tags=["Bias Detection"])
def get_monitoring_status(monitoring_id: int):
    """Get status of bias monitoring"""
    try:
        db = get_session()
        
        monitoring_record = db.query(BiasMonitoring).filter(
            BiasMonitoring.id == monitoring_id
        ).first()
        
        if not monitoring_record:
            raise HTTPException(status_code=404, detail="Monitoring record not found")
        
        # Get associated bias metrics
        bias_metrics = db.query(BiasMetric).filter(
            BiasMetric.monitoring_id == monitoring_id
        ).all()
        
        db.close()
        
        return {
            "monitoring_id": monitoring_id,
            "assessment_id": monitoring_record.assessment_id,
            "status": monitoring_record.status,
            "start_date": monitoring_record.monitoring_start_date.isoformat(),
            "period_days": monitoring_record.monitoring_period_days,
            "recommendations_monitored": len(monitoring_record.recommendation_ids),
            "metrics_collected": len(bias_metrics),
            "last_updated": monitoring_record.last_updated.isoformat() if monitoring_record.last_updated else None
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting monitoring status: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get status: {str(e)}")

@router.get("/bias/report/{assessment_id}", tags=["Bias Detection"])
def generate_bias_report(assessment_id: int):
    """Generate comprehensive bias report for an assessment"""
    try:
        db = get_session()
        
        # Get bias monitoring records
        monitoring_records = db.query(BiasMonitoring).filter(
            BiasMonitoring.assessment_id == assessment_id
        ).all()
        
        if not monitoring_records:
            return {
                "assessment_id": assessment_id,
                "message": "No bias monitoring data found for this assessment",
                "report": None
            }
        
        # Aggregate bias metrics
        all_metrics = []
        for record in monitoring_records:
            metrics = db.query(BiasMetric).filter(
                BiasMetric.monitoring_id == record.id
            ).all()
            all_metrics.extend(metrics)
        
        db.close()
        
        # Generate report summary
        report = {
            "assessment_id": assessment_id,
            "monitoring_periods": len(monitoring_records),
            "total_metrics": len(all_metrics),
            "bias_summary": {
                "high_bias_incidents": len([m for m in all_metrics if m.bias_score > 0.7]),
                "medium_bias_incidents": len([m for m in all_metrics if 0.4 <= m.bias_score <= 0.7]),
                "low_bias_incidents": len([m for m in all_metrics if m.bias_score < 0.4])
            },
            "fairness_trends": {
                "average_fairness": sum(m.fairness_score for m in all_metrics) / len(all_metrics) if all_metrics else 0,
                "transparency_average": sum(m.transparency_score for m in all_metrics) / len(all_metrics) if all_metrics else 0
            },
            "recommendations": [
                "Continue monitoring for bias patterns",
                "Implement suggested mitigation strategies",
                "Regular review of high-bias recommendations",
                "Update bias detection patterns based on findings"
            ]
        }
        
        return {
            "assessment_id": assessment_id,
            "report": report,
            "generated_at": datetime.utcnow().isoformat()
        }
        
    except Exception as e:
        logger.error(f"Error generating bias report: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate report: {str(e)}")

@router.get("/bias/statistics", tags=["Bias Detection"])
def get_bias_statistics():
    """Get overall bias detection system statistics"""
    try:
        db = get_session()
        
        # Get database statistics
        total_monitoring = db.query(BiasMonitoring).count() if hasattr(db.query(BiasMonitoring), 'count') else 0
        total_metrics = db.query(BiasMetric).count() if hasattr(db.query(BiasMetric), 'count') else 0
        
        db.close()
        
        # System statistics
        system_stats = {
            "bias_types_supported": len(BiasType),
            "severity_levels": len(SeverityLevel),
            "fairness_metrics": len(bias_detector.fairness_thresholds),
            "demographic_categories": len(bias_detector.demographic_terms),
            "pattern_count": sum(len(patterns) for patterns in bias_detector.bias_patterns.values())
        }
        
        return {
            "system_statistics": system_stats,
            "database_statistics": {
                "total_monitoring_sessions": total_monitoring,
                "total_bias_metrics": total_metrics
            },
            "bias_types": [bt.value for bt in BiasType],
            "severity_levels": [sl.value for sl in SeverityLevel]
        }
        
    except Exception as e:
        logger.error(f"Error getting bias statistics: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get statistics: {str(e)}")