"""
AI-Powered Feedback Engine for RiskAI Assessment
Integrates assessment scoring with RAG pipeline for intelligent recommendations
Aligned with SEET paper's holistic approach to emerging technology risk management
"""

import logging
import json
import time
from typing import Dict, List, Any, Tuple, Optional
from datetime import datetime
from dataclasses import dataclass

# RAG Pipeline imports
from rag_pipeline.compatibility_wrapper import (
    load_existing_embeddings, build_rag_chain, get_embedder
)

logger = logging.getLogger(__name__)

@dataclass
class AssessmentContext:
    """Context information from the completed assessment"""
    overall_score: float
    risk_level: str
    section_scores: Dict[str, Dict[str, Any]]
    responses: Dict[str, Dict[str, Any]]
    completion_rate: float
    critical_sections: List[str]
    high_risk_sections: List[str]
    
@dataclass
class AIRecommendation:
    """AI-generated recommendation with metadata"""
    category: str  # immediate, short_term, strategic
    priority: int  # 1-5 (1 = highest)
    title: str
    description: str
    implementation_steps: List[str]
    frameworks_referenced: List[str]
    confidence_score: float
    sources: List[str]
    estimated_impact: str
    estimated_effort: str
    timeline: str

@dataclass
class FeedbackResult:
    """Complete AI feedback result"""
    overall_assessment: str
    risk_summary: str
    immediate_actions: List[AIRecommendation]
    short_term_improvements: List[AIRecommendation]
    strategic_initiatives: List[AIRecommendation]
    emerging_tech_focus: List[str]
    confidence_metrics: Dict[str, float]
    sources_used: List[str]
    generation_timestamp: datetime

