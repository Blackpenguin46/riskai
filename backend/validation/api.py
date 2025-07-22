"""
Validation API Endpoints
Handles API endpoints for cross-industry validation
"""

from fastapi import APIRouter, HTTPException, Depends, File, UploadFile, Form, Query
from pydantic import BaseModel
from typing import Dict, List, Optional, Any
import logging
from datetime import datetime
import tempfile
import os

from validation.validator import validation_data_manager
from validation.industry_profiler import industry_profiler
from validation.statistical_analyzer import statistical_analyzer

logger = logging.getLogger(__name__)

router = APIRouter()

# --- Models ---
class IndustrySectorRequest(BaseModel):
    name: str
    description: Optional[str] = None

class SecurityFrameworkRequest(BaseModel):
    name: str
    version: Optional[str] = None
    description: Optional[str] = None
    source_url: Optional[str] = None

class SecurityDomainRequest(BaseModel):
    framework_id: int
    name: str
    description: Optional[str] = None
    weight: float = 1.0

class AssessmentQuestionRequest(BaseModel):
    domain_id: int
    question_text: str
    question_type: str
    options: Optional[List[str]] = None
    weight: float = 1.0
    guidance: Optional[str] = None
    evidence_required: bool = False

class IndustryValidationRequest(BaseModel):
    industry_id: int
    company_size: str
    company_count: int
    average_accuracy: Optional[float] = None
    confidence_interval_lower: Optional[float] = None
    confidence_interval_upper: Optional[float] = None
    precision_score: Optional[float] = None
    recall_score: Optional[float] = None
    f1_score: Optional[float] = None
    validation_methodology: Optional[str] = None

class ValidationMetricRequest(BaseModel):
    validation_id: int
    metric_name: str
    metric_value: float
    metric_description: Optional[str] = None

class ValidationResponseRequest(BaseModel):
    question_id: int
    industry_id: int
    company_size: str
    expert_response: str
    riskai_response: str
    is_correct: bool
    confidence_score: Optional[float] = None
    validator_id: Optional[str] = None

class ScoringRubricRequest(BaseModel):
    domain_id: int
    score_level: int
    description: str
    criteria: Optional[List[str]] = None
    industry_examples: Optional[Dict[str, str]] = None

class IndustryBenchmarkRequest(BaseModel):
    industry_id: int
    domain_id: int
    company_size: str
    average_score: float
    percentile_distribution: Optional[Dict[str, float]] = None
    sample_size: Optional[int] = None

class IndustryFrameworkAssociationRequest(BaseModel):
    industry_id: int
    framework_id: int

# --- Endpoints ---
@router.post("/validation/industry", tags=["Validation"])
def add_industry_sector(request: IndustrySectorRequest):
    """Add a new industry sector"""
    try:
        industry_id = validation_data_manager.add_industry_sector(
            name=request.name,
            description=request.description
        )
        
        if not industry_id:
            raise HTTPException(status_code=500, detail="Failed to add industry sector")
        
        return {
            "industry_id": industry_id,
            "created_at": datetime.utcnow().isoformat(),
            "status": "created"
        }
    except Exception as e:
        logger.error(f"Error adding industry sector: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to add industry sector: {str(e)}")

@router.post("/validation/framework", tags=["Validation"])
def add_security_framework(request: SecurityFrameworkRequest):
    """Add a new security framework"""
    try:
        framework_id = validation_data_manager.add_security_framework(
            name=request.name,
            version=request.version,
            description=request.description,
            source_url=request.source_url
        )
        
        if not framework_id:
            raise HTTPException(status_code=500, detail="Failed to add security framework")
        
        return {
            "framework_id": framework_id,
            "created_at": datetime.utcnow().isoformat(),
            "status": "created"
        }
    except Exception as e:
        logger.error(f"Error adding security framework: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to add security framework: {str(e)}")

