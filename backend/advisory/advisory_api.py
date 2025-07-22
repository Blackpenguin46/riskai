"""
API endpoints for Interactive Risk Advisory System
Provides detailed guidance on risk management and emerging technology integration
"""

from fastapi import APIRouter, HTTPException
from pydantic import BaseModel
from typing import Dict, List, Any, Optional
import logging
from datetime import datetime

from .risk_advisory_engine import (
    risk_advisory_engine,
    AdvisoryTopic,
    AdvisoryRequest,
    AdvisoryPlan,
    AdvisoryRecommendation
)

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/api/advisory", tags=["Risk Advisory"])

class AdvisoryTopicInfo(BaseModel):
    """Information about available advisory topics"""
    id: str
    name: str
    description: str
    typical_timeline: str
    complexity: str
    focus_areas: List[str]

class AdvisoryRequestModel(BaseModel):
    """Request model for advisory guidance"""
    topic: str
    specific_focus: str
    organization_context: Dict[str, Any]
    current_challenges: List[str]
    desired_outcomes: List[str]
    timeline: str
    budget_constraints: Optional[str] = None

class RecommendationModel(BaseModel):
    """Response model for advisory recommendations"""
    title: str
    description: str
    implementation_steps: List[str]
    prerequisites: List[str]
    success_metrics: List[str]
    risks_and_mitigations: List[Dict[str, str]]
    frameworks_referenced: List[str]
    estimated_timeline: str
    estimated_cost: str
    confidence_score: float
    sources: List[str]

class AdvisoryPlanResponse(BaseModel):
    """Response model for complete advisory plan"""
    topic: str
    executive_summary: str
    situation_analysis: str
    strategic_approach: str
    detailed_recommendations: List[RecommendationModel]
    implementation_roadmap: Dict[str, List[str]]
    success_factors: List[str]
    potential_challenges: List[str]
    next_steps: List[str]
    knowledge_sources: List[str]
    confidence_metrics: Dict[str, float]
    generation_timestamp: str

@router.get("/topics", response_model=List[AdvisoryTopicInfo])
async def get_available_topics():
    """Get list of available advisory topics with descriptions"""
    try:
        topics = [
            AdvisoryTopicInfo(
                id="risk_management_improvement",
                name="Risk Management Improvement",
                description="Enhance existing risk management processes, frameworks, and capabilities",
                typical_timeline="3-6 months",
                complexity="Medium",
                focus_areas=[
                    "Risk assessment methodology",
                    "Quantitative risk analysis",
                    "Risk monitoring and reporting",
                    "Governance integration",
                    "Stakeholder communication"
                ]
            ),
            AdvisoryTopicInfo(
                id="emerging_tech_integration",
                name="Emerging Technology Integration",
                description="Safely integrate emerging technologies while managing associated risks",
                typical_timeline="6-12 months",
                complexity="High",
                focus_areas=[
                    "Technology evaluation framework",
                    "Risk assessment for new technologies",
                    "Pilot program governance",
                    "Scaling and integration strategy",
                    "Continuous monitoring"
                ]
            ),
            AdvisoryTopicInfo(
                id="ai_ml_implementation",
                name="AI/ML Implementation",
                description="Implement artificial intelligence and machine learning systems securely",
                typical_timeline="4-8 months",
                complexity="High",
                focus_areas=[
                    "AI governance framework",
                    "Model security and validation",
                    "Bias detection and mitigation",
                    "Data privacy and protection",
                    "Ethical AI principles"
                ]
            ),
            AdvisoryTopicInfo(
                id="iot_security",
                name="IoT Security Strategy",
                description="Develop comprehensive security strategy for Internet of Things deployments",
                typical_timeline="3-6 months",
                complexity="Medium",
                focus_areas=[
                    "Device security standards",
                    "Network segmentation",
                    "Identity and access management",
                    "Firmware update management",
                    "Monitoring and incident response"
                ]
            ),
            AdvisoryTopicInfo(
                id="blockchain_adoption",
                name="Blockchain Adoption",
                description="Safely adopt blockchain technology for business applications",
                typical_timeline="6-9 months",
                complexity="High",
                focus_areas=[
                    "Use case evaluation",
                    "Security architecture design",
                    "Smart contract security",
                    "Key management",
                    "Regulatory compliance"
                ]
            ),
            AdvisoryTopicInfo(
                id="cloud_security_strategy",
                name="Cloud Security Strategy",
                description="Develop comprehensive cloud security strategy and implementation plan",
                typical_timeline="4-6 months",
                complexity="Medium",
                focus_areas=[
                    "Cloud security architecture",
                    "Shared responsibility model",
                    "Identity and access management",
                    "Data protection and encryption",
                    "Compliance and governance"
                ]
            ),
            AdvisoryTopicInfo(
                id="quantum_computing_prep",
                name="Quantum Computing Preparation",
                description="Prepare for quantum computing impact on cybersecurity",
                typical_timeline="12-18 months",
                complexity="High",
                focus_areas=[
                    "Post-quantum cryptography",
                    "Quantum-resistant algorithms",
                    "Migration planning",
                    "Risk assessment",
                    "Timeline monitoring"
                ]
            ),
            AdvisoryTopicInfo(
                id="governance_framework",
                name="Governance Framework Development",
                description="Establish or enhance cybersecurity governance framework",
                typical_timeline="3-6 months",
                complexity="Medium",
                focus_areas=[
                    "Governance structure design",
                    "Policy development",
                    "Risk oversight processes",
                    "Compliance management",
                    "Performance measurement"
                ]
            ),
            AdvisoryTopicInfo(
                id="compliance_alignment",
                name="Compliance Alignment",
                description="Align security practices with regulatory and industry requirements",
                typical_timeline="4-8 months",
                complexity="Medium",
                focus_areas=[
                    "Regulatory mapping",
                    "Gap analysis",
                    "Control implementation",
                    "Audit preparation",
                    "Continuous monitoring"
                ]
            ),
            AdvisoryTopicInfo(
                id="incident_response_enhancement",
                name="Incident Response Enhancement",
                description="Improve incident response capabilities and processes",
                typical_timeline="2-4 months",
                complexity="Medium",
                focus_areas=[
                    "Response plan development",
                    "Team training and exercises",
                    "Tool integration",
                    "Communication protocols",
                    "Lessons learned process"
                ]
            ),
            AdvisoryTopicInfo(
                id="security_awareness_program",
                name="Security Awareness Program",
                description="Develop comprehensive security awareness and training program",
                typical_timeline="3-6 months",
                complexity="Low",
                focus_areas=[
                    "Program design and content",
                    "Training delivery methods",
                    "Effectiveness measurement",
                    "Behavioral change strategies",
                    "Continuous improvement"
                ]
            ),
            AdvisoryTopicInfo(
                id="third_party_risk",
                name="Third-Party Risk Management",
                description="Establish comprehensive third-party risk management program",
                typical_timeline="4-6 months",
                complexity="Medium",
                focus_areas=[
                    "Vendor assessment processes",
                    "Contract security requirements",
                    "Ongoing monitoring",
                    "Incident response coordination",
                    "Supply chain security"
                ]
            )
        ]
        
        return topics
        
    except Exception as e:
        logger.error(f"Error getting advisory topics: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get topics: {str(e)}")

