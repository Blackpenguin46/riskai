#!/usr/bin/env python3
"""
Question Bank API
Serves tailored questions based on industry and compliance requirements
"""

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Dict, List, Optional, Any
import logging

from assessment.question_bank import (
    question_bank, QuestionType, IndustryType, ComplianceFramework, Question
)

logger = logging.getLogger(__name__)
router = APIRouter()

# Pydantic Models
class AssessmentRequest(BaseModel):
    industry: Optional[str] = None
    compliance_requirements: Optional[List[str]] = None
    company_size: Optional[str] = None
    data_types: Optional[List[str]] = None  # e.g., ["pii", "phi", "payment_data"]

class QuestionResponse(BaseModel):
    id: str
    domain: str
    question_text: str
    question_type: str
    weight: int
    options: Optional[List[str]] = None
    min_value: Optional[int] = None
    max_value: Optional[int] = None
    help_text: Optional[str] = None
    compliance_frameworks: Optional[List[str]] = None
    industry_specific: bool = False

@router.post("/assessment/questions", tags=["Assessment Questions"])
def get_tailored_questions(request: AssessmentRequest):
    """Get 120 tailored questions based on industry and compliance requirements"""
    try:
        # Convert string inputs to enums
        industry = None
        if request.industry:
            try:
                industry = IndustryType(request.industry.lower())
            except ValueError:
                logger.warning(f"Unknown industry: {request.industry}")
        
        compliance_frameworks = []
        if request.compliance_requirements:
            for cf in request.compliance_requirements:
                try:
                    compliance_frameworks.append(ComplianceFramework(cf.lower()))
                except ValueError:
                    logger.warning(f"Unknown compliance framework: {cf}")
        
        # Get tailored questions
        questions = question_bank.get_questions_for_assessment(
            industry=industry,
            compliance_requirements=compliance_frameworks,
            company_size=request.company_size
        )
        
        # Convert to response format
        question_responses = []
        for q in questions:
            question_responses.append(QuestionResponse(
                id=q.id,
                domain=q.domain,
                question_text=q.question_text,
                question_type=q.question_type.value,
                weight=q.weight,
                options=q.options,
                min_value=q.min_value,
                max_value=q.max_value,
                help_text=q.help_text,
                compliance_frameworks=[cf.value for cf in q.compliance_frameworks] if q.compliance_frameworks else None,
                industry_specific=not q.is_standard
            ))
        
        # Group by domain for easier frontend consumption
        domains = {}
        for qr in question_responses:
            if qr.domain not in domains:
                domains[qr.domain] = []
            domains[qr.domain].append(qr.dict())
        
        return {
            "total_questions": len(question_responses),
            "industry": request.industry,
            "compliance_requirements": request.compliance_requirements,
            "domains": domains,
            "domain_summary": {
                domain: len(questions) for domain, questions in domains.items()
            }
        }
        
    except Exception as e:
        logger.error(f"Error getting tailored questions: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get questions: {str(e)}")

@router.get("/assessment/questions/domain/{domain}", tags=["Assessment Questions"])
def get_domain_questions(domain: str, 
                        industry: Optional[str] = Query(None),
                        compliance: Optional[str] = Query(None)):
    """Get questions for a specific domain"""
    try:
        industry_enum = None
        if industry:
            try:
                industry_enum = IndustryType(industry.lower())
            except ValueError:
                pass
        
        questions = question_bank.get_questions_by_domain(domain, industry_enum)
        
        return {
            "domain": domain,
            "industry": industry,
            "questions": [
                {
                    "id": q.id,
                    "question_text": q.question_text,
                    "question_type": q.question_type.value,
                    "weight": q.weight,
                    "options": q.options,
                    "help_text": q.help_text,
                    "industry_specific": not q.is_standard
                } for q in questions
            ]
        }
        
    except Exception as e:
        logger.error(f"Error getting domain questions: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get domain questions: {str(e)}")

@router.get("/assessment/questions/compliance/{framework}", tags=["Assessment Questions"])
def get_compliance_questions(framework: str):
    """Get questions relevant to a specific compliance framework"""
    try:
        framework_enum = ComplianceFramework(framework.lower())
        questions = question_bank.get_compliance_questions([framework_enum])
        
        return {
            "compliance_framework": framework,
            "questions": [
                {
                    "id": q.id,
                    "domain": q.domain,
                    "question_text": q.question_text,
                    "question_type": q.question_type.value,
                    "weight": q.weight,
                    "help_text": q.help_text
                } for q in questions
            ]
        }
        
    except ValueError:
        raise HTTPException(status_code=400, detail=f"Unknown compliance framework: {framework}")
    except Exception as e:
        logger.error(f"Error getting compliance questions: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get compliance questions: {str(e)}")