@router.post("/validation/domain", tags=["Validation"])
def add_security_domain(request: SecurityDomainRequest):
    """Add a new security domain"""
    try:
        domain_id = validation_data_manager.add_security_domain(
            framework_id=request.framework_id,
            name=request.name,
            description=request.description,
            weight=request.weight
        )
        
        if not domain_id:
            raise HTTPException(status_code=500, detail="Failed to add security domain")
        
        return {
            "domain_id": domain_id,
            "created_at": datetime.utcnow().isoformat(),
            "status": "created"
        }
    except Exception as e:
        logger.error(f"Error adding security domain: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to add security domain: {str(e)}")

@router.post("/validation/question", tags=["Validation"])
def add_assessment_question(request: AssessmentQuestionRequest):
    """Add a new assessment question"""
    try:
        question_id = validation_data_manager.add_assessment_question(
            domain_id=request.domain_id,
            question_text=request.question_text,
            question_type=request.question_type,
            options=request.options,
            weight=request.weight,
            guidance=request.guidance,
            evidence_required=request.evidence_required
        )
        
        if not question_id:
            raise HTTPException(status_code=500, detail="Failed to add assessment question")
        
        return {
            "question_id": question_id,
            "created_at": datetime.utcnow().isoformat(),
            "status": "created"
        }
    except Exception as e:
        logger.error(f"Error adding assessment question: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to add assessment question: {str(e)}")

@router.post("/validation/industry-validation", tags=["Validation"])
def add_industry_validation(request: IndustryValidationRequest):
    """Add validation data for an industry sector"""
    try:
        confidence_interval = None
        if request.confidence_interval_lower is not None and request.confidence_interval_upper is not None:
            confidence_interval = (request.confidence_interval_lower, request.confidence_interval_upper)
        
        validation_id = validation_data_manager.add_industry_validation(
            industry_id=request.industry_id,
            company_size=request.company_size,
            company_count=request.company_count,
            average_accuracy=request.average_accuracy,
            confidence_interval=confidence_interval,
            precision_score=request.precision_score,
            recall_score=request.recall_score,
            f1_score=request.f1_score,
            validation_methodology=request.validation_methodology
        )
        
        if not validation_id:
            raise HTTPException(status_code=500, detail="Failed to add industry validation")
        
        return {
            "validation_id": validation_id,
            "created_at": datetime.utcnow().isoformat(),
            "status": "created"
        }
    except Exception as e:
        logger.error(f"Error adding industry validation: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to add industry validation: {str(e)}")

@router.post("/validation/metric", tags=["Validation"])
def add_validation_metric(request: ValidationMetricRequest):
    """Add a validation metric"""
    try:
        metric_id = validation_data_manager.add_validation_metric(
            validation_id=request.validation_id,
            metric_name=request.metric_name,
            metric_value=request.metric_value,
            metric_description=request.metric_description
        )
        
        if not metric_id:
            raise HTTPException(status_code=500, detail="Failed to add validation metric")
        
        return {
            "metric_id": metric_id,
            "created_at": datetime.utcnow().isoformat(),
            "status": "created"
        }
    except Exception as e:
        logger.error(f"Error adding validation metric: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to add validation metric: {str(e)}")

@router.post("/validation/response", tags=["Validation"])
def add_validation_response(request: ValidationResponseRequest):
    """Add a validation response"""
    try:
        response_id = validation_data_manager.add_validation_response(
            question_id=request.question_id,
            industry_id=request.industry_id,
            company_size=request.company_size,
            expert_response=request.expert_response,
            riskai_response=request.riskai_response,
            is_correct=request.is_correct,
            confidence_score=request.confidence_score,
            validator_id=request.validator_id
        )
        
        if not response_id:
            raise HTTPException(status_code=500, detail="Failed to add validation response")
        
        return {
            "response_id": response_id,
            "created_at": datetime.utcnow().isoformat(),
            "status": "created"
        }
    except Exception as e:
        logger.error(f"Error adding validation response: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to add validation response: {str(e)}")

