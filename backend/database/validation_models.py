"""
Validation Data Models for RiskAI
Handles storage and retrieval of cross-industry validation data
"""

from sqlalchemy import Column, String, Integer, Float, Text, DateTime, Boolean, JSON, ForeignKey, Table
from sqlalchemy.orm import relationship
from datetime import datetime
from .models import Base

# Association table for many-to-many relationship between industries and frameworks
industry_framework_association = Table(
    'industry_framework_association',
    Base.metadata,
    Column('industry_id', Integer, ForeignKey('industry_sectors.id')),
    Column('framework_id', Integer, ForeignKey('security_frameworks.id'))
)

class IndustrySector(Base):
    """Industry sectors for cross-industry validation"""
    __tablename__ = "industry_sectors"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False, unique=True)
    description = Column(Text, nullable=True)
    
    # Relationships
    validations = relationship("IndustryValidation", back_populates="industry", cascade="all, delete-orphan")
    frameworks = relationship("SecurityFramework", secondary=industry_framework_association, back_populates="industries")
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description
        }

class SecurityFramework(Base):
    """Security frameworks used in assessments"""
    __tablename__ = "security_frameworks"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False, unique=True)
    version = Column(String(50), nullable=True)
    description = Column(Text, nullable=True)
    source_url = Column(String(255), nullable=True)
    
    # Relationships
    industries = relationship("IndustrySector", secondary=industry_framework_association, back_populates="frameworks")
    domains = relationship("SecurityDomain", back_populates="framework", cascade="all, delete-orphan")
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "version": self.version,
            "description": self.description,
            "source_url": self.source_url
        }

class SecurityDomain(Base):
    """Security domains within frameworks"""
    __tablename__ = "security_domains"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    framework_id = Column(Integer, ForeignKey("security_frameworks.id"), nullable=False)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=True)
    weight = Column(Float, default=1.0)  # Domain weight for scoring
    
    # Relationships
    framework = relationship("SecurityFramework", back_populates="domains")
    questions = relationship("AssessmentQuestion", back_populates="domain", cascade="all, delete-orphan")
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            "id": self.id,
            "framework_id": self.framework_id,
            "name": self.name,
            "description": self.description,
            "weight": self.weight
        }

class AssessmentQuestion(Base):
    """Assessment questions for security domains"""
    __tablename__ = "assessment_questions"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    domain_id = Column(Integer, ForeignKey("security_domains.id"), nullable=False)
    question_text = Column(Text, nullable=False)
    question_type = Column(String(50), nullable=False)  # text, select, multiselect, scale, boolean
    options = Column(JSON, nullable=True)  # For select/multiselect questions
    weight = Column(Float, default=1.0)  # Question weight for scoring
    guidance = Column(Text, nullable=True)  # Guidance for answering
    evidence_required = Column(Boolean, default=False)
    
    # Relationships
    domain = relationship("SecurityDomain", back_populates="questions")
    validation_responses = relationship("ValidationResponse", back_populates="question", cascade="all, delete-orphan")
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            "id": self.id,
            "domain_id": self.domain_id,
            "question_text": self.question_text,
            "question_type": self.question_type,
            "options": self.options,
            "weight": self.weight,
            "guidance": self.guidance,
            "evidence_required": self.evidence_required
        }

class IndustryValidation(Base):
    """Validation data for industry sectors"""
    __tablename__ = "industry_validations"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    industry_id = Column(Integer, ForeignKey("industry_sectors.id"), nullable=False)
    company_size = Column(String(50), nullable=False)  # small, medium, large, enterprise
    company_count = Column(Integer, default=0)
    
    # Validation metrics
    average_accuracy = Column(Float, nullable=True)
    confidence_interval_lower = Column(Float, nullable=True)
    confidence_interval_upper = Column(Float, nullable=True)
    precision_score = Column(Float, nullable=True)
    recall_score = Column(Float, nullable=True)
    f1_score = Column(Float, nullable=True)
    
    # Methodology
    validation_methodology = Column(Text, nullable=True)
    validation_date = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    industry = relationship("IndustrySector", back_populates="validations")
    validation_metrics = relationship("ValidationMetric", back_populates="industry_validation", cascade="all, delete-orphan")
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            "id": self.id,
            "industry_id": self.industry_id,
            "industry_name": self.industry.name if self.industry else None,
            "company_size": self.company_size,
            "company_count": self.company_count,
            "average_accuracy": self.average_accuracy,
            "confidence_interval": [self.confidence_interval_lower, self.confidence_interval_upper] if self.confidence_interval_lower and self.confidence_interval_upper else None,
            "precision_score": self.precision_score,
            "recall_score": self.recall_score,
            "f1_score": self.f1_score,
            "validation_methodology": self.validation_methodology,
            "validation_date": self.validation_date.isoformat() if self.validation_date else None
        }

