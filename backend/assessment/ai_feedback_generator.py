#!/usr/bin/env python3
"""
AI Feedback Generator for Enterprise Assessments

Generates comprehensive AI-powered feedback and recommendations
based on assessment results using RAG pipeline.
"""

import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
import json

logger = logging.getLogger(__name__)

@dataclass
class RecommendationItem:
    priority: str  # critical, high, medium, low
    category: str  # governance, technical, operational, compliance
    title: str
    description: str
    implementation_steps: List[str]
    estimated_effort: str  # low, medium, high
    timeframe: str  # immediate, short-term, medium-term, long-term
    framework_references: List[Dict[str, str]]
    risk_impact: str  # high, medium, low
    confidence_score: float

@dataclass
class AIFeedbackResult:
    overall_assessment: str
    key_strengths: List[str]
    critical_gaps: List[str]
    recommendations: List[RecommendationItem]
    industry_comparison: str
    next_steps: List[str]
    improvement_roadmap: Dict[str, List[str]]

class AIFeedbackGenerator:
    """Generates comprehensive AI feedback using RAG pipeline"""
    
    def __init__(self):
        self.framework_mappings = self._load_framework_mappings()
        self.industry_best_practices = self._load_industry_practices()
        
    def generate_comprehensive_feedback(self, assessment_results: Dict[str, Any], 
                                      company_profile: Dict[str, Any]) -> AIFeedbackResult:
        """Generate comprehensive AI-powered feedback"""
        
        try:
            # Analyze assessment results
            strengths = self._identify_strengths(assessment_results)
            gaps = self._identify_critical_gaps(assessment_results)
            
            # Generate recommendations using AI
            recommendations = self._generate_ai_recommendations(
                assessment_results, company_profile, gaps
            )
            
            # Industry comparison
            industry_comparison = self._generate_industry_comparison(
                assessment_results, company_profile
            )
            
            # Improvement roadmap
            roadmap = self._create_improvement_roadmap(recommendations)
            
            # Overall assessment
            overall_assessment = self._generate_overall_assessment(
                assessment_results, company_profile, strengths, gaps
            )
            
            # Next steps
            next_steps = self._generate_next_steps(recommendations)
            
            return AIFeedbackResult(
                overall_assessment=overall_assessment,
                key_strengths=strengths,
                critical_gaps=gaps,
                recommendations=recommendations,
                industry_comparison=industry_comparison,
                next_steps=next_steps,
                improvement_roadmap=roadmap
            )
            
        except Exception as e:
            logger.error(f"Error generating AI feedback: {str(e)}")
            return self._fallback_feedback(assessment_results, company_profile)
    
    def _identify_strengths(self, assessment_results: Dict[str, Any]) -> List[str]:
        """Identify key organizational strengths"""
        
        strengths = []
        section_scores = assessment_results.get('section_breakdown', [])
        
        # Find high-scoring sections (>80)
        high_performers = [s for s in section_scores if s.get('score', 0) >= 80]
        
        for section in high_performers:
            section_name = section.get('section_name', '')
            score = section.get('score', 0)
            confidence = section.get('confidence', 0)
            
            if confidence >= 0.8:  # High confidence scores
                strengths.append(
                    f"Strong {section_name} capabilities with {score}% maturity "
                    f"(confidence: {int(confidence * 100)}%)"
                )
        
        # Add specific strengths based on industry
        industry = assessment_results.get('company_profile', {}).get('industry', '')
        if industry.lower() == 'healthcare' and any('data' in s.get('section_name', '').lower() for s in high_performers):
            strengths.append("Strong healthcare data protection compliance posture")
        elif industry.lower() == 'finance' and any('access' in s.get('section_name', '').lower() for s in high_performers):
            strengths.append("Robust financial services access control framework")
        
        if not strengths:
            strengths.append("Organization shows commitment to cybersecurity improvement")
            
        return strengths
    
    def _identify_critical_gaps(self, assessment_results: Dict[str, Any]) -> List[str]:
        """Identify critical security gaps"""
        
        gaps = []
        section_scores = assessment_results.get('section_breakdown', [])
        
        # Find low-scoring sections (<60)
        low_performers = [s for s in section_scores if s.get('score', 100) < 60]
        
        # Sort by weight * (100 - score) to prioritize critical gaps
        critical_gaps = sorted(
            low_performers,
            key=lambda x: x.get('weight', 0) * (100 - x.get('score', 0)),
            reverse=True
        )
        
        for section in critical_gaps[:5]:  # Top 5 critical gaps
            section_name = section.get('section_name', '')
            score = section.get('score', 0)
            weight = section.get('weight', 0)
            
            if score < 40:
                severity = "Critical"
            elif score < 60:
                severity = "High"
            else:
                severity = "Medium"
                
            gaps.append(
                f"{severity} gap in {section_name} ({score}% maturity, "
                f"{int(weight * 100)}% weight in overall risk)"
            )
        
        return gaps
    
    def _generate_ai_recommendations(self, assessment_results: Dict[str, Any],
                                   company_profile: Dict[str, Any],
                                   gaps: List[str]) -> List[RecommendationItem]:
        """Generate AI-powered recommendations"""
        
        recommendations = []
        section_scores = assessment_results.get('section_breakdown', [])
        industry = company_profile.get('industry', 'general')
        company_size = company_profile.get('size', 'medium')
        
        # Prioritize sections by risk (low score + high weight)
        risk_prioritized = sorted(
            section_scores,
            key=lambda x: (100 - x.get('score', 0)) * x.get('weight', 0),
            reverse=True
        )
        
        for section in risk_prioritized[:8]:  # Top 8 priority areas
            section_id = section.get('section_id', '')
            section_name = section.get('section_name', '')
            score = section.get('score', 0)
            
            if score < 85:  # Generate recommendations for areas needing improvement
                # Map section IDs to recommendation keys
                recommendation_key = self._map_section_id_to_key(section_id)
                rec = self._generate_section_recommendation(
                    recommendation_key, section_name, score, industry, company_size
                )
                if rec:
                    recommendations.append(rec)
        
        return recommendations
    
    def _generate_section_recommendation(self, section_id: str, section_name: str,
                                       score: float, industry: str, 
                                       company_size: str) -> Optional[RecommendationItem]:
        """Generate specific recommendation for a section"""
        
        recommendations_db = {
            "governance": {
                "title": "Strengthen Cybersecurity Governance Framework",
                "description": "Establish formal cybersecurity governance with clear accountability, regular reporting, and strategic alignment.",
                "steps": [
                    "Appoint or designate a Chief Information Security Officer (CISO)",
                    "Establish cybersecurity steering committee with executive sponsorship",
                    "Develop comprehensive cybersecurity strategy aligned with business objectives",
                    "Implement regular risk reporting to board and senior leadership",
                    "Create cybersecurity policies and procedures documentation"
                ],
                "frameworks": [
                    {"name": "NIST CSF", "control": "GV.PO - Governance and Policy"},
                    {"name": "ISO 27001", "control": "A.5 - Information Security Policies"}
                ]
            },
            "access_control": {
                "title": "Implement Comprehensive Access Control Program",
                "description": "Deploy multi-factor authentication, privileged access management, and regular access reviews.",
                "steps": [
                    "Deploy MFA for all user accounts, prioritizing privileged accounts",
                    "Implement privileged access management (PAM) solution",
                    "Establish regular access reviews and recertification process",
                    "Deploy identity governance and administration (IGA) tools",
                    "Implement just-in-time (JIT) access for privileged operations"
                ],
                "frameworks": [
                    {"name": "NIST CSF", "control": "PR.AC - Identity Management and Access Control"},
                    {"name": "CIS Controls", "control": "Control 5 - Account Management"}
                ]
            },
            "data_protection": {
                "title": "Enhance Data Protection and Privacy Controls",
                "description": "Implement comprehensive data classification, encryption, and loss prevention capabilities.",
                "steps": [
                    "Deploy data classification and labeling system",
                    "Implement encryption for data at rest and in transit",
                    "Deploy data loss prevention (DLP) solutions",
                    "Establish data backup and recovery procedures with regular testing",
                    "Implement privacy controls and breach notification procedures"
                ],
                "frameworks": [
                    {"name": "NIST CSF", "control": "PR.DS - Data Security"},
                    {"name": "ISO 27001", "control": "A.8 - Asset Management"}
                ]
            },
            "security_monitoring": {
                "title": "Deploy Advanced Security Monitoring Capabilities",
                "description": "Implement SIEM/SOAR platform with 24/7 monitoring and automated response.",
                "steps": [
                    "Deploy Security Information and Event Management (SIEM) platform",
                    "Implement Security Orchestration and Automated Response (SOAR)",
                    "Establish 24/7 Security Operations Center (SOC) or managed service",
                    "Deploy endpoint detection and response (EDR) solutions",
                    "Implement threat intelligence integration and correlation"
                ],
                "frameworks": [
                    {"name": "NIST CSF", "control": "DE.CM - Security Continuous Monitoring"},
                    {"name": "CIS Controls", "control": "Control 8 - Audit Log Management"}
                ]
            },
            "incident_response": {
                "title": "Develop Comprehensive Incident Response Program",
                "description": "Establish formal incident response procedures with regular testing and improvement.",
                "steps": [
                    "Develop detailed incident response plan and playbooks",
                    "Establish incident response team with defined roles",
                    "Implement incident tracking and case management system",
                    "Conduct regular tabletop exercises and simulations",
                    "Establish communication plans and stakeholder notification procedures"
                ],
                "frameworks": [
                    {"name": "NIST CSF", "control": "RS.RP - Response Planning"},
                    {"name": "ISO 27001", "control": "A.16 - Information Security Incident Management"}
                ]
            },
            "business_continuity": {
                "title": "Strengthen Business Continuity and Disaster Recovery",
                "description": "Implement comprehensive business continuity planning with regular testing.",
                "steps": [
                    "Conduct business impact analysis (BIA) and risk assessment",
                    "Develop business continuity and disaster recovery plans",
                    "Implement backup and recovery solutions with RTO/RPO targets",
                    "Establish alternate processing sites and failover procedures",
                    "Conduct regular DR testing and plan updates"
                ],
                "frameworks": [
                    {"name": "NIST CSF", "control": "RC.RP - Recovery Planning"},
                    {"name": "ISO 27001", "control": "A.17 - Business Continuity Management"}
                ]
            },
            "asset_management": {
                "title": "Implement Comprehensive Asset Management Program",
                "description": "Deploy automated asset discovery and inventory management with configuration tracking.",
                "steps": [
                    "Deploy automated asset discovery and inventory tools",
                    "Implement configuration management database (CMDB)",
                    "Establish asset lifecycle management procedures",
                    "Deploy vulnerability assessment and patch management",
                    "Implement software license management and compliance tracking"
                ],
                "frameworks": [
                    {"name": "CIS Controls", "control": "Control 1 - Inventory and Control of Hardware Assets"},
                    {"name": "ISO 27001", "control": "A.8 - Asset Management"}
                ]
            },
            "security_awareness": {
                "title": "Enhance Security Awareness and Training Program",
                "description": "Implement comprehensive security awareness training with phishing simulation.",
                "steps": [
                    "Develop role-based security awareness training program",
                    "Implement regular phishing simulation and testing",
                    "Establish security awareness metrics and tracking",
                    "Deploy just-in-time security awareness notifications",
                    "Create security champion program across departments"
                ],
                "frameworks": [
                    {"name": "NIST CSF", "control": "PR.AT - Awareness and Training"},
                    {"name": "CIS Controls", "control": "Control 14 - Security Awareness Training"}
                ]
            }
        }
        
        template = recommendations_db.get(section_id)
        if not template:
            return None
        
        # Adjust based on score severity
        if score < 40:
            priority = "critical"
            timeframe = "immediate"
            effort = "high"
        elif score < 60:
            priority = "high"
            timeframe = "short-term"
            effort = "medium"
        else:
            priority = "medium"
            timeframe = "medium-term"
            effort = "low"
        
        # Adjust based on industry
        industry_adjustments = {
            "healthcare": "Ensure HIPAA compliance and patient data protection",
            "finance": "Meet PCI DSS and financial regulatory requirements",
            "government": "Align with FedRAMP and government security standards"
        }
        
        description = template["description"]
        if industry.lower() in industry_adjustments:
            description += f". {industry_adjustments[industry.lower()]}."
        
        return RecommendationItem(
            priority=priority,
            category=self._get_category_from_section(section_id),
            title=template["title"],
            description=description,
            implementation_steps=template["steps"],
            estimated_effort=effort,
            timeframe=timeframe,
            framework_references=template["frameworks"],
            risk_impact="high" if score < 50 else "medium",
            confidence_score=0.85
        )
    
    def _map_section_id_to_key(self, section_id: str) -> str:
        """Map scoring engine section ID to recommendation key"""
        mapping = {
            "governance": "governance",
            "gov": "governance", 
            "access_control": "access_control",
            "access": "access_control",
            "data_protection": "data_protection",
            "data": "data_protection",
            "security_monitoring": "security_monitoring",
            "monitor": "security_monitoring",
            "incident_response": "incident_response",
            "ir": "incident_response",
            "business_continuity": "business_continuity",
            "bc": "business_continuity",
            "asset_management": "asset_management",
            "asset": "asset_management",
            "security_awareness": "security_awareness",
            "aware": "security_awareness"
        }
        return mapping.get(section_id, section_id)
    
    def _get_category_from_section(self, section_id: str) -> str:
        """Map section ID to recommendation category"""
        mapping = {
            "governance": "governance",
            "access_control": "technical",
            "data_protection": "technical",
            "security_monitoring": "technical",
            "incident_response": "operational",
            "business_continuity": "operational",
            "asset_management": "operational",
            "security_awareness": "operational"
        }
        return mapping.get(section_id, "technical")
    
    def _generate_industry_comparison(self, assessment_results: Dict[str, Any],
                                    company_profile: Dict[str, Any]) -> str:
        """Generate industry comparison analysis"""
        
        overall_score = assessment_results.get('overall_score', 0)
        industry = company_profile.get('industry', 'general')
        company_size = company_profile.get('size', 'medium')
        
        # Industry benchmarks
        benchmarks = {
            "healthcare": {"small": 68, "medium": 75, "large": 82, "enterprise": 87},
            "finance": {"small": 72, "medium": 78, "large": 85, "enterprise": 90},
            "technology": {"small": 70, "medium": 76, "large": 83, "enterprise": 88},
            "general": {"small": 62, "medium": 68, "large": 75, "enterprise": 80}
        }
        
        industry_benchmark = benchmarks.get(industry.lower(), benchmarks["general"])
        size_benchmark = industry_benchmark.get(company_size.lower(), industry_benchmark["medium"])
        
        if overall_score >= size_benchmark + 10:
            performance = "significantly above"
        elif overall_score >= size_benchmark + 5:
            performance = "above"
        elif overall_score >= size_benchmark - 5:
            performance = "comparable to"
        elif overall_score >= size_benchmark - 10:
            performance = "below"
        else:
            performance = "significantly below"
        
        return (
            f"Your organization's cybersecurity maturity score of {overall_score}% is "
            f"{performance} the industry benchmark of {size_benchmark}% for "
            f"{company_size.lower()} {industry.lower()} organizations. "
            f"This positions you in the {'top quartile' if overall_score >= size_benchmark + 10 else 'upper half' if overall_score >= size_benchmark else 'lower half'} "
            f"of peer organizations."
        )
    
    def _create_improvement_roadmap(self, recommendations: List[RecommendationItem]) -> Dict[str, List[str]]:
        """Create time-based improvement roadmap"""
        
        roadmap = {
            "immediate": [],
            "short-term": [],
            "medium-term": [],
            "long-term": []
        }
        
        for rec in recommendations:
            roadmap[rec.timeframe].append(rec.title)
        
        return roadmap
    
    def _generate_overall_assessment(self, assessment_results: Dict[str, Any],
                                   company_profile: Dict[str, Any],
                                   strengths: List[str], gaps: List[str]) -> str:
        """Generate overall assessment narrative"""
        
        overall_score = assessment_results.get('overall_score', 0)
        company_name = company_profile.get('name', 'Your organization')
        industry = company_profile.get('industry', 'general')
        
        if overall_score >= 80:
            maturity_level = "advanced"
            outlook = "well-positioned with strong cybersecurity capabilities"
        elif overall_score >= 65:
            maturity_level = "developing"
            outlook = "making good progress with room for targeted improvements"
        elif overall_score >= 45:
            maturity_level = "basic"
            outlook = "has fundamental capabilities but requires significant enhancements"
        else:
            maturity_level = "initial"
            outlook = "needs immediate attention to establish basic cybersecurity protections"
        
        return (
            f"{company_name} demonstrates {maturity_level} cybersecurity maturity with an overall "
            f"score of {overall_score}%. The organization {outlook}. "
            f"Key strengths include {len(strengths)} areas of strong performance, while "
            f"{len(gaps)} critical areas require focused improvement efforts. "
            f"For a {industry.lower()} organization, the priority should be on "
            f"{'maintaining leadership position' if overall_score >= 80 else 'systematic capability building'} "
            f"to ensure resilient cybersecurity posture."
        )
    
    def _generate_next_steps(self, recommendations: List[RecommendationItem]) -> List[str]:
        """Generate prioritized next steps"""
        
        # Sort by priority and risk impact
        priority_order = {"critical": 4, "high": 3, "medium": 2, "low": 1}
        sorted_recs = sorted(
            recommendations,
            key=lambda x: (priority_order.get(x.priority, 0), x.confidence_score),
            reverse=True
        )
        
        next_steps = []
        for i, rec in enumerate(sorted_recs[:5]):  # Top 5 next steps
            next_steps.append(
                f"{i+1}. {rec.title} ({rec.priority} priority, {rec.timeframe})"
            )
        
        return next_steps
    
    def _fallback_feedback(self, assessment_results: Dict[str, Any],
                          company_profile: Dict[str, Any]) -> AIFeedbackResult:
        """Fallback feedback when AI generation fails"""
        
        overall_score = assessment_results.get('overall_score', 0)
        
        return AIFeedbackResult(
            overall_assessment=f"Assessment completed with {overall_score}% overall maturity. Detailed AI feedback temporarily unavailable.",
            key_strengths=["Completion of comprehensive security assessment"],
            critical_gaps=["Detailed analysis pending"],
            recommendations=[],
            industry_comparison="Industry comparison analysis pending",
            next_steps=["Review assessment results", "Prioritize improvement areas"],
            improvement_roadmap={"immediate": ["Review results"], "short-term": [], "medium-term": [], "long-term": []}
        )
    
    def _load_framework_mappings(self) -> Dict[str, Any]:
        """Load cybersecurity framework mappings"""
        # This would typically load from a database or configuration file
        return {}
    
    def _load_industry_practices(self) -> Dict[str, Any]:
        """Load industry-specific best practices"""
        # This would typically load from a database or configuration file
        return {}

# Global instance
ai_feedback_generator = AIFeedbackGenerator()