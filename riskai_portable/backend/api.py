from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional, Any
from fastapi.encoders import jsonable_encoder
import logging
import os
import json
import traceback
import re
import time
from datetime import datetime

# unify with env vars so Docker-compose can override
DB_PERSIST_DIR = os.getenv("DB_PERSIST_DIR", "vectordb")
PDF_DATA_DIR   = os.getenv("PDF_DATA_DIR",   "data/")


# --- RAG/vector/LLM imports and initialization ---
from rag_pipeline.loader import load_documents, chunk_documents
from rag_pipeline.embedder import get_embedder
from rag_pipeline.store import store_embeddings, load_existing_embeddings
from rag_pipeline.retriever import build_rag_chain

# --- New modules for enhanced functionality ---
from metrics.dashboard import metrics_dashboard
from scoring.confidence import confidence_scorer
from validation.validator import risk_validator

# --- Phase 2 modules for peer review improvements ---
from data_management.company_data import company_data_manager
from scoring.objective_scoring import objective_scorer
from benchmarks.grc_comparison import grc_benchmarker

# --- Assessment redesign modules ---
from assessment.structured_assessment import structured_assessment
from assessment.modern_assessment import modern_assessment
from assessment.dashboard import assessment_dashboard
from chat.risk_mitigation_chat import risk_mitigation_chat

# --- Main dashboard module ---
from dashboard.main_dashboard import main_dashboard

# File upload handling
from fastapi import UploadFile, File, Form
from typing import List as ListType
import tempfile
import os

# ------------------------------------
# Logging Configuration
# ------------------------------------
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# ------------------------------------
# FastAPI Initialization
# ------------------------------------
app = FastAPI(title="RiskIQ-AI")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ------------------------------------
# Global RAG Pipeline Components & Limits
# ------------------------------------
DB_PERSIST_DIR = "vectordb"
PDF_DATA_DIR = "data/"
MAX_RAG_CONTEXT_CHARS = 1000
TARGET_LLM_PROMPT_TOTAL_CHARS = 3600

embedder = None
db = None
qa_chain = None

@app.on_event("startup")
async def startup_event():
    global embedder, db, qa_chain
    
    # Get port from environment for Render
    port = os.getenv("PORT", "8000")
    logger.info(f"Starting RiskAI Backend on port {port}")
    
    try:
        # Initialize database
        logger.info("Initializing database...")
        from database.models import init_database
        init_database()
        
        logger.info("Skipping embedder and RAG initialization for debugging...")
        # Temporarily disabled for debugging
        embedder = None
        db = None
        qa_chain = None
        logger.info("All AI components skipped for debugging")

        logger.info("RAG pipeline initialized successfully")
        logger.info(f"RiskAI Backend ready on port {port}")
    except Exception as e:
        logger.error(f"Failed to initialize RAG pipeline: {str(e)}")
        raise RuntimeError(f"Startup error: {str(e)}")

@app.get("/health")
def health_check():
    """Simple health check endpoint"""
    return {"status": "healthy", "timestamp": datetime.now().isoformat()}

@app.get("/")
def get_main_dashboard():
    """Get main project dashboard - central hub for all features"""
    try:
        return main_dashboard.get_main_dashboard()
    except Exception as e:
        logger.error(f"Error getting main dashboard: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get main dashboard: {str(e)}")

@app.get("/dashboard")
def get_dashboard():
    """Alternative route for main dashboard"""
    try:
        return main_dashboard.get_main_dashboard()
    except Exception as e:
        logger.error(f"Error getting dashboard: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get dashboard: {str(e)}")

@app.get("/dashboard/category/{category}")
def get_dashboard_category(category: str):
    """Get detailed information for a specific dashboard category"""
    try:
        return main_dashboard.get_category_details(category)
    except Exception as e:
        logger.error(f"Error getting dashboard category: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get category: {str(e)}")

@app.get("/dashboard/features")
def get_feature_status():
    """Get status of all dashboard features"""
    try:
        return main_dashboard.get_feature_status()
    except Exception as e:
        logger.error(f"Error getting feature status: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get feature status: {str(e)}")

@app.get("/healthz")
def health_check():
    if qa_chain:
        return {"status": "ok"}
    else:
        raise HTTPException(status_code=503, detail="RAG not ready")

class CompanyProfile(BaseModel):
    name: Optional[str] = None
    industry: str
    size: str
    tech_adoption: str
    security_controls: str
    risk_posture: str
    emerging_technologies: List[str]

class RiskAnswer(BaseModel):
    question_id: str
    answer: str

class RiskAnswersRequest(BaseModel):
    answers: List[RiskAnswer]

class RiskQuestion(BaseModel):
    id: str
    question_text: str
    category_name: str
    helper_text: Optional[str] = None
    scoring_focus: str

class RiskTableRow(BaseModel):
    id: str
    category: str
    definition: str
    scoring_focus: str
    score: int
    max_score: int
    weight: float
    explanation: str

class RiskAssessmentResult(BaseModel):
    overall_weighted_score: float
    confidence_interval: Optional[tuple] = None
    confidence_level: Optional[float] = None
    risk_table: List[RiskTableRow]
    recommendations: List[str]
    resources: List[Dict[str, str]]
    data_insights: List[str]
    raw_llm_output: Optional[str] = None
    uncertainty_analysis: Optional[Dict[str, Any]] = None
    validation_results: Optional[Dict[str, Any]] = None
    performance_metrics: Optional[Dict[str, Any]] = None

session_context: Dict[str, Any] = {}

