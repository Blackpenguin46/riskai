from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import List, Dict, Optional, Any
from fastapi.encoders import jsonable_encoder
import logging
import os
import json
import traceback

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
    try:
        logger.info("Initializing embedder...")
        embedder = get_embedder()
        if not embedder:
            raise RuntimeError("Failed to initialize embedder")

        logger.info("Initializing RAG pipeline...")
        if os.path.exists(DB_PERSIST_DIR) and os.listdir(DB_PERSIST_DIR):
            db = load_existing_embeddings(embedder, persist_dir=DB_PERSIST_DIR)
        else:
            docs = load_documents(PDF_DATA_DIR)
            if not docs:
                raise RuntimeError(f"No documents found in {PDF_DATA_DIR}")
            chunks = chunk_documents(docs)
            db = store_embeddings(chunks, embedder, persist_dir=DB_PERSIST_DIR)

        if not db:
            raise RuntimeError("Failed to initialize vector store")

        qa_chain = build_rag_chain(db)
        if not qa_chain:
            raise RuntimeError("Failed to build QA chain")

        logger.info("RAG pipeline initialized successfully")
    except Exception as e:
        logger.error(f"Failed to initialize RAG pipeline: {str(e)}")
        raise RuntimeError(f"Startup error: {str(e)}")

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
    risk_table: List[RiskTableRow]
    recommendations: List[str]
    resources: List[Dict[str, str]]
    data_insights: List[str]
    raw_llm_output: Optional[str] = None

session_context: Dict[str, Any] = {}

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
        answers_dict = {ans.question_id: ans.answer for ans in request.answers}
        risk_table, overall_weighted_score, data_insights = build_risk_table(profile, answers_dict)
        context = await retrieve_rag_context(profile, answers_dict, risk_table)
        recommendations, resources, raw_llm = await generate_llm_advice_async(profile, answers_dict, risk_table, context)

        return RiskAssessmentResult(
            overall_weighted_score=overall_weighted_score,
            risk_table=risk_table,
            recommendations=recommendations,
            resources=resources,
            data_insights=data_insights,
            raw_llm_output=raw_llm
        )
    except Exception as e:
        logger.error(f"Error processing answers: {traceback.format_exc()}")
        raise HTTPException(status_code=500, detail=f"Failed to process assessment: {str(e)}")

# Dummy placeholder functions to simulate the full pipeline

def generate_dynamic_questions(profile: CompanyProfile) -> List[RiskQuestion]:
    # This should be adapted to use actual categories and scoring focus
    return [
        RiskQuestion(
            id="cloud_security",
            question_text="How do you ensure security in your cloud environments?",
            category_name="Cloud Security",
            scoring_focus="CSPM usage, workload isolation"
        )
    ]

def build_risk_table(profile: CompanyProfile, answers: Dict[str, str]) -> tuple[List[RiskTableRow], float, List[str]]:
    # Basic scoring mock
    row = RiskTableRow(
        id="cloud_security",
        category="Cloud Security",
        definition="Protection of cloud infrastructure.",
        scoring_focus="CSPM, workload isolation",
        score=8,
        max_score=10,
        weight=0.1,
        explanation="Strong usage of CSPM and good segmentation policies."
    )
    return [row], 80.0, ["Scored well in cloud security."]

async def retrieve_rag_context(profile: CompanyProfile, answers: Dict[str, str], risk_table: List[RiskTableRow]) -> str:
    # TODO: Add context fetching from vector store
    return "Contextual RAG data placeholder."

async def generate_llm_advice_async(profile: CompanyProfile, answers: Dict[str, str], risk_table: List[RiskTableRow], context: str):
    if not qa_chain:
        logger.error("QA chain not initialized. Cannot generate LLM advice.")
        return ["LLM advice generation failed: RAG pipeline not ready."], [], "QA chain not initialized."

    prompt = f"""
Company Profile: {json.dumps(profile.dict(), indent=2)}
Answers: {json.dumps(answers, indent=2)}
Risk Table: {json.dumps([row.dict() for row in risk_table], indent=2)}
Context: {context}
Provide 2 security recommendations and 2 relevant resources.
"""

    try:
        response = qa_chain(prompt)
        parsed = json.loads(response)
        return parsed["recommendations"], parsed["resources"], response
    except Exception as e:
        logger.error(f"LLM response parsing failed: {str(e)}")
        return ["Error generating LLM output"], [], ""
