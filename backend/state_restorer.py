"""
State Restorer for RiskAI
Rebuilds assessment state when resuming a session
"""

import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime

from database.models import get_session, Assessment
from database.session_models import AssessmentSession, SectionProgress, SessionResponse
from session_manager import session_manager
from progress_tracker import progress_tracker

logger = logging.getLogger(__name__)

class StateRestorer:
    """Rebuilds assessment state when resuming a session"""
    
    @staticmethod
    def restore_session_state(session_id: str) -> Dict[str, Any]:
        """
        Restore the state of a session for resumption
        
        Args:
            session_id: Unique identifier for the session
            
        Returns:
            Complete session state including responses and progress
        """
        try:
            # Get session details
            session_details = session_manager.resume_session(session_id)
            if not session_details:
                logger.error(f"Failed to resume session {session_id}")
                return {"error": "Session not found or expired"}
            
            # Get assessment details
            assessment_details = StateRestorer._get_assessment_details(session_details["assessment_id"])
            if not assessment_details:
                logger.error(f"Failed to get assessment details for session {session_id}")
                return {"error": "Assessment not found"}
            
            # Get all responses
            responses = progress_tracker.get_all_responses(session_id)
            
            # Get progress information
            progress_info = progress_tracker.get_assessment_progress(session_id)
            
            # Get completed sections
            completed_sections = progress_tracker.get_completed_sections(session_id)
            
            # Build the complete state
            state = {
                "session": session_details,
                "assessment": assessment_details,
                "responses": responses,
                "progress": progress_info,
                "completed_sections": completed_sections,
                "current_section": session_details.get("current_section"),
                "current_question": session_details.get("current_question"),
                "restored_at": datetime.utcnow().isoformat()
            }
            
            logger.info(f"Successfully restored state for session {session_id}")
            return state
            
        except Exception as e:
            logger.error(f"Error restoring session state: {str(e)}")
            return {"error": str(e)}
    
    @staticmethod
    def _get_assessment_details(assessment_id: int) -> Optional[Dict[str, Any]]:
        """
        Get assessment details
        
        Args:
            assessment_id: Assessment ID
            
        Returns:
            Assessment details or None if not found
        """
        try:
            db = get_session()
            
            assessment = db.query(Assessment).filter(
                Assessment.id == assessment_id
            ).first()
            
            if not assessment:
                return None
            
            return {
                "id": assessment.id,
                "name": assessment.name,
                "description": assessment.description,
                "framework_version": assessment.framework_version,
                "total_questions": assessment.total_questions,
                "total_sections": assessment.total_sections
            }
            
        except Exception as e:
            logger.error(f"Error getting assessment details: {str(e)}")
            return None
        finally:
            db.close()
    
    @staticmethod
    def validate_restored_state(state: Dict[str, Any]) -> Tuple[bool, str]:
        """
        Validate that a restored state is complete and consistent
        
        Args:
            state: Restored session state
            
        Returns:
            (is_valid, message) tuple
        """
        try:
            # Check for required keys
            required_keys = ["session", "assessment", "responses", "progress"]
            for key in required_keys:
                if key not in state:
                    return False, f"Missing required key: {key}"
            
            # Check session details
            session = state["session"]
            if not session.get("session_id"):
                return False, "Missing session ID"
            
            # Check assessment details
            assessment = state["assessment"]
            if not assessment.get("id"):
                return False, "Missing assessment ID"
            
            # Check progress information
            progress = state["progress"]
            if "completion_percentage" not in progress:
                return False, "Missing completion percentage"
            
            return True, "State is valid"
            
        except Exception as e:
            logger.error(f"Error validating restored state: {str(e)}")
            return False, str(e)
    
    @staticmethod
    def get_resumable_sessions(user_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get all sessions that can be resumed
        
        Args:
            user_id: Optional user identifier
            
        Returns:
            List of resumable session summaries
        """
        try:
            # Get incomplete sessions
            incomplete_sessions = session_manager.get_incomplete_sessions(user_id)
            
            # Build summaries
            resumable_sessions = []
            for session in incomplete_sessions:
                assessment_id = session.get("assessment_id")
                assessment_details = StateRestorer._get_assessment_details(assessment_id)
                
                if not assessment_details:
                    continue
                
                # Get progress information
                progress_info = progress_tracker.get_assessment_progress(session.get("session_id"))
                
                resumable_sessions.append({
                    "session_id": session.get("session_id"),
                    "assessment_name": assessment_details.get("name", "Unnamed Assessment"),
                    "start_time": session.get("start_time"),
                    "last_activity": session.get("last_activity"),
                    "completion_percentage": progress_info.get("completion_percentage", 0.0),
                    "sections_completed": progress_info.get("sections_completed", 0),
                    "total_sections": progress_info.get("total_sections", 0)
                })
            
            return resumable_sessions
            
        except Exception as e:
            logger.error(f"Error getting resumable sessions: {str(e)}")
            return []

# Create a global instance
state_restorer = StateRestorer()