# Comprehensive risk categories definition with business focus
RISK_CATEGORIES_DEFINITION = [
    {"id": "business_strategy", "category": "Business Strategy Alignment", "definition": "How well emerging technology initiatives align with overall business goals and strategy.", "scoring_focus": "Strategic alignment, ROI measurement, business case development", "weight": 0.06, "max_score": 10},
    {"id": "market_position", "category": "Market Position & Competitive Advantage", "definition": "How emerging technologies affect market position and create competitive advantages.", "scoring_focus": "Market differentiation, first-mover advantage, competitive analysis", "weight": 0.05, "max_score": 10},
    {"id": "financial_impact", "category": "Financial Impact & Investment", "definition": "Financial considerations for emerging technology adoption including budgeting and ROI.", "scoring_focus": "Budget allocation, cost management, ROI forecasting", "weight": 0.05, "max_score": 10},
    {"id": "regulatory_compliance", "category": "Regulatory Compliance", "definition": "Adherence to relevant regulations and standards for emerging technologies.", "scoring_focus": "Compliance frameworks, regulatory monitoring, audit readiness", "weight": 0.05, "max_score": 10},
    {"id": "organizational_readiness", "category": "Organizational Readiness", "definition": "Company's cultural and structural readiness to adopt emerging technologies.", "scoring_focus": "Change management, skills assessment, leadership buy-in", "weight": 0.05, "max_score": 10},
    {"id": "asset_visibility", "category": "Asset Visibility", "definition": "Degree to which the organization knows and inventories its IT assets (hardware, software, cloud resources).", "scoring_focus": "Asset registry, CMDB, shadow IT detection", "weight": 0.04, "max_score": 10},
    {"id": "data_sensitivity", "category": "Data Sensitivity & Classification", "definition": "Processes for labeling, managing, and securing data based on confidentiality, integrity, and availability (CIA).", "scoring_focus": "Classification tiers, encryption, data flow maps", "weight": 0.05, "max_score": 10},
    {"id": "access_management", "category": "Access Management", "definition": "Enforcement of least privilege, role-based access controls (RBAC), SSO, MFA, and joiner/mover/leaver processes.", "scoring_focus": "IAM maturity, MFA adoption, AD hygiene", "weight": 0.05, "max_score": 10},
    {"id": "network_security", "category": "Network Security Posture", "definition": "Strength of network segmentation, firewall rules, intrusion detection, and Zero Trust principles.", "scoring_focus": "Segmentation, micro-perimeters, SDN, detection systems", "weight": 0.04, "max_score": 10},
    {"id": "cloud_security", "category": "Cloud Security", "definition": "Protection of cloud workloads and infrastructure (IaaS, PaaS, SaaS) using shared responsibility models.", "scoring_focus": "CSPM usage, workload isolation, key management", "weight": 0.05, "max_score": 10},
    {"id": "third_party_risk", "category": "Third-Party Risk", "definition": "Risk from vendors, partners, and supply chain entities with access to your systems or data.", "scoring_focus": "Vendor assessments, contract clauses, breach awareness", "weight": 0.05, "max_score": 10},
    {"id": "incident_response", "category": "Incident Detection & Response", "definition": "Ability to detect, triage, respond to, and recover from cyber incidents effectively.", "scoring_focus": "SIEM/SOAR, playbooks, RTO/RPO", "weight": 0.05, "max_score": 10},
    {"id": "security_awareness", "category": "Security Awareness Training", "definition": "Ongoing efforts to educate employees on phishing, password hygiene, and safe digital behavior.", "scoring_focus": "Frequency, phishing test scores, LMS coverage", "weight": 0.04, "max_score": 10},
    {"id": "grc", "category": "Governance, Risk & Compliance (GRC)", "definition": "Integration of policy, risk registers, regulatory mapping, and control audits.", "scoring_focus": "GRC tooling, policy gaps, audit frequency", "weight": 0.05, "max_score": 10},
    {"id": "secure_sdlc", "category": "Secure Development (SDLC)", "definition": "Degree to which security is integrated into software development lifecycle.", "scoring_focus": "SAST, DAST, threat modeling, dev training", "weight": 0.04, "max_score": 10},
    {"id": "business_continuity", "category": "Business Continuity & Resilience", "definition": "Organization's readiness to maintain operations during cyber attacks or outages.", "scoring_focus": "BCP/DR plans, failover tests, resilience strategy", "weight": 0.04, "max_score": 10},
    {"id": "security_monitoring", "category": "Security Monitoring & Logging", "definition": "Centralized logging, alerting thresholds, and actionable telemetry.", "scoring_focus": "Log aggregation, SIEM use, anomaly detection", "weight": 0.04, "max_score": 10},
    {"id": "risk_quantification", "category": "Risk Quantification & Reporting", "definition": "Methods used to quantify and communicate cyber risk to stakeholders.", "scoring_focus": "FAIR use, dashboards, board reporting", "weight": 0.03, "max_score": 10},
    {"id": "app_security", "category": "Application Security", "definition": "Security practices and tooling applied to web, mobile, and internal applications.", "scoring_focus": "AppSec tools, bug bounty, static/dynamic scanning", "weight": 0.04, "max_score": 10},
    {"id": "emerging_tech_adoption", "category": "Emerging Technology Adoption", "definition": "Preparedness to adopt and govern new technologies (AI, quantum, blockchain) securely.", "scoring_focus": "Risk vetting, PoC governance, PQC, AI use policy", "weight": 0.03, "max_score": 10},
    {"id": "innovation_culture", "category": "Innovation Culture", "definition": "Company's ability to foster innovation and experimentation with emerging technologies.", "scoring_focus": "Innovation programs, idea management, experimentation frameworks", "weight": 0.04, "max_score": 10},
    {"id": "talent_management", "category": "Talent Management", "definition": "Strategies for attracting, developing, and retaining talent for emerging technology initiatives.", "scoring_focus": "Skills development, recruitment strategy, retention programs", "weight": 0.05, "max_score": 10}
]

@app.post("/initialize-assessment")
def initialize_assessment(profile: CompanyProfile):
    if not qa_chain:
        logger.error("RAG pipeline not initialized")
        raise HTTPException(status_code=503, detail="Service not ready. Please try again in a few moments.")

    logger.info(f"Received company profile: {profile.name if profile.name else 'Unnamed Company'}")
    session_context["profile"] = profile
    try:
        questions = generate_dynamic_questions(profile)
        if not questions:
            raise HTTPException(status_code=500, detail="Failed to generate assessment questions")
        return jsonable_encoder(questions)
    except Exception as e:
        logger.error(f"Error generating questions: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to initialize assessment: {str(e)}")

