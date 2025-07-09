"""
Objective Scoring Module

Provides evidence-based, objective scoring guidelines to reduce subjectivity
in risk assessments. Implements clear 1-10 scale definitions with automated
score justification.
"""

import logging
import re
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import json

logger = logging.getLogger(__name__)

class ScoreLevel(Enum):
    """Score levels with clear definitions"""
    CRITICAL = (1, 2)      # Critical gaps, immediate action required
    POOR = (3, 4)          # Poor implementation, major improvements needed
    BASIC = (5, 6)         # Basic implementation, moderate improvements needed
    GOOD = (7, 8)          # Good implementation, minor improvements needed
    EXCELLENT = (9, 10)    # Excellent implementation, best practices followed

@dataclass
class ScoringCriteria:
    """Scoring criteria for a specific category"""
    category_id: str
    criteria_levels: Dict[int, str]  # Score -> Description
    evidence_indicators: Dict[str, int]  # Keyword/phrase -> Score boost
    maturity_levels: Dict[str, int]  # Maturity level -> Base score
    industry_adjustments: Dict[str, float]  # Industry -> Score modifier

@dataclass
class ScoreJustification:
    """Detailed justification for a score"""
    score: int
    base_score: int
    adjustments: List[Tuple[str, int, str]]  # (reason, adjustment, evidence)
    confidence: float
    evidence_found: List[str]
    missing_evidence: List[str]
    recommendations: List[str]

