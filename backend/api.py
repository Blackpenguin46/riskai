from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional, Any
from fastapi.encoders import jsonable_encoder
import logging
import os
import json
import re

# --- RAG/vector/LLM imports and initialization ---
from rag_pipeline.loader import load_documents, chunk_documents
from rag_pipeline.embedder import get_embedder
from rag_pipeline.store import store_embeddings, load_existing_embeddings
from rag_pipeline.retriever import build_rag_chain

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
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

# ------------------------------------
# Global RAG Pipeline Components & Limits
# ------------------------------------
DB_PERSIST_DIR = "vectordb"
PDF_DATA_DIR = "data/"

# Max characters for the RAG context to be retrieved. Model limit is ~1024 tokens.
# 1000 chars ~ 250 tokens. This leaves room for the rest of the prompt.
MAX_RAG_CONTEXT_CHARS = 1000
# Target for the total character length of the prompt sent to the LLM.
# Aiming well under 1024 tokens * ~4 chars/token (e.g. < 4000 chars)
TARGET_LLM_PROMPT_TOTAL_CHARS = 3600 # Reduced further for safety

embedder = None
db = None
qa_chain = None

@app.on_event("startup")
async def startup_event():
    global embedder, db, qa_chain
    try:
        logger.info("Initializing embedder...")
        embedder = get_embedder()
        if not embedder:
            raise RuntimeError("Failed to initialize embedder")

        logger.info("Initializing RAG pipeline...")
        if os.path.exists(DB_PERSIST_DIR) and os.listdir(DB_PERSIST_DIR):
            logger.info(f"Loading existing vector store from {DB_PERSIST_DIR}")
            db = load_existing_embeddings(embedder, persist_dir=DB_PERSIST_DIR)
        else:
            logger.info(f"No existing vector store found. Building new one from {PDF_DATA_DIR}")
            docs = load_documents(PDF_DATA_DIR)
            if not docs:
                raise RuntimeError(f"No documents found in {PDF_DATA_DIR}")
            chunks = chunk_documents(docs)
            db = store_embeddings(chunks, embedder, persist_dir=DB_PERSIST_DIR)
        
        if not db:
            raise RuntimeError("Failed to initialize vector store")
        
        logger.info("Building QA chain...")
        qa_chain = build_rag_chain(db)
        if not qa_chain:
            raise RuntimeError("Failed to build QA chain")
        
        logger.info("RAG pipeline initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize RAG pipeline: {str(e)}")
        raise RuntimeError(f"Failed to initialize RAG pipeline: {str(e)}")

class CompanyProfile(BaseModel):
    name: Optional[str] = None
    industry: str
    size: str
    tech_adoption: str
    security_controls: str
    risk_posture: str
    emerging_technologies: List[str]

class RiskTableRow(BaseModel):
    id: str
    category: str
    definition: str
    scoring_focus: str
    score: int
    max_score: int
    weight: float
    explanation: str

class RiskAnswer(BaseModel):
    question_id: str
    answer: str

class RiskAnswersRequest(BaseModel):
    answers: List[RiskAnswer]

class RiskAssessmentResult(BaseModel):
    overall_weighted_score: float
    risk_table: List[RiskTableRow]
    recommendations: List[str]
    resources: List[Dict[str, str]]
    data_insights: List[str]
    raw_llm_output: Optional[str] = None

class RiskQuestion(BaseModel):
    id: str
    question_text: str
    category_name: str
    helper_text: Optional[str] = None
    scoring_focus: str

session_context: Dict[str, Any] = {}