@app.post("/submit-answers", response_model=RiskAssessmentResult)
async def submit_answers(request: RiskAnswersRequest):
    if not qa_chain:
        logger.error("RAG pipeline not initialized")
        raise HTTPException(status_code=503, detail="Service not ready. Please try again in a few moments.")

    profile = session_context.get("profile")
    if not profile:
        logger.error("No company profile found in session for submitting answers.")
        raise HTTPException(status_code=400, detail="No company profile found. Please initialize assessment first.")

    try:
        logger.info(f"Received {len(request.answers)} answers for profile: {profile.name if profile.name else 'Unnamed Company'}")
        logger.info(f"Answer types: {[type(ans) for ans in request.answers]}")
        
        # Create a dictionary mapping question IDs to answers
        answers_dict = {}
        for ans in request.answers:
            logger.info(f"Processing answer: {ans}")
            answers_dict[ans.question_id] = ans.answer
        
        logger.info(f"Processed {len(answers_dict)} answers into dictionary")
        
        risk_table, overall_weighted_score, data_insights = build_risk_table(profile, answers_dict)
        logger.info(f"Built risk table with {len(risk_table)} rows, overall score: {overall_weighted_score}")
        
        context = await retrieve_rag_context(profile, answers_dict, risk_table)
        logger.info(f"Retrieved RAG context of length: {len(context)}")
        
        recommendations, resources, raw_llm = await generate_llm_advice_async(profile, answers_dict, risk_table, context)
        logger.info(f"Generated {len(recommendations)} recommendations and {len(resources)} resources")

        # Calculate confidence scoring and uncertainty analysis
        start_time = time.time()
        
        # Calculate answer quality and data completeness
        answer_quality = confidence_scorer.calculate_answer_quality(answers_dict)
        data_completeness = confidence_scorer.calculate_data_completeness(answers_dict, len(RISK_CATEGORIES_DEFINITION))
        
        # Calculate confidence score for overall assessment
        confidence_score = confidence_scorer.calculate_confidence_score(
            overall_weighted_score, answer_quality, data_completeness
        )
        
        # Perform uncertainty analysis
        uncertainty_analysis = confidence_scorer.analyze_uncertainty(risk_table, answers_dict)
        
        # Perform validation
        validation_results = risk_validator.validate_assessment(risk_table, profile.dict(), answers_dict)
        validation_report = risk_validator.generate_validation_report(validation_results)
        
        processing_time = time.time() - start_time
        
        # Record assessment for metrics
        assessment_data = {
            'id': f"assessment_{int(time.time())}",
            'overall_weighted_score': overall_weighted_score,
            'confidence_interval': confidence_score.confidence_interval,
            'risk_table': [row.dict() for row in risk_table],
            'processing_time': processing_time,
            'company_profile': profile.dict()
        }
        metrics_dashboard.record_assessment(assessment_data)
        
        # Get performance metrics
        performance_metrics = {
            'answer_quality': answer_quality,
            'data_completeness': data_completeness,
            'processing_time': processing_time,
            'validation_status': validation_report['overall_status']
        }
        
        return RiskAssessmentResult(
            overall_weighted_score=overall_weighted_score,
            confidence_interval=confidence_score.confidence_interval,
            confidence_level=confidence_score.confidence_level,
            risk_table=risk_table,
            recommendations=recommendations,
            resources=resources,
            data_insights=data_insights,
            raw_llm_output=raw_llm,
            uncertainty_analysis=uncertainty_analysis.__dict__,
            validation_results=validation_report,
            performance_metrics=performance_metrics
        )
    except Exception as e:
        logger.error(f"Error processing answers: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Failed to process assessment: {str(e)}")

@app.get("/metrics")
def get_metrics():
    """Get system performance metrics"""
    try:
        return metrics_dashboard.export_metrics()
    except Exception as e:
        logger.error(f"Error getting metrics: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get metrics: {str(e)}")

@app.get("/metrics/dashboard/realtime")
def get_realtime_dashboard():
    """Get comprehensive real-time dashboard with advanced analytics"""
    try:
        return metrics_dashboard.get_real_time_dashboard()
    except Exception as e:
        logger.error(f"Error getting real-time dashboard: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get dashboard: {str(e)}")

@app.get("/metrics/validate")
def validate_system():
    """Validate system performance against thresholds"""
    try:
        # Get recent assessment for validation
        if not metrics_dashboard.assessment_history:
            return {"status": "no_data", "message": "No assessments available for validation"}
        
        recent_assessment = metrics_dashboard.assessment_history[-1]
        quality_report = metrics_dashboard.validate_assessment_quality({
            'overall_weighted_score': recent_assessment.overall_score,
            'confidence_interval': recent_assessment.confidence_interval,
            'risk_table': [{'id': k, 'score': v} for k, v in recent_assessment.category_scores.items()],
            'processing_time': recent_assessment.processing_time
        })
        
        return quality_report
    except Exception as e:
        logger.error(f"Error validating system: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to validate system: {str(e)}")

@app.post("/company/workspace")
def create_company_workspace(profile: CompanyProfile):
    """Create isolated workspace for company data"""
    try:
        company_id = f"company_{profile.industry}_{profile.size}_{int(time.time())}"
        result = company_data_manager.create_company_workspace(company_id, profile.dict())
        return result
    except Exception as e:
        logger.error(f"Error creating company workspace: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create workspace: {str(e)}")

@app.post("/company/upload-ai")
async def upload_ai_document(
    company_id: str = Form(...),
    document_type: str = Form(...),
    file: UploadFile = File(...)
):
    """Upload document with AI-powered parsing and analysis"""
    try:
        # Validate file type
        allowed_extensions = {'.pdf', '.docx', '.doc', '.txt', '.xlsx', '.xls', '.csv', '.json'}
        file_extension = os.path.splitext(file.filename)[1].lower()
        
        if file_extension not in allowed_extensions:
            raise HTTPException(
                status_code=400, 
                detail=f"Unsupported file type: {file_extension}. Allowed: {', '.join(allowed_extensions)}"
            )
        
        # Create temporary file
        with tempfile.NamedTemporaryFile(delete=False, suffix=file_extension) as temp_file:
            content = await file.read()
            temp_file.write(content)
            temp_file_path = temp_file.name
        
        try:
            # Parse document with AI
            from data_management.company_data import DocumentType
            doc_type = DocumentType(document_type)
            
            parsing_result = company_data_manager.ai_parser.parse_document(temp_file_path, doc_type)
            
            # Store parsed results
            storage_result = company_data_manager.store_parsed_document(company_id, parsing_result)
            
            return {
                "status": "success",
                "document_id": parsing_result.document_id,
                "parsing_result": {
                    "document_name": parsing_result.document_name,
                    "document_type": parsing_result.document_type.value,
                    "confidence_scores": parsing_result.confidence_scores,
                    "security_topics": parsing_result.security_topics,
                    "compliance_frameworks": parsing_result.compliance_frameworks,
                    "risk_indicators": parsing_result.risk_indicators,
                    "parsing_timestamp": parsing_result.parsing_timestamp.isoformat()
                },
                "storage_result": storage_result
            }
            
        finally:
            # Clean up temporary file
            os.unlink(temp_file_path)
            
    except Exception as e:
        logger.error(f"Error in AI document upload: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to process document: {str(e)}")

@app.get("/company/{company_id}/parsing-results")
def get_ai_parsing_results(company_id: str):
    """Get AI document parsing results for a company"""
    try:
        results = company_data_manager.get_company_parsing_results(company_id)
        return {"company_id": company_id, "parsing_results": results}
    except Exception as e:
        logger.error(f"Error getting parsing results: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get parsing results: {str(e)}")

