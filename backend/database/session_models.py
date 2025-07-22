"""
Session Management Database Models
Handles persistence of assessment sessions and progress tracking
"""

from sqlalchemy import Column, String, Integer, Float, Text, DateTime, Boolean, JSON, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from .models import Base

class AssessmentSession(Base):
    """Assessment session for persistence across multiple user sessions"""
    __tablename__ = "assessment_sessions"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(String(100), nullable=False, unique=True)
    assessment_id = Column(Integer, ForeignKey("assessments.id"), nullable=False)
    user_id = Column(String(100), nullable=True)  # Optional user identification
    
    # Session metadata
    start_time = Column(DateTime, default=datetime.utcnow)
    last_activity = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completion_status = Column(String(50), default="in_progress")  # in_progress, completed, abandoned
    current_section = Column(String(100), nullable=True)
    current_question = Column(String(100), nullable=True)
    
    # Relationships
    section_progress = relationship("SectionProgress", back_populates="session", cascade="all, delete-orphan")
    responses = relationship("SessionResponse", back_populates="session", cascade="all, delete-orphan")
    
    # Session state
    state_data = Column(JSON, nullable=True)  # Additional state data
    
    def to_dict(self):
        """Convert session to dictionary"""
        return {
            "id": self.id,
            "session_id": self.session_id,
            "assessment_id": self.assessment_id,
            "user_id": self.user_id,
            "start_time": self.start_time.isoformat() if self.start_time else None,
            "last_activity": self.last_activity.isoformat() if self.last_activity else None,
            "completion_status": self.completion_status,
            "current_section": self.current_section,
            "current_question": self.current_question,
            "section_progress": [sp.to_dict() for sp in self.section_progress],
            "responses": [r.to_dict() for r in self.responses],
            "state_data": self.state_data
        }

class SectionProgress(Base):
    """Progress tracking for assessment sections"""
    __tablename__ = "section_progress"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(Integer, ForeignKey("assessment_sessions.id"), nullable=False)
    section_id = Column(String(100), nullable=False)
    
    # Progress data
    completion_percentage = Column(Float, default=0.0)
    completed_questions = Column(Integer, default=0)
    total_questions = Column(Integer, default=0)
    last_question_answered = Column(String(100), nullable=True)
    
    # Status
    is_complete = Column(Boolean, default=False)
    completed_at = Column(DateTime, nullable=True)
    
    # Relationship
    session = relationship("AssessmentSession", back_populates="section_progress")
    
    def to_dict(self):
        """Convert section progress to dictionary"""
        return {
            "id": self.id,
            "section_id": self.section_id,
            "completion_percentage": self.completion_percentage,
            "completed_questions": self.completed_questions,
            "total_questions": self.total_questions,
            "last_question_answered": self.last_question_answered,
            "is_complete": self.is_complete,
            "completed_at": self.completed_at.isoformat() if self.completed_at else None
        }

class SessionResponse(Base):
    """Individual question responses within a session"""
    __tablename__ = "session_responses"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    session_id = Column(Integer, ForeignKey("assessment_sessions.id"), nullable=False)
    question_id = Column(String(100), nullable=False)
    section_id = Column(String(100), nullable=False)
    
    # Response data
    response_value = Column(Text, nullable=True)  # The actual response
    response_type = Column(String(50), nullable=True)  # Type of response (text, choice, etc.)
    
    # Metadata
    response_time = Column(DateTime, default=datetime.utcnow)
    time_spent_seconds = Column(Integer, nullable=True)
    
    # Relationship
    session = relationship("AssessmentSession", back_populates="responses")
    
    def to_dict(self):
        """Convert response to dictionary"""
        return {
            "id": self.id,
            "question_id": self.question_id,
            "section_id": self.section_id,
            "response_value": self.response_value,
            "response_type": self.response_type,
            "response_time": self.response_time.isoformat() if self.response_time else None,
            "time_spent_seconds": self.time_spent_seconds
        }