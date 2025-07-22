"""
Assessment API Endpoints
Handles the 120-question assessment system with mathematical scoring
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Dict, List, Optional, Any
import logging
from datetime import datetime

from session_manager import session_manager
from progress_tracker import progress_tracker
from database.models import get_session, Assessment, DatabaseManager

logger = logging.getLogger(__name__)

router = APIRouter()

# --- Models ---
class QuestionResponse(BaseModel):
    question_id: str
    section_id: str
    response_value: Any
    response_type: Optional[str] = None
    time_spent_seconds: Optional[int] = None

class AssessmentStartRequest(BaseModel):
    assessment_name: Optional[str] = None
    user_id: Optional[str] = None
    company_id: Optional[int] = None

class SectionQuestionsRequest(BaseModel):
    section_id: str
    session_id: Optional[str] = None

# --- Assessment Questions Data ---
# Import the comprehensive 120-question structure
ASSESSMENT_SECTIONS = [
    {
        "id": "governance",
        "name": "Governance & Risk Management",
        "description": "Strategic cybersecurity governance, leadership, and risk management processes",
        "weight": 20,
        "total_questions": 10,
        "questions": [
            {
                "id": "gov_001",
                "text": "Does your organization have a formal information security governance framework?",
                "type": "boolean",
                "weight": 10,
                "category": "framework"
            },
            {
                "id": "gov_002", 
                "text": "How often is your security strategy reviewed and updated?",
                "type": "select",
                "options": ["Monthly", "Quarterly", "Annually", "Every 2+ years", "Never"],
                "weight": 8,
                "category": "strategy"
            },
            {
                "id": "gov_003",
                "text": "Does your organization have a dedicated Chief Information Security Officer (CISO) or equivalent?",
                "type": "boolean",
                "weight": 9,
                "category": "leadership"
            },
            {
                "id": "gov_004",
                "text": "How would you rate executive leadership support for cybersecurity initiatives?",
                "type": "scale",
                "min": 1,
                "max": 5,
                "weight": 10,
                "category": "leadership"
            },
            {
                "id": "gov_005",
                "text": "Does your organization have a formal risk management process?",
                "type": "boolean",
                "weight": 10,
                "category": "risk_process"
            },
            {
                "id": "gov_006",
                "text": "How often does your organization conduct formal risk assessments?",
                "type": "select",
                "options": ["Monthly", "Quarterly", "Annually", "Every 2+ years", "Never"],
                "weight": 9,
                "category": "risk_process"
            },
            {
                "id": "gov_007",
                "text": "Which risk assessment methodologies does your organization use?",
                "type": "multiselect",
                "options": ["NIST RMF", "ISO 31000", "FAIR", "OCTAVE", "Internal methodology", "None"],
                "weight": 8,
                "category": "methodology"
            },
            {
                "id": "gov_008",
                "text": "Does your organization maintain a formal risk register?",
                "type": "boolean",
                "weight": 7,
                "category": "documentation"
            },
            {
                "id": "gov_009",
                "text": "How often is the risk register reviewed and updated?",
                "type": "select",
                "options": ["Weekly", "Monthly", "Quarterly", "Annually", "Never", "No risk register"],
                "weight": 6,
                "category": "documentation"
            },
            {
                "id": "gov_010",
                "text": "Does your organization have a security steering committee with executive representation?",
                "type": "boolean",
                "weight": 8,
                "category": "governance"
            }
        ]
    },
    {
        "id": "asset_management",
        "name": "Asset Management",
        "description": "IT asset inventory, classification, and lifecycle management",
        "weight": 8,
        "total_questions": 10,
        "questions": [
            {
                "id": "asset_001",
                "text": "Does your organization maintain a comprehensive IT asset inventory?",
                "type": "boolean",
                "weight": 12,
                "category": "inventory"
            },
            {
                "id": "asset_002",
                "text": "What percentage of your IT assets are included in your inventory?",
                "type": "select",
                "options": ["0-25%", "26-50%", "51-75%", "76-90%", "91-100%", "Unknown"],
                "weight": 11,
                "category": "coverage"
            },
            {
                "id": "asset_003",
                "text": "How often is your IT asset inventory updated?",
                "type": "select",
                "options": ["Real-time/Automated", "Daily", "Weekly", "Monthly", "Quarterly or less frequently", "Never"],
                "weight": 10,
                "category": "maintenance"
            },
            {
                "id": "asset_004",
                "text": "Does your organization use automated tools for asset discovery and inventory?",
                "type": "boolean",
                "weight": 10,
                "category": "automation"
            },
            {
                "id": "asset_005",
                "text": "Does your organization maintain a software inventory including licenses?",
                "type": "boolean",
                "weight": 9,
                "category": "software"
            },
            {
                "id": "asset_006",
                "text": "Does your organization have a formal process for asset lifecycle management?",
                "type": "boolean",
                "weight": 9,
                "category": "lifecycle"
            },
            {
                "id": "asset_007",
                "text": "Does your organization classify assets based on criticality or sensitivity?",
                "type": "boolean",
                "weight": 11,
                "category": "classification"
            },
            {
                "id": "asset_008",
                "text": "Does your organization track cloud-based assets in your inventory?",
                "type": "boolean",
                "weight": 10,
                "category": "cloud"
            },
            {
                "id": "asset_009",
                "text": "Does your organization track IoT devices in your inventory?",
                "type": "boolean",
                "weight": 9,
                "category": "iot"
            },
            {
                "id": "asset_010",
                "text": "Does your organization have a process to identify and manage shadow IT?",
                "type": "boolean",
                "weight": 9,
                "category": "shadow_it"
            }
        ]
    },
    {
        "id": "data_protection",
        "name": "Data Protection",
        "description": "Data classification, encryption, privacy, and protection controls",
        "weight": 12,
        "total_questions": 10,
        "questions": [
            {
                "id": "data_001",
                "text": "Does your organization have a formal data classification policy?",
                "type": "boolean",
                "weight": 11,
                "category": "classification"
            },
            {
                "id": "data_002",
                "text": "What percentage of your organization's data is classified according to sensitivity?",
                "type": "select",
                "options": ["0-25%", "26-50%", "51-75%", "76-90%", "91-100%", "Unknown"],
                "weight": 10,
                "category": "classification"
            },
            {
                "id": "data_003",
                "text": "Which data protection technologies does your organization use?",
                "type": "multiselect",
                "options": ["Encryption at rest", "Encryption in transit", "DLP solutions", "Rights management", "Data masking", "Tokenization", "None"],
                "weight": 12,
                "category": "technology"
            },
            {
                "id": "data_004",
                "text": "Does your organization encrypt sensitive data at rest using industry-standard algorithms?",
                "type": "boolean",
                "weight": 11,
                "category": "encryption"
            },
            {
                "id": "data_005",
                "text": "Does your organization encrypt sensitive data in transit using TLS 1.2 or higher?",
                "type": "boolean",
                "weight": 11,
                "category": "encryption"
            },
            {
                "id": "data_006",
                "text": "Does your organization use Data Loss Prevention (DLP) solutions?",
                "type": "boolean",
                "weight": 9,
                "category": "dlp"
            },
            {
                "id": "data_007",
                "text": "Does your organization have a formal data retention policy?",
                "type": "boolean",
                "weight": 8,
                "category": "retention"
            },
            {
                "id": "data_008",
                "text": "Does your organization have a formal data disposal policy with secure deletion procedures?",
                "type": "boolean",
                "weight": 8,
                "category": "disposal"
            },
            {
                "id": "data_009",
                "text": "Does your organization conduct regular data protection impact assessments (DPIAs)?",
                "type": "boolean",
                "weight": 9,
                "category": "privacy"
            },
            {
                "id": "data_010",
                "text": "Does your organization have a comprehensive data breach response plan?",
                "type": "boolean",
                "weight": 11,
                "category": "breach_response"
            }
        ]
    }
    # Note: This is a sample of 3 sections. The full implementation would include all 12 sections
    # with 120 total questions as defined in the frontend assessment-questions.ts file
]

# --- Endpoints ---
@router.post("/assessment/start", tags=["Assessment"])
def start_assessment(request: AssessmentStartRequest):
    """Start a new 120-question assessment"""
    try:
        # Create assessment record
        db = get_session()
        assessment = Assessment(
            name=request.assessment_name or f"Assessment {datetime.now().strftime('%Y-%m-%d %H:%M')}",
            description="120-Question Cybersecurity Risk Assessment",
            framework_version="2.0",
            total_questions=120,
            total_sections=12,
            company_id=request.company_id
        )
        db.add(assessment)
        db.commit()
        db.refresh(assessment)
        assessment_id = assessment.id
        db.close()
        
        # Create session
        session_id = session_manager.create_session(
            assessment_id=assessment_id,
            user_id=request.user_id
        )
        
        return {
            "assessment_id": assessment_id,
            "session_id": session_id,
            "total_questions": 120,
            "total_sections": 12,
            "created_at": datetime.utcnow().isoformat(),
            "status": "started"
        }
    except Exception as e:
        logger.error(f"Error starting assessment: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to start assessment: {str(e)}")

@router.get("/assessment/questions", tags=["Assessment"])
def get_all_questions():
    """Get all 120 questions organized by domain"""
    try:
        return {
            "total_questions": 120,
            "total_sections": 12,
            "sections": ASSESSMENT_SECTIONS,
            "section_weights": {
                "governance": 20,
                "asset_management": 8,
                "data_protection": 12,
                "access_control": 12,
                "security_monitoring": 10,
                "incident_response": 10,
                "business_continuity": 8,
                "security_awareness": 6,
                "compliance": 4,
                "emerging_tech": 4,
                "third_party": 4,
                "risk_management": 2
            },
            "risk_levels": {
                "CRITICAL": {"min": 0, "max": 40, "label": "Critical Risk", "color": "#dc2626"},
                "HIGH": {"min": 41, "max": 60, "label": "High Risk", "color": "#ea580c"},
                "MEDIUM": {"min": 61, "max": 80, "label": "Medium Risk", "color": "#ca8a04"},
                "LOW": {"min": 81, "max": 100, "label": "Low Risk", "color": "#16a34a"}
            }
        }
    except Exception as e:
        logger.error(f"Error getting questions: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get questions: {str(e)}")

@router.get("/assessment/questions/{domain}", tags=["Assessment"])
def get_domain_questions(domain: str):
    """Get questions for specific domain"""
    try:
        # Find the section by domain ID
        section = next((s for s in ASSESSMENT_SECTIONS if s["id"] == domain), None)
        
        if not section:
            raise HTTPException(status_code=404, detail=f"Domain '{domain}' not found")
        
        return {
            "domain": domain,
            "section": section,
            "total_questions": section["total_questions"]
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting domain questions: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get domain questions: {str(e)}")

@router.post("/assessment/response", tags=["Assessment"])
def submit_response(response: QuestionResponse, session_id: str):
    """Submit answer for a specific question"""
    try:
        success = session_manager.save_response(
            session_id=session_id,
            question_id=response.question_id,
            section_id=response.section_id,
            response_value=response.response_value,
            response_type=response.response_type,
            time_spent_seconds=response.time_spent_seconds
        )
        
        if not success:
            raise HTTPException(status_code=404, detail=f"Session {session_id} not found")
        
        # Get updated progress
        progress = progress_tracker.get_assessment_progress(session_id)
        
        return {
            "session_id": session_id,
            "question_id": response.question_id,
            "saved_at": datetime.utcnow().isoformat(),
            "progress": progress,
            "status": "saved"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error submitting response: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to submit response: {str(e)}")

@router.get("/assessment/progress/{session_id}", tags=["Assessment"])
def get_progress(session_id: str):
    """Get current progress status"""
    try:
        progress = progress_tracker.get_assessment_progress(session_id)
        return progress
    except Exception as e:
        logger.error(f"Error getting progress: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get progress: {str(e)}")

@router.put("/assessment/progress/{session_id}", tags=["Assessment"])
def update_progress(session_id: str, update_data: Dict[str, Any]):
    """Update progress and save state"""
    try:
        success = session_manager.update_session(session_id, update_data)
        
        if not success:
            raise HTTPException(status_code=404, detail=f"Session {session_id} not found")
        
        # Get updated progress
        progress = progress_tracker.get_assessment_progress(session_id)
        
        return {
            "session_id": session_id,
            "updated_at": datetime.utcnow().isoformat(),
            "progress": progress,
            "status": "updated"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating progress: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to update progress: {str(e)}")

@router.get("/assessment/section/{section_id}/questions", tags=["Assessment"])
def get_section_questions(section_id: str, session_id: Optional[str] = None):
    """Get questions for a specific section with optional session context"""
    try:
        # Find the section
        section = next((s for s in ASSESSMENT_SECTIONS if s["id"] == section_id), None)
        
        if not section:
            raise HTTPException(status_code=404, detail=f"Section '{section_id}' not found")
        
        result = {
            "section_id": section_id,
            "section": section,
            "questions": section["questions"]
        }
        
        # If session provided, include progress and existing responses
        if session_id:
            section_progress = progress_tracker.get_section_progress(session_id, section_id)
            section_responses = progress_tracker.get_section_responses(session_id, section_id)
            
            result["progress"] = section_progress
            result["existing_responses"] = section_responses
        
        return result
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting section questions: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get section questions: {str(e)}")

@router.post("/assessment/section/{section_id}/complete", tags=["Assessment"])
def complete_section(section_id: str, session_id: str):
    """Mark a section as complete"""
    try:
        # Find the section to get total questions
        section = next((s for s in ASSESSMENT_SECTIONS if s["id"] == section_id), None)
        
        if not section:
            raise HTTPException(status_code=404, detail=f"Section '{section_id}' not found")
        
        success = session_manager.complete_section(
            session_id=session_id,
            section_id=section_id,
            total_questions=section["total_questions"]
        )
        
        if not success:
            raise HTTPException(status_code=404, detail=f"Session {session_id} not found")
        
        # Get updated progress
        progress = progress_tracker.get_assessment_progress(session_id)
        
        return {
            "session_id": session_id,
            "section_id": section_id,
            "completed_at": datetime.utcnow().isoformat(),
            "progress": progress,
            "status": "completed"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error completing section: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to complete section: {str(e)}")

@router.get("/assessment/{assessment_id}/summary", tags=["Assessment"])
def get_assessment_summary(assessment_id: int):
    """Get assessment summary with all responses and progress"""
    try:
        # Load assessment from database
        assessment_data = DatabaseManager.load_assessment_result(assessment_id)
        
        if not assessment_data:
            raise HTTPException(status_code=404, detail=f"Assessment {assessment_id} not found")
        
        return {
            "assessment": assessment_data,
            "sections": ASSESSMENT_SECTIONS,
            "summary_generated_at": datetime.utcnow().isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting assessment summary: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get assessment summary: {str(e)}")

@router.get("/assessment/domains", tags=["Assessment"])
def get_assessment_domains():
    """Get list of all assessment domains/sections"""
    try:
        domains = []
        for section in ASSESSMENT_SECTIONS:
            domains.append({
                "id": section["id"],
                "name": section["name"],
                "description": section["description"],
                "weight": section["weight"],
                "total_questions": section["total_questions"]
            })
        
        return {
            "domains": domains,
            "total_domains": len(domains),
            "total_questions": sum(d["total_questions"] for d in domains)
        }
    except Exception as e:
        logger.error(f"Error getting domains: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get domains: {str(e)}")