@app.post("/company/{company_id}/documents/analyze")
def analyze_company_documents(company_id: str):
    """Perform comprehensive analysis of all company documents"""
    try:
        analysis_result = company_data_manager.perform_comprehensive_analysis(company_id)
        return analysis_result
    except Exception as e:
        logger.error(f"Error analyzing company documents: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to analyze documents: {str(e)}")

@app.get("/company/{company_id}/security-insights")
def get_security_insights(company_id: str):
    """Get AI-generated security insights from uploaded documents"""
    try:
        insights = company_data_manager.generate_security_insights(company_id)
        return {"company_id": company_id, "security_insights": insights}
    except Exception as e:
        logger.error(f"Error getting security insights: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get insights: {str(e)}")

@app.get("/scoring/guidance/{category_id}")
def get_scoring_guidance(category_id: str):
    """Get objective scoring guidance for a category"""
    try:
        guidance = objective_scorer.get_scoring_guidance(category_id)
        return guidance
    except Exception as e:
        logger.error(f"Error getting scoring guidance: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get guidance: {str(e)}")

@app.post("/scoring/evidence-based")
def generate_evidence_based_score(scoring_request: Dict[str, Any]):
    """Generate evidence-based score with comprehensive justification"""
    try:
        category_id = scoring_request.get('category_id')
        response = scoring_request.get('response')
        question_metadata = scoring_request.get('metadata', {})
        
        if not category_id or not response:
            raise HTTPException(
                status_code=400, 
                detail="Missing required fields: category_id and response"
            )
        
        justification = objective_scorer.generate_evidence_based_justification(
            category_id, 
            response, 
            question_metadata
        )
        
        return justification
        
    except Exception as e:
        logger.error(f"Error generating evidence-based score: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate score: {str(e)}")

@app.get("/benchmarks/comparison")
def get_benchmark_comparison():
    """Get quantitative comparison with other GRC tools"""
    try:
        return grc_benchmarker.export_benchmark_data()
    except Exception as e:
        logger.error(f"Error getting benchmark comparison: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get comparison: {str(e)}")

@app.get("/benchmarks/roi/{company_size}")
def get_roi_analysis(company_size: str, assessment_frequency: Optional[int] = None):
    """Get ROI analysis for specific company size"""
    try:
        return grc_benchmarker.generate_roi_analysis(company_size, assessment_frequency)
    except Exception as e:
        logger.error(f"Error generating ROI analysis: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate ROI analysis: {str(e)}")

@app.get("/benchmarks/realtime")
def get_realtime_grc_comparison():
    """Get real-time GRC platform comparison with current market data"""
    try:
        return grc_benchmarker.get_real_time_comparison()
    except Exception as e:
        logger.error(f"Error generating real-time comparison: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to generate real-time comparison: {str(e)}")

@app.get("/assessment/dashboard")
def get_assessment_dashboard():
    """Get unified dashboard with clickable section cards"""
    try:
        return assessment_dashboard.get_dashboard_overview()
    except Exception as e:
        logger.error(f"Error getting assessment dashboard: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get dashboard: {str(e)}")

@app.get("/assessment/modern")
def get_modern_assessment():
    """Get modern test-based assessment overview"""
    try:
        return modern_assessment.get_assessment_overview()
    except Exception as e:
        logger.error(f"Error getting modern assessment: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get assessment: {str(e)}")

@app.get("/assessment/structured")
def get_structured_assessment():
    """Get structured assessment form based on industry frameworks (legacy)"""
    try:
        return structured_assessment.get_full_assessment()
    except Exception as e:
        logger.error(f"Error getting structured assessment: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get assessment: {str(e)}")

@app.get("/assessment/section/{section_id}")
def get_assessment_section(section_id: str):
    """Get specific assessment section with dashboard details"""
    try:
        return assessment_dashboard.get_section_details(section_id)
    except Exception as e:
        logger.error(f"Error getting assessment section: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get section: {str(e)}")

@app.get("/assessment/modern/section/{section_id}")
def get_modern_assessment_section(section_id: str):
    """Get modern assessment section with questions"""
    try:
        return modern_assessment.get_section_questions(section_id)
    except Exception as e:
        logger.error(f"Error getting modern assessment section: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get section: {str(e)}")

@app.post("/assessment/modern/section/{section_id}/score")
def score_modern_assessment_section(section_id: str, responses: Dict[str, Any]):
    """Score modern assessment section with NIST CSF 2.0 methodology"""
    try:
        return modern_assessment.calculate_section_score(section_id, responses)
    except Exception as e:
        logger.error(f"Error scoring modern assessment section: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to score section: {str(e)}")

@app.get("/assessment/section/{section_id}/questions")
def get_section_questions(section_id: str):
    """Get questions for specific assessment section (legacy)"""
    try:
        section = structured_assessment.get_section(section_id)
        if not section:
            raise HTTPException(status_code=404, detail=f"Section {section_id} not found")
        return section
    except Exception as e:
        logger.error(f"Error getting section questions: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get section questions: {str(e)}")

@app.post("/assessment/section/{section_id}/progress")
def update_section_progress(section_id: str, answers: Dict[str, Any]):
    """Update progress for specific assessment section"""
    try:
        return assessment_dashboard.update_section_progress(section_id, answers)
    except Exception as e:
        logger.error(f"Error updating section progress: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to update progress: {str(e)}")

@app.post("/assessment/score/{section_id}")
def score_assessment_section(section_id: str, responses: Dict[str, Any]):
    """Score specific assessment section"""
    try:
        return structured_assessment.calculate_section_score(section_id, responses)
    except Exception as e:
        logger.error(f"Error scoring assessment section: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to score section: {str(e)}")

@app.get("/assessment/summary")
def get_assessment_summary():
    """Get complete assessment summary with all section results"""
    try:
        return assessment_dashboard.get_assessment_summary()
    except Exception as e:
        logger.error(f"Error getting assessment summary: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get summary: {str(e)}")

@app.post("/chat/start")
def start_chat_session(request: Dict[str, Any]):
    """Start new chat session for risk mitigation"""
    try:
        assessment_id = request.get('assessment_id')
        assessment_results = request.get('assessment_results', {})
        
        if not assessment_id:
            raise HTTPException(status_code=400, detail="Assessment ID is required")
        
        session_id = risk_mitigation_chat.start_chat_session(assessment_id, assessment_results)
        return {"session_id": session_id}
    except Exception as e:
        logger.error(f"Error starting chat session: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to start chat: {str(e)}")

