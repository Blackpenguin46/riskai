"""
Benchmark API Endpoints
Handles API endpoints for benchmark data and comparisons
"""

from fastapi import APIRouter, HTTPException, Depends, File, UploadFile, Form, Query
from pydantic import BaseModel
from typing import Dict, List, Optional, Any
import logging
from datetime import datetime
import tempfile
import os

from benchmarks.benchmark_collector import benchmark_collector
from benchmarks.comparative_analyzer import comparative_analyzer
from benchmarks.visualization_engine import visualization_engine

logger = logging.getLogger(__name__)

router = APIRouter()

# --- Models ---
class BenchmarkDataRequest(BaseModel):
    tool_name: str
    category: str
    metric_name: str
    metric_value: float
    unit: Optional[str] = None
    measurement_methodology: Optional[str] = None
    source_reference: Optional[str] = None

class ToolComparisonRequest(BaseModel):
    benchmark_id: int
    riskai_value: float
    comparison_value: float
    industry: Optional[str] = None
    company_size: Optional[str] = None
    strengths: Optional[List[str]] = None
    weaknesses: Optional[List[str]] = None
    notes: Optional[str] = None

class ROIAnalysisRequest(BaseModel):
    company_size: str
    riskai_cost: float
    traditional_cost: float
    riskai_time: float
    traditional_time: float
    riskai_effectiveness: float
    traditional_effectiveness: float
    assessment_frequency: Optional[int] = None
    methodology: Optional[str] = None
    assumptions: Optional[List[str]] = None

class BenchmarkMethodologyRequest(BaseModel):
    name: str
    description: str
    data_collection_method: str
    sample_size: Optional[int] = None
    date_range: Optional[str] = None
    limitations: Optional[List[str]] = None
    sources: Optional[List[str]] = None

# --- Endpoints ---
@router.post("/benchmarks/data", tags=["Benchmarks"])
def add_benchmark_data(request: BenchmarkDataRequest):
    """Add a new benchmark data point"""
    try:
        benchmark_id = benchmark_collector.add_benchmark_data(
            tool_name=request.tool_name,
            category=request.category,
            metric_name=request.metric_name,
            metric_value=request.metric_value,
            unit=request.unit,
            measurement_methodology=request.measurement_methodology,
            source_reference=request.source_reference
        )
        
        if not benchmark_id:
            raise HTTPException(status_code=500, detail="Failed to add benchmark data")
        
        return {
            "benchmark_id": benchmark_id,
            "created_at": datetime.utcnow().isoformat(),
            "status": "created"
        }
    except Exception as e:
        logger.error(f"Error adding benchmark data: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to add benchmark data: {str(e)}")

@router.post("/benchmarks/comparison", tags=["Benchmarks"])
def add_tool_comparison(request: ToolComparisonRequest):
    """Add a comparison between RiskAI and another tool"""
    try:
        comparison_id = benchmark_collector.add_tool_comparison(
            benchmark_id=request.benchmark_id,
            riskai_value=request.riskai_value,
            comparison_value=request.comparison_value,
            industry=request.industry,
            company_size=request.company_size,
            strengths=request.strengths,
            weaknesses=request.weaknesses,
            notes=request.notes
        )
        
        if not comparison_id:
            raise HTTPException(status_code=500, detail="Failed to add tool comparison")
        
        return {
            "comparison_id": comparison_id,
            "created_at": datetime.utcnow().isoformat(),
            "status": "created"
        }
    except Exception as e:
        logger.error(f"Error adding tool comparison: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to add tool comparison: {str(e)}")

@router.post("/benchmarks/roi", tags=["Benchmarks"])
def add_roi_analysis(request: ROIAnalysisRequest):
    """Add ROI analysis data"""
    try:
        roi_id = benchmark_collector.add_roi_analysis(
            company_size=request.company_size,
            riskai_cost=request.riskai_cost,
            traditional_cost=request.traditional_cost,
            riskai_time=request.riskai_time,
            traditional_time=request.traditional_time,
            riskai_effectiveness=request.riskai_effectiveness,
            traditional_effectiveness=request.traditional_effectiveness,
            assessment_frequency=request.assessment_frequency,
            methodology=request.methodology,
            assumptions=request.assumptions
        )
        
        if not roi_id:
            raise HTTPException(status_code=500, detail="Failed to add ROI analysis")
        
        return {
            "roi_id": roi_id,
            "created_at": datetime.utcnow().isoformat(),
            "status": "created"
        }
    except Exception as e:
        logger.error(f"Error adding ROI analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to add ROI analysis: {str(e)}")