@router.post("/validation/rubric", tags=["Validation"])
def add_scoring_rubric(request: ScoringRubricRequest):
    """Add a scoring rubric"""
    try:
        rubric_id = validation_data_manager.add_scoring_rubric(
            domain_id=request.domain_id,
            score_level=request.score_level,
            description=request.description,
            criteria=request.criteria,
            industry_examples=request.industry_examples
        )
        
        if not rubric_id:
            raise HTTPException(status_code=500, detail="Failed to add scoring rubric")
        
        return {
            "rubric_id": rubric_id,
            "created_at": datetime.utcnow().isoformat(),
            "status": "created"
        }
    except Exception as e:
        logger.error(f"Error adding scoring rubric: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to add scoring rubric: {str(e)}")

@router.post("/validation/benchmark", tags=["Validation"])
def add_industry_benchmark(request: IndustryBenchmarkRequest):
    """Add an industry benchmark"""
    try:
        benchmark_id = validation_data_manager.add_industry_benchmark(
            industry_id=request.industry_id,
            domain_id=request.domain_id,
            company_size=request.company_size,
            average_score=request.average_score,
            percentile_distribution=request.percentile_distribution,
            sample_size=request.sample_size
        )
        
        if not benchmark_id:
            raise HTTPException(status_code=500, detail="Failed to add industry benchmark")
        
        return {
            "benchmark_id": benchmark_id,
            "created_at": datetime.utcnow().isoformat(),
            "status": "created"
        }
    except Exception as e:
        logger.error(f"Error adding industry benchmark: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to add industry benchmark: {str(e)}")

@router.post("/validation/import/validation-data", tags=["Validation"])
async def import_validation_data_from_csv(file: UploadFile = File(...)):
    """Import validation data from a CSV file"""
    try:
        # Create a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as temp_file:
            temp_file_path = temp_file.name
            # Write the uploaded file content to the temporary file
            content = await file.read()
            temp_file.write(content)
        
        # Process the file
        results = validation_data_manager.import_validation_data_from_csv(temp_file_path)
        
        # Clean up the temporary file
        os.unlink(temp_file_path)
        
        return results
    except Exception as e:
        logger.error(f"Error importing validation data from CSV: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to import validation data: {str(e)}")

@router.post("/validation/import/scoring-rubrics", tags=["Validation"])
async def import_scoring_rubrics_from_csv(file: UploadFile = File(...)):
    """Import scoring rubrics from a CSV file"""
    try:
        # Create a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as temp_file:
            temp_file_path = temp_file.name
            # Write the uploaded file content to the temporary file
            content = await file.read()
            temp_file.write(content)
        
        # Process the file
        results = validation_data_manager.import_scoring_rubrics_from_csv(temp_file_path)
        
        # Clean up the temporary file
        os.unlink(temp_file_path)
        
        return results
    except Exception as e:
        logger.error(f"Error importing scoring rubrics from CSV: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to import scoring rubrics: {str(e)}")

@router.post("/validation/import/industry-benchmarks", tags=["Validation"])
async def import_industry_benchmarks_from_csv(file: UploadFile = File(...)):
    """Import industry benchmarks from a CSV file"""
    try:
        # Create a temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=".csv") as temp_file:
            temp_file_path = temp_file.name
            # Write the uploaded file content to the temporary file
            content = await file.read()
            temp_file.write(content)
        
        # Process the file
        results = validation_data_manager.import_industry_benchmarks_from_csv(temp_file_path)
        
        # Clean up the temporary file
        os.unlink(temp_file_path)
        
        return results
    except Exception as e:
        logger.error(f"Error importing industry benchmarks from CSV: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to import industry benchmarks: {str(e)}")

@router.get("/validation/industries", tags=["Validation"])
def get_industry_sectors():
    """Get all industry sectors"""
    try:
        industries = validation_data_manager.get_industry_sectors()
        
        return {
            "count": len(industries),
            "industries": industries
        }
    except Exception as e:
        logger.error(f"Error getting industry sectors: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get industry sectors: {str(e)}")