@app.post("/chat/{session_id}/message")
def send_chat_message(session_id: str, request: Dict[str, Any]):
    """Send message to chat session"""
    try:
        user_message = request.get('message')
        if not user_message:
            raise HTTPException(status_code=400, detail="Message is required")
        
        response = risk_mitigation_chat.process_user_message(session_id, user_message)
        return response
    except Exception as e:
        logger.error(f"Error processing chat message: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to process message: {str(e)}")

@app.get("/chat/{session_id}/history")
def get_chat_history(session_id: str):
    """Get chat session history"""
    try:
        return risk_mitigation_chat.get_session_history(session_id)
    except Exception as e:
        logger.error(f"Error getting chat history: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get history: {str(e)}")

def generate_dynamic_questions(profile: CompanyProfile) -> List[RiskQuestion]:
    """Generate a comprehensive set of risk assessment questions based on the company profile."""
    questions = []
    
    # Determine which categories to prioritize based on company profile
    prioritized_categories = []
    
    # Prioritize business strategy for all companies
    prioritized_categories.append("business_strategy")
    
    # Prioritize financial impact for smaller companies
    if profile.size.lower() in ["startup", "small", "sme", "medium"]:
        prioritized_categories.extend(["financial_impact", "talent_management"])
    
    # Prioritize market position for larger companies
    if profile.size.lower() in ["large", "enterprise", "corporation"]:
        prioritized_categories.extend(["market_position", "regulatory_compliance"])
    
    # Prioritize innovation for early adopters
    if profile.tech_adoption.lower() in ["early adopter", "innovator", "leader"]:
        prioritized_categories.extend(["innovation_culture", "emerging_tech_adoption"])
    
    # Prioritize security for regulated industries
    if profile.industry.lower() in ["finance", "banking", "healthcare", "government", "insurance"]:
        prioritized_categories.extend(["data_sensitivity", "regulatory_compliance", "third_party_risk"])
    
    # Add questions for all categories, prioritizing the selected ones
    for cat_def in RISK_CATEGORIES_DEFINITION:
        # Customize question based on category and profile
        question_text = f"Regarding {cat_def['category'].lower()} ({cat_def['definition']}), how would you describe your current practices related to {cat_def['scoring_focus'].lower()}?"
        
        # Customize helper text based on whether this is a priority category
        helper_text = f"Consider: {cat_def['definition']}. Focus on aspects like: {cat_def['scoring_focus']}."
        if cat_def['id'] in prioritized_categories:
            helper_text += f" This is a priority area for {profile.industry} companies of your size and technology adoption level."
        
        # Add specific customizations for certain categories
        if cat_def['id'] == "cloud_security" and "cloud" not in profile.emerging_technologies and not any("cloud" in tech.lower() for tech in profile.emerging_technologies):
            question_text = f"Regarding {cat_def['category'].lower()} ({cat_def['definition']}), even if not a primary focus, what are your considerations or practices for {cat_def['scoring_focus'].lower()} when evaluating or using any cloud services?"
        
        if cat_def['id'] == "emerging_tech_adoption":
            tech_list = ", ".join(profile.emerging_technologies)
            question_text = f"Regarding {cat_def['category'].lower()}, how do you evaluate and govern the adoption of new technologies like {tech_list} in your organization?"
        
        questions.append(RiskQuestion(
            id=cat_def['id'],
            question_text=question_text,
            category_name=cat_def['category'],
            helper_text=helper_text,
            scoring_focus=cat_def['scoring_focus']
        ))
    
    logger.info(f"Generated {len(questions)} dynamic questions with {len(prioritized_categories)} prioritized categories")
    return questions