@router.get("/assessment/industries", tags=["Assessment Questions"])
def get_supported_industries():
    """Get list of supported industries"""
    return {
        "industries": [industry.value for industry in IndustryType],
        "descriptions": {
            "healthcare": "Healthcare providers, hospitals, medical practices",
            "financial_services": "Banks, credit unions, investment firms, insurance",
            "technology": "Software companies, SaaS providers, tech startups",
            "manufacturing": "Industrial manufacturers, automotive, aerospace",
            "government": "Federal, state, local government agencies",
            "education": "Schools, universities, educational institutions",
            "retail": "Retail stores, e-commerce, consumer goods",
            "energy": "Utilities, oil & gas, renewable energy"
        }
    }

@router.get("/assessment/compliance-frameworks", tags=["Assessment Questions"])
def get_compliance_frameworks():
    """Get list of supported compliance frameworks"""
    return {
        "frameworks": [framework.value for framework in ComplianceFramework],
        "descriptions": {
            "hipaa": "Health Insurance Portability and Accountability Act",
            "pci_dss": "Payment Card Industry Data Security Standard",
            "sox": "Sarbanes-Oxley Act",
            "gdpr": "General Data Protection Regulation",
            "iso27001": "ISO/IEC 27001 Information Security Management",
            "nist_csf": "NIST Cybersecurity Framework",
            "soc2": "Service Organization Control 2",
            "fisma": "Federal Information Security Management Act"
        }
    }

@router.get("/assessment/question/{question_id}", tags=["Assessment Questions"])
def get_question_details(question_id: str):
    """Get detailed information about a specific question"""
    try:
        question = question_bank.get_question_by_id(question_id)
        if not question:
            raise HTTPException(status_code=404, detail=f"Question {question_id} not found")
        
        return {
            "id": question.id,
            "domain": question.domain,
            "question_text": question.question_text,
            "question_type": question.question_type.value,
            "weight": question.weight,
            "options": question.options,
            "min_value": question.min_value,
            "max_value": question.max_value,
            "help_text": question.help_text,
            "compliance_frameworks": [cf.value for cf in question.compliance_frameworks] if question.compliance_frameworks else [],
            "industry_specific": not question.is_standard,
            "applicable_industries": [ind.value for ind in question.industry_specific] if question.industry_specific else []
        }
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting question details: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get question details: {str(e)}")

@router.get("/assessment/test-questions", tags=["Assessment Questions"])
def test_question_system():
    """Test endpoint to verify question system is working"""
    try:
        # Test different industry configurations
        healthcare_questions = question_bank.get_questions_for_assessment(
            industry=IndustryType.HEALTHCARE,
            compliance_requirements=[ComplianceFramework.HIPAA]
        )
        
        fintech_questions = question_bank.get_questions_for_assessment(
            industry=IndustryType.FINANCIAL_SERVICES,
            compliance_requirements=[ComplianceFramework.PCI_DSS, ComplianceFramework.SOX]
        )
        
        tech_questions = question_bank.get_questions_for_assessment(
            industry=IndustryType.TECHNOLOGY
        )
        
        return {
            "message": "Question system test completed",
            "results": {
                "healthcare": {
                    "total_questions": len(healthcare_questions),
                    "industry_specific": len([q for q in healthcare_questions if not q.is_standard]),
                    "hipaa_questions": len([q for q in healthcare_questions if q.compliance_frameworks and ComplianceFramework.HIPAA in q.compliance_frameworks])
                },
                "financial_services": {
                    "total_questions": len(fintech_questions),
                    "industry_specific": len([q for q in fintech_questions if not q.is_standard]),
                    "compliance_questions": len([q for q in fintech_questions if q.compliance_frameworks])
                },
                "technology": {
                    "total_questions": len(tech_questions),
                    "industry_specific": len([q for q in tech_questions if not q.is_standard])
                }
            },
            "status": "working"
        }
        
    except Exception as e:
        logger.error(f"Error in question system test: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Test failed: {str(e)}")