RISK_CATEGORIES_DEFINITION = [
    {"id": "asset_visibility", "category": "Asset Visibility", "definition": "Degree to which the organization knows and inventories its IT assets (hardware, software, cloud resources).", "scoring_focus": "Asset registry, CMDB, shadow IT detection", "weight": 0.05, "max_score": 10},
    {"id": "data_sensitivity", "category": "Data Sensitivity & Classification", "definition": "Processes for labeling, managing, and securing data based on confidentiality, integrity, and availability (CIA).", "scoring_focus": "Classification tiers, encryption, data flow maps", "weight": 0.05, "max_score": 10},
    {"id": "access_management", "category": "Access Management", "definition": "Enforcement of least privilege, role-based access controls (RBAC), SSO, MFA, and joiner/mover/leaver processes.", "scoring_focus": "IAM maturity, MFA adoption, AD hygiene", "weight": 0.06, "max_score": 10},
    {"id": "network_security", "category": "Network Security Posture", "definition": "Strength of network segmentation, firewall rules, intrusion detection, and Zero Trust principles.", "scoring_focus": "Segmentation, micro-perimeters, SDN, detection systems", "weight": 0.05, "max_score": 10},
    {"id": "endpoint_security", "category": "Endpoint Security", "definition": "Use of EDR/XDR, antivirus, mobile device management (MDM), and hardening baselines.", "scoring_focus": "Device hygiene, patching, visibility", "weight": 0.05, "max_score": 10},
    {"id": "patch_vulnerability_management", "category": "Patch & Vulnerability Management", "definition": "Speed and completeness of addressing known software/hardware vulnerabilities.", "scoring_focus": "Time-to-remediate, CVSS prioritization, SBOM use", "weight": 0.06, "max_score": 10},
    {"id": "cloud_security", "category": "Cloud Security", "definition": "Protection of cloud workloads and infrastructure (IaaS, PaaS, SaaS) using shared responsibility models.", "scoring_focus": "CSPM usage, workload isolation, key management", "weight": 0.05, "max_score": 10},
    {"id": "third_party_risk", "category": "Third-Party Risk", "definition": "Risk from vendors, partners, and supply chain entities with access to your systems or data.", "scoring_focus": "Vendor assessments, contract clauses, breach awareness", "weight": 0.05, "max_score": 10},
    {"id": "incident_response", "category": "Incident Detection & Response", "definition": "Ability to detect, triage, respond to, and recover from cyber incidents effectively.", "scoring_focus": "SIEM/SOAR, playbooks, RTO/RPO", "weight": 0.07, "max_score": 10},
    {"id": "security_awareness", "category": "Security Awareness Training", "definition": "Ongoing efforts to educate employees on phishing, password hygiene, and safe digital behavior.", "scoring_focus": "Frequency, phishing test scores, LMS coverage", "weight": 0.04, "max_score": 10},
    {"id": "grc", "category": "Governance, Risk & Compliance (GRC)", "definition": "Integration of policy, risk registers, regulatory mapping, and control audits.", "scoring_focus": "GRC tooling, policy gaps, audit frequency", "weight": 0.05, "max_score": 10},
    {"id": "secure_sdlc", "category": "Secure Development (SDLC)", "definition": "Degree to which security is integrated into software development lifecycle.", "scoring_focus": "SAST, DAST, threat modeling, dev training", "weight": 0.04, "max_score": 10},
    {"id": "identity_auth", "category": "Identity & Authentication", "definition": "Strength and centralization of identity control systems (IdP, SSO, OAuth, OpenID).", "scoring_focus": "Auth methods, federation, IdP maturity", "weight": 0.04, "max_score": 10},
    {"id": "business_continuity", "category": "Business Continuity & Resilience", "definition": "Organization's readiness to maintain operations during cyber attacks or outages.", "scoring_focus": "BCP/DR plans, failover tests, resilience strategy", "weight": 0.04, "max_score": 10},
    {"id": "security_monitoring", "category": "Security Monitoring & Logging", "definition": "Centralized logging, alerting thresholds, and actionable telemetry.", "scoring_focus": "Log aggregation, SIEM use, anomaly detection", "weight": 0.04, "max_score": 10},
    {"id": "risk_quantification", "category": "Risk Quantification & Reporting", "definition": "Methods used to quantify and communicate cyber risk to stakeholders.", "scoring_focus": "FAIR use, dashboards, board reporting", "weight": 0.03, "max_score": 10},
    {"id": "app_security", "category": "Application Security", "definition": "Security practices and tooling applied to web, mobile, and internal applications.", "scoring_focus": "AppSec tools, bug bounty, static/dynamic scanning", "weight": 0.04, "max_score": 10},
    {"id": "physical_security", "category": "Physical Security Controls", "definition": "Protection of on-premise assets and data centers from unauthorized physical access.", "scoring_focus": "Badging, cameras, cage access, visitor controls", "weight": 0.02, "max_score": 10},
    {"id": "security_architecture", "category": "Security Architecture & Design", "definition": "Maturity of enterprise architecture for securely integrating infrastructure, services, and identity.", "scoring_focus": "Zero Trust design, tiering, reference architectures", "weight": 0.03, "max_score": 10},
    {"id": "emerging_tech_adoption", "category": "Emerging Technology Adoption", "definition": "Preparedness to adopt and govern new technologies (AI, quantum, blockchain) securely.", "scoring_focus": "Risk vetting, PoC governance, PQC, AI use policy", "weight": 0.03, "max_score": 10}
]