@router.post("/generate-plan", response_model=AdvisoryPlanResponse)
async def generate_advisory_plan(request: AdvisoryRequestModel):
    """Generate comprehensive advisory plan based on user requirements"""
    try:
        logger.info(f"Generating advisory plan for topic: {request.topic}")
        
        # Validate topic
        try:
            topic_enum = AdvisoryTopic(request.topic)
        except ValueError:
            raise HTTPException(
                status_code=400, 
                detail=f"Invalid topic: {request.topic}. Use /topics endpoint to see available topics."
            )
        
        # Create advisory request
        advisory_request = AdvisoryRequest(
            topic=topic_enum,
            specific_focus=request.specific_focus,
            organization_context=request.organization_context,
            current_challenges=request.current_challenges,
            desired_outcomes=request.desired_outcomes,
            timeline=request.timeline,
            budget_constraints=request.budget_constraints
        )
        
        # Generate advisory plan
        advisory_plan = risk_advisory_engine.generate_advisory_plan(advisory_request)
        
        # Convert to response format
        def convert_recommendation(rec: AdvisoryRecommendation) -> RecommendationModel:
            return RecommendationModel(
                title=rec.title,
                description=rec.description,
                implementation_steps=rec.implementation_steps,
                prerequisites=rec.prerequisites,
                success_metrics=rec.success_metrics,
                risks_and_mitigations=rec.risks_and_mitigations,
                frameworks_referenced=rec.frameworks_referenced,
                estimated_timeline=rec.estimated_timeline,
                estimated_cost=rec.estimated_cost,
                confidence_score=rec.confidence_score,
                sources=rec.sources
            )
        
        response = AdvisoryPlanResponse(
            topic=advisory_plan.topic,
            executive_summary=advisory_plan.executive_summary,
            situation_analysis=advisory_plan.situation_analysis,
            strategic_approach=advisory_plan.strategic_approach,
            detailed_recommendations=[convert_recommendation(rec) for rec in advisory_plan.detailed_recommendations],
            implementation_roadmap=advisory_plan.implementation_roadmap,
            success_factors=advisory_plan.success_factors,
            potential_challenges=advisory_plan.potential_challenges,
            next_steps=advisory_plan.next_steps,
            knowledge_sources=advisory_plan.knowledge_sources,
            confidence_metrics=advisory_plan.confidence_metrics,
            generation_timestamp=advisory_plan.generation_timestamp.isoformat()
        )
        
        logger.info(f"Successfully generated advisory plan with {len(response.detailed_recommendations)} recommendations")
        return response
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Error generating advisory plan: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to generate advisory plan: {str(e)}"
        )

