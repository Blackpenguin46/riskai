"""
Database Models for RiskAI
Handles persistence of assessment results, company data, and system state
"""

from sqlalchemy import create_engine, Column, String, Integer, Float, Text, DateTime, Boolean, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from datetime import datetime
import os
import json
from typing import Dict, Any, Optional

Base = declarative_base()

class Company(Base):
    """Company information and configuration"""
    __tablename__ = "companies"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(255), nullable=False)
    industry = Column(String(100))
    size = Column(String(50))  # e.g., "200-500 employees"
    country = Column(String(100))
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Configuration data
    settings = Column(JSON)  # Company-specific settings
    contact_info = Column(JSON)  # Contact information
    compliance_requirements = Column(JSON)  # Regulatory requirements

class Assessment(Base):
    """Assessment instances and metadata"""
    __tablename__ = "assessments"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    company_id = Column(Integer, nullable=True)  # Foreign key to companies
    name = Column(String(255), nullable=False)
    description = Column(Text)
    
    # Assessment metadata
    framework_version = Column(String(50), default="2.0")
    total_questions = Column(Integer, default=127)
    total_sections = Column(Integer, default=10)
    
    # Progress tracking
    status = Column(String(50), default="in_progress")  # in_progress, completed, archived
    completion_percentage = Column(Float, default=0.0)
    sections_completed = Column(Integer, default=0)
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    completed_at = Column(DateTime, nullable=True)
    
    # Results
    overall_score = Column(Float, nullable=True)
    maturity_level = Column(String(50), nullable=True)
    risk_level = Column(String(50), nullable=True)

class AssessmentResponse(Base):
    """Individual question responses"""
    __tablename__ = "assessment_responses"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    assessment_id = Column(Integer, nullable=False)  # Foreign key to assessments
    
    # Question identification
    section_id = Column(String(100), nullable=False)
    question_id = Column(String(100), nullable=False)
    
    # Response data
    response_value = Column(Text)  # The actual response (string, number, etc.)
    response_type = Column(String(50))  # likert_scale, multiple_choice, etc.
    
    # Scoring
    raw_score = Column(Float, nullable=True)
    weighted_score = Column(Float, nullable=True)
    confidence_level = Column(Float, nullable=True)
    
    # Metadata
    answered_at = Column(DateTime, default=datetime.utcnow)
    time_spent_seconds = Column(Integer, nullable=True)

class SectionScore(Base):
    """Section-level scoring results"""
    __tablename__ = "section_scores"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    assessment_id = Column(Integer, nullable=False)  # Foreign key to assessments
    section_id = Column(String(100), nullable=False)
    
    # Scoring results
    score = Column(Float, nullable=False)
    maturity_level = Column(String(50))
    maturity_description = Column(Text)
    
    # Progress
    questions_answered = Column(Integer, default=0)
    total_questions = Column(Integer, default=0)
    completion_rate = Column(Float, default=0.0)
    
    # Analysis
    risk_breakdown = Column(JSON)  # Risk level breakdown
    recommendations = Column(JSON)  # List of recommendations
    
    # Metadata
    completed_at = Column(DateTime, default=datetime.utcnow)

class CompanyDocument(Base):
    """Uploaded company documents and data"""
    __tablename__ = "company_documents"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    company_id = Column(Integer, nullable=True)  # Foreign key to companies
    
    # File information
    filename = Column(String(255), nullable=False)
    original_filename = Column(String(255), nullable=False)
    file_path = Column(String(500), nullable=False)
    file_size = Column(Integer)
    mime_type = Column(String(100))
    
    # Document metadata
    document_type = Column(String(100))  # policy, procedure, audit_report, etc.
    category = Column(String(100))
    description = Column(Text)
    
    # Processing status
    processed = Column(Boolean, default=False)
    extracted_content = Column(Text)  # AI-extracted content
    analysis_results = Column(JSON)  # Document analysis results
    
    # Timestamps
    uploaded_at = Column(DateTime, default=datetime.utcnow)
    processed_at = Column(DateTime, nullable=True)