@router.get("/validation/frameworks", tags=["Validation"])
def get_security_frameworks():
    """Get all security frameworks"""
    try:
        frameworks = validation_data_manager.get_security_frameworks()
        
        return {
            "count": len(frameworks),
            "frameworks": frameworks
        }
    except Exception as e:
        logger.error(f"Error getting security frameworks: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get security frameworks: {str(e)}")

@router.get("/validation/domains", tags=["Validation"])
def get_security_domains(framework_id: Optional[int] = None):
    """Get security domains, optionally filtered by framework"""
    try:
        domains = validation_data_manager.get_security_domains(framework_id)
        
        return {
            "count": len(domains),
            "domains": domains
        }
    except Exception as e:
        logger.error(f"Error getting security domains: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get security domains: {str(e)}")

@router.get("/validation/questions", tags=["Validation"])
def get_assessment_questions(domain_id: Optional[int] = None):
    """Get assessment questions, optionally filtered by domain"""
    try:
        questions = validation_data_manager.get_assessment_questions(domain_id)
        
        return {
            "count": len(questions),
            "questions": questions
        }
    except Exception as e:
        logger.error(f"Error getting assessment questions: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get assessment questions: {str(e)}")

@router.get("/validation/industry-validations", tags=["Validation"])
def get_industry_validations(industry_id: Optional[int] = None, company_size: Optional[str] = None):
    """Get industry validations, optionally filtered by industry and company size"""
    try:
        validations = validation_data_manager.get_industry_validations(industry_id, company_size)
        
        return {
            "count": len(validations),
            "validations": validations
        }
    except Exception as e:
        logger.error(f"Error getting industry validations: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get industry validations: {str(e)}")

@router.get("/validation/metrics/{validation_id}", tags=["Validation"])
def get_validation_metrics(validation_id: int):
    """Get validation metrics for an industry validation"""
    try:
        metrics = validation_data_manager.get_validation_metrics(validation_id)
        
        return {
            "count": len(metrics),
            "metrics": metrics
        }
    except Exception as e:
        logger.error(f"Error getting validation metrics: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get validation metrics: {str(e)}")

@router.get("/validation/responses", tags=["Validation"])
def get_validation_responses(
    question_id: Optional[int] = None,
    industry_id: Optional[int] = None,
    company_size: Optional[str] = None
):
    """Get validation responses, optionally filtered by question, industry, and company size"""
    try:
        responses = validation_data_manager.get_validation_responses(question_id, industry_id, company_size)
        
        return {
            "count": len(responses),
            "responses": responses
        }
    except Exception as e:
        logger.error(f"Error getting validation responses: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get validation responses: {str(e)}")

@router.get("/validation/rubrics", tags=["Validation"])
def get_scoring_rubrics(domain_id: Optional[int] = None):
    """Get scoring rubrics, optionally filtered by domain"""
    try:
        rubrics = validation_data_manager.get_scoring_rubrics(domain_id)
        
        return {
            "count": len(rubrics),
            "rubrics": rubrics
        }
    except Exception as e:
        logger.error(f"Error getting scoring rubrics: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get scoring rubrics: {str(e)}")

@router.get("/validation/benchmarks", tags=["Validation"])
def get_industry_benchmarks(
    industry_id: Optional[int] = None,
    domain_id: Optional[int] = None,
    company_size: Optional[str] = None
):
    """Get industry benchmarks, optionally filtered by industry, domain, and company size"""
    try:
        benchmarks = validation_data_manager.get_industry_benchmarks(industry_id, domain_id, company_size)
        
        return {
            "count": len(benchmarks),
            "benchmarks": benchmarks
        }
    except Exception as e:
        logger.error(f"Error getting industry benchmarks: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get industry benchmarks: {str(e)}")

@router.post("/validation/associate-industry-framework", tags=["Validation"])
def associate_industry_with_framework(request: IndustryFrameworkAssociationRequest):
    """Associate an industry with a security framework"""
    try:
        success = industry_profiler.associate_industry_with_framework(
            industry_id=request.industry_id,
            framework_id=request.framework_id
        )
        
        if not success:
            raise HTTPException(status_code=500, detail="Failed to associate industry with framework")
        
        return {
            "industry_id": request.industry_id,
            "framework_id": request.framework_id,
            "created_at": datetime.utcnow().isoformat(),
            "status": "associated"
        }
    except Exception as e:
        logger.error(f"Error associating industry with framework: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to associate industry with framework: {str(e)}")

