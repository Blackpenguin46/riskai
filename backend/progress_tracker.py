"""
Progress Tracker for RiskAI
Tracks and manages assessment progress across sessions
"""

import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime

from database.models import get_session
from database.session_models import AssessmentSession, SectionProgress, SessionResponse
from session_manager import session_manager

logger = logging.getLogger(__name__)

class ProgressTracker:
    """Tracks and manages assessment progress"""
    
    @staticmethod
    def track_question_response(session_id: str, question_id: str, section_id: str, 
                              response: Any, question_type: str = "text") -> bool:
        """
        Track a question response and update progress
        
        Args:
            session_id: Unique identifier for the session
            question_id: Question identifier
            section_id: Section identifier
            response: User's response
            question_type: Type of question/response
            
        Returns:
            Success status
        """
        try:
            # Save response using session manager
            success = session_manager.save_response(
                session_id=session_id,
                question_id=question_id,
                section_id=section_id,
                response_value=response,
                response_type=question_type
            )
            
            if not success:
                logger.error(f"Failed to save response for question {question_id}")
                return False
            
            logger.info(f"Tracked response for question {question_id} in section {section_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error tracking question response: {str(e)}")
            return False
    
    @staticmethod
    def get_section_progress(session_id: str, section_id: str) -> Dict[str, Any]:
        """
        Get progress for a specific section
        
        Args:
            session_id: Unique identifier for the session
            section_id: Section identifier
            
        Returns:
            Section progress details
        """
        try:
            db = get_session()
            
            # Get session
            session = db.query(AssessmentSession).filter(
                AssessmentSession.session_id == session_id
            ).first()
            
            if not session:
                logger.warning(f"Session {session_id} not found for getting section progress")
                return {
                    "section_id": section_id,
                    "completion_percentage": 0.0,
                    "completed_questions": 0,
                    "total_questions": 0,
                    "is_complete": False
                }
            
            # Get section progress
            section_progress = db.query(SectionProgress).filter(
                SectionProgress.session_id == session.id,
                SectionProgress.section_id == section_id
            ).first()
            
            if not section_progress:
                return {
                    "section_id": section_id,
                    "completion_percentage": 0.0,
                    "completed_questions": 0,
                    "total_questions": 0,
                    "is_complete": False
                }
            
            return section_progress.to_dict()
            
        except Exception as e:
            logger.error(f"Error getting section progress: {str(e)}")
            return {
                "section_id": section_id,
                "completion_percentage": 0.0,
                "completed_questions": 0,
                "total_questions": 0,
                "is_complete": False,
                "error": str(e)
            }
        finally:
            db.close()
    
    @staticmethod
    def get_assessment_progress(session_id: str) -> Dict[str, Any]:
        """
        Get overall progress for an assessment
        
        Args:
            session_id: Unique identifier for the session
            
        Returns:
            Assessment progress details
        """
        try:
            db = get_session()
            
            # Get session
            session = db.query(AssessmentSession).filter(
                AssessmentSession.session_id == session_id
            ).first()
            
            if not session:
                logger.warning(f"Session {session_id} not found for getting assessment progress")
                return {
                    "completion_percentage": 0.0,
                    "sections_completed": 0,
                    "total_sections": 0,
                    "status": "not_found"
                }
            
            # Get all section progress records
            section_progress_records = db.query(SectionProgress).filter(
                SectionProgress.session_id == session.id
            ).all()
            
            # Calculate overall progress
            total_sections = len(section_progress_records)
            completed_sections = sum(1 for sp in section_progress_records if sp.is_complete)
            
            if total_sections == 0:
                completion_percentage = 0.0
            else:
                # Average of section completion percentages
                completion_percentage = sum(
                    sp.completion_percentage for sp in section_progress_records
                ) / total_sections
            
            return {
                "completion_percentage": completion_percentage,
                "sections_completed": completed_sections,
                "total_sections": total_sections,
                "status": session.completion_status,
                "section_progress": [sp.to_dict() for sp in section_progress_records]
            }
            
        except Exception as e:
            logger.error(f"Error getting assessment progress: {str(e)}")
            return {
                "completion_percentage": 0.0,
                "sections_completed": 0,
                "total_sections": 0,
                "status": "error",
                "error": str(e)
            }
        finally:
            db.close()
    
    @staticmethod
    def mark_section_complete(session_id: str, section_id: str, total_questions: int) -> bool:
        """
        Mark a section as complete
        
        Args:
            session_id: Unique identifier for the session
            section_id: Section identifier
            total_questions: Total number of questions in the section
            
        Returns:
            Success status
        """
        try:
            return session_manager.complete_section(
                session_id=session_id,
                section_id=section_id,
                total_questions=total_questions
            )
        except Exception as e:
            logger.error(f"Error marking section complete: {str(e)}")
            return False
    
    @staticmethod
    def get_completed_sections(session_id: str) -> List[str]:
        """
        Get list of completed section IDs
        
        Args:
            session_id: Unique identifier for the session
            
        Returns:
            List of completed section IDs
        """
        try:
            db = get_session()
            
            # Get session
            session = db.query(AssessmentSession).filter(
                AssessmentSession.session_id == session_id
            ).first()
            
            if not session:
                logger.warning(f"Session {session_id} not found for getting completed sections")
                return []
            
            # Get completed sections
            completed_sections = db.query(SectionProgress).filter(
                SectionProgress.session_id == session.id,
                SectionProgress.is_complete == True
            ).all()
            
            return [section.section_id for section in completed_sections]
            
        except Exception as e:
            logger.error(f"Error getting completed sections: {str(e)}")
            return []
        finally:
            db.close()
    
    @staticmethod
    def get_section_responses(session_id: str, section_id: str) -> Dict[str, Any]:
        """
        Get all responses for a section
        
        Args:
            session_id: Unique identifier for the session
            section_id: Section identifier
            
        Returns:
            Dictionary of question_id -> response_value
        """
        try:
            db = get_session()
            
            # Get session
            session = db.query(AssessmentSession).filter(
                AssessmentSession.session_id == session_id
            ).first()
            
            if not session:
                logger.warning(f"Session {session_id} not found for getting section responses")
                return {}
            
            # Get responses for section
            responses = db.query(SessionResponse).filter(
                SessionResponse.session_id == session.id,
                SessionResponse.section_id == section_id
            ).all()
            
            return {response.question_id: response.response_value for response in responses}
            
        except Exception as e:
            logger.error(f"Error getting section responses: {str(e)}")
            return {}
        finally:
            db.close()
    
    @staticmethod
    def get_all_responses(session_id: str) -> Dict[str, Dict[str, Any]]:
        """
        Get all responses for a session, organized by section
        
        Args:
            session_id: Unique identifier for the session
            
        Returns:
            Dictionary of section_id -> {question_id -> response_value}
        """
        try:
            db = get_session()
            
            # Get session
            session = db.query(AssessmentSession).filter(
                AssessmentSession.session_id == session_id
            ).first()
            
            if not session:
                logger.warning(f"Session {session_id} not found for getting all responses")
                return {}
            
            # Get all responses
            responses = db.query(SessionResponse).filter(
                SessionResponse.session_id == session.id
            ).all()
            
            # Organize by section
            result = {}
            for response in responses:
                if response.section_id not in result:
                    result[response.section_id] = {}
                result[response.section_id][response.question_id] = response.response_value
            
            return result
            
        except Exception as e:
            logger.error(f"Error getting all responses: {str(e)}")
            return {}
        finally:
            db.close()

# Create a global instance
progress_tracker = ProgressTracker()