@app.post("/initialize-assessment")
def initialize_assessment(profile: CompanyProfile):
    if not qa_chain:
        logger.error("RAG pipeline not initialized")
        raise HTTPException(status_code=503, detail="Service not ready. Please try again in a few moments.")
    
    logger.info(f"Received company profile: {profile.name if profile.name else 'Unnamed Company'}")
    session_context["profile"] = profile
    try:
        questions = generate_dynamic_questions_for_categories(profile)
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
        logger.info(f"Received answers for profile: {profile.name if profile.name else 'Unnamed'}")
        logger.info(f"DEBUG: request.answers = {request.answers}")

        # Defensive: ensure each answer is a dict/object with question_id and answer
        answers_list = []
        for ans in request.answers:
            if isinstance(ans, dict):
                answers_list.append(RiskAnswer(**ans))
            elif isinstance(ans, RiskAnswer):
                answers_list.append(ans)
            else:
                logger.error(f"Malformed answer: {ans}")
                raise HTTPException(status_code=400, detail=f"Malformed answer: {ans}")

        answers_dict = {ans.question_id: ans.answer for ans in answers_list}

        risk_table, overall_weighted_score, data_insights = build_risk_table_from_answers(profile, answers_dict)
        
        context = await retrieve_rag_context(profile, answers_dict, risk_table)
        
        recommendations, resources, raw_llm = await generate_llm_advice_async(profile, answers_dict, risk_table, context)
        
        if not recommendations or not resources:
            raise HTTPException(status_code=500, detail="Failed to generate recommendations")
        
        return RiskAssessmentResult(
            overall_weighted_score=overall_weighted_score,
            risk_table=risk_table,
            recommendations=recommendations,
            resources=resources,
            data_insights=data_insights,
            raw_llm_output=raw_llm
        )
    except Exception as e:
        logger.error(f"Error processing answers: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to process assessment: {str(e)}")

def generate_dynamic_questions_for_categories(profile: CompanyProfile) -> List[RiskQuestion]:
    questions = []
    for cat_def in RISK_CATEGORIES_DEFINITION:
        question_text = f"Regarding {cat_def['category'].lower()} ({cat_def['definition']}), how would you describe your current practices related to {cat_def['scoring_focus'].lower()}?"
        if cat_def['id'] == "cloud_security" and "cloud" not in profile.emerging_technologies and not any("cloud" in tech.lower() for tech in profile.emerging_technologies):
             question_text = f"Regarding {cat_def['category'].lower()} ({cat_def['definition']}), even if not a primary focus, what are your considerations or practices for {cat_def['scoring_focus'].lower()} when evaluating or using any cloud services?"
        questions.append(RiskQuestion(
            id=cat_def['id'],
            question_text=question_text,
            category_name=cat_def['category'],
            helper_text=f"Consider: {cat_def['definition']}. Focus on aspects like: {cat_def['scoring_focus']}.",
            scoring_focus=cat_def['scoring_focus']
        ))
    logger.info(f"Generated {len(questions)} dynamic questions.")
    return questions

