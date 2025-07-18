"""
Session Management System

Provides automatic session persistence, data recovery, and user state management
for improved user experience and data continuity.
"""

import logging
import uuid
import json
import hashlib
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from sqlalchemy.orm import Session
from .database.models import SessionData, AssessmentHistory, ImprovementTracking, get_session
import threading
import time

logger = logging.getLogger(__name__)

@dataclass
class SessionInfo:
    """Session information"""
    session_id: str
    company_id: Optional[int]
    session_type: str
    created_at: datetime
    last_activity: datetime
    total_time_spent: int
    page_views: int
    progress_data: Dict[str, Any]
    preferences: Dict[str, Any]

class SessionManager:
    """Manages user sessions and automatic data persistence"""
    
    def __init__(self):
        self.active_sessions: Dict[str, SessionInfo] = {}
        self.session_timeout = timedelta(hours=24)  # 24-hour timeout
        self.cleanup_interval = 3600  # Clean up every hour
        self.auto_save_interval = 300  # Auto-save every 5 minutes
        
        # Start background tasks
        self._start_background_tasks()
        
    def _start_background_tasks(self):
        """Start background tasks for session management"""
        
        # Session cleanup thread
        cleanup_thread = threading.Thread(target=self._cleanup_expired_sessions, daemon=True)
        cleanup_thread.start()
        
        # Auto-save thread
        autosave_thread = threading.Thread(target=self._auto_save_sessions, daemon=True)
        autosave_thread.start()
        
    def create_session(self, 
                      company_id: Optional[int] = None,
                      session_type: str = "assessment",
                      user_agent: str = "",
                      ip_address: str = "") -> str:
        """Create a new session"""
        
        session_id = str(uuid.uuid4())
        
        # Create session info
        session_info = SessionInfo(
            session_id=session_id,
            company_id=company_id,
            session_type=session_type,
            created_at=datetime.utcnow(),
            last_activity=datetime.utcnow(),
            total_time_spent=0,
            page_views=0,
            progress_data={},
            preferences={}
        )
        
        # Store in memory
        self.active_sessions[session_id] = session_info
        
        # Store in database
        db = get_session()
        try:
            db_session = SessionData(
                session_id=session_id,
                company_id=company_id,
                session_type=session_type,
                user_agent=user_agent,
                ip_address=ip_address,
                expires_at=datetime.utcnow() + self.session_timeout
            )
            db.add(db_session)
            db.commit()
            
            logger.info(f"Created new session: {session_id}")
            
        except Exception as e:
            logger.error(f"Error creating session in database: {e}")
            db.rollback()
        finally:
            db.close()
            
        return session_id
    
    def get_session(self, session_id: str) -> Optional[SessionInfo]:
        """Get session information"""
        
        # Check memory first
        if session_id in self.active_sessions:
            return self.active_sessions[session_id]
            
        # Load from database
        db = get_session()
        try:
            db_session = db.query(SessionData).filter(
                SessionData.session_id == session_id
            ).first()
            
            if db_session and db_session.expires_at > datetime.utcnow():
                # Load into memory
                session_info = SessionInfo(
                    session_id=db_session.session_id,
                    company_id=db_session.company_id,
                    session_type=db_session.session_type,
                    created_at=db_session.created_at,
                    last_activity=db_session.last_activity,
                    total_time_spent=db_session.total_time_spent or 0,
                    page_views=db_session.page_views or 0,
                    progress_data=db_session.progress_data or {},
                    preferences=db_session.preferences or {}
                )
                
                self.active_sessions[session_id] = session_info
                return session_info
                
        except Exception as e:
            logger.error(f"Error loading session from database: {e}")
        finally:
            db.close()
            
        return None
    
    def update_session_activity(self, session_id: str, page: str = "", time_spent: int = 0):
        """Update session activity"""
        
        session_info = self.get_session(session_id)
        if not session_info:
            return
            
        # Update in memory
        session_info.last_activity = datetime.utcnow()
        session_info.page_views += 1
        session_info.total_time_spent += time_spent
        
        # Update database
        db = get_session()
        try:
            db_session = db.query(SessionData).filter(
                SessionData.session_id == session_id
            ).first()
            
            if db_session:
                db_session.last_activity = datetime.utcnow()
                db_session.page_views = session_info.page_views
                db_session.total_time_spent = session_info.total_time_spent
                db_session.current_page = page
                db.commit()
                
        except Exception as e:
            logger.error(f"Error updating session activity: {e}")
            db.rollback()
        finally:
            db.close()
    
    def save_progress_data(self, session_id: str, progress_data: Dict[str, Any]):
        """Save progress data for session"""
        
        session_info = self.get_session(session_id)
        if not session_info:
            return
            
        # Update in memory
        session_info.progress_data.update(progress_data)
        
        # Update database
        db = get_session()
        try:
            db_session = db.query(SessionData).filter(
                SessionData.session_id == session_id
            ).first()
            
            if db_session:
                db_session.progress_data = session_info.progress_data
                db.commit()
                
        except Exception as e:
            logger.error(f"Error saving progress data: {e}")
            db.rollback()
        finally:
            db.close()
    
    def get_progress_data(self, session_id: str) -> Dict[str, Any]:
        """Get progress data for session"""
        
        session_info = self.get_session(session_id)
        if session_info:
            return session_info.progress_data
        return {}
    
    def save_preferences(self, session_id: str, preferences: Dict[str, Any]):
        """Save user preferences"""
        
        session_info = self.get_session(session_id)
        if not session_info:
            return
            
        # Update in memory
        session_info.preferences.update(preferences)
        
        # Update database
        db = get_session()
        try:
            db_session = db.query(SessionData).filter(
                SessionData.session_id == session_id
            ).first()
            
            if db_session:
                db_session.preferences = session_info.preferences
                db.commit()
                
        except Exception as e:
            logger.error(f"Error saving preferences: {e}")
            db.rollback()
        finally:
            db.close()
    
    def get_preferences(self, session_id: str) -> Dict[str, Any]:
        """Get user preferences"""
        
        session_info = self.get_session(session_id)
        if session_info:
            return session_info.preferences
        return {}
    
    def recover_session_data(self, session_id: str) -> Dict[str, Any]:
        """Recover all session data for resuming"""
        
        session_info = self.get_session(session_id)
        if not session_info:
            return {"error": "Session not found"}
            
        # Get additional data from database
        db = get_session()
        try:
            # Get recent assessment history
            assessment_history = db.query(AssessmentHistory).filter(
                AssessmentHistory.company_id == session_info.company_id
            ).order_by(AssessmentHistory.snapshot_date.desc()).limit(5).all()
            
            # Get improvement tracking
            improvements = db.query(ImprovementTracking).filter(
                ImprovementTracking.company_id == session_info.company_id,
                ImprovementTracking.status.in_(['in_progress', 'planned'])
            ).all()
            
            return {
                "session_info": asdict(session_info),
                "progress_data": session_info.progress_data,
                "preferences": session_info.preferences,
                "assessment_history": [
                    {
                        "id": h.id,
                        "snapshot_date": h.snapshot_date.isoformat(),
                        "overall_score": h.overall_score,
                        "maturity_level": h.maturity_level,
                        "section_scores": h.section_scores
                    } for h in assessment_history
                ],
                "active_improvements": [
                    {
                        "id": i.id,
                        "name": i.initiative_name,
                        "status": i.status,
                        "progress": i.impact_percentage or 0,
                        "target_date": i.target_date.isoformat() if i.target_date else None
                    } for i in improvements
                ]
            }
            
        except Exception as e:
            logger.error(f"Error recovering session data: {e}")
            return {"error": "Failed to recover session data"}
        finally:
            db.close()
    
    def delete_session(self, session_id: str):
        """Delete a session"""
        
        # Remove from memory
        if session_id in self.active_sessions:
            del self.active_sessions[session_id]
            
        # Remove from database
        db = get_session()
        try:
            db_session = db.query(SessionData).filter(
                SessionData.session_id == session_id
            ).first()
            
            if db_session:
                db.delete(db_session)
                db.commit()
                
        except Exception as e:
            logger.error(f"Error deleting session: {e}")
            db.rollback()
        finally:
            db.close()
    
    def _cleanup_expired_sessions(self):
        """Background task to clean up expired sessions"""
        
        while True:
            try:
                time.sleep(self.cleanup_interval)
                
                db = get_session()
                try:
                    # Find expired sessions
                    expired_sessions = db.query(SessionData).filter(
                        SessionData.expires_at < datetime.utcnow()
                    ).all()
                    
                    for session in expired_sessions:
                        # Remove from memory
                        if session.session_id in self.active_sessions:
                            del self.active_sessions[session.session_id]
                        
                        # Remove from database
                        db.delete(session)
                    
                    db.commit()
                    
                    if expired_sessions:
                        logger.info(f"Cleaned up {len(expired_sessions)} expired sessions")
                        
                except Exception as e:
                    logger.error(f"Error cleaning up sessions: {e}")
                    db.rollback()
                finally:
                    db.close()
                    
            except Exception as e:
                logger.error(f"Error in cleanup thread: {e}")
    
    def _auto_save_sessions(self):
        """Background task to auto-save active sessions"""
        
        while True:
            try:
                time.sleep(self.auto_save_interval)
                
                if not self.active_sessions:
                    continue
                    
                db = get_session()
                try:
                    for session_id, session_info in self.active_sessions.items():
                        db_session = db.query(SessionData).filter(
                            SessionData.session_id == session_id
                        ).first()
                        
                        if db_session:
                            db_session.last_activity = session_info.last_activity
                            db_session.total_time_spent = session_info.total_time_spent
                            db_session.page_views = session_info.page_views
                            db_session.progress_data = session_info.progress_data
                            db_session.preferences = session_info.preferences
                    
                    db.commit()
                    logger.debug(f"Auto-saved {len(self.active_sessions)} sessions")
                    
                except Exception as e:
                    logger.error(f"Error auto-saving sessions: {e}")
                    db.rollback()
                finally:
                    db.close()
                    
            except Exception as e:
                logger.error(f"Error in auto-save thread: {e}")
    
    def get_session_analytics(self, session_id: str) -> Dict[str, Any]:
        """Get analytics for a session"""
        
        session_info = self.get_session(session_id)
        if not session_info:
            return {"error": "Session not found"}
            
        # Calculate analytics
        duration = datetime.utcnow() - session_info.created_at
        avg_time_per_page = (session_info.total_time_spent / session_info.page_views) if session_info.page_views > 0 else 0
        
        return {
            "session_duration": duration.total_seconds(),
            "total_time_spent": session_info.total_time_spent,
            "page_views": session_info.page_views,
            "average_time_per_page": avg_time_per_page,
            "session_type": session_info.session_type,
            "progress_completion": len(session_info.progress_data)
        }
    
    def export_session_data(self, session_id: str) -> Optional[str]:
        """Export session data as JSON"""
        
        session_data = self.recover_session_data(session_id)
        if "error" in session_data:
            return None
            
        try:
            return json.dumps(session_data, indent=2, default=str)
        except Exception as e:
            logger.error(f"Error exporting session data: {e}")
            return None
    
    def import_session_data(self, session_data: str) -> Optional[str]:
        """Import session data and create new session"""
        
        try:
            data = json.loads(session_data)
            
            # Create new session
            session_id = self.create_session(
                company_id=data.get("session_info", {}).get("company_id"),
                session_type=data.get("session_info", {}).get("session_type", "assessment")
            )
            
            # Restore progress data
            if "progress_data" in data:
                self.save_progress_data(session_id, data["progress_data"])
                
            # Restore preferences
            if "preferences" in data:
                self.save_preferences(session_id, data["preferences"])
                
            return session_id
            
        except Exception as e:
            logger.error(f"Error importing session data: {e}")
            return None

# Global session manager instance
session_manager = SessionManager()