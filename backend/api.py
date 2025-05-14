from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from rag_pipeline.loader import load_documents, chunk_documents
from rag_pipeline.embedder import get_embedder
from rag_pipeline.store import store_embeddings, load_existing_embeddings
from rag_pipeline.retriever import build_rag_chain
from typing import List, Dict, Optional
from fastapi.encoders import jsonable_encoder

import logging
import os
import json
import re

# ------------------------------------
# Logging Configuration
# ------------------------------------
logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# ------------------------------------
# Constants
# ------------------------------------
DATA_DIR = "data/"
VECTOR_DIR = "vectordb/"

# ------------------------------------
# FastAPI Initialization
# ------------------------------------
app = FastAPI(title="RiskIQ-AI")

# ------------------------------------
# CORS Middleware Setup
# ------------------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Change to ["http://localhost:3000"] or your Vercel URL in production
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# ------------------------------------
# Load or Build Vector DB
# ------------------------------------
logger.info("Starting up RiskIQ-AI backend...")
embedder = get_embedder()  # ✅ Get the embedder before using

if os.path.exists(os.path.join(VECTOR_DIR, "chroma.sqlite3")):
    logger.info("Found existing vector DB. Loading from disk.")
    db = load_existing_embeddings(embedder, persist_dir=VECTOR_DIR)  # ✅ Pass embedder
else:
    logger.info("No vector DB found. Ingesting and embedding documents...")
    docs = load_documents(DATA_DIR)
    chunks = chunk_documents(docs)
    db = store_embeddings(chunks, embedder, persist_dir=VECTOR_DIR)

# ------------------------------------
# Build Retrieval-Augmented Generation Chain
# ------------------------------------
qa_chain = build_rag_chain(db)
logger.info("RAG chain initialized and ready.")

# ------------------------------------
# Request Schema
# ------------------------------------
class QueryRequest(BaseModel):
    question: str

class BusinessOverview(BaseModel):
    industry: str
    core_services: str
    critical_technologies: str

class RiskQuestion(BaseModel):
    id: str
    question: str
    category: str
    helper_text: Optional[str] = None  # Add helper text for guidance

class RiskAnswers(BaseModel):
    answers: Dict[str, str]  # question_id -> answer

class RiskAssessmentResult(BaseModel):
    riskScore: int
    riskLevel: str
    mitigationGuidance: str
    techIntegrationTips: str
    roadmap: Dict[str, str]
    freeform: str

# ------------------------------------
# RAG Endpoint
# ------------------------------------
@app.post("/query")
async def query_rag(request: QueryRequest):
    try:
        result = qa_chain.invoke(request.question)
        # Try to parse the result as JSON
        try:
            structured = json.loads(result["result"])
        except Exception:
            # Fallback: put the whole answer in freeform
            structured = {
                "companyOverview": "",
                "riskLandscape": "",
                "mitigationStrategy": "",
                "freeform": result["result"]
            }
        return structured
    except Exception as e:
        logger.error(f"Query failed: {e}")
        raise HTTPException(status_code=500, detail="Internal model inference error.")

# --- In-memory session/context store (for demo) ---
session_context = {}

@app.post("/business-overview", response_model=List[RiskQuestion])
def business_overview(overview: BusinessOverview):
    questions = generate_dynamic_questions(overview)
    session_context['overview'] = overview
    print("Returning questions:", questions)
    return jsonable_encoder(questions)

@app.post("/risk-assessment")
def risk_assessment(answers: RiskAnswers):
    overview = session_context.get('overview')
    if not overview:
        raise HTTPException(status_code=400, detail="No business overview found.")
    # 1. Compute risk score
    risk_score, risk_level = compute_risk_score(overview, answers)
    # 2. Retrieve context from vector DB (RAG)
    context = retrieve_context(overview, answers)
    # 3. Generate recommendations with LLM
    mitigation, tips, roadmap, freeform = generate_llm_recommendations(overview, answers, risk_score, context)
    return RiskAssessmentResult(
        riskScore=risk_score,
        riskLevel=risk_level,
        mitigationGuidance=mitigation,
        techIntegrationTips=tips,
        roadmap=roadmap,
        freeform=freeform
    )

