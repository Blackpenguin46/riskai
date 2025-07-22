#!/usr/bin/env python3
"""
Source Attribution API
REST API endpoints for framework source attribution functionality
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Dict, List, Optional, Any
import logging
from datetime import datetime

from assessment.source_attribution import source_attributor, SourceAttribution, FrameworkReference, FrameworkType
from database.models import get_session, LLMRecommendation, RecommendationSource

logger = logging.getLogger(__name__)
router = APIRouter()

# Pydantic Models
class AttributionRequest(BaseModel):
    recommendation_text: str
    section_id: Optional[str] = None
    assessment_context: Optional[Dict[str, Any]] = None

class FrameworkReferenceResponse(BaseModel):
    framework: str
    control_id: str
    control_title: str
    description: str
    section: Optional[str] = None
    subsection: Optional[str] = None
    page_number: Optional[int] = None
    url: Optional[str] = None
    relevance_score: float

class SourceAttributionResponse(BaseModel):
    recommendation_id: str
    primary_sources: List[FrameworkReferenceResponse]
    supporting_sources: List[FrameworkReferenceResponse]
    confidence_score: float
    reliability_score: float
    coverage_score: float
    validation_results: Dict[str, Any]
    last_updated: str

class BulkAttributionRequest(BaseModel):
    recommendations: List[Dict[str, Any]]  # List of {text, section_id, context}

# --- Source Attribution Endpoints ---

@router.post("/attribution/analyze", tags=["Source Attribution"])
def analyze_recommendation_sources(request: AttributionRequest):
    """Analyze and attribute sources for a single recommendation"""
    try:
        # Perform source attribution
        attribution = source_attributor.attribute_recommendation(
            recommendation_text=request.recommendation_text,
            section_id=request.section_id,
            assessment_context=request.assessment_context
        )
        
        # Validate attribution quality
        validation_results = source_attributor.validate_attribution(attribution)
        
        # Convert to response format
        response = SourceAttributionResponse(
            recommendation_id=attribution.recommendation_id,
            primary_sources=[
                FrameworkReferenceResponse(
                    framework=source.framework.value,
                    control_id=source.control_id,
                    control_title=source.control_title,
                    description=source.description,
                    section=source.section,
                    subsection=source.subsection,
                    page_number=source.page_number,
                    url=source.url,
                    relevance_score=source.relevance_score
                ) for source in attribution.primary_sources
            ],
            supporting_sources=[
                FrameworkReferenceResponse(
                    framework=source.framework.value,
                    control_id=source.control_id,
                    control_title=source.control_title,
                    description=source.description,
                    section=source.section,
                    subsection=source.subsection,
                    page_number=source.page_number,
                    url=source.url,
                    relevance_score=source.relevance_score
                ) for source in attribution.supporting_sources
            ],
            confidence_score=attribution.confidence_score,
            reliability_score=attribution.reliability_score,
            coverage_score=attribution.coverage_score,
            validation_results=validation_results,
            last_updated=attribution.last_updated.isoformat()
        )
        
        return response
        
    except Exception as e:
        logger.error(f"Error analyzing recommendation sources: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to analyze sources: {str(e)}")

@router.post("/attribution/bulk", tags=["Source Attribution"])
def bulk_analyze_sources(request: BulkAttributionRequest):
    """Analyze sources for multiple recommendations"""
    try:
        results = []
        
        for rec_data in request.recommendations:
            attribution = source_attributor.attribute_recommendation(
                recommendation_text=rec_data.get('text', ''),
                section_id=rec_data.get('section_id'),
                assessment_context=rec_data.get('context')
            )
            
            validation_results = source_attributor.validate_attribution(attribution)
            
            results.append({
                "recommendation_text": rec_data.get('text', ''),
                "attribution": {
                    "recommendation_id": attribution.recommendation_id,
                    "primary_sources": len(attribution.primary_sources),
                    "supporting_sources": len(attribution.supporting_sources),
                    "confidence_score": attribution.confidence_score,
                    "reliability_score": attribution.reliability_score,
                    "coverage_score": attribution.coverage_score,
                    "is_valid": validation_results["is_valid"]
                }
            })
        
        return {
            "total_recommendations": len(request.recommendations),
            "results": results,
            "summary": {
                "high_confidence": len([r for r in results if r["attribution"]["confidence_score"] > 0.7]),
                "medium_confidence": len([r for r in results if 0.5 <= r["attribution"]["confidence_score"] <= 0.7]),
                "low_confidence": len([r for r in results if r["attribution"]["confidence_score"] < 0.5])
            }
        }
        
    except Exception as e:
        logger.error(f"Error in bulk source analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to analyze bulk sources: {str(e)}")

@router.get("/attribution/frameworks", tags=["Source Attribution"])
def get_supported_frameworks():
    """Get list of supported cybersecurity frameworks"""
    try:
        frameworks = []
        
        for framework_type in FrameworkType:
            details = source_attributor.get_framework_details(framework_type)
            frameworks.append({
                "id": framework_type.name,
                "name": framework_type.value,
                "details": details
            })
        
        return {
            "frameworks": frameworks,
            "total_count": len(frameworks)
        }
        
    except Exception as e:
        logger.error(f"Error getting frameworks: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get frameworks: {str(e)}")

@router.get("/attribution/framework/{framework_id}", tags=["Source Attribution"])
def get_framework_details(framework_id: str):
    """Get detailed information about a specific framework"""
    try:
        # Find framework by ID
        framework_type = None
        for ft in FrameworkType:
            if ft.name == framework_id.upper():
                framework_type = ft
                break
        
        if not framework_type:
            raise HTTPException(status_code=404, detail=f"Framework '{framework_id}' not found")
        
        details = source_attributor.get_framework_details(framework_type)
        
        # Get available controls for this framework
        available_controls = []
        for category, sources in source_attributor.framework_mappings.items():
            for source in sources:
                if source.framework == framework_type:
                    available_controls.append({
                        "control_id": source.control_id,
                        "control_title": source.control_title,
                        "description": source.description,
                        "section": source.section,
                        "category": category
                    })
        
        return {
            "framework": {
                "id": framework_type.name,
                "name": framework_type.value,
                **details
            },
            "available_controls": available_controls,
            "control_count": len(available_controls)
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting framework details: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get framework details: {str(e)}")

@router.get("/attribution/search", tags=["Source Attribution"])
def search_framework_controls(
    query: str = Query(..., description="Search query for framework controls"),
    framework: Optional[str] = Query(None, description="Filter by specific framework"),
    category: Optional[str] = Query(None, description="Filter by category")
):
    """Search for framework controls by keyword"""
    try:
        results = []
        query_lower = query.lower()
        
        for cat, sources in source_attributor.framework_mappings.items():
            # Filter by category if specified
            if category and cat != category:
                continue
                
            for source in sources:
                # Filter by framework if specified
                if framework and source.framework.name != framework.upper():
                    continue
                
                # Check if query matches control title or description
                if (query_lower in source.control_title.lower() or 
                    query_lower in source.description.lower() or
                    query_lower in source.control_id.lower()):
                    
                    results.append({
                        "framework": source.framework.value,
                        "framework_id": source.framework.name,
                        "control_id": source.control_id,
                        "control_title": source.control_title,
                        "description": source.description,
                        "section": source.section,
                        "category": cat,
                        "relevance_score": source_attributor._calculate_text_relevance(query, source)
                    })
        
        # Sort by relevance
        results.sort(key=lambda x: x["relevance_score"], reverse=True)
        
        return {
            "query": query,
            "results": results[:20],  # Limit to top 20 results
            "total_found": len(results)
        }
        
    except Exception as e:
        logger.error(f"Error searching framework controls: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to search controls: {str(e)}")

@router.post("/attribution/validate", tags=["Source Attribution"])
def validate_attribution_quality(attribution_data: Dict[str, Any]):
    """Validate the quality of a source attribution"""
    try:
        # Convert input data to SourceAttribution object
        attribution = SourceAttribution(
            recommendation_id=attribution_data.get("recommendation_id", ""),
            primary_sources=[],  # Would need to reconstruct from data
            supporting_sources=[],
            confidence_score=attribution_data.get("confidence_score", 0.0),
            reliability_score=attribution_data.get("reliability_score", 0.0),
            coverage_score=attribution_data.get("coverage_score", 0.0),
            last_updated=datetime.utcnow()
        )
        
        validation_results = source_attributor.validate_attribution(attribution)
        
        return {
            "validation_results": validation_results,
            "recommendations": {
                "improve_confidence": validation_results["confidence_level"] != "High",
                "add_sources": len(validation_results.get("recommendations", [])) > 0,
                "review_required": not validation_results["is_valid"]
            }
        }
        
    except Exception as e:
        logger.error(f"Error validating attribution: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to validate attribution: {str(e)}")

@router.get("/attribution/stats", tags=["Source Attribution"])
def get_attribution_statistics():
    """Get statistics about source attribution system"""
    try:
        db = get_session()
        
        # Get database statistics if available
        total_recommendations = db.query(LLMRecommendation).count() if hasattr(db.query(LLMRecommendation), 'count') else 0
        total_sources = db.query(RecommendationSource).count() if hasattr(db.query(RecommendationSource), 'count') else 0
        
        # Framework statistics
        framework_stats = {}
        for category, sources in source_attributor.framework_mappings.items():
            for source in sources:
                framework_name = source.framework.value
                if framework_name not in framework_stats:
                    framework_stats[framework_name] = 0
                framework_stats[framework_name] += 1
        
        db.close()
        
        return {
            "system_stats": {
                "total_frameworks": len(FrameworkType),
                "total_categories": len(source_attributor.framework_mappings),
                "total_controls": sum(len(sources) for sources in source_attributor.framework_mappings.values())
            },
            "database_stats": {
                "total_recommendations": total_recommendations,
                "total_source_attributions": total_sources
            },
            "framework_distribution": framework_stats,
            "keyword_patterns": {
                category: len(keywords) 
                for category, keywords in source_attributor.keyword_patterns.items()
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting attribution statistics: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get statistics: {str(e)}")

@router.post("/attribution/save/{assessment_id}", tags=["Source Attribution"])
def save_attribution_to_database(assessment_id: int, attribution_data: SourceAttributionResponse):
    """Save source attribution to database for an assessment"""
    try:
        db = get_session()
        
        # Create LLM recommendation record
        llm_recommendation = LLMRecommendation(
            assessment_id=assessment_id,
            recommendation_text="",  # Would be provided in full implementation
            confidence_score=attribution_data.confidence_score,
            reasoning_path="Source attribution analysis",
            frameworks_referenced=[source.framework for source in attribution_data.primary_sources],
            implementation_difficulty="Medium",  # Would be calculated
            expected_impact="High",  # Would be calculated
            generation_timestamp=datetime.utcnow()
        )
        
        db.add(llm_recommendation)
        db.flush()  # Get the ID
        
        # Create source records
        for source in attribution_data.primary_sources + attribution_data.supporting_sources:
            source_record = RecommendationSource(
                recommendation_id=llm_recommendation.id,
                source_type="framework",
                reference=f"{source.framework}:{source.control_id}",
                relevance_score=source.relevance_score,
                page_number=source.page_number,
                quote=source.description
            )
            db.add(source_record)
        
        db.commit()
        db.close()
        
        return {
            "message": "Attribution saved successfully",
            "recommendation_id": llm_recommendation.id,
            "sources_saved": len(attribution_data.primary_sources + attribution_data.supporting_sources)
        }
        
    except Exception as e:
        db.rollback()
        db.close()
        logger.error(f"Error saving attribution: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to save attribution: {str(e)}")