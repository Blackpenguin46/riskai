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

# unify with env vars so Docker-compose can override
DB_PERSIST_DIR = os.getenv("DB_PERSIST_DIR", "vectordb")
PDF_DATA_DIR   = os.getenv("PDF_DATA_DIR",   "data/")


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
        
        # Basic scoring logic based on answer length and keywords
        score = 0
        if answer_text.lower() == "no answer provided":
            score = 2  # Low score for no answer
        elif len(answer_text) < 20:
            score = 4  # Slightly higher for brief answer
        elif len(answer_text) < 100:
            score = 6  # Medium score for moderate answer
        else:
            score = 8  # Higher score for detailed answer
        
        # Adjust score based on positive/negative keywords
        positive_keywords = ["strong", "comprehensive", "fully implemented", "excellent", "robust", 
                            "mature", "advanced", "complete", "thorough", "effective"]
        negative_keywords = ["weak", "lacking", "not implemented", "poor", "minimal", 
                            "immature", "basic", "incomplete", "inadequate", "ineffective"]
        
        if any(kw in answer_text.lower() for kw in positive_keywords):
            score = min(cat_def['max_score'], score + 2)
        elif any(kw in answer_text.lower() for kw in negative_keywords):
            score = max(0, score - 2)
        
        # Ensure score is within bounds
        score = max(0, min(cat_def['max_score'], score))
        
        # Generate explanation
        explanation = f"Based on your response: '{answer_text[:100]}{'...' if len(answer_text) > 100 else ''}'. "
        explanation += f"Assessment focused on {cat_def['scoring_focus']}."
        
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