# --- Helper functions (to implement) ---
def generate_dynamic_questions(overview: BusinessOverview) -> List[RiskQuestion]:
    # More specific and guided questions, with helper text
    questions = [
        RiskQuestion(
            id="regulatory",
            question=f"What regulatory standards apply to your business (e.g. {'HIPAA' if 'health' in overview.industry.lower() else 'GDPR, PCI-DSS'})?",
            category="compliance",
            helper_text="List all compliance frameworks or regulations that your business must follow."
        ),
        RiskQuestion(
            id="data_type",
            question="What types of sensitive data do you store or process? (PII, PHI, financial, etc.)",
            category="data",
            helper_text="Specify all types of sensitive data, e.g., patient health info, credit cards, etc."
        ),
        RiskQuestion(
            id="encryption",
            question="How is sensitive data currently encrypted (at rest/in transit)?",
            category="data",
            helper_text="Describe encryption methods, e.g., AES-256, TLS 1.2, etc."
        ),
        RiskQuestion(
            id="third_party",
            question="What third-party vendors, SaaS platforms, or cloud providers do you use?",
            category="vendors",
            helper_text="List all major third-party services, e.g., AWS, Azure, Salesforce, etc."
        ),
        RiskQuestion(
            id="ai_iot",
            question="What's the current level of AI/IoT adoption in your business?",
            category="emerging_tech",
            helper_text="Describe any AI, ML, or IoT systems in use or planned."
        ),
        RiskQuestion(
            id="maturity",
            question="How would you describe your cybersecurity maturity? (Initial, Developing, Defined, Managed, Optimizing)",
            category="maturity",
            helper_text="Use a standard maturity model or describe your current state."
        ),
        RiskQuestion(
            id="incident_response",
            question="Do you have an incident response plan? How often is it tested?",
            category="process",
            helper_text="Describe your incident response process and testing frequency."
        ),
        RiskQuestion(
            id="access_control",
            question="How is access to critical systems and data managed?",
            category="access",
            helper_text="Describe your access control policies, MFA, least privilege, etc."
        ),
        RiskQuestion(
            id="supply_chain",
            question="How do you assess and manage supply chain risks?",
            category="supply_chain",
            helper_text="Describe your process for evaluating and monitoring suppliers."
        ),
        RiskQuestion(
            id="training",
            question="What security and compliance training do employees receive?",
            category="training",
            helper_text="Describe frequency and content of employee training."
        ),
    ]
    return questions

def compute_risk_score(overview: BusinessOverview, answers: RiskAnswers) -> (int, str):
    # Example weights (customize as needed)
    weights = {
        "regulatory": 20,
        "data_type": 20,
        "encryption": 20,
        "third_party": 20,
        "ai_iot": 10,
        "maturity": 10,
    }
    score = 100
    # Example scoring logic (customize for your rubric)
    if "regulatory" in answers.answers and "none" in answers.answers["regulatory"].lower():
        score -= weights["regulatory"]
    if "data_type" in answers.answers and "yes" in answers.answers["data_type"].lower():
        score -= weights["data_type"]
    if "encryption" in answers.answers and "no" in answers.answers["encryption"].lower():
        score -= weights["encryption"]
    if "third_party" in answers.answers and "yes" in answers.answers["third_party"].lower():
        score -= weights["third_party"]
    if "ai_iot" in answers.answers and "high" in answers.answers["ai_iot"].lower():
        score -= weights["ai_iot"]
    if "maturity" in answers.answers and "initial" in answers.answers["maturity"].lower():
        score -= weights["maturity"]

    # Clamp score between 0 and 100
    score = max(0, min(100, score))

    # Risk level
    if score <= 30:
        risk_level = "Critical"
    elif score <= 60:
        risk_level = "At Risk"
    else:
        risk_level = "Low Risk"
    return score, risk_level

def retrieve_context(overview, answers):
    # Combine overview and answers into a query
    query = f"{overview.industry} {overview.core_services} {overview.critical_technologies} " + " ".join(answers.answers.values())
    # Use your RAG retriever to get relevant docs
    docs = db.similarity_search(query, k=5)
    context = "\n".join([doc.page_content for doc in docs])
    return context

def extract_json(text):
    # Try to extract the first JSON object from the text
    match = re.search(r'\\{[\\s\\S]*\\}', text)
    if match:
        return match.group(0)
    return None

def generate_llm_recommendations(overview, answers, risk_score, context):
    prompt = f'''
Respond ONLY with valid JSON in the following format. Do NOT include any explanations, markdown, or extra text. If you don't know, use an empty string.

{{
  "mitigationGuidance": "...",
  "techIntegrationTips": "...",
  "roadmap": {{
    "shortTerm": "...",
    "mediumTerm": "...",
    "longTerm": "..."
  }},
  "freeform": "..."
}}

Business Overview: {overview}
Risk Answers: {answers}
Risk Score: {risk_score}
Relevant Context: {context}
'''
    result = qa_chain.invoke(prompt)
    output = result["result"]
    # Try to extract JSON if extra text is present
    json_str = extract_json(output)
    try:
        structured = json.loads(json_str if json_str else output)
        mitigation = structured.get("mitigationGuidance", "No mitigation guidance provided.")
        tips = structured.get("techIntegrationTips", "No tech integration tips provided.")
        roadmap = structured.get("roadmap", {
            "shortTerm": "No short term actions provided.",
            "mediumTerm": "No medium term actions provided.",
            "longTerm": "No long term actions provided."
        })
        freeform = structured.get("freeform", "No freeform advice provided.")
    except Exception:
        mitigation = "The AI was unable to generate a structured response. Please try again or refine your input."
        tips = ""
        roadmap = {
            "shortTerm": "",
            "mediumTerm": "",
            "longTerm": ""
        }
        freeform = output
    return mitigation, tips, roadmap, freeform