class ObjectiveScorer:
    """Main class for objective risk scoring"""
    
    def __init__(self):
        self.scoring_criteria = self._initialize_scoring_criteria()
        self.maturity_keywords = self._initialize_maturity_keywords()
        self.evidence_patterns = self._initialize_evidence_patterns()
        
    def _initialize_scoring_criteria(self) -> Dict[str, ScoringCriteria]:
        """Initialize detailed scoring criteria for each category"""
        
        criteria = {}
        
        # Business Strategy Alignment
        criteria['business_strategy'] = ScoringCriteria(
            category_id='business_strategy',
            criteria_levels={
                1: "No strategic alignment documented; technology adoption happens ad-hoc",
                2: "Minimal strategic consideration; technology decisions made in isolation",
                3: "Basic strategic awareness; some technology decisions consider business goals",
                4: "Limited strategic integration; technology roadmap loosely aligned with business",
                5: "Moderate strategic alignment; technology initiatives support some business objectives",
                6: "Good strategic integration; most technology decisions aligned with business goals",
                7: "Strong strategic alignment; technology roadmap integrated with business strategy",
                8: "Comprehensive strategic integration; technology drives business innovation",
                9: "Excellent strategic alignment; technology and business strategies fully integrated",
                10: "Best practice strategic alignment; technology as core business differentiator"
            },
            evidence_indicators={
                'strategic roadmap': 2,
                'business case': 2,
                'roi analysis': 2,
                'stakeholder alignment': 1,
                'executive sponsor': 1,
                'governance committee': 1,
                'kpi tracking': 1,
                'regular review': 1
            },
            maturity_levels={
                'ad-hoc': 2,
                'basic': 4,
                'defined': 6,
                'managed': 8,
                'optimizing': 10
            },
            industry_adjustments={
                'finance': 1.1,
                'healthcare': 1.0,
                'technology': 0.9,
                'manufacturing': 1.0
            }
        )
        
        # Data Sensitivity & Classification
        criteria['data_sensitivity'] = ScoringCriteria(
            category_id='data_sensitivity',
            criteria_levels={
                1: "No data classification; all data treated the same",
                2: "Minimal data awareness; basic public/private distinction",
                3: "Basic classification scheme; limited enforcement",
                4: "Defined classification levels; inconsistent application",
                5: "Moderate classification system; some automated enforcement",
                6: "Good classification framework; mostly consistent application",
                7: "Comprehensive classification; automated enforcement in most systems",
                8: "Advanced classification with data flow mapping; strong enforcement",
                9: "Excellent data governance; comprehensive labeling and protection",
                10: "Best practice data classification; automated discovery and protection"
            },
            evidence_indicators={
                'data classification policy': 3,
                'data labeling': 2,
                'automated discovery': 2,
                'data flow mapping': 2,
                'encryption': 1,
                'access controls': 1,
                'data loss prevention': 1,
                'regular audit': 1
            },
            maturity_levels={
                'none': 1,
                'basic': 3,
                'defined': 5,
                'managed': 7,
                'optimized': 9
            },
            industry_adjustments={
                'finance': 1.2,
                'healthcare': 1.2,
                'technology': 1.0,
                'government': 1.3
            }
        )
        
        # Access Management
        criteria['access_management'] = ScoringCriteria(
            category_id='access_management',
            criteria_levels={
                1: "No formal access controls; shared accounts common",
                2: "Basic access controls; manual provisioning/deprovisioning",
                3: "Defined access policies; inconsistent enforcement",
                4: "Role-based access partially implemented; some automation",
                5: "Moderate RBAC implementation; regular access reviews",
                6: "Good access management; automated provisioning for most systems",
                7: "Comprehensive RBAC; automated lifecycle management",
                8: "Advanced access governance; risk-based access decisions",
                9: "Excellent identity governance; zero-trust principles",
                10: "Best practice access management; continuous verification and adaptation"
            },
            evidence_indicators={
                'multi-factor authentication': 2,
                'single sign-on': 2,
                'role-based access': 2,
                'automated provisioning': 2,
                'access reviews': 1,
                'privileged access management': 1,
                'just-in-time access': 1,
                'zero trust': 1
            },
            maturity_levels={
                'manual': 2,
                'basic': 4,
                'rbac': 6,
                'automated': 8,
                'adaptive': 10
            },
            industry_adjustments={
                'finance': 1.1,
                'healthcare': 1.1,
                'technology': 0.95,
                'government': 1.2
            }
        )
        
        # Add more categories...
        self._add_additional_criteria(criteria)
        
        return criteria
    
    def _add_additional_criteria(self, criteria: Dict[str, ScoringCriteria]):
        """Add criteria for remaining categories"""
        
        # Incident Response
        criteria['incident_response'] = ScoringCriteria(
            category_id='incident_response',
            criteria_levels={
                1: "No incident response plan; reactive firefighting only",
                2: "Basic incident awareness; ad-hoc response procedures",
                3: "Documented incident procedures; limited testing",
                4: "Defined incident response plan; basic team structure",
                5: "Moderate IR capability; some automation and regular drills",
                6: "Good IR processes; integrated with business continuity",
                7: "Comprehensive IR program; threat intelligence integration",
                8: "Advanced IR with automated response; continuous improvement",
                9: "Excellent IR capability; predictive threat hunting",
                10: "Best practice IR; fully automated and adaptive response"
            },
            evidence_indicators={
                'incident response plan': 3,
                'response team': 2,
                'playbooks': 2,
                'automated response': 2,
                'threat intelligence': 1,
                'forensic capability': 1,
                'communication plan': 1,
                'lessons learned': 1
            },
            maturity_levels={
                'reactive': 2,
                'basic': 4,
                'defined': 6,
                'managed': 8,
                'adaptive': 10
            },
            industry_adjustments={
                'finance': 1.1,
                'healthcare': 1.1,
                'technology': 1.0,
                'critical_infrastructure': 1.2
            }
        )
        
        # Security Awareness Training
        criteria['security_awareness'] = ScoringCriteria(
            category_id='security_awareness',
            criteria_levels={
                1: "No security training; employees unaware of security policies",
                2: "Minimal security briefing during onboarding only",
                3: "Basic annual security training; generic content",
                4: "Regular security training; some role-specific content",
                5: "Moderate training program; phishing simulations",
                6: "Good training program; metrics tracking and improvement",
                7: "Comprehensive training; personalized and adaptive content",
                8: "Advanced training with gamification; real-time feedback",
                9: "Excellent security culture; continuous micro-learning",
                10: "Best practice security awareness; behavior-driven security culture"
            },
            evidence_indicators={
                'regular training': 2,
                'phishing simulation': 2,
                'role-specific training': 2,
                'metrics tracking': 2,
                'gamification': 1,
                'micro-learning': 1,
                'security champions': 1,
                'culture metrics': 1
            },
            maturity_levels={
                'none': 1,
                'basic': 3,
                'regular': 5,
                'targeted': 7,
                'adaptive': 9
            },
            industry_adjustments={
                'finance': 1.1,
                'healthcare': 1.1,
                'technology': 1.0,
                'education': 0.95
            }
        )
    
    def _initialize_maturity_keywords(self) -> Dict[str, List[str]]:
        """Initialize maturity level keywords"""
        
        return {
            'none': ['no', 'none', 'not implemented', 'absent', 'lacking'],
            'ad-hoc': ['ad-hoc', 'informal', 'unstructured', 'reactive', 'basic'],
            'basic': ['basic', 'minimal', 'simple', 'limited', 'starting'],
            'defined': ['defined', 'documented', 'formal', 'structured', 'established'],
            'managed': ['managed', 'monitored', 'measured', 'controlled', 'systematic'],
            'optimized': ['optimized', 'continuous', 'adaptive', 'innovative', 'best practice']
        }
    
    def _initialize_evidence_patterns(self) -> Dict[str, List[str]]:
        """Initialize evidence detection patterns"""
        
        return {
            'policy_existence': [
                r'policy|procedure|standard|guideline',
                r'documented|written|formal',
                r'approved|ratified|signed'
            ],
            'implementation': [
                r'implemented|deployed|configured|active',
                r'in place|operational|functioning',
                r'established|set up|configured'
            ],
            'automation': [
                r'automated|automatic|scripted',
                r'tool|system|platform|solution',
                r'integrated|centralized'
            ],
            'monitoring': [
                r'monitoring|tracking|measuring|metrics',
                r'dashboard|reporting|alerts',
                r'audit|review|assessment'
            ],
            'training': [
                r'training|education|awareness',
                r'certified|qualified|competent',
                r'workshop|course|session'
            ]
        }
    
    def calculate_objective_score(self, 
                                category_id: str,
                                answer: str,
                                company_profile: Dict[str, Any]) -> ScoreJustification:
        """Calculate objective score with detailed justification"""
        
        try:
            if category_id not in self.scoring_criteria:
                return self._get_default_score_justification(category_id, answer)
            
            criteria = self.scoring_criteria[category_id]
            
            # Start with base maturity assessment
            base_score = self._assess_maturity_level(answer, criteria)
            
            # Apply evidence-based adjustments
            adjustments = []
            evidence_found = []
            
            for evidence, boost in criteria.evidence_indicators.items():
                if self._find_evidence(answer, evidence):
                    adjustments.append(('evidence', boost, evidence))
                    evidence_found.append(evidence)
            
            # Apply industry adjustments
            industry = company_profile.get('industry', '').lower()
            if industry in criteria.industry_adjustments:
                industry_modifier = criteria.industry_adjustments[industry]
                industry_adjustment = int((base_score * industry_modifier) - base_score)
                if industry_adjustment != 0:
                    adjustments.append(('industry', industry_adjustment, f'Industry: {industry}'))
            
            # Calculate final score
            total_adjustments = sum(adj[1] for adj in adjustments)
            final_score = max(1, min(10, base_score + total_adjustments))
            
            # Calculate confidence based on evidence
            confidence = self._calculate_confidence(answer, evidence_found, criteria)
            
            # Generate recommendations
            missing_evidence = [evidence for evidence in criteria.evidence_indicators.keys() 
                              if evidence not in evidence_found]
            recommendations = self._generate_recommendations(final_score, missing_evidence, criteria)
            
            return ScoreJustification(
                score=final_score,
                base_score=base_score,
                adjustments=adjustments,
                confidence=confidence,
                evidence_found=evidence_found,
                missing_evidence=missing_evidence[:5],  # Top 5 missing
                recommendations=recommendations
            )
            
        except Exception as e:
            logger.error(f"Error calculating objective score for {category_id}: {str(e)}")
            return self._get_default_score_justification(category_id, answer)
    
    def _assess_maturity_level(self, answer: str, criteria: ScoringCriteria) -> int:
        """Assess maturity level from answer text"""
        
        answer_lower = answer.lower()
        maturity_scores = []
        
        for maturity_level, keywords in self.maturity_keywords.items():
            keyword_count = sum(1 for keyword in keywords if keyword in answer_lower)
            if keyword_count > 0 and maturity_level in criteria.maturity_levels:
                maturity_scores.append((keyword_count, criteria.maturity_levels[maturity_level]))
        
        if maturity_scores:
            # Return highest scoring maturity level
            return max(maturity_scores, key=lambda x: x[0])[1]
        else:
            # Default based on answer length and content
            if len(answer) < 20:
                return 2  # Minimal response
            elif len(answer) < 100:
                return 4  # Basic response
            else:
                return 6  # Detailed response
    
    def _find_evidence(self, answer: str, evidence_type: str) -> bool:
        """Find evidence of specific capability in answer"""
        
        answer_lower = answer.lower()
        evidence_lower = evidence_type.lower()
        
        # Direct keyword match
        if evidence_lower in answer_lower:
            return True
        
        # Pattern-based matching
        evidence_words = evidence_lower.split()
        if len(evidence_words) > 1:
            # Check if all words appear in answer
            return all(word in answer_lower for word in evidence_words)
        
        # Synonym matching
        synonyms = {
            'multi-factor authentication': ['mfa', '2fa', 'two-factor', 'multifactor'],
            'single sign-on': ['sso', 'single sign on'],
            'role-based access': ['rbac', 'role based'],
            'data loss prevention': ['dlp', 'data leakage'],
            'privileged access management': ['pam', 'privileged access'],
            'incident response plan': ['ir plan', 'incident plan', 'response plan']
        }
        
        if evidence_lower in synonyms:
            return any(synonym in answer_lower for synonym in synonyms[evidence_lower])
        
        return False
    
    def _calculate_confidence(self, 
                            answer: str,
                            evidence_found: List[str],
                            criteria: ScoringCriteria) -> float:
        """Calculate confidence in the score"""
        
        # Base confidence from answer quality
        answer_quality = min(1.0, len(answer) / 200)  # Normalize to 200 chars
        
        # Evidence coverage
        evidence_coverage = len(evidence_found) / len(criteria.evidence_indicators)
        
        # Specificity bonus
        specificity_keywords = ['implemented', 'configured', 'deployed', 'documented', 'tested']
        specificity_score = sum(1 for keyword in specificity_keywords if keyword in answer.lower())
        specificity_bonus = min(0.2, specificity_score * 0.05)
        
        confidence = 0.4 * answer_quality + 0.4 * evidence_coverage + 0.2 + specificity_bonus
        return min(1.0, confidence)
    
    def _generate_recommendations(self, 
                                score: int,
                                missing_evidence: List[str],
                                criteria: ScoringCriteria) -> List[str]:
        """Generate improvement recommendations"""
        
        recommendations = []
        
        if score <= 4:
            recommendations.append(f"Critical improvement needed in {criteria.category_id}")
            recommendations.append("Focus on establishing basic policies and procedures")
        elif score <= 6:
            recommendations.append(f"Moderate improvements needed in {criteria.category_id}")
            recommendations.append("Work on implementing consistent practices")
        elif score <= 8:
            recommendations.append(f"Good foundation in {criteria.category_id}, focus on optimization")
        
        # Specific recommendations based on missing evidence
        priority_evidence = {
            'automated': 'Consider implementing automation to improve efficiency',
            'monitoring': 'Add monitoring and metrics to track effectiveness',
            'training': 'Implement regular training and awareness programs',
            'policy': 'Document formal policies and procedures',
            'review': 'Establish regular review and improvement processes'
        }
        
        for evidence in missing_evidence[:3]:  # Top 3 missing
            for key, recommendation in priority_evidence.items():
                if key in evidence.lower():
                    recommendations.append(recommendation)
                    break
        
        return recommendations[:5]  # Limit to 5 recommendations
    
    def _get_default_score_justification(self, category_id: str, answer: str) -> ScoreJustification:
        """Get default score justification when criteria not available"""
        
        # Simple scoring based on answer quality
        if not answer or answer.lower() in ['no answer provided', 'n/a', 'unknown']:
            score = 1
        elif len(answer) < 20:
            score = 3
        elif len(answer) < 100:
            score = 5
        else:
            score = 7
        
        return ScoreJustification(
            score=score,
            base_score=score,
            adjustments=[],
            confidence=0.5,
            evidence_found=[],
            missing_evidence=[],
            recommendations=[f"Provide more detailed information about {category_id}"]
        )
    
    def get_scoring_guidance(self, category_id: str) -> Dict[str, Any]:
        """Get scoring guidance for a specific category"""
        
        if category_id not in self.scoring_criteria:
            return {'error': f'No scoring criteria available for {category_id}'}
        
        criteria = self.scoring_criteria[category_id]
        
        return {
            'category': category_id,
            'score_levels': criteria.criteria_levels,
            'evidence_to_mention': list(criteria.evidence_indicators.keys()),
            'maturity_levels': criteria.maturity_levels,
            'scoring_tips': [
                'Provide specific examples of implementation',
                'Mention tools, processes, and policies in place',
                'Describe automation and monitoring capabilities',
                'Include metrics and measurement approaches',
                'Reference industry standards and frameworks'
            ]
        }
    
    def validate_scoring_consistency(self, 
                                   assessments: List[Dict[str, Any]]) -> Dict[str, Any]:
        """Validate scoring consistency across multiple assessments"""
        
        consistency_report = {
            'overall_consistency': 0.0,
            'category_consistency': {},
            'outliers': [],
            'recommendations': []
        }
        
        try:
            # Group by company profile similarity
            similar_groups = self._group_similar_assessments(assessments)
            
            for group in similar_groups:
                if len(group) < 2:
                    continue
                
                # Calculate consistency within group
                group_consistency = self._calculate_group_consistency(group)
                consistency_report['category_consistency'].update(group_consistency)
            
            # Overall consistency
            if consistency_report['category_consistency']:
                consistency_report['overall_consistency'] = sum(
                    consistency_report['category_consistency'].values()
                ) / len(consistency_report['category_consistency'])
            
            # Generate recommendations
            if consistency_report['overall_consistency'] < 0.8:
                consistency_report['recommendations'].append(
                    "Consider reviewing scoring guidelines for consistency"
                )
                
        except Exception as e:
            logger.error(f"Error validating scoring consistency: {str(e)}")
            consistency_report['error'] = str(e)
        
        return consistency_report
    
    def _group_similar_assessments(self, assessments: List[Dict[str, Any]]) -> List[List[Dict[str, Any]]]:
        """Group assessments by similar company profiles"""
        
        groups = []
        
        for assessment in assessments:
            profile = assessment.get('company_profile', {})
            industry = profile.get('industry', '')
            size = profile.get('size', '')
            
            # Find matching group
            matched = False
            for group in groups:
                if group:
                    group_profile = group[0].get('company_profile', {})
                    if (group_profile.get('industry') == industry and 
                        group_profile.get('size') == size):
                        group.append(assessment)
                        matched = True
                        break
            
            if not matched:
                groups.append([assessment])
        
        return groups
    
    def _calculate_group_consistency(self, group: List[Dict[str, Any]]) -> Dict[str, float]:
        """Calculate consistency within a group of similar assessments"""
        
        consistency = {}
        
        # Get all categories
        categories = set()
        for assessment in group:
            for row in assessment.get('risk_table', []):
                categories.add(row.get('id', row.get('category', '')))
        
        # Calculate variance for each category
        for category in categories:
            scores = []
            for assessment in group:
                for row in assessment.get('risk_table', []):
                    if row.get('id') == category or row.get('category') == category:
                        scores.append(row.get('score', 0))
                        break
            
            if len(scores) > 1:
                # Calculate coefficient of variation (normalized variance)
                mean_score = sum(scores) / len(scores)
                variance = sum((score - mean_score) ** 2 for score in scores) / len(scores)
                cv = (variance ** 0.5) / mean_score if mean_score > 0 else 1.0
                consistency[category] = max(0.0, 1.0 - cv)  # Convert to consistency score
        
        return consistency

# Global instance
objective_scorer = ObjectiveScorer()