class SystemState(Base):
    """System configuration and state"""
    __tablename__ = "system_state"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    key = Column(String(100), nullable=False, unique=True)
    value = Column(JSON)
    description = Column(Text)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class ChatHistory(Base):
    """Chat conversation history"""
    __tablename__ = "chat_history"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    company_id = Column(Integer, nullable=True)  # Foreign key to companies
    assessment_id = Column(Integer, nullable=True)  # Related assessment if any
    
    # Message data
    message_type = Column(String(50), nullable=False)  # user, assistant, system
    content = Column(Text, nullable=False)
    
    # Context
    context_data = Column(JSON)  # Additional context information
    session_id = Column(String(100))  # Group related messages
    
    # Timestamps
    created_at = Column(DateTime, default=datetime.utcnow)

# Database configuration
DATABASE_DIR = os.getenv("DATABASE_DIR", "/app/database_data")
os.makedirs(DATABASE_DIR, exist_ok=True)
DATABASE_URL = os.getenv("DATABASE_URL", f"sqlite:///{DATABASE_DIR}/riskai.db")
engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False} if "sqlite" in DATABASE_URL else {})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

def get_db():
    """Get database session"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_database():
    """Initialize database tables"""
    Base.metadata.create_all(bind=engine)
    print("Database initialized successfully")

def get_session():
    """Get a database session for direct use"""
    return SessionLocal()

# Database utility functions
class DatabaseManager:
    """Database management utilities"""
    
    @staticmethod
    def save_assessment_result(assessment_data: Dict[str, Any], company_id: Optional[int] = None) -> int:
        """Save complete assessment result"""
        db = get_session()
        try:
            # Create assessment record
            assessment = Assessment(
                company_id=company_id,
                name=assessment_data.get("name", f"Assessment {datetime.now().strftime('%Y-%m-%d %H:%M')}"),
                description=assessment_data.get("description", "RiskAI Security Assessment"),
                status="completed" if assessment_data.get("completed", False) else "in_progress",
                completion_percentage=assessment_data.get("completion_percentage", 0.0),
                sections_completed=assessment_data.get("sections_completed", 0),
                overall_score=assessment_data.get("overall_score"),
                maturity_level=assessment_data.get("maturity_level"),
                risk_level=assessment_data.get("risk_level"),
                completed_at=datetime.utcnow() if assessment_data.get("completed", False) else None
            )
            
            db.add(assessment)
            db.commit()
            db.refresh(assessment)
            
            # Save responses
            for section_id, responses in assessment_data.get("responses", {}).items():
                for question_id, response_value in responses.items():
                    response = AssessmentResponse(
                        assessment_id=assessment.id,
                        section_id=section_id,
                        question_id=question_id,
                        response_value=str(response_value),
                        answered_at=datetime.utcnow()
                    )
                    db.add(response)
            
            # Save section scores
            for section_id, score_data in assessment_data.get("section_scores", {}).items():
                section_score = SectionScore(
                    assessment_id=assessment.id,
                    section_id=section_id,
                    score=score_data.get("score", 0.0),
                    maturity_level=score_data.get("maturity_level", ""),
                    maturity_description=score_data.get("maturity_description", ""),
                    questions_answered=score_data.get("questions_answered", 0),
                    total_questions=score_data.get("total_questions", 0),
                    completion_rate=score_data.get("completion_rate", 0.0),
                    risk_breakdown=score_data.get("risk_breakdown", {}),
                    recommendations=score_data.get("recommendations", [])
                )
                db.add(section_score)
            
            db.commit()
            return assessment.id
            
        except Exception as e:
            db.rollback()
            print(f"Error saving assessment: {e}")
            raise
        finally:
            db.close()
    
    @staticmethod
    def load_assessment_result(assessment_id: int) -> Optional[Dict[str, Any]]:
        """Load complete assessment result"""
        db = get_session()
        try:
            # Get assessment
            assessment = db.query(Assessment).filter(Assessment.id == assessment_id).first()
            if not assessment:
                return None
            
            # Get responses
            responses = {}
            response_records = db.query(AssessmentResponse).filter(
                AssessmentResponse.assessment_id == assessment_id
            ).all()
            
            for response in response_records:
                if response.section_id not in responses:
                    responses[response.section_id] = {}
                responses[response.section_id][response.question_id] = response.response_value
            
            # Get section scores
            section_scores = {}
            score_records = db.query(SectionScore).filter(
                SectionScore.assessment_id == assessment_id
            ).all()
            
            for score in score_records:
                section_scores[score.section_id] = {
                    "score": score.score,
                    "maturity_level": score.maturity_level,
                    "maturity_description": score.maturity_description,
                    "questions_answered": score.questions_answered,
                    "total_questions": score.total_questions,
                    "completion_rate": score.completion_rate,
                    "risk_breakdown": score.risk_breakdown or {},
                    "recommendations": score.recommendations or []
                }
            
            return {
                "id": assessment.id,
                "name": assessment.name,
                "description": assessment.description,
                "status": assessment.status,
                "completion_percentage": assessment.completion_percentage,
                "sections_completed": assessment.sections_completed,
                "overall_score": assessment.overall_score,
                "maturity_level": assessment.maturity_level,
                "risk_level": assessment.risk_level,
                "created_at": assessment.created_at.isoformat(),
                "completed_at": assessment.completed_at.isoformat() if assessment.completed_at else None,
                "responses": responses,
                "section_scores": section_scores
            }
            
        except Exception as e:
            print(f"Error loading assessment: {e}")
            return None
        finally:
            db.close()
    
    @staticmethod
    def get_latest_assessment(company_id: Optional[int] = None) -> Optional[Dict[str, Any]]:
        """Get the most recent assessment"""
        db = get_session()
        try:
            query = db.query(Assessment)
            if company_id:
                query = query.filter(Assessment.company_id == company_id)
            
            assessment = query.order_by(Assessment.created_at.desc()).first()
            if assessment:
                return DatabaseManager.load_assessment_result(assessment.id)
            return None
            
        except Exception as e:
            print(f"Error getting latest assessment: {e}")
            return None
        finally:
            db.close()
    
    @staticmethod
    def save_company_data(company_data: Dict[str, Any]) -> int:
        """Save company information"""
        db = get_session()
        try:
            company = Company(
                name=company_data.get("name", "Unknown Company"),
                industry=company_data.get("industry"),
                size=company_data.get("size"),
                country=company_data.get("country"),
                settings=company_data.get("settings", {}),
                contact_info=company_data.get("contact_info", {}),
                compliance_requirements=company_data.get("compliance_requirements", {})
            )
            
            db.add(company)
            db.commit()
            db.refresh(company)
            return company.id
            
        except Exception as e:
            db.rollback()
            print(f"Error saving company data: {e}")
            raise
        finally:
            db.close()
    
    @staticmethod
    def save_system_state(key: str, value: Any, description: str = "") -> None:
        """Save system state"""
        db = get_session()
        try:
            # Check if key exists
            existing = db.query(SystemState).filter(SystemState.key == key).first()
            if existing:
                existing.value = value
                existing.description = description
                existing.updated_at = datetime.utcnow()
            else:
                state = SystemState(key=key, value=value, description=description)
                db.add(state)
            
            db.commit()
            
        except Exception as e:
            db.rollback()
            print(f"Error saving system state: {e}")
            raise
        finally:
            db.close()
    
    @staticmethod
    def get_system_state(key: str) -> Any:
        """Get system state"""
        db = get_session()
        try:
            state = db.query(SystemState).filter(SystemState.key == key).first()
            return state.value if state else None
            
        except Exception as e:
            print(f"Error getting system state: {e}")
            return None
        finally:
            db.close()