@router.get("/health")
async def check_advisory_health():
    """Check the health of the advisory system"""
    try:
        # Check if RAG pipeline is available
        rag_available = risk_advisory_engine.qa_chain is not None
        
        return {
            "status": "healthy",
            "rag_pipeline_available": rag_available,
            "local_llm_model": "tiiuae/falcon-rw-1b",
            "available_topics": len(AdvisoryTopic),
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Advisory health check failed: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Health check failed: {str(e)}")

@router.post("/reload-knowledge")
async def reload_advisory_knowledge():
    """Reload the RAG knowledge base for advisory system"""
    try:
        logger.info("Reloading advisory knowledge base...")
        
        # Reinitialize the RAG pipeline
        risk_advisory_engine.initialize_rag_pipeline()
        
        return {
            "status": "success",
            "message": "Advisory knowledge base reloaded successfully",
            "rag_available": risk_advisory_engine.qa_chain is not None,
            "timestamp": datetime.now().isoformat()
        }
    except Exception as e:
        logger.error(f"Error reloading advisory knowledge base: {str(e)}")
        raise HTTPException(
            status_code=500, 
            detail=f"Failed to reload knowledge base: {str(e)}"
        )

@router.get("/topic/{topic_id}/examples")
async def get_topic_examples(topic_id: str):
    """Get example scenarios and use cases for a specific topic"""
    try:
        examples = {
            "risk_management_improvement": {
                "scenarios": [
                    "Organization needs to transition from qualitative to quantitative risk assessment",
                    "Existing risk management process lacks integration with business strategy",
                    "Risk reporting to board needs enhancement and standardization"
                ],
                "use_cases": [
                    "Implementing FAIR methodology for cyber risk quantification",
                    "Establishing risk appetite statements and tolerance levels",
                    "Creating executive risk dashboards and KPIs"
                ]
            },
            "emerging_tech_integration": {
                "scenarios": [
                    "Organization wants to adopt AI/ML for business processes",
                    "Need to evaluate blockchain for supply chain transparency",
                    "Planning IoT deployment for operational efficiency"
                ],
                "use_cases": [
                    "Creating technology evaluation and approval process",
                    "Establishing innovation labs with security controls",
                    "Developing emerging technology risk assessment framework"
                ]
            },
            "ai_ml_implementation": {
                "scenarios": [
                    "Implementing AI for fraud detection in financial services",
                    "Deploying ML models for predictive maintenance",
                    "Using AI for customer service automation"
                ],
                "use_cases": [
                    "Establishing AI governance and ethics committee",
                    "Implementing model validation and testing processes",
                    "Creating bias detection and mitigation controls"
                ]
            }
        }
        
        if topic_id not in examples:
            return {"message": f"No examples available for topic: {topic_id}"}
        
        return examples[topic_id]
        
    except Exception as e:
        logger.error(f"Error getting topic examples: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get examples: {str(e)}")

@router.get("/knowledge-coverage")
async def get_knowledge_coverage():
    """Get information about knowledge base coverage for advisory topics"""
    try:
        import os
        
        data_dir = "data/"
        coverage_info = {
            "total_documents": 0,
            "document_categories": {},
            "framework_coverage": [],
            "topic_coverage": {}
        }
        
        if os.path.exists(data_dir):
            pdf_files = [f for f in os.listdir(data_dir) if f.endswith('.pdf')]
            coverage_info["total_documents"] = len(pdf_files)
            
            # Categorize documents by keywords
            categories = {
                "Risk Management": ["risk", "management", "governance"],
                "AI/ML": ["AI", "artificial", "intelligence", "machine", "learning"],
                "IoT": ["IoT", "internet", "things"],
                "Blockchain": ["blockchain", "distributed", "ledger"],
                "Cloud Security": ["cloud", "security"],
                "Compliance": ["compliance", "regulatory", "audit"],
                "NIST": ["NIST", "framework"],
                "ISO": ["ISO", "27001", "standard"]
            }
            
            for category, keywords in categories.items():
                count = sum(1 for file in pdf_files if any(keyword.lower() in file.lower() for keyword in keywords))
                coverage_info["document_categories"][category] = count
            
            # Framework coverage
            coverage_info["framework_coverage"] = [
                "NIST Cybersecurity Framework",
                "ISO 27001/27002",
                "COBIT",
                "FAIR",
                "NIST Risk Management Framework",
                "CyBOK (Cyber Security Body of Knowledge)"
            ]
        
        return coverage_info
        
    except Exception as e:
        logger.error(f"Error getting knowledge coverage: {str(e)}")
        raise HTTPException(status_code=500, detail=f"Failed to get coverage info: {str(e)}")