def build_risk_table_from_answers(profile: CompanyProfile, answers: Dict[str, str]) -> tuple[List[RiskTableRow], float, List[str]]:
    table = []
    total_weighted_score_sum = 0.0
    total_weight_sum = 0.0
    data_insights = []
    for cat_def in RISK_CATEGORIES_DEFINITION:
        answer_text = answers.get(cat_def['id'], "No answer provided")
        score = 0
        if answer_text.lower() == "no answer provided": score = 2
        elif len(answer_text) < 20: score = 4
        elif len(answer_text) < 100: score = 6
        else: score = 8
        if any(kw in answer_text.lower() for kw in ["strong", "comprehensive", "fully implemented", "excellent"]): score = min(cat_def['max_score'], score + 2)
        elif any(kw in answer_text.lower() for kw in ["weak", "lacking", "not implemented", "poor"]): score = max(0, score - 2)
        score = max(0, min(cat_def['max_score'], score))
        explanation = f"User's answer for {cat_def['category']}: '{answer_text}'. Scoring based on perceived detail and keywords against focus: {cat_def['scoring_focus']}."
        table.append(RiskTableRow(id=cat_def['id'], category=cat_def['category'], definition=cat_def['definition'], scoring_focus=cat_def['scoring_focus'], score=score, max_score=cat_def['max_score'], weight=cat_def['weight'], explanation=explanation))
        total_weighted_score_sum += score * cat_def['weight']
        total_weight_sum += cat_def['weight']
        data_insights.append(f"{cat_def['category']} (Weight: {cat_def['weight']*100}%): Score {score}/{cat_def['max_score']}. Rationale: {explanation}")
    overall_score_normalized = (total_weighted_score_sum / (10 * total_weight_sum)) * 100 if total_weight_sum > 0 else 0
    overall_score_normalized = round(overall_score_normalized, 2)
    logger.info(f"Calculated risk table. Overall weighted score: {overall_score_normalized}")
    return table, overall_score_normalized, data_insights

async def generate_llm_advice_async(profile: CompanyProfile, answers: Dict[str, str], risk_table: List[RiskTableRow], context: str):
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

    len_static_prompt = (
        len(static_prompt_header) +
        len(static_prompt_answers_header) +
        len(static_prompt_table_header) +
        len(static_prompt_context_header) +
        len(static_prompt_footer)
    )

    # Truncate context if it exceeds the target prompt length
    if len(context) > MAX_RAG_CONTEXT_CHARS:
        context = context[:MAX_RAG_CONTEXT_CHARS]

    # Define dynamic parts of the prompt
    dynamic_prompt_header = f"Risk Assessment Answers:\n"
    dynamic_prompt_answers = "\n" + "\n".join([f"{ans.question_id}: {ans.answer}" for ans in answers]) + "\n"
    dynamic_prompt_table = "\n" + "\n".join([f"{row.id}: {row.score}/{row.max_score} ({row.category})" for row in risk_table]) + "\n"
    dynamic_prompt_context = "\n" + context + "\n"
    dynamic_prompt_footer = "\n\nFocus on providing practical, actionable advice. Prioritize recommendations based on the risk scores (lower scores indicate higher risk) and their weights.\n"""

    len_dynamic_prompt = (
        len(dynamic_prompt_header) +
        len(dynamic_prompt_answers) +
        len(dynamic_prompt_table) +
        len(dynamic_prompt_context) +
        len(dynamic_prompt_footer)
    )

    # Ensure total prompt length is within the target
    if len_static_prompt + len_dynamic_prompt > TARGET_LLM_PROMPT_TOTAL_CHARS:
        # Truncate the context to fit within the target
        context = context[:MAX_RAG_CONTEXT_CHARS]
        len_dynamic_prompt = (
            len(dynamic_prompt_header) +
            len(dynamic_prompt_answers) +
            len(dynamic_prompt_table) +
            len(dynamic_prompt_context) +
            len(dynamic_prompt_footer)
        )

    # Construct the final prompt
    prompt = static_prompt_header + static_prompt_answers_header + static_prompt_table_header + static_prompt_context_header + static_prompt_footer + dynamic_prompt_header + dynamic_prompt_answers + dynamic_prompt_table + dynamic_prompt_context + dynamic_prompt_footer

    # Generate the response
    response = qa_chain(prompt)

    # Parse the response
    try:
        response_json = json.loads(response)
        recommendations = response_json["recommendations"]
        resources = response_json["resources"]
        raw_llm = response_json["rawLLMOutput"]
    except Exception as e:
        logger.error(f"Error parsing LLM response: {str(e)}")
        return ["LLM advice generation failed: Error parsing response"], [], "LLM advice generation failed: Error parsing response"

    return recommendations, resources, raw_llm

async def retrieve_rag_context(profile: CompanyProfile, answers: Dict[str, str], risk_table: List[RiskTableRow]) -> str:
    # This function needs to be implemented to retrieve relevant context from the RAG pipeline
    # For now, we'll return an empty string as a placeholder
    return ""