@router.get("/validation/industry-profile/{industry_id}", tags=["Validation"])
def get_industry_profile(industry_id: int):
    """Get a complete profile for an industry"""
    try:
        profile = industry_profiler.get_industry_profile(industry_id)
        
        if "error" in profile:
            raise HTTPException(status_code=404, detail=profile["error"])
        
        return profile
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting industry profile: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get industry profile: {str(e)}")

@router.get("/validation/company-size-profile/{company_size}", tags=["Validation"])
def get_company_size_profile(company_size: str):
    """Get a complete profile for a company size"""
    try:
        profile = industry_profiler.get_company_size_profile(company_size)
        
        if "error" in profile:
            raise HTTPException(status_code=404, detail=profile["error"])
        
        return profile
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting company size profile: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get company size profile: {str(e)}")

@router.get("/validation/assessment-template", tags=["Validation"])
def get_assessment_template(
    industry_id: Optional[int] = None,
    company_size: Optional[str] = None,
    framework_id: Optional[int] = None
):
    """Get an assessment template for a specific industry and company size"""
    try:
        template = industry_profiler.get_assessment_template(industry_id, company_size, framework_id)
        
        if "error" in template:
            raise HTTPException(status_code=404, detail=template["error"])
        
        return template
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting assessment template: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get assessment template: {str(e)}")

@router.get("/validation/industry-specific-questions/{industry_id}", tags=["Validation"])
def get_industry_specific_questions(industry_id: int):
    """Get industry-specific assessment questions"""
    try:
        questions = industry_profiler.get_industry_specific_questions(industry_id)
        
        return {
            "count": len(questions),
            "questions": questions
        }
    except Exception as e:
        logger.error(f"Error getting industry-specific questions: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get industry-specific questions: {str(e)}")

@router.get("/validation/industry-benchmark-comparison/{industry_id}", tags=["Validation"])
def get_industry_benchmark_comparison(
    industry_id: int,
    domain_id: Optional[int] = None,
    company_size: Optional[str] = None
):
    """Get benchmark comparison for an industry"""
    try:
        comparison = industry_profiler.get_industry_benchmark_comparison(industry_id, domain_id, company_size)
        
        if "error" in comparison:
            raise HTTPException(status_code=404, detail=comparison["error"])
        
        return comparison
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting industry benchmark comparison: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get industry benchmark comparison: {str(e)}")

@router.get("/validation/confidence-intervals", tags=["Validation"])
def calculate_confidence_intervals(
    industry_id: Optional[int] = None,
    company_size: Optional[str] = None
):
    """Calculate confidence intervals for validation metrics"""
    try:
        intervals = statistical_analyzer.calculate_confidence_intervals(industry_id, company_size)
        
        if "error" in intervals:
            raise HTTPException(status_code=404, detail=intervals["error"])
        
        return intervals
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error calculating confidence intervals: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to calculate confidence intervals: {str(e)}")

@router.get("/validation/hypothesis-test", tags=["Validation"])
def perform_hypothesis_test(
    industry_id1: int,
    industry_id2: int,
    company_size: Optional[str] = None
):
    """Perform hypothesis test to compare two industries"""
    try:
        test_results = statistical_analyzer.perform_hypothesis_test(industry_id1, industry_id2, company_size)
        
        if "error" in test_results:
            raise HTTPException(status_code=404, detail=test_results["error"])
        
        return test_results
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error performing hypothesis test: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to perform hypothesis test: {str(e)}")

@router.get("/validation/generalizability", tags=["Validation"])
def analyze_generalizability():
    """Analyze generalizability of RiskAI across industries and company sizes"""
    try:
        analysis = statistical_analyzer.analyze_generalizability()
        
        if "error" in analysis:
            raise HTTPException(status_code=404, detail=analysis["error"])
        
        return analysis
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing generalizability: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to analyze generalizability: {str(e)}")

