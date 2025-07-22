"""
Session Manager for RiskAI
Handles creation, retrieval, and updating of assessment sessions
"""

import logging
import uuid
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Union
from sqlalchemy.orm import Session as DBSession

from database.models import get_session
from database.session_models import AssessmentSession, SectionProgress, SessionResponse

logger = logging.getLogger(__name__)

class SessionManager:
    """Manages assessment sessions for persistence across multiple user sessions"""
    
    @staticmethod
    def create_session(assessment_id: int, user_id: Optional[str] = None) -> str:
        """
        Create a new assessment session
        
        Args:
            assessment_id: ID of the assessment
            user_id: Optional user identifier
            
        Returns:
            session_id: Unique identifier for the session
        """
        try:
            db = get_session()
            
            # Generate a unique session ID
            session_id = f"session_{uuid.uuid4().hex}"
            
            # Create session record
            session = AssessmentSession(
                session_id=session_id,
                assessment_id=assessment_id,
                user_id=user_id,
                start_time=datetime.utcnow(),
                last_activity=datetime.utcnow(),
                completion_status="in_progress"
            )
            
            db.add(session)
            db.commit()
            db.refresh(session)
            
            logger.info(f"Created new session {session_id} for assessment {assessment_id}")
            return session_id
            
        except Exception as e:
            logger.error(f"Error creating session: {str(e)}")
            db.rollback()
            raise
        finally:
            db.close()
    
    @staticmethod
    def get_session(session_id: str) -> Optional[Dict[str, Any]]:
        """
        Get session details by session ID
        
        Args:
            session_id: Unique identifier for the session
            
        Returns:
            Session details as dictionary or None if not found
        """
        try:
            db = get_session()
            
            session = db.query(AssessmentSession).filter(
                AssessmentSession.session_id == session_id
            ).first()
            
            if not session:
                logger.warning(f"Session {session_id} not found")
                return None
            
            # Update last activity
            session.last_activity = datetime.utcnow()
            db.commit()
            
            return session.to_dict()
            
        except Exception as e:
            logger.error(f"Error retrieving session {session_id}: {str(e)}")
            return None
        finally:
            db.close()
    
    @staticmethod
    def update_session(session_id: str, update_data: Dict[str, Any]) -> bool:
        """
        Update session details
        
        Args:
            session_id: Unique identifier for the session
            update_data: Dictionary of fields to update
            
        Returns:
            Success status
        """
        try:
            db = get_session()
            
            session = db.query(AssessmentSession).filter(
                AssessmentSession.session_id == session_id
            ).first()
            
            if not session:
                logger.warning(f"Session {session_id} not found for update")
                return False
            
            # Update allowed fields
            allowed_fields = [
                "current_section", "current_question", "completion_status", "state_data"
            ]
            
            for field in allowed_fields:
                if field in update_data:
                    setattr(session, field, update_data[field])
            
            # Always update last activity
            session.last_activity = datetime.utcnow()
            
            db.commit()
            logger.info(f"Updated session {session_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error updating session {session_id}: {str(e)}")
            db.rollback()
            return False
        finally:
            db.close()
    
    @staticmethod
    def save_response(session_id: str, question_id: str, section_id: str, 
                     response_value: Any, response_type: Optional[str] = None,
                     time_spent_seconds: Optional[int] = None) -> bool:
        """
        Save a question response
        
        Args:
            session_id: Unique identifier for the session
            question_id: Question identifier
            section_id: Section identifier
            response_value: User's response
            response_type: Type of response (text, choice, etc.)
            time_spent_seconds: Time spent on the question
            
        Returns:
            Success status
        """
        try:
            db = get_session()
            
            # Get session
            session = db.query(AssessmentSession).filter(
                AssessmentSession.session_id == session_id
            ).first()
            
            if not session:
                logger.warning(f"Session {session_id} not found for saving response")
                return False
            
            # Check if response already exists
            existing_response = db.query(SessionResponse).filter(
                SessionResponse.session_id == session.id,
                SessionResponse.question_id == question_id
            ).first()
            
            if existing_response:
                # Update existing response
                existing_response.response_value = str(response_value)
                existing_response.response_type = response_type
                existing_response.response_time = datetime.utcnow()
                if time_spent_seconds:
                    existing_response.time_spent_seconds = time_spent_seconds
            else:
                # Create new response
                response = SessionResponse(
                    session_id=session.id,
                    question_id=question_id,
                    section_id=section_id,
                    response_value=str(response_value),
                    response_type=response_type,
                    response_time=datetime.utcnow(),
                    time_spent_seconds=time_spent_seconds
                )
                db.add(response)
            
            # Update session
            session.last_activity = datetime.utcnow()
            session.current_question = question_id
            session.current_section = section_id
            
            # Update section progress
            SessionManager._update_section_progress(db, session.id, section_id, question_id)
            
            db.commit()
            logger.info(f"Saved response for question {question_id} in session {session_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error saving response in session {session_id}: {str(e)}")
            db.rollback()
            return False
        finally:
            db.close()
    
    @staticmethod
    def _update_section_progress(db: DBSession, session_id: int, section_id: str, question_id: str) -> None:
        """
        Update section progress after saving a response
        
        Args:
            db: Database session
            session_id: Session ID (database ID, not session_id string)
            section_id: Section identifier
            question_id: Question identifier
        """
        # Get or create section progress
        section_progress = db.query(SectionProgress).filter(
            SectionProgress.session_id == session_id,
            SectionProgress.section_id == section_id
        ).first()
        
        if not section_progress:
            # Create new section progress
            section_progress = SectionProgress(
                session_id=session_id,
                section_id=section_id,
                completion_percentage=0.0,
                completed_questions=0,
                total_questions=0,  # Will be updated when we know the total
                last_question_answered=question_id
            )
            db.add(section_progress)
        else:
            # Update existing section progress
            section_progress.last_question_answered = question_id
        
        # Count responses for this section
        response_count = db.query(SessionResponse).filter(
            SessionResponse.session_id == session_id,
            SessionResponse.section_id == section_id
        ).count()
        
        # Update completion data
        section_progress.completed_questions = response_count
        
        # If we know the total questions, update percentage
        if section_progress.total_questions > 0:
            section_progress.completion_percentage = (
                response_count / section_progress.total_questions
            ) * 100.0
    
    @staticmethod
    def complete_section(session_id: str, section_id: str, total_questions: int) -> bool:
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
            db = get_session()
            
            # Get session
            session = db.query(AssessmentSession).filter(
                AssessmentSession.session_id == session_id
            ).first()
            
            if not session:
                logger.warning(f"Session {session_id} not found for completing section")
                return False
            
            # Get section progress
            section_progress = db.query(SectionProgress).filter(
                SectionProgress.session_id == session.id,
                SectionProgress.section_id == section_id
            ).first()
            
            if not section_progress:
                # Create new section progress
                section_progress = SectionProgress(
                    session_id=session.id,
                    section_id=section_id,
                    completion_percentage=100.0,
                    completed_questions=total_questions,
                    total_questions=total_questions,
                    is_complete=True,
                    completed_at=datetime.utcnow()
                )
                db.add(section_progress)
            else:
                # Update existing section progress
                section_progress.total_questions = total_questions
                section_progress.completion_percentage = 100.0
                section_progress.is_complete = True
                section_progress.completed_at = datetime.utcnow()
            
            # Update session
            session.last_activity = datetime.utcnow()
            
            db.commit()
            logger.info(f"Marked section {section_id} as complete in session {session_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error completing section in session {session_id}: {str(e)}")
            db.rollback()
            return False
        finally:
            db.close()
    
    @staticmethod
    def get_user_sessions(user_id: str) -> List[Dict[str, Any]]:
        """
        Get all sessions for a user
        
        Args:
            user_id: User identifier
            
        Returns:
            List of session details
        """
        try:
            db = get_session()
            
            sessions = db.query(AssessmentSession).filter(
                AssessmentSession.user_id == user_id
            ).order_by(AssessmentSession.last_activity.desc()).all()
            
            return [session.to_dict() for session in sessions]
            
        except Exception as e:
            logger.error(f"Error retrieving sessions for user {user_id}: {str(e)}")
            return []
        finally:
            db.close()
    
    @staticmethod
    def get_incomplete_sessions(user_id: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get all incomplete sessions, optionally filtered by user
        
        Args:
            user_id: Optional user identifier
            
        Returns:
            List of session details
        """
        try:
            db = get_session()
            
            query = db.query(AssessmentSession).filter(
                AssessmentSession.completion_status == "in_progress"
            )
            
            if user_id:
                query = query.filter(AssessmentSession.user_id == user_id)
            
            sessions = query.order_by(AssessmentSession.last_activity.desc()).all()
            
            return [session.to_dict() for session in sessions]
            
        except Exception as e:
            logger.error(f"Error retrieving incomplete sessions: {str(e)}")
            return []
        finally:
            db.close()
    
    @staticmethod
    def resume_session(session_id: str) -> Optional[Dict[str, Any]]:
        """
        Resume an existing session
        
        Args:
            session_id: Unique identifier for the session
            
        Returns:
            Session details or None if not found
        """
        try:
            db = get_session()
            
            session = db.query(AssessmentSession).filter(
                AssessmentSession.session_id == session_id
            ).first()
            
            if not session:
                logger.warning(f"Session {session_id} not found for resuming")
                return None
            
            # Check if session is expired (inactive for more than 24 hours)
            if datetime.utcnow() - session.last_activity > timedelta(hours=24):
                logger.warning(f"Session {session_id} has expired")
                return None
            
            # Update last activity
            session.last_activity = datetime.utcnow()
            db.commit()
            
            return session.to_dict()
            
        except Exception as e:
            logger.error(f"Error resuming session {session_id}: {str(e)}")
            return None
        finally:
            db.close()
    
    @staticmethod
    def auto_save_session(session_id: str, current_question: str, current_section: str, 
                         auto_save_data: Optional[Dict[str, Any]] = None) -> bool:
        """
        Auto-save session state for recovery
        
        Args:
            session_id: Unique identifier for the session
            current_question: Current question being answered
            current_section: Current section being worked on
            auto_save_data: Additional data to save
            
        Returns:
            Success status
        """
        try:
            db = get_session()
            
            session = db.query(AssessmentSession).filter(
                AssessmentSession.session_id == session_id
            ).first()
            
            if not session:
                logger.warning(f"Session {session_id} not found for auto-save")
                return False
            
            # Update session state
            session.current_question = current_question
            session.current_section = current_section
            session.last_activity = datetime.utcnow()
            
            # Update state data if provided
            if auto_save_data:
                if session.state_data:
                    session.state_data.update(auto_save_data)
                else:
                    session.state_data = auto_save_data
            
            db.commit()
            logger.debug(f"Auto-saved session {session_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error auto-saving session {session_id}: {str(e)}")
            db.rollback()
            return False
        finally:
            db.close()
    
    @staticmethod
    def cleanup_expired_sessions(hours: int = 24) -> int:
        """
        Clean up sessions that have been inactive for more than specified hours
        
        Args:
            hours: Number of hours of inactivity before cleanup
            
        Returns:
            Number of sessions cleaned up
        """
        try:
            db = get_session()
            
            cutoff_time = datetime.utcnow() - timedelta(hours=hours)
            
            # Find expired sessions
            expired_sessions = db.query(AssessmentSession).filter(
                AssessmentSession.last_activity < cutoff_time,
                AssessmentSession.completion_status == "in_progress"
            ).all()
            
            count = len(expired_sessions)
            
            # Mark as abandoned instead of deleting
            for session in expired_sessions:
                session.completion_status = "abandoned"
            
            db.commit()
            logger.info(f"Cleaned up {count} expired sessions")
            return count
            
        except Exception as e:
            logger.error(f"Error cleaning up expired sessions: {str(e)}")
            db.rollback()
            return 0
        finally:
            db.close()
    
    @staticmethod
    def complete_session(session_id: str) -> bool:
        """
        Mark a session as complete
        
        Args:
            session_id: Unique identifier for the session
            
        Returns:
            Success status
        """
        try:
            db = get_session()
            
            session = db.query(AssessmentSession).filter(
                AssessmentSession.session_id == session_id
            ).first()
            
            if not session:
                logger.warning(f"Session {session_id} not found for completion")
                return False
            
            # Update session
            session.completion_status = "completed"
            session.last_activity = datetime.utcnow()
            
            db.commit()
            logger.info(f"Marked session {session_id} as complete")
            return True
            
        except Exception as e:
            logger.error(f"Error completing session {session_id}: {str(e)}")
            db.rollback()
            return False
        finally:
            db.close()

# Create a global instance
session_manager = SessionManager()