class ValidationMetric(Base):
    """Specific validation metrics for industry validations"""
    __tablename__ = "validation_metrics"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    validation_id = Column(Integer, ForeignKey("industry_validations.id"), nullable=False)
    metric_name = Column(String(100), nullable=False)
    metric_value = Column(Float, nullable=False)
    metric_description = Column(Text, nullable=True)
    
    # Relationships
    industry_validation = relationship("IndustryValidation", back_populates="validation_metrics")
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            "id": self.id,
            "validation_id": self.validation_id,
            "metric_name": self.metric_name,
            "metric_value": self.metric_value,
            "metric_description": self.metric_description
        }

class ValidationResponse(Base):
    """Expert validation responses for assessment questions"""
    __tablename__ = "validation_responses"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    question_id = Column(Integer, ForeignKey("assessment_questions.id"), nullable=False)
    industry_id = Column(Integer, ForeignKey("industry_sectors.id"), nullable=False)
    company_size = Column(String(50), nullable=False)  # small, medium, large, enterprise
    
    # Response data
    expert_response = Column(Text, nullable=True)  # Expert's response
    riskai_response = Column(Text, nullable=True)  # RiskAI's response
    is_correct = Column(Boolean, nullable=True)  # Is RiskAI's response correct?
    confidence_score = Column(Float, nullable=True)  # Confidence in RiskAI's response
    
    # Metadata
    validation_date = Column(DateTime, default=datetime.utcnow)
    validator_id = Column(String(100), nullable=True)  # ID of the expert validator
    
    # Relationships
    question = relationship("AssessmentQuestion", back_populates="validation_responses")
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            "id": self.id,
            "question_id": self.question_id,
            "industry_id": self.industry_id,
            "company_size": self.company_size,
            "expert_response": self.expert_response,
            "riskai_response": self.riskai_response,
            "is_correct": self.is_correct,
            "confidence_score": self.confidence_score,
            "validation_date": self.validation_date.isoformat() if self.validation_date else None,
            "validator_id": self.validator_id
        }

class ScoringRubric(Base):
    """Scoring rubrics for assessment questions"""
    __tablename__ = "scoring_rubrics"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    domain_id = Column(Integer, ForeignKey("security_domains.id"), nullable=False)
    score_level = Column(Integer, nullable=False)  # 1-10
    description = Column(Text, nullable=False)
    criteria = Column(JSON, nullable=True)  # List of criteria for this score level
    
    # Industry-specific examples
    industry_examples = Column(JSON, nullable=True)  # Dict of industry -> example
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            "id": self.id,
            "domain_id": self.domain_id,
            "score_level": self.score_level,
            "description": self.description,
            "criteria": self.criteria,
            "industry_examples": self.industry_examples
        }

class IndustryBenchmark(Base):
    """Benchmark scores for industries and company sizes"""
    __tablename__ = "industry_benchmarks"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    industry_id = Column(Integer, ForeignKey("industry_sectors.id"), nullable=False)
    domain_id = Column(Integer, ForeignKey("security_domains.id"), nullable=False)
    company_size = Column(String(50), nullable=False)  # small, medium, large, enterprise
    
    # Benchmark data
    average_score = Column(Float, nullable=False)
    percentile_10 = Column(Float, nullable=True)
    percentile_25 = Column(Float, nullable=True)
    percentile_50 = Column(Float, nullable=True)
    percentile_75 = Column(Float, nullable=True)
    percentile_90 = Column(Float, nullable=True)
    
    # Metadata
    sample_size = Column(Integer, nullable=True)
    last_updated = Column(DateTime, default=datetime.utcnow)
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            "id": self.id,
            "industry_id": self.industry_id,
            "domain_id": self.domain_id,
            "company_size": self.company_size,
            "average_score": self.average_score,
            "percentile_distribution": {
                "10": self.percentile_10,
                "25": self.percentile_25,
                "50": self.percentile_50,
                "75": self.percentile_75,
                "90": self.percentile_90
            },
            "sample_size": self.sample_size,
            "last_updated": self.last_updated.isoformat() if self.last_updated else None
        }