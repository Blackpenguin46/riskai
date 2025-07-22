"""
Benchmark Data Models for RiskAI
Handles storage and retrieval of benchmark data for comparison with other GRC tools
"""

from sqlalchemy import Column, String, Integer, Float, Text, DateTime, Boolean, JSON, ForeignKey
from sqlalchemy.orm import relationship
from datetime import datetime
from .models import Base

class BenchmarkData(Base):
    """Benchmark data for GRC tools"""
    __tablename__ = "benchmark_data"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    tool_name = Column(String(100), nullable=False)
    category = Column(String(100), nullable=False)
    metric_name = Column(String(100), nullable=False)
    metric_value = Column(Float, nullable=False)
    unit = Column(String(50), nullable=True)
    
    # Metadata
    measurement_date = Column(DateTime, default=datetime.utcnow)
    measurement_methodology = Column(Text, nullable=True)
    source_reference = Column(String(255), nullable=True)
    
    # Relationships
    comparisons = relationship("ToolComparison", back_populates="benchmark_data", cascade="all, delete-orphan")
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            "id": self.id,
            "tool_name": self.tool_name,
            "category": self.category,
            "metric_name": self.metric_name,
            "metric_value": self.metric_value,
            "unit": self.unit,
            "measurement_date": self.measurement_date.isoformat() if self.measurement_date else None,
            "measurement_methodology": self.measurement_methodology,
            "source_reference": self.source_reference
        }

class ToolComparison(Base):
    """Comparison between RiskAI and other GRC tools"""
    __tablename__ = "tool_comparisons"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    benchmark_id = Column(Integer, ForeignKey("benchmark_data.id"), nullable=False)
    industry = Column(String(100), nullable=True)
    company_size = Column(String(50), nullable=True)
    
    # Comparison data
    riskai_value = Column(Float, nullable=False)
    comparison_value = Column(Float, nullable=False)
    percentage_difference = Column(Float, nullable=True)
    is_better = Column(Boolean, nullable=True)  # True if RiskAI is better
    
    # Analysis
    strengths = Column(JSON, nullable=True)  # List of strengths
    weaknesses = Column(JSON, nullable=True)  # List of weaknesses
    notes = Column(Text, nullable=True)
    
    # Relationship
    benchmark_data = relationship("BenchmarkData", back_populates="comparisons")
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            "id": self.id,
            "benchmark_id": self.benchmark_id,
            "industry": self.industry,
            "company_size": self.company_size,
            "riskai_value": self.riskai_value,
            "comparison_value": self.comparison_value,
            "percentage_difference": self.percentage_difference,
            "is_better": self.is_better,
            "strengths": self.strengths,
            "weaknesses": self.weaknesses,
            "notes": self.notes,
            "benchmark_data": self.benchmark_data.to_dict() if self.benchmark_data else None
        }

class ROIAnalysis(Base):
    """ROI analysis for RiskAI compared to traditional GRC approaches"""
    __tablename__ = "roi_analysis"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    company_size = Column(String(50), nullable=False)
    assessment_frequency = Column(Integer, nullable=True)  # Number of assessments per year
    
    # Cost data
    riskai_cost = Column(Float, nullable=False)
    traditional_cost = Column(Float, nullable=False)
    cost_savings = Column(Float, nullable=True)
    cost_savings_percentage = Column(Float, nullable=True)
    
    # Time data
    riskai_time = Column(Float, nullable=False)  # Hours
    traditional_time = Column(Float, nullable=False)  # Hours
    time_savings = Column(Float, nullable=True)  # Hours
    time_savings_percentage = Column(Float, nullable=True)
    
    # Effectiveness data
    riskai_effectiveness = Column(Float, nullable=False)  # 0-100
    traditional_effectiveness = Column(Float, nullable=False)  # 0-100
    effectiveness_improvement = Column(Float, nullable=True)  # Percentage
    
    # ROI metrics
    roi_percentage = Column(Float, nullable=True)
    payback_period = Column(Float, nullable=True)  # Months
    
    # Metadata
    analysis_date = Column(DateTime, default=datetime.utcnow)
    methodology = Column(Text, nullable=True)
    assumptions = Column(JSON, nullable=True)
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            "id": self.id,
            "company_size": self.company_size,
            "assessment_frequency": self.assessment_frequency,
            "riskai_cost": self.riskai_cost,
            "traditional_cost": self.traditional_cost,
            "cost_savings": self.cost_savings,
            "cost_savings_percentage": self.cost_savings_percentage,
            "riskai_time": self.riskai_time,
            "traditional_time": self.traditional_time,
            "time_savings": self.time_savings,
            "time_savings_percentage": self.time_savings_percentage,
            "riskai_effectiveness": self.riskai_effectiveness,
            "traditional_effectiveness": self.traditional_effectiveness,
            "effectiveness_improvement": self.effectiveness_improvement,
            "roi_percentage": self.roi_percentage,
            "payback_period": self.payback_period,
            "analysis_date": self.analysis_date.isoformat() if self.analysis_date else None,
            "methodology": self.methodology,
            "assumptions": self.assumptions
        }

class BenchmarkMethodology(Base):
    """Methodology for benchmark data collection and analysis"""
    __tablename__ = "benchmark_methodologies"
    
    id = Column(Integer, primary_key=True, autoincrement=True)
    name = Column(String(100), nullable=False)
    description = Column(Text, nullable=False)
    
    # Methodology details
    data_collection_method = Column(Text, nullable=False)
    sample_size = Column(Integer, nullable=True)
    date_range = Column(String(100), nullable=True)
    limitations = Column(JSON, nullable=True)  # List of limitations
    sources = Column(JSON, nullable=True)  # List of sources
    
    # Metadata
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    def to_dict(self):
        """Convert to dictionary"""
        return {
            "id": self.id,
            "name": self.name,
            "description": self.description,
            "data_collection_method": self.data_collection_method,
            "sample_size": self.sample_size,
            "date_range": self.date_range,
            "limitations": self.limitations,
            "sources": self.sources,
            "created_at": self.created_at.isoformat() if self.created_at else None,
            "updated_at": self.updated_at.isoformat() if self.updated_at else None
        }