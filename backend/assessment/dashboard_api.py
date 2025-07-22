#!/usr/bin/env python3
"""
Dashboard API
Provides endpoints for dashboard data
"""

from fastapi import APIRouter, HTTPException
from typing import Dict, List, Any
import logging
from datetime import datetime

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/dashboard/data", tags=["Dashboard"])
def get_dashboard_data():
    """Get dashboard data for the research demo"""
    try:
        # Sample dashboard data for demonstration
        return {
            "status": "success",
            "data": {
                "overall_score": 72.5,
                "risk_level": "Medium Risk",
                "risk_color": "#ca8a04",
                "completion_rate": 95,
                "section_breakdown": [
                    {
                        "section_id": "governance",
                        "section_name": "Governance & Risk Management",
                        "score": 78.0,
                        "risk_level": "Medium Risk",
                        "weight": 20,
                        "questions_answered": 10,
                        "total_questions": 10
                    },
                    {
                        "section_id": "data_protection",
                        "section_name": "Data Protection",
                        "score": 85.0,
                        "risk_level": "Low Risk",
                        "weight": 12,
                        "questions_answered": 10,
                        "total_questions": 10
                    },
                    {
                        "section_id": "access_control",
                        "section_name": "Access Control",
                        "score": 65.0,
                        "risk_level": "Medium Risk",
                        "weight": 12,
                        "questions_answered": 10,
                        "total_questions": 10
                    },
                    {
                        "section_id": "security_monitoring",
                        "section_name": "Security Monitoring",
                        "score": 70.0,
                        "risk_level": "Medium Risk",
                        "weight": 10,
                        "questions_answered": 10,
                        "total_questions": 10
                    },
                    {
                        "section_id": "incident_response",
                        "section_name": "Incident Response",
                        "score": 68.0,
                        "risk_level": "Medium Risk",
                        "weight": 10,
                        "questions_answered": 10,
                        "total_questions": 10
                    },
                    {
                        "section_id": "business_continuity",
                        "section_name": "Business Continuity",
                        "score": 75.0,
                        "risk_level": "Medium Risk",
                        "weight": 8,
                        "questions_answered": 8,
                        "total_questions": 10
                    },
                    {
                        "section_id": "security_awareness",
                        "section_name": "Security Awareness",
                        "score": 80.0,
                        "risk_level": "Medium Risk",
                        "weight": 6,
                        "questions_answered": 6,
                        "total_questions": 10
                    },
                    {
                        "section_id": "compliance",
                        "section_name": "Compliance",
                        "score": 82.0,
                        "risk_level": "Low Risk",
                        "weight": 4,
                        "questions_answered": 4,
                        "total_questions": 10
                    },
                    {
                        "section_id": "emerging_technologies",
                        "section_name": "Emerging Technologies",
                        "score": 60.0,
                        "risk_level": "Medium Risk",
                        "weight": 4,
                        "questions_answered": 4,
                        "total_questions": 10
                    },
                    {
                        "section_id": "third_party_risk",
                        "section_name": "Third Party Risk",
                        "score": 72.0,
                        "risk_level": "Medium Risk",
                        "weight": 4,
                        "questions_answered": 4,
                        "total_questions": 10
                    },
                    {
                        "section_id": "risk_management_process",
                        "section_name": "Risk Management Process",
                        "score": 76.0,
                        "risk_level": "Medium Risk",
                        "weight": 2,
                        "questions_answered": 2,
                        "total_questions": 10
                    },
                    {
                        "section_id": "asset_management",
                        "section_name": "Asset Management",
                        "score": 74.0,
                        "risk_level": "Medium Risk",
                        "weight": 8,
                        "questions_answered": 8,
                        "total_questions": 10
                    }
                ],
                "risk_categorization": {
                    "confidence_interval": {
                        "lower_bound": 68.2,
                        "upper_bound": 76.8,
                        "confidence_level": 0.95,
                        "margin_of_error": 4.3,
                        "sample_size": 120
                    },
                    "recommendations": [
                        "Implement multi-factor authentication across all systems",
                        "Establish formal incident response procedures",
                        "Enhance security awareness training program",
                        "Develop comprehensive data classification policy",
                        "Implement regular vulnerability scanning",
                        "Establish third-party risk assessment process",
                        "Develop formal change management procedures",
                        "Implement security monitoring for cloud environments",
                        "Establish formal risk assessment methodology"
                    ]
                },
                "industry_benchmarks": {
                    "industry": "healthcare",
                    "industry_average": 65.0,
                    "top_quartile": 82.0,
                    "bottom_quartile": 48.0,
                    "comparison": "above_average"
                },
                "recent_assessments": [
                    {
                        "id": 1,
                        "name": "Q1 2023 Assessment",
                        "date": "2023-01-15",
                        "score": 68.5,
                        "risk_level": "Medium Risk"
                    },
                    {
                        "id": 2,
                        "name": "Q2 2023 Assessment",
                        "date": "2023-04-10",
                        "score": 70.2,
                        "risk_level": "Medium Risk"
                    },
                    {
                        "id": 3,
                        "name": "Q3 2023 Assessment",
                        "date": "2023-07-22",
                        "score": 72.5,
                        "risk_level": "Medium Risk"
                    }
                ]
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting dashboard data: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get dashboard data: {str(e)}")

@router.get("/dashboard/stats", tags=["Dashboard"])
def get_dashboard_stats():
    """Get dashboard statistics for the research demo"""
    try:
        return {
            "status": "success",
            "data": {
                "total_assessments": 3,
                "average_score": 70.4,
                "trend": "improving",
                "completion_rate": 95,
                "most_improved_domain": "Access Control",
                "weakest_domain": "Emerging Technologies",
                "strongest_domain": "Data Protection"
            },
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        logger.error(f"Error getting dashboard stats: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get dashboard stats: {str(e)}")