class AIFeedbackEngine:
    """AI-powered feedback engine using local LLM and RAG pipeline"""
    
    def __init__(self, db_persist_dir: str = "vectordb"):
        self.db_persist_dir = db_persist_dir
        self.embedder = None
        self.db = None
        self.qa_chain = None
        self.initialize_rag_pipeline()
    
    def initialize_rag_pipeline(self):
        """Initialize the RAG pipeline components"""
        try:
            logger.info("Initializing AI Feedback Engine RAG pipeline...")
            
            # Get embedder
            self.embedder = get_embedder()
            
            # Load existing embeddings
            self.db = load_existing_embeddings(self.embedder, self.db_persist_dir)
            
            # Build RAG chain with local LLM
            self.qa_chain = build_rag_chain(self.db)
            
            logger.info("AI Feedback Engine RAG pipeline initialized successfully")
            
        except Exception as e:
            logger.error(f"Failed to initialize RAG pipeline: {str(e)}")
            # Continue without RAG - will use fallback recommendations
            self.qa_chain = None
    
    def generate_comprehensive_feedback(
        self, 
        assessment_context: AssessmentContext
    ) -> FeedbackResult:
        """Generate comprehensive AI-powered feedback based on assessment results"""
        
        start_time = time.time()
        logger.info(f"Generating AI feedback for assessment with overall score: {assessment_context.overall_score}")
        
        try:
            # Generate context-aware queries for RAG
            rag_queries = self._generate_rag_queries(assessment_context)
            
            # Retrieve relevant knowledge from documents
            knowledge_context = self._retrieve_knowledge(rag_queries)
            
            # Generate recommendations using local LLM
            recommendations = self._generate_recommendations(assessment_context, knowledge_context)
            
            # Calculate confidence metrics
            confidence_metrics = self._calculate_confidence_metrics(
                assessment_context, knowledge_context, recommendations
            )
            
            # Create comprehensive feedback result
            feedback_result = FeedbackResult(
                overall_assessment=self._generate_overall_assessment(assessment_context),
                risk_summary=self._generate_risk_summary(assessment_context),
                immediate_actions=recommendations['immediate'],
                short_term_improvements=recommendations['short_term'],
                strategic_initiatives=recommendations['strategic'],
                emerging_tech_focus=self._identify_emerging_tech_focus(assessment_context),
                confidence_metrics=confidence_metrics,
                sources_used=knowledge_context.get('sources', []),
                generation_timestamp=datetime.now()
            )
            
            processing_time = time.time() - start_time
            logger.info(f"AI feedback generated in {processing_time:.2f} seconds")
            
            return feedback_result
            
        except Exception as e:
            logger.error(f"Error generating AI feedback: {str(e)}")
            # Return fallback recommendations
            return self._generate_fallback_feedback(assessment_context)
    
    def _generate_rag_queries(self, context: AssessmentContext) -> List[str]:
        """Generate targeted queries for RAG based on assessment context"""
        queries = []
        
        # Base query for overall risk level
        queries.append(f"cybersecurity risk management {context.risk_level} risk organizations")
        
        # Queries for critical sections
        for section in context.critical_sections:
            section_name = section.replace('_', ' ')
            queries.append(f"{section_name} security controls best practices")
            queries.append(f"{section_name} risk mitigation strategies")
        
        # Queries for high-risk sections
        for section in context.high_risk_sections:
            section_name = section.replace('_', ' ')
            queries.append(f"improving {section_name} security posture")
        
        # Emerging technology specific queries
        if 'emerging_tech' in context.section_scores:
            emerging_score = context.section_scores['emerging_tech'].get('percentage', 0)
            if emerging_score < 60:
                queries.extend([
                    "emerging technology risk management frameworks",
                    "AI ML security governance standards",
                    "blockchain IoT security best practices",
                    "quantum computing cybersecurity preparation"
                ])
        
        # Governance and compliance queries
        if context.overall_score < 50:
            queries.extend([
                "cybersecurity governance framework implementation",
                "risk management process improvement",
                "security compliance program development"
            ])
        
        return queries[:10]  # Limit to top 10 queries for performance
    
    def _retrieve_knowledge(self, queries: List[str]) -> Dict[str, Any]:
        """Retrieve relevant knowledge from RAG pipeline"""
        knowledge_context = {
            'relevant_content': [],
            'sources': [],
            'confidence_scores': []
        }
        
        if not self.qa_chain:
            logger.warning("RAG pipeline not available, using fallback knowledge")
            return knowledge_context
        
        try:
            for query in queries:
                try:
                    # Query the RAG pipeline
                    result = self.qa_chain({"query": query})
                    
                    if result and 'result' in result:
                        knowledge_context['relevant_content'].append({
                            'query': query,
                            'content': result['result'],
                            'confidence': 0.8  # Default confidence
                        })
                    
                    # Extract sources if available
                    if 'source_documents' in result:
                        for doc in result['source_documents']:
                            if hasattr(doc, 'metadata') and 'source' in doc.metadata:
                                source = doc.metadata['source']
                                if source not in knowledge_context['sources']:
                                    knowledge_context['sources'].append(source)
                
                except Exception as e:
                    logger.warning(f"Error querying RAG for '{query}': {str(e)}")
                    continue
            
            logger.info(f"Retrieved knowledge from {len(knowledge_context['relevant_content'])} queries")
            
        except Exception as e:
            logger.error(f"Error retrieving knowledge: {str(e)}")
        
        return knowledge_context
    
    def _generate_recommendations(
        self, 
        context: AssessmentContext, 
        knowledge: Dict[str, Any]
    ) -> Dict[str, List[AIRecommendation]]:
        """Generate categorized recommendations using local LLM and retrieved knowledge"""
        
        recommendations = {
            'immediate': [],
            'short_term': [],
            'strategic': []
        }
        
        try:
            # Generate immediate actions for critical sections
            for section in context.critical_sections:
                immediate_rec = self._generate_section_recommendation(
                    section, context, knowledge, 'immediate'
                )
                if immediate_rec:
                    recommendations['immediate'].append(immediate_rec)
            
            # Generate short-term improvements for high-risk sections
            for section in context.high_risk_sections:
                short_term_rec = self._generate_section_recommendation(
                    section, context, knowledge, 'short_term'
                )
                if short_term_rec:
                    recommendations['short_term'].append(short_term_rec)
            
            # Generate strategic initiatives based on overall score
            strategic_recs = self._generate_strategic_recommendations(context, knowledge)
            recommendations['strategic'].extend(strategic_recs)
            
            # Sort by priority
            for category in recommendations:
                recommendations[category].sort(key=lambda x: x.priority)
            
        except Exception as e:
            logger.error(f"Error generating recommendations: {str(e)}")
            # Add fallback recommendations
            recommendations = self._generate_fallback_recommendations(context)
        
        return recommendations
    
    def _generate_section_recommendation(
        self, 
        section_id: str, 
        context: AssessmentContext, 
        knowledge: Dict[str, Any], 
        category: str
    ) -> Optional[AIRecommendation]:
        """Generate a recommendation for a specific section"""
        
        section_info = context.section_scores.get(section_id, {})
        section_name = section_info.get('sectionName', section_id.replace('_', ' ').title())
        section_score = section_info.get('percentage', 0)
        
        # Define recommendation templates based on section and category
        templates = self._get_recommendation_templates()
        
        template_key = f"{section_id}_{category}"
        if template_key not in templates:
            template_key = f"generic_{category}"
        
        template = templates.get(template_key, templates['generic_immediate'])
        
        # Find relevant knowledge for this section
        relevant_knowledge = []
        section_keywords = section_id.replace('_', ' ').split()
        
        for content in knowledge.get('relevant_content', []):
            content_text = content.get('content', '').lower()
            if any(keyword in content_text for keyword in section_keywords):
                relevant_knowledge.append(content)
        
        # Generate recommendation using template and knowledge
        try:
            recommendation = AIRecommendation(
                category=category,
                priority=self._calculate_priority(section_score, category),
                title=template['title'].format(section_name=section_name),
                description=template['description'].format(
                    section_name=section_name, 
                    score=section_score
                ),
                implementation_steps=template['steps'],
                frameworks_referenced=template['frameworks'],
                confidence_score=0.8 if relevant_knowledge else 0.6,
                sources=[k.get('query', '') for k in relevant_knowledge[:3]],
                estimated_impact=template['impact'],
                estimated_effort=template['effort'],
                timeline=template['timeline']
            )
            
            return recommendation
            
        except Exception as e:
            logger.error(f"Error generating recommendation for {section_id}: {str(e)}")
            return None
    
    def _generate_strategic_recommendations(
        self, 
        context: AssessmentContext, 
        knowledge: Dict[str, Any]
    ) -> List[AIRecommendation]:
        """Generate strategic-level recommendations"""
        
        strategic_recs = []
        
        # Holistic risk management framework (SEET paper alignment)
        if context.overall_score < 70:
            strategic_recs.append(AIRecommendation(
                category='strategic',
                priority=1,
                title='Implement Holistic Risk Management Framework',
                description=f'Establish comprehensive risk management approach aligned with business objectives. Current overall score of {context.overall_score}% indicates need for systematic improvement.',
                implementation_steps=[
                    'Conduct enterprise risk assessment',
                    'Align security strategy with business objectives',
                    'Implement continuous risk monitoring',
                    'Establish risk governance structure'
                ],
                frameworks_referenced=['NIST RMF', 'ISO 31000', 'FAIR'],
                confidence_score=0.9,
                sources=knowledge.get('sources', [])[:3],
                estimated_impact='High',
                estimated_effort='High',
                timeline='6-12 months'
            ))
        
        # Emerging technology governance (SEET focus)
        emerging_tech_score = context.section_scores.get('emerging_tech', {}).get('percentage', 0)
        if emerging_tech_score < 60:
            strategic_recs.append(AIRecommendation(
                category='strategic',
                priority=2,
                title='Establish Emerging Technology Governance',
                description='Develop governance framework for AI, IoT, blockchain, and other emerging technologies to manage innovation risks proactively.',
                implementation_steps=[
                    'Create emerging technology risk assessment process',
                    'Establish AI/ML governance committee',
                    'Develop technology adoption criteria',
                    'Implement continuous technology risk monitoring'
                ],
                frameworks_referenced=['NIST AI RMF', 'ISO/IEC 23053', 'IEEE Standards'],
                confidence_score=0.85,
                sources=knowledge.get('sources', [])[:2],
                estimated_impact='High',
                estimated_effort='Medium',
                timeline='3-6 months'
            ))
        
        # Security center of excellence
        if context.overall_score > 60:
            strategic_recs.append(AIRecommendation(
                category='strategic',
                priority=3,
                title='Establish Security Center of Excellence',
                description='Create centralized security expertise hub to drive continuous improvement and innovation in cybersecurity practices.',
                implementation_steps=[
                    'Define center charter and objectives',
                    'Establish security metrics and KPIs',
                    'Create security innovation program',
                    'Implement knowledge sharing platform'
                ],
                frameworks_referenced=['COBIT', 'ITIL', 'TOGAF'],
                confidence_score=0.75,
                sources=knowledge.get('sources', [])[:2],
                estimated_impact='Medium',
                estimated_effort='Medium',
                timeline='6-9 months'
            ))
        
        return strategic_recs
    
    def _calculate_priority(self, score: float, category: str) -> int:
        """Calculate recommendation priority based on score and category"""
        if category == 'immediate':
            if score < 20:
                return 1  # Highest priority
            elif score < 40:
                return 2
            else:
                return 3
        elif category == 'short_term':
            if score < 40:
                return 1
            elif score < 60:
                return 2
            else:
                return 3
        else:  # strategic
            if score < 50:
                return 1
            elif score < 70:
                return 2
            else:
                return 3
    
    def _get_recommendation_templates(self) -> Dict[str, Dict[str, Any]]:
        """Get recommendation templates for different sections and categories"""
        return {
            'governance_immediate': {
                'title': 'Establish Basic {section_name} Framework',
                'description': '{section_name} scored {score}%, requiring immediate attention to establish foundational governance.',
                'steps': [
                    'Define security governance charter',
                    'Establish security steering committee',
                    'Create basic security policies',
                    'Implement risk register'
                ],
                'frameworks': ['NIST CSF', 'ISO 27001'],
                'impact': 'High',
                'effort': 'Medium',
                'timeline': '0-30 days'
            },
            'emerging_tech_short_term': {
                'title': 'Enhance {section_name} Security Standards',
                'description': 'Improve {section_name} capabilities (current score: {score}%) through systematic enhancement.',
                'steps': [
                    'Develop technology risk assessment process',
                    'Create AI/ML security standards',
                    'Implement emerging tech governance',
                    'Establish innovation security review'
                ],
                'frameworks': ['NIST AI RMF', 'ISO/IEC 23053'],
                'impact': 'High',
                'effort': 'Medium',
                'timeline': '1-6 months'
            },
            'generic_immediate': {
                'title': 'Address Critical {section_name} Gaps',
                'description': '{section_name} requires immediate attention with a score of {score}%.',
                'steps': [
                    'Conduct immediate risk assessment',
                    'Implement basic security controls',
                    'Establish monitoring procedures',
                    'Create incident response plan'
                ],
                'frameworks': ['NIST CSF'],
                'impact': 'High',
                'effort': 'Low',
                'timeline': '0-30 days'
            }
        }
    
    def _generate_overall_assessment(self, context: AssessmentContext) -> str:
        """Generate overall assessment summary"""
        risk_level = context.risk_level.lower()
        score = context.overall_score
        
        if score < 40:
            return f"Your organization has a {risk_level} risk profile with significant security gaps requiring immediate attention. The overall score of {score}% indicates fundamental security controls need to be established."
        elif score < 60:
            return f"Your organization shows {risk_level} risk levels with important areas for improvement. The score of {score}% suggests good foundational security but requires systematic enhancement."
        elif score < 80:
            return f"Your organization demonstrates {risk_level} risk management with solid security practices. The score of {score}% indicates mature security posture with opportunities for optimization."
        else:
            return f"Your organization exhibits {risk_level} risk profile with advanced security capabilities. The score of {score}% reflects mature, well-managed cybersecurity practices."
    
    def _generate_risk_summary(self, context: AssessmentContext) -> str:
        """Generate risk summary based on section scores"""
        critical_count = len(context.critical_sections)
        high_risk_count = len(context.high_risk_sections)
        
        summary = f"Assessment completed with {context.completion_rate:.1%} completion rate. "
        
        if critical_count > 0:
            summary += f"{critical_count} critical areas identified requiring immediate action. "
        
        if high_risk_count > 0:
            summary += f"{high_risk_count} high-risk areas need priority attention. "
        
        if critical_count == 0 and high_risk_count == 0:
            summary += "No critical or high-risk areas identified. Focus on continuous improvement opportunities."
        
        return summary
    
    def _identify_emerging_tech_focus(self, context: AssessmentContext) -> List[str]:
        """Identify emerging technology focus areas based on responses"""
        focus_areas = []
        
        # Check emerging tech responses
        emerging_responses = context.responses.get('emerging_tech', {})
        
        # Check which technologies are being used or planned
        tech_adoption = emerging_responses.get('tech_001', [])
        if isinstance(tech_adoption, list):
            focus_areas.extend(tech_adoption)
        
        # Add focus areas based on low scores
        emerging_score = context.section_scores.get('emerging_tech', {}).get('percentage', 0)
        if emerging_score < 60:
            focus_areas.extend([
                'AI/ML Security Governance',
                'IoT Device Management',
                'Cloud Security Posture',
                'Emerging Technology Risk Assessment'
            ])
        
        return list(set(focus_areas))  # Remove duplicates
    
    def _calculate_confidence_metrics(
        self, 
        context: AssessmentContext, 
        knowledge: Dict[str, Any], 
        recommendations: Dict[str, List[AIRecommendation]]
    ) -> Dict[str, float]:
        """Calculate confidence metrics for the generated feedback"""
        
        # Base confidence on completion rate
        completion_confidence = context.completion_rate
        
        # Knowledge availability confidence
        knowledge_confidence = min(len(knowledge.get('relevant_content', [])) / 10, 1.0)
        
        # Recommendation confidence (average of all recommendations)
        all_recs = []
        for category in recommendations.values():
            all_recs.extend(category)
        
        rec_confidence = sum(rec.confidence_score for rec in all_recs) / len(all_recs) if all_recs else 0.5
        
        # Overall confidence
        overall_confidence = (completion_confidence * 0.4 + knowledge_confidence * 0.3 + rec_confidence * 0.3)
        
        return {
            'overall_confidence': overall_confidence,
            'completion_confidence': completion_confidence,
            'knowledge_confidence': knowledge_confidence,
            'recommendation_confidence': rec_confidence
        }
    
    def _generate_fallback_feedback(self, context: AssessmentContext) -> FeedbackResult:
        """Generate fallback feedback when RAG pipeline is not available"""
        logger.warning("Generating fallback feedback without RAG pipeline")
        
        fallback_recommendations = self._generate_fallback_recommendations(context)
        
        return FeedbackResult(
            overall_assessment=self._generate_overall_assessment(context),
            risk_summary=self._generate_risk_summary(context),
            immediate_actions=fallback_recommendations['immediate'],
            short_term_improvements=fallback_recommendations['short_term'],
            strategic_initiatives=fallback_recommendations['strategic'],
            emerging_tech_focus=self._identify_emerging_tech_focus(context),
            confidence_metrics={'overall_confidence': 0.6, 'fallback_mode': True},
            sources_used=['Built-in knowledge base'],
            generation_timestamp=datetime.now()
        )
    
    def _generate_fallback_recommendations(self, context: AssessmentContext) -> Dict[str, List[AIRecommendation]]:
        """Generate basic recommendations without RAG pipeline"""
        recommendations = {
            'immediate': [],
            'short_term': [],
            'strategic': []
        }
        
        # Add basic recommendations for critical sections
        for section in context.critical_sections:
            section_name = section.replace('_', ' ').title()
            recommendations['immediate'].append(AIRecommendation(
                category='immediate',
                priority=1,
                title=f'Address Critical {section_name} Issues',
                description=f'Immediate action required for {section_name} due to low score.',
                implementation_steps=[
                    'Conduct immediate assessment',
                    'Implement basic controls',
                    'Establish monitoring'
                ],
                frameworks_referenced=['NIST CSF'],
                confidence_score=0.6,
                sources=['Built-in recommendations'],
                estimated_impact='High',
                estimated_effort='Medium',
                timeline='0-30 days'
            ))
        
        return recommendations

# Global instance
ai_feedback_engine = AIFeedbackEngine()