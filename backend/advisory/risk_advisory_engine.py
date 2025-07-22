"""
Interactive Risk Advisory Engine
Uses RAG pipeline to provide detailed guidance on risk management and emerging technology integration
Aligned with SEET paper's holistic approach to emerging technology risk management
"""

import logging
import json
import time
from typing import Dict, List, Any, Tuple, Optional
from datetime import datetime
from dataclasses import dataclass
from enum import Enum

# RAG Pipeline imports
from rag_pipeline.compatibility_wrapper import (
    load_existing_embeddings, build_rag_chain, get_embedder
)

logger = logging.getLogger(__name__)

class AdvisoryTopic(Enum):
    """Available advisory topics"""
    RISK_MANAGEMENT_IMPROVEMENT = "risk_management_improvement"
    EMERGING_TECH_INTEGRATION = "emerging_tech_integration"
    AI_ML_IMPLEMENTATION = "ai_ml_implementation"
    IOT_SECURITY = "iot_security"
    BLOCKCHAIN_ADOPTION = "blockchain_adoption"
    CLOUD_SECURITY_STRATEGY = "cloud_security_strategy"
    QUANTUM_COMPUTING_PREP = "quantum_computing_prep"
    GOVERNANCE_FRAMEWORK = "governance_framework"
    COMPLIANCE_ALIGNMENT = "compliance_alignment"
    INCIDENT_RESPONSE_ENHANCEMENT = "incident_response_enhancement"
    SECURITY_AWARENESS_PROGRAM = "security_awareness_program"
    THIRD_PARTY_RISK = "third_party_risk"

@dataclass
class AdvisoryRequest:
    """Request for advisory guidance"""
    topic: AdvisoryTopic
    specific_focus: str
    organization_context: Dict[str, Any]
    current_challenges: List[str]
    desired_outcomes: List[str]
    timeline: str
    budget_constraints: Optional[str] = None

@dataclass
class AdvisoryRecommendation:
    """Individual advisory recommendation"""
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

@dataclass
class AdvisoryPlan:
    """Comprehensive advisory plan"""
    topic: str
    executive_summary: str
    situation_analysis: str
    strategic_approach: str
    detailed_recommendations: List[AdvisoryRecommendation]
    implementation_roadmap: Dict[str, List[str]]
    success_factors: List[str]
    potential_challenges: List[str]
    next_steps: List[str]
    knowledge_sources: List[str]
    confidence_metrics: Dict[str, float]
    generation_timestamp: datetime

