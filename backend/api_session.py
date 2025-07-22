"""
Session Management API Endpoints
Handles session persistence, progress tracking, and state restoration
"""

from fastapi import APIRouter, HTTPException, Depends
from pydantic import BaseModel
from typing import Dict, List, Optional, Any
import logging
from datetime import datetime

from session_manager import session_manager
from progress_tracker import progress_tracker
from state_restorer import state_restorer

logger = logging.getLogger(__name__)

router = APIRouter()

# --- Models ---
class CreateSessionRequest(BaseModel):
    assessment_id: int
    user_id: Optional[str] = None

class SessionUpdateRequest(BaseModel):
    current_section: Optional[str] = None
    current_question: Optional[str] = None
    completion_status: Optional[str] = None
    state_data: Optional[Dict[str, Any]] = None

class ResponseRequest(BaseModel):
    question_id: str
    section_id: str
    response_value: Any
    response_type: Optional[str] = None
    time_spent_seconds: Optional[int] = None

class SectionCompleteRequest(BaseModel):
    section_id: str
    total_questions: int

# --- Endpoints ---
@router.post("/assessment/session/create", tags=["Session Management"])
def create_session(request: CreateSessionRequest):
    """Create a new assessment session"""
    try:
        session_id = session_manager.create_session(
            assessment_id=request.assessment_id,
            user_id=request.user_id
        )
        
        return {
            "session_id": session_id,
            "created_at": datetime.utcnow().isoformat(),
            "status": "created"
        }
    except Exception as e:
        logger.error(f"Error creating session: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create session: {str(e)}")

@router.get("/assessment/session/{session_id}", tags=["Session Management"])
def get_session(session_id: str):
    """Get session details"""
    try:
        session = session_manager.get_session(session_id)
        if not session:
            raise HTTPException(status_code=404, detail=f"Session {session_id} not found")
        
        return session
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting session: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get session: {str(e)}")

