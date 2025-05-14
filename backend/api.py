from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional
from fastapi.encoders import jsonable_encoder
import logging
import os
import json
import re

# --- Your RAG/vector/LLM imports and initialization here ---
# from rag_pipeline.loader import ...
# from rag_pipeline.embedder import ...
# from rag_pipeline.store import ...
# from rag_pipeline.retriever import ...
# qa_chain = build_rag_chain(db)
# etc.

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
# Data Models
# ------------------------------------
class CompanyProfile(BaseModel):
    name: Optional[str]
    industry: str
    size: str
    tech_adoption: str
    security_controls: str
    risk_posture: str
    emerging_technologies: List[str]

class RiskTableRow(BaseModel):
    category: str
    score: int
    max: int
    explanation: str
    resource: Optional[str] = None

class RiskAnswers(BaseModel):
    answers: Dict[str, str]

class RiskAssessmentResult(BaseModel):
    overallScore: int
    riskTable: List[RiskTableRow]
    recommendations: List[str]
    resources: List[Dict[str, str]]
    dataInsights: List[str]
    rawLLMOutput: str

class RiskQuestion(BaseModel):
    id: str
    question: str
    category: str
    helper_text: str

# --- In-memory session/context store (for demo) ---
session_context = {}

# ------------------------------------
# Endpoints
# ------------------------------------
@app.post("/company-profile")
def company_profile(profile: CompanyProfile):
    session_context['profile'] = profile
    questions = generate_dynamic_questions(profile)
    return jsonable_encoder(questions)

@app.post("/risk-assessment", response_model=RiskAssessmentResult)
def risk_assessment(answers: RiskAnswers):
    profile = session_context.get('profile')
    if not profile:
        raise HTTPException(status_code=400, detail="No company profile found.")
    # 1. Build risk table
    risk_table, overall_score, data_insights = build_risk_table(profile, answers)
    # 2. Retrieve context from vector DB (RAG)
    context = retrieve_context(profile, answers)
    # 3. Generate recommendations/resources with LLM
    recommendations, resources, raw_llm = generate_llm_advice(profile, answers, risk_table, context)
    return RiskAssessmentResult(
        overallScore=overall_score,
        riskTable=risk_table,
        recommendations=recommendations,
        resources=resources,
        dataInsights=data_insights,
        rawLLMOutput=raw_llm
    )

# ------------------------------------
# Risk Table Generation
# ------------------------------------
def build_risk_table(profile: CompanyProfile, answers: RiskAnswers):
    categories = [
        {"category": "Governance", "id": "regulatory", "max": 5, "resource": "NIST SP 800-37"},
        {"category": "Data Protection", "id": "data_type", "max": 5, "resource": "ENISA AI Cybersecurity"},
        {"category": "Network Security", "id": "encryption", "max": 5, "resource": "NIST SP 800-53"},
        # ...add more categories up to 20-30 as needed...
    ]
    table = []
    total = 0
    data_insights = []
    for cat in categories:
        answer = answers.answers.get(cat["id"], "")
        score = 5 if "yes" in answer.lower() or "gdpr" in answer.lower() else 3 if answer else 2
        explanation = f"Answer: {answer or 'No answer provided'}"
        table.append(RiskTableRow(
            category=cat["category"],
            score=score,
            max=cat["max"],
            explanation=explanation,
            resource=cat["resource"]
        ))
        total += score
        data_insights.append(f"{cat['category']} score rationale: {explanation}")
    overall_score = int(total / len(categories) * 20)  # Example: scale to 100
    return table, overall_score, data_insights

# ------------------------------------
# RAG-Driven LLM Integration
# ------------------------------------
def generate_llm_advice(profile, answers, risk_table, context):
    prompt = f"""
You are an expert in risk management for emerging technologies. Given the following company profile, risk answers, risk table, and context, respond ONLY with valid JSON in this format (no extra text):

{{
  "recommendations": ["..."],
  "resources": [{{"title": "...", "url": "..."}}],
  "rawLLMOutput": "..."
}}

Company Profile: {profile}
Risk Answers: {answers}
Risk Table: {risk_table}
Relevant Context: {context}
"""
    result = qa_chain.invoke(prompt)
    output = result["result"]
    match = re.search(r'\{[\s\S]*\}', output)
    json_str = match.group(0) if match else output
    try:
        structured = json.loads(json_str)
        recommendations = structured.get("recommendations", [])
        resources = structured.get("resources", [])
        raw_llm = structured.get("rawLLMOutput", output)
    except Exception:
        recommendations = ["The AI was unable to generate structured recommendations."]
        resources = []
        raw_llm = output
    return recommendations, resources, raw_llm

# ------------------------------------
# Context Retrieval (RAG)
# ------------------------------------
def retrieve_context(profile, answers):
    # Combine profile and answers into a query string
    query = f"{profile.industry} {profile.size} {profile.tech_adoption} {profile.security_controls} {profile.risk_posture} {' '.join(profile.emerging_technologies)} " + " ".join(answers.answers.values())
    # Use your RAG retriever to get relevant docs
    docs = db.similarity_search(query, k=5)
    context = "\n".join([doc.page_content for doc in docs])
    return context

def generate_dynamic_questions(profile: CompanyProfile) -> List[RiskQuestion]:
    # Example: tailor questions based on profile fields
    questions = [
        RiskQuestion(
            id="regulatory",
            question=f"What regulatory standards apply to your business (e.g. {'HIPAA' if 'health' in profile.industry.lower() else 'GDPR, PCI-DSS'})?",
            category="compliance",
            helper_text="List all compliance frameworks or regulations that your business must follow."
        ),
        RiskQuestion(
            id="data_type",
            question="What types of sensitive data do you store or process? (PII, PHI, financial, etc.)",
            category="data",
            helper_text="Specify all types of sensitive data, e.g., patient health info, credit cards, etc."
        ),
        # ...add more questions as needed, using profile fields for tailoring...
    ]
    return questions