@router.get("/validation/domain-performance", tags=["Validation"])
def analyze_domain_performance(
    industry_id: Optional[int] = None,
    company_size: Optional[str] = None
):
    """Analyze RiskAI's performance across security domains"""
    try:
        analysis = statistical_analyzer.analyze_domain_performance(industry_id, company_size)
        
        if "error" in analysis:
            raise HTTPException(status_code=404, detail=analysis["error"])
        
        return analysis
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error analyzing domain performance: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to analyze domain performance: {str(e)}")

@router.post("/validation/calculate-metrics/{industry_id}", tags=["Validation"])
def calculate_validation_metrics(
    industry_id: int,
    company_size: Optional[str] = None
):
    """Calculate validation metrics for an industry"""
    try:
        metrics = validation_data_manager.calculate_validation_metrics(industry_id, company_size)
        
        if "error" in metrics:
            raise HTTPException(status_code=404, detail=metrics["error"])
        
        return metrics
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error calculating validation metrics: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to calculate validation metrics: {str(e)}")

@router.get("/validation/categorize-company", tags=["Validation"])
def categorize_company_by_size(employee_count: int):
    """Categorize a company by size based on employee count"""
    try:
        category = industry_profiler.categorize_company_by_size(employee_count)
        
        return {
            "employee_count": employee_count,
            "company_size": category
        }
    except Exception as e:
        logger.error(f"Error categorizing company by size: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to categorize company by size: {str(e)}")
# --- Scoring System Endpoints ---
from validation.scoring_system import scoring_system

class DomainScoreRequest(BaseModel):
    domain_id: int
    responses: Dict[str, Any]
    industry_id: Optional[int] = None
    company_size: Optional[str] = None

class AssessmentScoreRequest(BaseModel):
    responses: Dict[str, Dict[str, Any]]
    framework_id: Optional[int] = None
    industry_id: Optional[int] = None
    company_size: Optional[str] = None

@router.post("/validation/score/domain", tags=["Validation"])
def calculate_domain_score(request: DomainScoreRequest):
    """Calculate a score for a security domain based on responses"""
    try:
        score = scoring_system.calculate_domain_score(
            domain_id=request.domain_id,
            responses=request.responses,
            industry_id=request.industry_id,
            company_size=request.company_size
        )
        
        if "error" in score:
            raise HTTPException(status_code=404, detail=score["error"])
        
        return score
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error calculating domain score: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to calculate domain score: {str(e)}")

@router.post("/validation/score/assessment", tags=["Validation"])
def calculate_assessment_score(request: AssessmentScoreRequest):
    """Calculate an overall assessment score based on responses"""
    try:
        score = scoring_system.calculate_assessment_score(
            responses=request.responses,
            framework_id=request.framework_id,
            industry_id=request.industry_id,
            company_size=request.company_size
        )
        
        if "error" in score:
            raise HTTPException(status_code=404, detail=score["error"])
        
        return score
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error calculating assessment score: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to calculate assessment score: {str(e)}")

@router.post("/validation/recommendations", tags=["Validation"])
def generate_recommendations(request: AssessmentScoreRequest):
    """Generate recommendations based on assessment score"""
    try:
        # First calculate the assessment score
        score = scoring_system.calculate_assessment_score(
            responses=request.responses,
            framework_id=request.framework_id,
            industry_id=request.industry_id,
            company_size=request.company_size
        )
        
        if "error" in score:
            raise HTTPException(status_code=404, detail=score["error"])
        
        # Then generate recommendations
        recommendations = scoring_system.generate_recommendations(
            assessment_score=score,
            industry_id=request.industry_id,
            company_size=request.company_size
        )
        
        if "error" in recommendations:
            raise HTTPException(status_code=404, detail=recommendations["error"])
        
        # Return both score and recommendations
        return {
            "score": score,
            "recommendations": recommendations
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating recommendations: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate recommendations: {str(e)}")