def build_risk_table(profile: CompanyProfile, answers: Dict[str, str]) -> tuple[List[RiskTableRow], float, List[str]]:
    """Build a risk assessment table based on the company profile and answers."""
    table = []
    total_weighted_score_sum = 0.0
    total_weight_sum = 0.0
    data_insights = []
    
    for cat_def in RISK_CATEGORIES_DEFINITION:
        answer_text = answers.get(cat_def['id'], "No answer provided")
        
        # Use objective scoring with detailed justification
        try:
            score_justification = objective_scorer.calculate_objective_score(
                cat_def['id'], answer_text, profile.dict()
            )
            score = score_justification.score
            
            # Create detailed explanation
            explanation = f"Score: {score}/10 (Confidence: {score_justification.confidence:.2f}). "
            explanation += f"Base score: {score_justification.base_score}, "
            if score_justification.adjustments:
                adjustments_text = ", ".join([f"{adj[0]}: {adj[1]:+d}" for adj in score_justification.adjustments])
                explanation += f"Adjustments: {adjustments_text}. "
            
            if score_justification.evidence_found:
                explanation += f"Evidence found: {', '.join(score_justification.evidence_found[:3])}. "
            
            if score_justification.recommendations:
                explanation += f"Recommendation: {score_justification.recommendations[0]}"
            
        except Exception as e:
            logger.warning(f"Objective scoring failed for {cat_def['id']}: {str(e)}, using fallback")
            # Fallback to simple scoring
            score = 2 if answer_text.lower() == "no answer provided" else min(8, max(2, len(answer_text) // 25))
            explanation = f"Based on your response length and content. Assessment focused on {cat_def['scoring_focus']}."
        
        # Ensure score is within bounds
        score = max(0, min(cat_def['max_score'], score))
        
        # Create table row
        table.append(RiskTableRow(
            id=cat_def['id'],
            category=cat_def['category'],
            definition=cat_def['definition'],
            scoring_focus=cat_def['scoring_focus'],
            score=score,
            max_score=cat_def['max_score'],
            weight=cat_def['weight'],
            explanation=explanation
        ))
        
        # Update totals
        total_weighted_score_sum += score * cat_def['weight']
        total_weight_sum += cat_def['weight']
        
        # Add to insights
        data_insights.append(f"{cat_def['category']} (Weight: {cat_def['weight']*100}%): Score {score}/{cat_def['max_score']}. {explanation}")
    
    # Calculate normalized score (0-100)
    overall_score_normalized = (total_weighted_score_sum / (10 * total_weight_sum)) * 100 if total_weight_sum > 0 else 0
    overall_score_normalized = round(overall_score_normalized, 2)
    
    logger.info(f"Calculated risk table with {len(table)} rows. Overall weighted score: {overall_score_normalized}")
    return table, overall_score_normalized, data_insights

async def retrieve_rag_context(profile: CompanyProfile, answers: Dict[str, str], risk_table: List[RiskTableRow]) -> str:
    """Retrieve relevant context from the RAG system based on profile, answers, and risk table."""
    if not db:
        logger.error("Vector DB not initialized. Cannot retrieve context.")
        return "Vector DB not initialized."

    # Sort risks by score (ascending) to focus on highest risk areas
    sorted_risks = sorted(risk_table, key=lambda x: x.score)
    high_risk_categories = [f"{r.category} ({r.scoring_focus})" for r in sorted_risks[:3]]  # Top 3 high-risk areas

    # Create query from profile and high-risk areas
    query_parts = [
        f"Company industry: {profile.industry}",
        f"Company size: {profile.size}",
        f"Technology adoption level: {profile.tech_adoption}",
        f"Security controls summary: {profile.security_controls[:150]}",
        f"Risk posture summary: {profile.risk_posture[:150]}",
        f"Emerging technologies: {', '.join(profile.emerging_technologies)}",
        f"Key risk areas: {', '.join(high_risk_categories)}"
    ]
    
    # Add some key answers for context
    for risk_id, answer in list(answers.items())[:3]:  # Add first 3 answers
        category = next((cat['category'] for cat in RISK_CATEGORIES_DEFINITION if cat['id'] == risk_id), risk_id)
        query_parts.append(f"Response about {category}: {answer[:100]}")
    
    query = "\n".join(query_parts)
    logger.info(f"Retrieving RAG context with query (first 300 chars): {query[:300]}...")
    
    try:
        # Get relevant documents from vector store
        docs = db.similarity_search(query, k=3)  # Get top 3 relevant chunks
        
        # Process and truncate context to fit within limits
        current_context_len = 0
        context_parts = []
        separator = "\n\n---\n\n"
        
        for doc in docs:
            source_info = f"Source: {doc.metadata.get('source', 'Unknown')}"
            content = doc.page_content
            
            # Calculate budget for this document
            per_doc_content_budget = (MAX_RAG_CONTEXT_CHARS // len(docs)) - len(source_info) - len(separator) - 10
            per_doc_content_budget = max(50, per_doc_content_budget)  # Ensure minimum content
            
            # Truncate content to fit budget
            truncated_content = content[:per_doc_content_budget]
            doc_context_segment = f"{source_info}\nContent: {truncated_content}"
            
            # Check if adding this segment would exceed total budget
            if current_context_len + len(doc_context_segment) + (len(separator) if context_parts else 0) > MAX_RAG_CONTEXT_CHARS:
                break
            
            context_parts.append(doc_context_segment)
            current_context_len += len(doc_context_segment) + (len(separator) if len(context_parts) > 1 else 0)

        # Join context parts with separator
        context = separator.join(context_parts)
        logger.info(f"Retrieved and truncated RAG context from {len(context_parts)} documents. Total context length: {len(context)} chars.")
    except Exception as e:
        logger.error(f"Error during RAG context retrieval: {e}", exc_info=True)
        context = f"Error retrieving RAG context: {str(e)}"
        
    return context

async def generate_llm_advice_async(profile: CompanyProfile, answers: Dict[str, str], risk_table: List[RiskTableRow], context: str):
    """Generate advice using the LLM based on profile, answers, risk table, and RAG context."""
    if not qa_chain:
        logger.error("QA chain not initialized. Cannot generate LLM advice.")
        return ["LLM advice generation failed: RAG pipeline not ready."], [], "QA chain not initialized."

    # Define static parts of the prompt
    static_prompt_header = f"""
You are an expert cybersecurity and emerging technology risk management advisor.
Given the following company profile, their answers to risk assessment questions, the calculated risk table, and relevant context from governance documents, provide:
1. Actionable, prioritized recommendations to mitigate identified risks and improve their posture for adopting emerging technologies ({', '.join(profile.emerging_technologies)}).
2. Links to 2-3 key resources (from the provided context or well-known standards) that are most relevant to their highest risk areas.

Respond ONLY with a single valid JSON object in the following format (no extra text before or after the JSON object):

{{
  "recommendations": [
    "Recommendation 1 (with brief rationale)...",
    "Recommendation 2 (with brief rationale)..."
  ],
  "resources": [
    {{"title": "Resource Title 1", "url": "Resource URL 1 (if available from context, otherwise general standard)"}},
    {{"title": "Resource Title 2", "url": "Resource URL 2"}}
  ],
  "rawLLMOutput": "Your detailed thought process and summary of key risks observed before formulating recommendations."
}}

Company Profile:
"""
    static_prompt_answers_header = "\n\nRisk Assessment Answers:\n"
    static_prompt_table_header = "\n\nCalculated Risk Table (Scores out of 10, lower is worse):\n"
    static_prompt_context_header = "\n\nRelevant Context from Knowledge Base:\n"
    static_prompt_footer = "\n\nFocus on providing practical, actionable advice. Prioritize recommendations based on the risk scores (lower scores indicate higher risk) and their weights.\n"""

    # Calculate lengths of static parts
    len_static_prompt = (
        len(static_prompt_header) +
        len(static_prompt_answers_header) +
        len(static_prompt_table_header) +
        len(static_prompt_context_header) +
        len(static_prompt_footer)
    )
    logger.info(f"Static prompt parts total length: {len_static_prompt} chars")

    # Calculate budget for dynamic parts
    budget_for_other_dynamic_parts = TARGET_LLM_PROMPT_TOTAL_CHARS - len_static_prompt - len(context)
    logger.info(f"RAG context length: {len(context)} chars (Max allowed: {MAX_RAG_CONTEXT_CHARS})")
    logger.info(f"Budget for (profile + answers + table): {budget_for_other_dynamic_parts} chars")

    # Handle case where static + context already exceeds target
    if budget_for_other_dynamic_parts < 0:
        logger.warning(f"Static prompt ({len_static_prompt}) + RAG context ({len(context)}) exceeds target total ({TARGET_LLM_PROMPT_TOTAL_CHARS}). Truncating RAG context further.")
        context = context[:max(0, MAX_RAG_CONTEXT_CHARS // 2)]  # Drastically reduce context
        budget_for_other_dynamic_parts = TARGET_LLM_PROMPT_TOTAL_CHARS - len_static_prompt - len(context)
        logger.info(f"Further truncated RAG context to: {len(context)} chars. New budget: {budget_for_other_dynamic_parts}")

    # Prepare full dynamic content
    profile_info_full = f"Industry: {profile.industry}, Size: {profile.size}, Tech Adoption: {profile.tech_adoption}, Stated Controls: {profile.security_controls}, Stated Posture: {profile.risk_posture}, Emerging Tech: {', '.join(profile.emerging_technologies)}"
    
    # Focus on high-risk answers for the LLM
    sorted_risk_rows = sorted(risk_table, key=lambda x: x.score)
    high_risk_answers = {}
    for row in sorted_risk_rows[:5]:  # Top 5 risk areas
        if row.id in answers:
            high_risk_answers[row.id] = answers[row.id]
    
    answers_json_full = json.dumps(high_risk_answers, indent=2)
    risk_table_json_full = json.dumps([rt.dict() for rt in sorted_risk_rows[:8]], indent=2)  # Top 8 risk areas

    # Allocate budget for dynamic parts
    profile_chars_limit = int(budget_for_other_dynamic_parts * 0.20)
    answers_json_chars_limit = int(budget_for_other_dynamic_parts * 0.40)
    risk_table_json_chars_limit = int(budget_for_other_dynamic_parts * 0.40)

    # Truncate dynamic parts
    truncated_profile_info = profile_info_full[:profile_chars_limit]
    truncated_answers_json = answers_json_full[:answers_json_chars_limit]
    truncated_risk_table_json = risk_table_json_full[:risk_table_json_chars_limit]

    logger.info(f"Dynamic content lengths (chars) - Profile: {len(truncated_profile_info)}/{profile_chars_limit}, Answers: {len(truncated_answers_json)}/{answers_json_chars_limit}, RiskTable: {len(truncated_risk_table_json)}/{risk_table_json_chars_limit}")

    # Assemble final prompt
    prompt = (
        static_prompt_header + truncated_profile_info +
        static_prompt_answers_header + truncated_answers_json +
        static_prompt_table_header + truncated_risk_table_json +
        static_prompt_context_header + context +
        static_prompt_footer
    )
    final_prompt_len = len(prompt)
    logger.info(f"Final assembled prompt length: {final_prompt_len} chars. Target: {TARGET_LLM_PROMPT_TOTAL_CHARS}")

    # Warning if prompt is still too long
    if final_prompt_len > TARGET_LLM_PROMPT_TOTAL_CHARS * 1.05:
        logger.warning(f"WARNING: Final prompt length {final_prompt_len} significantly exceeds target {TARGET_LLM_PROMPT_TOTAL_CHARS}. LLM call might fail or be truncated by model.")

    try:
        # Invoke LLM
        logger.info("Invoking LLM with prompt...")
        result = qa_chain.invoke({"query": prompt})
        output = result.get("result", "")
        logger.info(f"Raw LLM output received (first 500 chars): {output[:500]}...")

        # Parse JSON response
        match = re.search(r'\{[\s\S]*\}', output)
        if match:
            json_str = match.group(0)
            try:
                structured_response = json.loads(json_str)
                recommendations = structured_response.get("recommendations", ["LLM failed to provide structured recommendations."])
                resources = structured_response.get("resources", [])
                raw_llm_summary = structured_response.get("rawLLMOutput", output)
                logger.info("Successfully parsed LLM JSON response.")
            except json.JSONDecodeError as e:
                logger.error(f"Failed to decode JSON from LLM output: {e}\nOutput was: {json_str}")
                recommendations = ["LLM response was not valid JSON. Please check logs."]
                resources = []
                raw_llm_summary = output
        else:
            logger.warning("No JSON object found in LLM output. Storing raw output.")
            recommendations = ["LLM did not return a JSON object. Storing raw output."]
            resources = []
            raw_llm_summary = output
    except Exception as e:
        logger.error(f"Error during LLM advice generation: {e}", exc_info=True)
        recommendations = ["An error occurred while generating LLM advice."]
        resources = []
        raw_llm_summary = f"Error: {str(e)}"
    
    # Ensure we have at least some recommendations
    if not recommendations or len(recommendations) == 0:
        recommendations = [
            "Implement a formal risk assessment process for emerging technology adoption.",
            "Develop a comprehensive security framework aligned with industry standards.",
            "Establish clear governance procedures for technology evaluation and implementation."
        ]
    
    # Ensure we have at least some resources
    if not resources or len(resources) == 0:
        resources = [
            {"title": "NIST Cybersecurity Framework", "url": "https://www.nist.gov/cyberframework"},
            {"title": "ISO/IEC 27001 Information Security Management", "url": "https://www.iso.org/isoiec-27001-information-security.html"}
        ]
    
    return recommendations, resources, raw_llm_summary

# --- Assessment Persistence Endpoints ---

@app.post("/assessment/save")
def save_assessment(assessment_data: Dict[str, Any]):
    """Save complete assessment results"""
    try:
        from database.models import DatabaseManager
        assessment_id = DatabaseManager.save_assessment_result(assessment_data)
        return {"assessment_id": assessment_id, "message": "Assessment saved successfully"}
    except Exception as e:
        logger.error(f"Error saving assessment: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to save assessment: {str(e)}")

@app.get("/assessment/load/{assessment_id}")
def load_assessment(assessment_id: int):
    """Load assessment results by ID"""
    try:
        from database.models import DatabaseManager
        assessment_data = DatabaseManager.load_assessment_result(assessment_id)
        if not assessment_data:
            raise HTTPException(status_code=404, detail="Assessment not found")
        return assessment_data
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error loading assessment: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to load assessment: {str(e)}")

@app.get("/assessment/latest")
def get_latest_assessment(company_id: Optional[int] = None):
    """Get the most recent assessment"""
    try:
        from database.models import DatabaseManager
        assessment_data = DatabaseManager.get_latest_assessment(company_id)
        if not assessment_data:
            return {"message": "No assessments found"}
        return assessment_data
    except Exception as e:
        logger.error(f"Error getting latest assessment: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get latest assessment: {str(e)}")

@app.get("/assessments/list")
def list_assessments(company_id: Optional[int] = None, limit: int = 10):
    """List recent assessments"""
    try:
        from database.models import get_session, Assessment
        db = get_session()
        query = db.query(Assessment)
        if company_id:
            query = query.filter(Assessment.company_id == company_id)
        
        assessments = query.order_by(Assessment.created_at.desc()).limit(limit).all()
        
        result = []
        for assessment in assessments:
            result.append({
                "id": assessment.id,
                "name": assessment.name,
                "status": assessment.status,
                "completion_percentage": assessment.completion_percentage,
                "overall_score": assessment.overall_score,
                "created_at": assessment.created_at.isoformat(),
                "completed_at": assessment.completed_at.isoformat() if assessment.completed_at else None
            })
        
        db.close()
        return {"assessments": result}
    except Exception as e:
        logger.error(f"Error listing assessments: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to list assessments: {str(e)}")

# --- Company Data Persistence Endpoints ---

@app.post("/company/save")
def save_company(company_data: Dict[str, Any]):
    """Save company information"""
    try:
        from database.models import DatabaseManager
        company_id = DatabaseManager.save_company_data(company_data)
        return {"company_id": company_id, "message": "Company data saved successfully"}
    except Exception as e:
        logger.error(f"Error saving company data: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to save company data: {str(e)}")

@app.get("/company/{company_id}")
def get_company(company_id: int):
    """Get company information"""
    try:
        from database.models import get_session, Company
        db = get_session()
        company = db.query(Company).filter(Company.id == company_id).first()
        db.close()
        
        if not company:
            raise HTTPException(status_code=404, detail="Company not found")
        
        return {
            "id": company.id,
            "name": company.name,
            "industry": company.industry,
            "size": company.size,
            "country": company.country,
            "settings": company.settings,
            "contact_info": company.contact_info,
            "compliance_requirements": company.compliance_requirements,
            "created_at": company.created_at.isoformat(),
            "updated_at": company.updated_at.isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error getting company data: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get company data: {str(e)}")

# --- System State Persistence ---

@app.post("/system/state/save")
def save_system_state(state_data: Dict[str, Any]):
    """Save system state"""
    try:
        from database.models import DatabaseManager
        for key, value in state_data.items():
            DatabaseManager.save_system_state(key, value, f"System state: {key}")
        return {"message": "System state saved successfully"}
    except Exception as e:
        logger.error(f"Error saving system state: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to save system state: {str(e)}")

@app.get("/system/state/{key}")
def get_system_state(key: str):
    """Get system state"""
    try:
        from database.models import DatabaseManager
        value = DatabaseManager.get_system_state(key)
        return {"key": key, "value": value}
    except Exception as e:
        logger.error(f"Error getting system state: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get system state: {str(e)}")

# --- Data Backup and Export ---

@app.get("/data/backup")
def backup_data():
    """Create backup of all assessment and company data"""
    try:
        from database.models import get_session, Assessment, Company, AssessmentResponse, SectionScore
        import json
        
        db = get_session()
        
        # Backup assessments
        assessments = db.query(Assessment).all()
        assessments_data = []
        for assessment in assessments:
            # Get responses
            responses = db.query(AssessmentResponse).filter(
                AssessmentResponse.assessment_id == assessment.id
            ).all()
            
            # Get section scores
            section_scores = db.query(SectionScore).filter(
                SectionScore.assessment_id == assessment.id
            ).all()
            
            assessment_data = {
                "id": assessment.id,
                "company_id": assessment.company_id,
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
                "responses": [
                    {
                        "section_id": r.section_id,
                        "question_id": r.question_id,
                        "response_value": r.response_value,
                        "answered_at": r.answered_at.isoformat()
                    } for r in responses
                ],
                "section_scores": [
                    {
                        "section_id": s.section_id,
                        "score": s.score,
                        "maturity_level": s.maturity_level,
                        "maturity_description": s.maturity_description,
                        "questions_answered": s.questions_answered,
                        "total_questions": s.total_questions,
                        "completion_rate": s.completion_rate,
                        "risk_breakdown": s.risk_breakdown,
                        "recommendations": s.recommendations,
                        "completed_at": s.completed_at.isoformat()
                    } for s in section_scores
                ]
            }
            assessments_data.append(assessment_data)
        
        # Backup companies
        companies = db.query(Company).all()
        companies_data = [
            {
                "id": c.id,
                "name": c.name,
                "industry": c.industry,
                "size": c.size,
                "country": c.country,
                "settings": c.settings,
                "contact_info": c.contact_info,
                "compliance_requirements": c.compliance_requirements,
                "created_at": c.created_at.isoformat(),
                "updated_at": c.updated_at.isoformat()
            } for c in companies
        ]
        
        db.close()
        
        backup_data = {
            "backup_date": datetime.utcnow().isoformat(),
            "version": "2.0",
            "assessments": assessments_data,
            "companies": companies_data
        }
        
        return backup_data
        
    except Exception as e:
        logger.error(f"Error creating backup: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to create backup: {str(e)}")

@app.post("/data/restore")
def restore_data(backup_data: Dict[str, Any]):
    """Restore data from backup"""
    try:
        from database.models import get_session, Assessment, Company, AssessmentResponse, SectionScore
        from datetime import datetime
        
        db = get_session()
        
        # Clear existing data (optional - you might want to make this configurable)
        # db.query(AssessmentResponse).delete()
        # db.query(SectionScore).delete()
        # db.query(Assessment).delete()
        # db.query(Company).delete()
        
        restored_assessments = 0
        restored_companies = 0
        
        # Restore companies
        for company_data in backup_data.get("companies", []):
            company = Company(
                name=company_data["name"],
                industry=company_data.get("industry"),
                size=company_data.get("size"),
                country=company_data.get("country"),
                settings=company_data.get("settings", {}),
                contact_info=company_data.get("contact_info", {}),
                compliance_requirements=company_data.get("compliance_requirements", {})
            )
            db.add(company)
            restored_companies += 1
        
        # Restore assessments
        for assessment_data in backup_data.get("assessments", []):
            assessment = Assessment(
                company_id=assessment_data.get("company_id"),
                name=assessment_data["name"],
                description=assessment_data.get("description"),
                status=assessment_data.get("status", "completed"),
                completion_percentage=assessment_data.get("completion_percentage", 0.0),
                sections_completed=assessment_data.get("sections_completed", 0),
                overall_score=assessment_data.get("overall_score"),
                maturity_level=assessment_data.get("maturity_level"),
                risk_level=assessment_data.get("risk_level")
            )
            db.add(assessment)
            db.commit()
            db.refresh(assessment)
            
            # Restore responses
            for response_data in assessment_data.get("responses", []):
                response = AssessmentResponse(
                    assessment_id=assessment.id,
                    section_id=response_data["section_id"],
                    question_id=response_data["question_id"],
                    response_value=response_data["response_value"]
                )
                db.add(response)
            
            # Restore section scores
            for score_data in assessment_data.get("section_scores", []):
                section_score = SectionScore(
                    assessment_id=assessment.id,
                    section_id=score_data["section_id"],
                    score=score_data["score"],
                    maturity_level=score_data.get("maturity_level"),
                    maturity_description=score_data.get("maturity_description"),
                    questions_answered=score_data.get("questions_answered", 0),
                    total_questions=score_data.get("total_questions", 0),
                    completion_rate=score_data.get("completion_rate", 0.0),
                    risk_breakdown=score_data.get("risk_breakdown", {}),
                    recommendations=score_data.get("recommendations", [])
                )
                db.add(section_score)
            
            restored_assessments += 1
        
        db.commit()
        db.close()
        
        return {
            "message": "Data restored successfully",
            "restored_companies": restored_companies,
            "restored_assessments": restored_assessments
        }
        
    except Exception as e:
        logger.error(f"Error restoring data: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to restore data: {str(e)}")