class RiskAdvisoryEngine:
    """Interactive advisory engine using RAG pipeline and local LLM"""
    
    def __init__(self, db_persist_dir: str = "vectordb"):
        self.db_persist_dir = db_persist_dir
        self.embedder = None
        self.db = None
        self.qa_chain = None
        self.initialize_rag_pipeline()
        
        # Topic-specific query templates
        self.topic_templates = self._initialize_topic_templates()
    
    def initialize_rag_pipeline(self):
        """Initialize the RAG pipeline components"""
        try:
            logger.info("Initializing Risk Advisory Engine RAG pipeline...")
            
            # Get embedder
            self.embedder = get_embedder()
            
            # Load existing embeddings
            self.db = load_existing_embeddings(self.embedder, self.db_persist_dir)
            
            # Build RAG chain with local LLM
            self.qa_chain = build_rag_chain(self.db)
            
            logger.info("Risk Advisory Engine RAG pipeline initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize RAG pipeline: {str(e)}")
            self.qa_chain = None
    
    def generate_advisory_plan(self, request: AdvisoryRequest) -> AdvisoryPlan:
        """Generate comprehensive advisory plan based on user request"""
        
        start_time = time.time()
        logger.info(f"Generating advisory plan for topic: {request.topic.value}")
        
        try:
            # Generate context-specific queries
            queries = self._generate_advisory_queries(request)
            
            # Retrieve relevant knowledge
            knowledge_context = self._retrieve_advisory_knowledge(queries)
            
            # Generate situation analysis
            situation_analysis = self._analyze_situation(request, knowledge_context)
            
            # Generate strategic approach
            strategic_approach = self._develop_strategic_approach(request, knowledge_context)
            
            # Generate detailed recommendations
            recommendations = self._generate_detailed_recommendations(request, knowledge_context)
            
            # Create implementation roadmap
            roadmap = self._create_implementation_roadmap(recommendations, request.timeline)
            
            # Generate executive summary
            executive_summary = self._generate_executive_summary(request, recommendations)
            
            # Calculate confidence metrics
            confidence_metrics = self._calculate_advisory_confidence(knowledge_context, recommendations)
            
            # Create comprehensive plan
            advisory_plan = AdvisoryPlan(
                topic=request.topic.value.replace('_', ' ').title(),
                executive_summary=executive_summary,
                situation_analysis=situation_analysis,
                strategic_approach=strategic_approach,
                detailed_recommendations=recommendations,
                implementation_roadmap=roadmap,
                success_factors=self._identify_success_factors(request, knowledge_context),
                potential_challenges=self._identify_challenges(request, knowledge_context),
                next_steps=self._generate_next_steps(recommendations),
                knowledge_sources=knowledge_context.get('sources', []),
                confidence_metrics=confidence_metrics,
                generation_timestamp=datetime.now()
            )
            
            processing_time = time.time() - start_time
            logger.info(f"Advisory plan generated in {processing_time:.2f} seconds")
            
            return advisory_plan
            
        except Exception as e:
            logger.error(f"Error generating advisory plan: {str(e)}")
            return self._generate_fallback_plan(request)
    
    def _generate_advisory_queries(self, request: AdvisoryRequest) -> List[str]:
        """Generate targeted queries based on advisory request"""
        queries = []
        topic = request.topic.value
        
        # Get base queries from templates
        if topic in self.topic_templates:
            queries.extend(self.topic_templates[topic]['base_queries'])
        
        # Add context-specific queries
        if request.specific_focus:
            queries.append(f"{request.specific_focus} best practices implementation")
            queries.append(f"{request.specific_focus} risk mitigation strategies")
        
        # Add challenge-specific queries
        for challenge in request.current_challenges:
            queries.append(f"solving {challenge} cybersecurity challenge")
        
        # Add outcome-specific queries
        for outcome in request.desired_outcomes:
            queries.append(f"achieving {outcome} security objective")
        
        # Add organization context queries
        org_context = request.organization_context
        if org_context.get('industry'):
            industry = org_context['industry']
            queries.append(f"{industry} sector cybersecurity requirements")
            queries.append(f"{topic} implementation {industry} industry")
        
        if org_context.get('size'):
            size = org_context['size']
            queries.append(f"{topic} {size} organization approach")
        
        # Add timeline-specific queries
        if request.timeline:
            queries.append(f"{topic} {request.timeline} implementation timeline")
        
        return queries[:15]  # Limit for performance
    
    def _retrieve_advisory_knowledge(self, queries: List[str]) -> Dict[str, Any]:
        """Retrieve comprehensive knowledge for advisory guidance"""
        knowledge_context = {
            'relevant_content': [],
            'sources': [],
            'frameworks': [],
            'best_practices': [],
            'case_studies': []
        }
        
        if not self.qa_chain:
            logger.warning("RAG pipeline not available for advisory")
            return knowledge_context
        
        try:
            for query in queries:
                try:
                    result = self.qa_chain({"query": query})
                    
                    if result and 'result' in result:
                        content = result['result']
                        knowledge_context['relevant_content'].append({
                            'query': query,
                            'content': content,
                            'confidence': 0.8
                        })
                        
                        # Extract frameworks mentioned
                        frameworks = self._extract_frameworks(content)
                        knowledge_context['frameworks'].extend(frameworks)
                        
                        # Extract best practices
                        practices = self._extract_best_practices(content)
                        knowledge_context['best_practices'].extend(practices)
                    
                    # Extract sources
                    if 'source_documents' in result:
                        for doc in result['source_documents']:
                            if hasattr(doc, 'metadata') and 'source' in doc.metadata:
                                source = doc.metadata['source']
                                if source not in knowledge_context['sources']:
                                    knowledge_context['sources'].append(source)
                
                except Exception as e:
                    logger.warning(f"Error querying RAG for '{query}': {str(e)}")
                    continue
            
            # Remove duplicates
            knowledge_context['frameworks'] = list(set(knowledge_context['frameworks']))
            knowledge_context['best_practices'] = list(set(knowledge_context['best_practices']))
            
            logger.info(f"Retrieved knowledge from {len(knowledge_context['relevant_content'])} queries")
            
        except Exception as e:
            logger.error(f"Error retrieving advisory knowledge: {str(e)}")
        
        return knowledge_context
    
    def _analyze_situation(self, request: AdvisoryRequest, knowledge: Dict[str, Any]) -> str:
        """Analyze current situation based on request and knowledge"""
        
        topic_name = request.topic.value.replace('_', ' ').title()
        org_context = request.organization_context
        
        analysis = f"Current Situation Analysis for {topic_name}:\n\n"
        
        # Organization context
        if org_context.get('industry') and org_context.get('size'):
            analysis += f"Organization Profile: {org_context['size']} {org_context['industry']} organization "
            
        # Current challenges
        if request.current_challenges:
            analysis += f"\nKey Challenges Identified:\n"
            for i, challenge in enumerate(request.current_challenges, 1):
                analysis += f"{i}. {challenge}\n"
        
        # Desired outcomes
        if request.desired_outcomes:
            analysis += f"\nDesired Outcomes:\n"
            for i, outcome in enumerate(request.desired_outcomes, 1):
                analysis += f"{i}. {outcome}\n"
        
        # Knowledge-based insights
        relevant_content = knowledge.get('relevant_content', [])
        if relevant_content:
            analysis += f"\nIndustry Context and Best Practices:\n"
            analysis += "Based on current cybersecurity standards and frameworks, "
            
            # Extract key insights from knowledge
            key_insights = []
            for content in relevant_content[:3]:  # Top 3 most relevant
                content_text = content.get('content', '')
                if len(content_text) > 100:
                    key_insights.append(content_text[:200] + "...")
            
            if key_insights:
                analysis += "key considerations include: " + " ".join(key_insights[:2])
        
        return analysis
    
    def _develop_strategic_approach(self, request: AdvisoryRequest, knowledge: Dict[str, Any]) -> str:
        """Develop strategic approach based on SEET paper methodology"""
        
        topic = request.topic.value
        approach = f"Strategic Approach for {topic.replace('_', ' ').title()}:\n\n"
        
        # Holistic risk management approach (SEET alignment)
        approach += "1. Holistic Risk Assessment:\n"
        approach += "   - Evaluate technical, operational, and strategic dimensions\n"
        approach += "   - Consider emerging technology interdependencies\n"
        approach += "   - Assess organizational readiness and capability gaps\n\n"
        
        # Governance integration
        approach += "2. Governance Integration:\n"
        approach += "   - Align with existing risk management frameworks\n"
        approach += "   - Establish clear accountability and oversight\n"
        approach += "   - Integrate with business strategy and objectives\n\n"
        
        # Phased implementation
        timeline = request.timeline.lower() if request.timeline else "medium-term"
        if "immediate" in timeline or "urgent" in timeline:
            approach += "3. Rapid Implementation Strategy:\n"
            approach += "   - Focus on critical risk mitigation first\n"
            approach += "   - Implement quick wins and foundational controls\n"
            approach += "   - Establish monitoring and feedback loops\n\n"
        else:
            approach += "3. Phased Implementation Strategy:\n"
            approach += "   - Phase 1: Foundation and planning (0-3 months)\n"
            approach += "   - Phase 2: Core implementation (3-9 months)\n"
            approach += "   - Phase 3: Optimization and scaling (9+ months)\n\n"
        
        # Continuous improvement
        approach += "4. Continuous Improvement:\n"
        approach += "   - Establish metrics and KPIs for success measurement\n"
        approach += "   - Implement regular review and adjustment cycles\n"
        approach += "   - Foster learning and adaptation culture\n"
        
        return approach
    
    def _generate_detailed_recommendations(
        self, 
        request: AdvisoryRequest, 
        knowledge: Dict[str, Any]
    ) -> List[AdvisoryRecommendation]:
        """Generate detailed, actionable recommendations"""
        
        recommendations = []
        topic = request.topic.value
        
        # Get topic-specific recommendation templates
        if topic in self.topic_templates:
            templates = self.topic_templates[topic]['recommendations']
            
            for template in templates:
                # Customize template based on request context
                customized_rec = self._customize_recommendation(template, request, knowledge)
                recommendations.append(customized_rec)
        
        # Add context-specific recommendations
        context_recs = self._generate_context_recommendations(request, knowledge)
        recommendations.extend(context_recs)
        
        # Sort by priority and confidence
        recommendations.sort(key=lambda x: (-x.confidence_score, x.title))
        
        return recommendations[:8]  # Limit to top 8 recommendations
    
    def _customize_recommendation(
        self, 
        template: Dict[str, Any], 
        request: AdvisoryRequest, 
        knowledge: Dict[str, Any]
    ) -> AdvisoryRecommendation:
        """Customize recommendation template based on context"""
        
        # Extract relevant sources
        relevant_sources = []
        for content in knowledge.get('relevant_content', []):
            if any(keyword in content.get('content', '').lower() 
                   for keyword in template.get('keywords', [])):
                relevant_sources.append(content.get('query', ''))
        
        return AdvisoryRecommendation(
            title=template['title'],
            description=template['description'],
            implementation_steps=template['steps'],
            prerequisites=template.get('prerequisites', []),
            success_metrics=template.get('metrics', []),
            risks_and_mitigations=template.get('risks', []),
            frameworks_referenced=knowledge.get('frameworks', [])[:3],
            estimated_timeline=template.get('timeline', request.timeline or '3-6 months'),
            estimated_cost=template.get('cost', 'Medium'),
            confidence_score=0.8 if relevant_sources else 0.6,
            sources=relevant_sources[:3]
        )
    
    def _generate_context_recommendations(
        self, 
        request: AdvisoryRequest, 
        knowledge: Dict[str, Any]
    ) -> List[AdvisoryRecommendation]:
        """Generate recommendations based on specific context"""
        
        context_recs = []
        
        # Challenge-specific recommendations
        for challenge in request.current_challenges:
            if "governance" in challenge.lower():
                context_recs.append(self._create_governance_recommendation(challenge, knowledge))
            elif "compliance" in challenge.lower():
                context_recs.append(self._create_compliance_recommendation(challenge, knowledge))
            elif "emerging" in challenge.lower() or "technology" in challenge.lower():
                context_recs.append(self._create_emerging_tech_recommendation(challenge, knowledge))
        
        return [rec for rec in context_recs if rec is not None]
    
    def _create_governance_recommendation(self, challenge: str, knowledge: Dict[str, Any]) -> AdvisoryRecommendation:
        """Create governance-specific recommendation"""
        return AdvisoryRecommendation(
            title="Establish Comprehensive Governance Framework",
            description=f"Address governance challenge: {challenge}",
            implementation_steps=[
                "Define governance charter and objectives",
                "Establish governance committee with executive sponsorship",
                "Create governance policies and procedures",
                "Implement governance monitoring and reporting"
            ],
            prerequisites=["Executive leadership commitment", "Resource allocation"],
            success_metrics=["Governance maturity score", "Policy compliance rate"],
            risks_and_mitigations=[
                {"risk": "Lack of adoption", "mitigation": "Change management program"},
                {"risk": "Resource constraints", "mitigation": "Phased implementation"}
            ],
            frameworks_referenced=["COBIT", "NIST CSF", "ISO 27001"],
            estimated_timeline="3-6 months",
            estimated_cost="Medium",
            confidence_score=0.85,
            sources=knowledge.get('sources', [])[:2]
        )
    
    def _create_compliance_recommendation(self, challenge: str, knowledge: Dict[str, Any]) -> AdvisoryRecommendation:
        """Create compliance-specific recommendation"""
        return AdvisoryRecommendation(
            title="Implement Integrated Compliance Program",
            description=f"Address compliance challenge: {challenge}",
            implementation_steps=[
                "Conduct compliance gap analysis",
                "Map requirements to controls",
                "Implement compliance monitoring",
                "Establish audit and reporting processes"
            ],
            prerequisites=["Regulatory requirement analysis", "Control framework"],
            success_metrics=["Compliance score", "Audit findings reduction"],
            risks_and_mitigations=[
                {"risk": "Regulatory changes", "mitigation": "Continuous monitoring"},
                {"risk": "Control gaps", "mitigation": "Regular assessments"}
            ],
            frameworks_referenced=["ISO 27001", "SOC 2", "GDPR"],
            estimated_timeline="4-8 months",
            estimated_cost="High",
            confidence_score=0.8,
            sources=knowledge.get('sources', [])[:2]
        )
    
    def _create_emerging_tech_recommendation(self, challenge: str, knowledge: Dict[str, Any]) -> AdvisoryRecommendation:
        """Create emerging technology-specific recommendation"""
        return AdvisoryRecommendation(
            title="Develop Emerging Technology Risk Framework",
            description=f"Address emerging technology challenge: {challenge}",
            implementation_steps=[
                "Establish technology evaluation criteria",
                "Create risk assessment methodology",
                "Implement pilot program governance",
                "Develop scaling and integration strategy"
            ],
            prerequisites=["Technology strategy", "Risk appetite definition"],
            success_metrics=["Technology adoption success rate", "Risk incident reduction"],
            risks_and_mitigations=[
                {"risk": "Technology immaturity", "mitigation": "Pilot testing"},
                {"risk": "Security vulnerabilities", "mitigation": "Continuous assessment"}
            ],
            frameworks_referenced=["NIST AI RMF", "ISO/IEC 23053"],
            estimated_timeline="2-4 months",
            estimated_cost="Medium",
            confidence_score=0.75,
            sources=knowledge.get('sources', [])[:2]
        )
    
    def _create_implementation_roadmap(
        self, 
        recommendations: List[AdvisoryRecommendation], 
        timeline: str
    ) -> Dict[str, List[str]]:
        """Create phased implementation roadmap"""
        
        roadmap = {
            "Phase 1 (0-3 months)": [],
            "Phase 2 (3-6 months)": [],
            "Phase 3 (6+ months)": []
        }
        
        # Categorize recommendations by timeline
        for rec in recommendations:
            rec_timeline = rec.estimated_timeline.lower()
            
            if "immediate" in rec_timeline or "0-3" in rec_timeline:
                roadmap["Phase 1 (0-3 months)"].append(rec.title)
            elif "3-6" in rec_timeline or "short" in rec_timeline:
                roadmap["Phase 2 (3-6 months)"].append(rec.title)
            else:
                roadmap["Phase 3 (6+ months)"].append(rec.title)
        
        return roadmap
    
    def _generate_executive_summary(
        self, 
        request: AdvisoryRequest, 
        recommendations: List[AdvisoryRecommendation]
    ) -> str:
        """Generate executive summary of the advisory plan"""
        
        topic_name = request.topic.value.replace('_', ' ').title()
        
        summary = f"Executive Summary: {topic_name} Advisory Plan\n\n"
        summary += f"This comprehensive plan addresses {len(request.current_challenges)} key challenges "
        summary += f"and provides {len(recommendations)} detailed recommendations to achieve "
        summary += f"{len(request.desired_outcomes)} strategic outcomes.\n\n"
        
        # Key benefits
        summary += "Key Benefits:\n"
        summary += "• Enhanced risk management and security posture\n"
        summary += "• Structured approach to emerging technology adoption\n"
        summary += "• Alignment with industry best practices and frameworks\n"
        summary += "• Measurable outcomes and success metrics\n\n"
        
        # Investment overview
        high_cost_recs = len([r for r in recommendations if r.estimated_cost == "High"])
        medium_cost_recs = len([r for r in recommendations if r.estimated_cost == "Medium"])
        
        summary += f"Investment Overview: {high_cost_recs} high-investment initiatives, "
        summary += f"{medium_cost_recs} medium-investment initiatives.\n\n"
        
        # Timeline
        summary += f"Implementation Timeline: {request.timeline or '6-12 months'} with phased approach "
        summary += "ensuring manageable implementation and early value realization."
        
        return summary
    
    def _identify_success_factors(self, request: AdvisoryRequest, knowledge: Dict[str, Any]) -> List[str]:
        """Identify critical success factors"""
        return [
            "Executive leadership commitment and sponsorship",
            "Adequate resource allocation and budget approval",
            "Cross-functional team collaboration and communication",
            "Clear governance and decision-making processes",
            "Regular monitoring and progress measurement",
            "Change management and stakeholder engagement",
            "Continuous learning and adaptation capability"
        ]
    
    def _identify_challenges(self, request: AdvisoryRequest, knowledge: Dict[str, Any]) -> List[str]:
        """Identify potential implementation challenges"""
        return [
            "Resource constraints and competing priorities",
            "Organizational resistance to change",
            "Technical complexity and integration challenges",
            "Regulatory and compliance requirements",
            "Skills gaps and training needs",
            "Vendor selection and management",
            "Timeline pressures and scope creep"
        ]
    
    def _generate_next_steps(self, recommendations: List[AdvisoryRecommendation]) -> List[str]:
        """Generate immediate next steps"""
        return [
            "Review and approve advisory plan with executive leadership",
            "Establish project governance and steering committee",
            "Allocate resources and budget for implementation",
            "Begin Phase 1 activities with highest-priority recommendations",
            "Set up monitoring and reporting mechanisms",
            "Schedule regular progress reviews and checkpoints"
        ]
    
    def _calculate_advisory_confidence(
        self, 
        knowledge: Dict[str, Any], 
        recommendations: List[AdvisoryRecommendation]
    ) -> Dict[str, float]:
        """Calculate confidence metrics for advisory plan"""
        
        # Knowledge availability confidence
        knowledge_confidence = min(len(knowledge.get('relevant_content', [])) / 10, 1.0)
        
        # Recommendation confidence (average)
        rec_confidence = sum(rec.confidence_score for rec in recommendations) / len(recommendations) if recommendations else 0.5
        
        # Source reliability confidence
        source_confidence = min(len(knowledge.get('sources', [])) / 5, 1.0)
        
        # Overall confidence
        overall_confidence = (knowledge_confidence * 0.4 + rec_confidence * 0.4 + source_confidence * 0.2)
        
        return {
            'overall_confidence': overall_confidence,
            'knowledge_confidence': knowledge_confidence,
            'recommendation_confidence': rec_confidence,
            'source_confidence': source_confidence
        }
    
    def _extract_frameworks(self, content: str) -> List[str]:
        """Extract framework references from content"""
        frameworks = []
        framework_keywords = [
            'NIST', 'ISO 27001', 'COBIT', 'FAIR', 'OCTAVE', 'COSO', 'ITIL',
            'SOC 2', 'GDPR', 'HIPAA', 'PCI DSS', 'NIST CSF', 'ISO 31000'
        ]
        
        content_upper = content.upper()
        for framework in framework_keywords:
            if framework.upper() in content_upper:
                frameworks.append(framework)
        
        return frameworks
    
    def _extract_best_practices(self, content: str) -> List[str]:
        """Extract best practices from content"""
        practices = []
        
        # Simple extraction based on common patterns
        sentences = content.split('.')
        for sentence in sentences:
            if any(keyword in sentence.lower() for keyword in ['should', 'must', 'recommend', 'best practice']):
                if len(sentence.strip()) > 20 and len(sentence.strip()) < 200:
                    practices.append(sentence.strip())
        
        return practices[:5]  # Limit to top 5
    
    def _initialize_topic_templates(self) -> Dict[str, Dict[str, Any]]:
        """Initialize topic-specific templates and queries"""
        return {
            'emerging_tech_integration': {
                'base_queries': [
                    'emerging technology integration best practices',
                    'AI ML implementation security framework',
                    'IoT blockchain adoption risk management',
                    'emerging technology governance standards',
                    'technology innovation risk assessment'
                ],
                'recommendations': [
                    {
                        'title': 'Establish Emerging Technology Governance Framework',
                        'description': 'Create comprehensive governance for emerging technology adoption',
                        'steps': [
                            'Define technology evaluation criteria',
                            'Establish innovation governance committee',
                            'Create risk assessment methodology',
                            'Implement pilot program processes'
                        ],
                        'keywords': ['governance', 'emerging', 'technology'],
                        'timeline': '3-6 months',
                        'cost': 'Medium'
                    }
                ]
            },
            'ai_ml_implementation': {
                'base_queries': [
                    'AI ML security implementation guidelines',
                    'artificial intelligence risk management',
                    'machine learning governance framework',
                    'AI bias detection mitigation',
                    'ML model security best practices'
                ],
                'recommendations': [
                    {
                        'title': 'Implement AI/ML Security Framework',
                        'description': 'Establish comprehensive security controls for AI/ML systems',
                        'steps': [
                            'Conduct AI risk assessment',
                            'Implement model validation processes',
                            'Establish bias detection mechanisms',
                            'Create AI governance policies'
                        ],
                        'keywords': ['AI', 'ML', 'artificial intelligence'],
                        'timeline': '4-8 months',
                        'cost': 'High'
                    }
                ]
            },
            'risk_management_improvement': {
                'base_queries': [
                    'risk management framework improvement',
                    'cybersecurity risk assessment enhancement',
                    'enterprise risk management best practices',
                    'risk governance optimization',
                    'quantitative risk analysis methods'
                ],
                'recommendations': [
                    {
                        'title': 'Enhance Risk Management Framework',
                        'description': 'Improve existing risk management processes and capabilities',
                        'steps': [
                            'Assess current risk management maturity',
                            'Implement quantitative risk analysis',
                            'Enhance risk monitoring and reporting',
                            'Integrate with business processes'
                        ],
                        'keywords': ['risk', 'management', 'framework'],
                        'timeline': '3-6 months',
                        'cost': 'Medium'
                    }
                ]
            }
        }
    
    def _generate_fallback_plan(self, request: AdvisoryRequest) -> AdvisoryPlan:
        """Generate fallback plan when RAG pipeline is unavailable"""
        logger.warning("Generating fallback advisory plan without RAG pipeline")
        
        topic_name = request.topic.value.replace('_', ' ').title()
        
        fallback_rec = AdvisoryRecommendation(
            title=f"Basic {topic_name} Implementation",
            description=f"Foundational approach to {topic_name.lower()}",
            implementation_steps=[
                "Conduct initial assessment",
                "Define requirements and objectives",
                "Develop implementation plan",
                "Execute pilot program",
                "Scale and optimize"
            ],
            prerequisites=["Management approval", "Resource allocation"],
            success_metrics=["Implementation progress", "Risk reduction"],
            risks_and_mitigations=[
                {"risk": "Resource constraints", "mitigation": "Phased approach"}
            ],
            frameworks_referenced=["NIST CSF"],
            estimated_timeline=request.timeline or "6 months",
            estimated_cost="Medium",
            confidence_score=0.5,
            sources=["Built-in knowledge base"]
        )
        
        return AdvisoryPlan(
            topic=topic_name,
            executive_summary=f"Basic advisory plan for {topic_name.lower()} implementation.",
            situation_analysis="Limited analysis available without knowledge base access.",
            strategic_approach="Standard phased implementation approach recommended.",
            detailed_recommendations=[fallback_rec],
            implementation_roadmap={"Phase 1": [fallback_rec.title]},
            success_factors=["Leadership support", "Resource availability"],
            potential_challenges=["Limited guidance", "Generic recommendations"],
            next_steps=["Enable knowledge base access for detailed guidance"],
            knowledge_sources=["Built-in templates"],
            confidence_metrics={"overall_confidence": 0.5, "fallback_mode": True},
            generation_timestamp=datetime.now()
        )

# Global instance
risk_advisory_engine = RiskAdvisoryEngine()