@router.put("/assessment/session/{session_id}/update", tags=["Session Management"])
def update_session(session_id: str, request: SessionUpdateRequest):
    """Update session details"""
    try:
        success = session_manager.update_session(
            session_id=session_id,
            update_data=request.dict(exclude_none=True)
        )
        
        if not success:
            raise HTTPException(status_code=404, detail=f"Session {session_id} not found")
        
        return {
            "session_id": session_id,
            "updated_at": datetime.utcnow().isoformat(),
            "status": "updated"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error updating session: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to update session: {str(e)}")

@router.post("/assessment/session/{session_id}/response", tags=["Session Management"])
def save_response(session_id: str, request: ResponseRequest):
    """Save a question response"""
    try:
        success = session_manager.save_response(
            session_id=session_id,
            question_id=request.question_id,
            section_id=request.section_id,
            response_value=request.response_value,
            response_type=request.response_type,
            time_spent_seconds=request.time_spent_seconds
        )
        
        if not success:
            raise HTTPException(status_code=404, detail=f"Session {session_id} not found")
        
        return {
            "session_id": session_id,
            "question_id": request.question_id,
            "saved_at": datetime.utcnow().isoformat(),
            "status": "saved"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error saving response: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to save response: {str(e)}")

@router.post("/assessment/session/{session_id}/section/complete", tags=["Session Management"])
def complete_section(session_id: str, request: SectionCompleteRequest):
    """Mark a section as complete"""
    try:
        success = session_manager.complete_section(
            session_id=session_id,
            section_id=request.section_id,
            total_questions=request.total_questions
        )
        
        if not success:
            raise HTTPException(status_code=404, detail=f"Session {session_id} not found")
        
        return {
            "session_id": session_id,
            "section_id": request.section_id,
            "completed_at": datetime.utcnow().isoformat(),
            "status": "completed"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error completing section: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to complete section: {str(e)}")

@router.get("/assessment/sessions/user/{user_id}", tags=["Session Management"])
def get_user_sessions(user_id: str):
    """Get all sessions for a user"""
    try:
        sessions = session_manager.get_user_sessions(user_id)
        return {
            "user_id": user_id,
            "sessions": sessions,
            "count": len(sessions)
        }
    except Exception as e:
        logger.error(f"Error getting user sessions: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get user sessions: {str(e)}")

@router.get("/assessment/sessions/incomplete", tags=["Session Management"])
def get_incomplete_sessions(user_id: Optional[str] = None):
    """Get all incomplete sessions"""
    try:
        sessions = session_manager.get_incomplete_sessions(user_id)
        return {
            "user_id": user_id,
            "sessions": sessions,
            "count": len(sessions)
        }
    except Exception as e:
        logger.error(f"Error getting incomplete sessions: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get incomplete sessions: {str(e)}")

@router.post("/assessment/session/{session_id}/resume", tags=["Session Management"])
def resume_session(session_id: str):
    """Resume an existing session"""
    try:
        state = state_restorer.restore_session_state(session_id)
        if "error" in state:
            raise HTTPException(status_code=404, detail=state["error"])
        
        # Validate the restored state
        is_valid, message = state_restorer.validate_restored_state(state)
        if not is_valid:
            raise HTTPException(status_code=500, detail=f"Invalid session state: {message}")
        
        return state
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error resuming session: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to resume session: {str(e)}")

@router.get("/assessment/sessions/resumable", tags=["Session Management"])
def get_resumable_sessions(user_id: Optional[str] = None):
    """Get all sessions that can be resumed"""
    try:
        sessions = state_restorer.get_resumable_sessions(user_id)
        return {
            "user_id": user_id,
            "sessions": sessions,
            "count": len(sessions)
        }
    except Exception as e:
        logger.error(f"Error getting resumable sessions: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get resumable sessions: {str(e)}")

@router.post("/assessment/session/{session_id}/complete", tags=["Session Management"])
def complete_session(session_id: str):
    """Mark a session as complete"""
    try:
        success = session_manager.complete_session(session_id)
        if not success:
            raise HTTPException(status_code=404, detail=f"Session {session_id} not found")
        
        return {
            "session_id": session_id,
            "completed_at": datetime.utcnow().isoformat(),
            "status": "completed"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error completing session: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to complete session: {str(e)}")

@router.get("/assessment/session/{session_id}/progress", tags=["Session Management"])
def get_assessment_progress(session_id: str):
    """Get overall progress for an assessment"""
    try:
        progress = progress_tracker.get_assessment_progress(session_id)
        return progress
    except Exception as e:
        logger.error(f"Error getting assessment progress: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get assessment progress: {str(e)}")

@router.get("/assessment/session/{session_id}/section/{section_id}/progress", tags=["Session Management"])
def get_section_progress(session_id: str, section_id: str):
    """Get progress for a specific section"""
    try:
        progress = progress_tracker.get_section_progress(session_id, section_id)
        return progress
    except Exception as e:
        logger.error(f"Error getting section progress: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get section progress: {str(e)}")

@router.get("/assessment/session/{session_id}/section/{section_id}/responses", tags=["Session Management"])
def get_section_responses(session_id: str, section_id: str):
    """Get all responses for a section"""
    try:
        responses = progress_tracker.get_section_responses(session_id, section_id)
        return {
            "session_id": session_id,
            "section_id": section_id,
            "responses": responses,
            "count": len(responses)
        }
    except Exception as e:
        logger.error(f"Error getting section responses: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get section responses: {str(e)}")

@router.get("/assessment/session/{session_id}/responses", tags=["Session Management"])
def get_all_responses(session_id: str):
    """Get all responses for a session"""
    try:
        responses = progress_tracker.get_all_responses(session_id)
        return {
            "session_id": session_id,
            "responses": responses
        }
    except Exception as e:
        logger.error(f"Error getting all responses: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get all responses: {str(e)}")

@router.get("/assessment/session/{session_id}/completed-sections", tags=["Session Management"])
def get_completed_sections(session_id: str):
    """Get list of completed section IDs"""
    try:
        sections = progress_tracker.get_completed_sections(session_id)
        return {
            "session_id": session_id,
            "completed_sections": sections,
            "count": len(sections)
        }
    except Exception as e:
        logger.error(f"Error getting completed sections: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get completed sections: {str(e)}")

@router.post("/assessment/session/{session_id}/auto-save", tags=["Session Management"])
def auto_save_session(session_id: str, auto_save_data: Dict[str, Any]):
    """Auto-save session state for recovery"""
    try:
        current_question = auto_save_data.get("current_question", "")
        current_section = auto_save_data.get("current_section", "")
        additional_data = auto_save_data.get("state_data", {})
        
        success = session_manager.auto_save_session(
            session_id=session_id,
            current_question=current_question,
            current_section=current_section,
            auto_save_data=additional_data
        )
        
        if not success:
            raise HTTPException(status_code=404, detail=f"Session {session_id} not found")
        
        return {
            "session_id": session_id,
            "auto_saved_at": datetime.utcnow().isoformat(),
            "status": "auto_saved"
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error auto-saving session: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to auto-save session: {str(e)}")

@router.post("/assessment/sessions/cleanup", tags=["Session Management"])
def cleanup_expired_sessions(hours: Optional[int] = 24):
    """Clean up expired sessions"""
    try:
        count = session_manager.cleanup_expired_sessions(hours)
        return {
            "cleaned_up_count": count,
            "cleanup_threshold_hours": hours,
            "cleaned_up_at": datetime.utcnow().isoformat(),
            "status": "completed"
        }
    except Exception as e:
        logger.error(f"Error cleaning up sessions: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to cleanup sessions: {str(e)}")