@router.post("/benchmarks/methodology", tags=["Benchmarks"])
def add_benchmark_methodology(request: BenchmarkMethodologyRequest):
    """Add benchmark methodology information"""
    try:
        methodology_id = benchmark_collector.add_benchmark_methodology(
            name=request.name,
            description=request.description,
            data_collection_method=request.data_collection_method,
            sample_size=request.sample_size,
            date_range=request.date_range,
            limitations=request.limitations,
            sources=request.sources
        )
        
        if not methodology_id:
            raise HTTPException(status_code=500, detail="Failed to add benchmark methodology")
        
        return {
            "methodology_id": methodology_id,
            "created_at": datetime.utcnow().isoformat(),
            "status": "created"
        }
    except Exception as e:
        logger.error(f"Error adding benchmark methodology: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to add benchmark methodology: {str(e)}")

@router.post("/benchmarks/import/csv", tags=["Benchmarks"])
async def import_benchmark_data_from_csv(file: UploadFile = File(...)):
    """Import benchmark data from a CSV file"""
    try:
        # Create a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as temp_file:
            temp_file_path = temp_file.name
            # Write the uploaded file content to the temporary file
            content = await file.read()
            temp_file.write(content)
        
        # Process the file
        results = benchmark_collector.import_benchmark_data_from_csv(temp_file_path)
        
        # Clean up the temporary file
        os.unlink(temp_file_path)
        
        return results
    except Exception as e:
        logger.error(f"Error importing benchmark data from CSV: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to import benchmark data: {str(e)}")

@router.post("/benchmarks/import/roi/csv", tags=["Benchmarks"])
async def import_roi_analysis_from_csv(file: UploadFile = File(...)):
    """Import ROI analysis data from a CSV file"""
    try:
        # Create a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as temp_file:
            temp_file_path = temp_file.name
            # Write the uploaded file content to the temporary file
            content = await file.read()
            temp_file.write(content)
        
        # Process the file
        results = benchmark_collector.import_roi_analysis_from_csv(temp_file_path)
        
        # Clean up the temporary file
        os.unlink(temp_file_path)
        
        return results
    except Exception as e:
        logger.error(f"Error importing ROI analysis from CSV: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to import ROI analysis: {str(e)}")

@router.get("/benchmarks/data", tags=["Benchmarks"])
def get_benchmark_data(
    tool_name: Optional[str] = None,
    category: Optional[str] = None,
    metric_name: Optional[str] = None
):
    """Get benchmark data with optional filters"""
    try:
        data = benchmark_collector.get_benchmark_data(
            tool_name=tool_name,
            category=category,
            metric_name=metric_name
        )
        
        return {
            "count": len(data),
            "data": data
        }
    except Exception as e:
        logger.error(f"Error getting benchmark data: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get benchmark data: {str(e)}")

@router.get("/benchmarks/comparisons", tags=["Benchmarks"])
def get_tool_comparisons(
    tool_name: Optional[str] = None,
    category: Optional[str] = None,
    industry: Optional[str] = None,
    company_size: Optional[str] = None
):
    """Get tool comparisons with optional filters"""
    try:
        comparisons = benchmark_collector.get_tool_comparisons(
            tool_name=tool_name,
            category=category,
            industry=industry,
            company_size=company_size
        )
        
        return {
            "count": len(comparisons),
            "comparisons": comparisons
        }
    except Exception as e:
        logger.error(f"Error getting tool comparisons: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get tool comparisons: {str(e)}")

@router.get("/benchmarks/roi", tags=["Benchmarks"])
def get_roi_analysis(company_size: Optional[str] = None):
    """Get ROI analysis data with optional filter"""
    try:
        analyses = benchmark_collector.get_roi_analysis(company_size)
        
        return {
            "count": len(analyses),
            "analyses": analyses
        }
    except Exception as e:
        logger.error(f"Error getting ROI analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get ROI analysis: {str(e)}")

@router.get("/benchmarks/methodologies", tags=["Benchmarks"])
def get_benchmark_methodologies():
    """Get all benchmark methodologies"""
    try:
        methodologies = benchmark_collector.get_benchmark_methodologies()
        
        return {
            "count": len(methodologies),
            "methodologies": methodologies
        }
    except Exception as e:
        logger.error(f"Error getting benchmark methodologies: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get benchmark methodologies: {str(e)}")

@router.get("/benchmarks/validate", tags=["Benchmarks"])
def validate_benchmark_data():
    """Validate benchmark data for consistency and completeness"""
    try:
        results = benchmark_collector.validate_benchmark_data()
        
        return results
    except Exception as e:
        logger.error(f"Error validating benchmark data: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to validate benchmark data: {str(e)}")

@router.get("/benchmarks/compare/category/{category}", tags=["Benchmarks"])
def compare_tools_by_category(
    category: str,
    industry: Optional[str] = None,
    company_size: Optional[str] = None
):
    """Compare RiskAI with other tools for a specific category"""
    try:
        comparison = comparative_analyzer.compare_tools_by_category(
            category=category,
            industry=industry,
            company_size=company_size
        )
        
        return comparison
    except Exception as e:
        logger.error(f"Error comparing tools by category: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to compare tools by category: {str(e)}")

@router.get("/benchmarks/compare/all", tags=["Benchmarks"])
def compare_all_categories(
    industry: Optional[str] = None,
    company_size: Optional[str] = None
):
    """Compare RiskAI with other tools across all categories"""
    try:
        comparison = comparative_analyzer.compare_all_categories(
            industry=industry,
            company_size=company_size
        )
        
        return comparison
    except Exception as e:
        logger.error(f"Error comparing all categories: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to compare all categories: {str(e)}")

@router.get("/benchmarks/roi/metrics", tags=["Benchmarks"])
def calculate_roi_metrics(company_size: Optional[str] = None):
    """Calculate ROI metrics for RiskAI"""
    try:
        metrics = comparative_analyzer.calculate_roi_metrics(company_size)
        
        return metrics
    except Exception as e:
        logger.error(f"Error calculating ROI metrics: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to calculate ROI metrics: {str(e)}")

@router.get("/benchmarks/strengths-weaknesses", tags=["Benchmarks"])
def analyze_strengths_and_weaknesses():
    """Analyze RiskAI's strengths and weaknesses compared to other tools"""
    try:
        analysis = comparative_analyzer.analyze_strengths_and_weaknesses()
        
        return analysis
    except Exception as e:
        logger.error(f"Error analyzing strengths and weaknesses: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to analyze strengths and weaknesses: {str(e)}")

@router.get("/benchmarks/report", tags=["Benchmarks"])
def generate_comparative_report(
    industry: Optional[str] = None,
    company_size: Optional[str] = None
):
    """Generate a comprehensive comparative report"""
    try:
        report = comparative_analyzer.generate_comparative_report(
            industry=industry,
            company_size=company_size
        )
        
        return report
    except Exception as e:
        logger.error(f"Error generating comparative report: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate comparative report: {str(e)}")

@router.get("/benchmarks/visualization/tool-comparison", tags=["Benchmarks"])
def generate_tool_comparison_chart(
    category: str,
    metric_name: Optional[str] = None,
    industry: Optional[str] = None,
    company_size: Optional[str] = None
):
    """Generate data for tool comparison chart"""
    try:
        chart_data = visualization_engine.generate_tool_comparison_chart(
            category=category,
            metric_name=metric_name,
            industry=industry,
            company_size=company_size
        )
        
        return chart_data
    except Exception as e:
        logger.error(f"Error generating tool comparison chart: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate tool comparison chart: {str(e)}")

@router.get("/benchmarks/visualization/category-comparison", tags=["Benchmarks"])
def generate_category_comparison_chart(
    industry: Optional[str] = None,
    company_size: Optional[str] = None
):
    """Generate data for category comparison chart"""
    try:
        chart_data = visualization_engine.generate_category_comparison_chart(
            industry=industry,
            company_size=company_size
        )
        
        return chart_data
    except Exception as e:
        logger.error(f"Error generating category comparison chart: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate category comparison chart: {str(e)}")

@router.get("/benchmarks/visualization/roi", tags=["Benchmarks"])
def generate_roi_chart(company_size: Optional[str] = None):
    """Generate data for ROI analysis chart"""
    try:
        chart_data = visualization_engine.generate_roi_chart(company_size)
        
        return chart_data
    except Exception as e:
        logger.error(f"Error generating ROI chart: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate ROI chart: {str(e)}")

@router.get("/benchmarks/visualization/strengths-weaknesses", tags=["Benchmarks"])
def generate_strengths_weaknesses_chart():
    """Generate data for strengths and weaknesses chart"""
    try:
        chart_data = visualization_engine.generate_strengths_weaknesses_chart()
        
        return chart_data
    except Exception as e:
        logger.error(f"Error generating strengths and weaknesses chart: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate strengths and weaknesses chart: {str(e)}")

@router.get("/benchmarks/visualization/dashboard", tags=["Benchmarks"])
def generate_dashboard_data(
    industry: Optional[str] = None,
    company_size: Optional[str] = None
):
    """Generate comprehensive dashboard data"""
    try:
        dashboard_data = visualization_engine.generate_dashboard_data(
            industry=industry,
            company_size=company_size
        )
        
        return dashboard_data
    except Exception as e:
        logger.error(f"Error generating dashboard data: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate dashboard data: {str(e)}")

@router.get("/benchmarks/visualization/report", tags=["Benchmarks"])
def generate_report_data(
    industry: Optional[str] = None,
    company_size: Optional[str] = None,
    format: str = "json"
):
    """Generate comprehensive report data"""
    try:
        report_data = visualization_engine.generate_report_data(
            industry=industry,
            company_size=company_size,
            format=format
        )
        
        return report_data
    except Exception as e:
        logger.error(f"Error generating report data: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate report data: {str(e)}")