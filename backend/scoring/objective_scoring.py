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
    
    def generate_evidence_based_justification(self, 
                                            category_id: str,
                                            response: Any,
                                            question_metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Generate comprehensive evidence-based scoring justification"""
        
        try:
            # Handle different response types
            if isinstance(response, str):
                answer_text = response
                score_value = self._extract_score_from_text(response)
            elif isinstance(response, dict) and 'answer' in response:
                answer_text = response['answer']
                score_value = response.get('score', self._extract_score_from_text(answer_text))
            elif isinstance(response, (int, float)):
                score_value = int(response)
                answer_text = f"Score: {score_value}/10"
            else:
                answer_text = str(response)
                score_value = self._extract_score_from_text(answer_text)
            
            # Get scoring justification
            justification = self.calculate_objective_score(
                category_id, 
                answer_text, 
                question_metadata.get('company_profile', {})
            )
            
            # Enhanced evidence analysis
            evidence_analysis = self._perform_detailed_evidence_analysis(
                answer_text, 
                category_id,
                question_metadata
            )
            
            # Generate industry benchmarks
            industry_benchmark = self._get_industry_benchmark(
                category_id,
                question_metadata.get('company_profile', {})
            )
            
            # Risk impact assessment
            risk_impact = self._assess_risk_impact(score_value, category_id, question_metadata)
            
            return {
                'category_id': category_id,
                'final_score': justification.score,
                'confidence_level': justification.confidence,
                'scoring_breakdown': {
                    'base_score': justification.base_score,
                    'adjustments': [
                        {
                            'type': adj[0],
                            'value': adj[1],
                            'reason': adj[2]
                        } for adj in justification.adjustments
                    ],
                    'final_score': justification.score
                },
                'evidence_analysis': evidence_analysis,
                'industry_benchmark': industry_benchmark,
                'risk_impact': risk_impact,
                'recommendations': {
                    'immediate_actions': justification.recommendations[:3],
                    'long_term_improvements': self._generate_long_term_recommendations(
                        justification.score, 
                        category_id
                    ),
                    'industry_best_practices': self._get_industry_best_practices(
                        category_id,
                        question_metadata.get('company_profile', {})
                    )
                },
                'quality_indicators': {
                    'evidence_found': justification.evidence_found,
                    'missing_evidence': justification.missing_evidence,
                    'response_completeness': len(answer_text) / 200,  # Normalized
                    'specificity_score': self._calculate_specificity_score(answer_text)
                }
            }
            
        except Exception as e:
            logger.error(f"Error generating evidence-based justification: {str(e)}")
            return {
                'error': str(e),
                'category_id': category_id,
                'fallback_score': 5
            }
    
    def _extract_score_from_text(self, text: str) -> int:
        """Extract numeric score from text response"""
        
        import re
        
        # Look for patterns like "5/10", "score: 7", "rating of 8"
        patterns = [
            r'(\d+)/10',
            r'score:?\s*(\d+)',
            r'rating:?\s*(?:of\s*)?(\d+)',
            r'level:?\s*(\d+)',
            r'^(\d+)(?:\s|$)'  # Number at start
        ]
        
        for pattern in patterns:
            match = re.search(pattern, text.lower())
            if match:
                score = int(match.group(1))
                return max(1, min(10, score))
        
        # Default scoring based on content quality
        if 'excellent' in text.lower() or 'outstanding' in text.lower():
            return 9
        elif 'good' in text.lower() or 'strong' in text.lower():
            return 7
        elif 'adequate' in text.lower() or 'moderate' in text.lower():
            return 5
        elif 'poor' in text.lower() or 'weak' in text.lower():
            return 3
        elif 'none' in text.lower() or 'no' in text.lower():
            return 1
        else:
            return 5  # Default middle score
    
    def _perform_detailed_evidence_analysis(self, 
                                          answer_text: str,
                                          category_id: str,
                                          metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Perform detailed evidence analysis on the response"""
        
        evidence_analysis = {
            'quantitative_indicators': [],
            'qualitative_indicators': [],
            'implementation_maturity': 'basic',
            'automation_level': 'manual',
            'governance_strength': 'developing'
        }
        
        text_lower = answer_text.lower()
        
        # Quantitative indicators
        number_patterns = [
            (r'(\d+)%', 'percentage_metric'),
            (r'(\d+)\s*(?:times?|instances?)', 'frequency_metric'),
            (r'(\d+)\s*(?:years?|months?)', 'timeline_metric'),
            (r'(\d+)\s*(?:employees?|users?)', 'scale_metric')
        ]
        
        for pattern, metric_type in number_patterns:
            matches = re.findall(pattern, text_lower)
            for match in matches:
                evidence_analysis['quantitative_indicators'].append({
                    'type': metric_type,
                    'value': int(match),
                    'context': 'extracted_from_response'
                })
        
        # Qualitative indicators
        quality_indicators = {
            'implementation': ['implemented', 'deployed', 'configured', 'established'],
            'documentation': ['documented', 'written', 'formal', 'policy'],
            'monitoring': ['monitored', 'tracked', 'measured', 'dashboard'],
            'training': ['trained', 'certified', 'educated', 'awareness'],
            'automation': ['automated', 'scripted', 'tool', 'system'],
            'review': ['reviewed', 'audited', 'assessed', 'evaluated']
        }
        
        for category, keywords in quality_indicators.items():
            found_keywords = [kw for kw in keywords if kw in text_lower]
            if found_keywords:
                evidence_analysis['qualitative_indicators'].append({
                    'category': category,
                    'evidence': found_keywords,
                    'strength': len(found_keywords) / len(keywords)
                })
        
        # Determine maturity levels
        maturity_keywords = {
            'ad-hoc': ['ad-hoc', 'informal', 'basic', 'manual'],
            'repeatable': ['process', 'procedure', 'standard', 'consistent'],
            'defined': ['documented', 'formal', 'established', 'policy'],
            'managed': ['monitored', 'measured', 'controlled', 'metrics'],
            'optimized': ['optimized', 'continuous', 'adaptive', 'best practice']
        }
        
        maturity_scores = {}
        for level, keywords in maturity_keywords.items():
            score = sum(1 for kw in keywords if kw in text_lower)
            if score > 0:
                maturity_scores[level] = score
        
        if maturity_scores:
            evidence_analysis['implementation_maturity'] = max(maturity_scores, key=maturity_scores.get)
        
        return evidence_analysis
    
    def _get_industry_benchmark(self, 
                               category_id: str,
                               company_profile: Dict[str, Any]) -> Dict[str, Any]:
        """Get industry-specific benchmarks for comparison"""
        
        industry = company_profile.get('industry', '').lower()
        company_size = company_profile.get('size', '').lower()
        
        # Industry benchmark data
        industry_benchmarks = {
            'financial services': {
                'access_management': {'average': 7.2, 'top_quartile': 8.5},
                'data_sensitivity': {'average': 8.0, 'top_quartile': 9.2},
                'incident_response': {'average': 6.8, 'top_quartile': 8.1}
            },
            'healthcare': {
                'data_sensitivity': {'average': 8.5, 'top_quartile': 9.4},
                'access_management': {'average': 7.0, 'top_quartile': 8.3},
                'security_awareness': {'average': 6.2, 'top_quartile': 7.8}
            },
            'technology': {
                'access_management': {'average': 8.2, 'top_quartile': 9.1},
                'incident_response': {'average': 7.8, 'top_quartile': 8.9},
                'business_strategy': {'average': 7.5, 'top_quartile': 8.7}
            }
        }
        
        # Size adjustments
        size_modifiers = {
            'startup': -0.5,
            'small': -0.3,
            'medium': 0.0,
            'large': 0.2,
            'enterprise': 0.4
        }
        
        benchmark = {
            'industry': industry,
            'category': category_id,
            'industry_average': 6.5,  # Default
            'top_quartile': 8.0,      # Default
            'peer_comparison': 'average'
        }
        
        if industry in industry_benchmarks and category_id in industry_benchmarks[industry]:
            category_data = industry_benchmarks[industry][category_id]
            benchmark['industry_average'] = category_data['average']
            benchmark['top_quartile'] = category_data['top_quartile']
            
            # Apply size modifier
            for size_key, modifier in size_modifiers.items():
                if size_key in company_size:
                    benchmark['industry_average'] += modifier
                    benchmark['top_quartile'] += modifier
                    break
        
        return benchmark
    
    def _assess_risk_impact(self, 
                           score: int,
                           category_id: str,
                           metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Assess risk impact based on score and context"""
        
        # Risk impact mapping
        risk_levels = {
            (1, 3): {'level': 'critical', 'description': 'Immediate action required'},
            (4, 5): {'level': 'high', 'description': 'Significant improvements needed'},
            (6, 7): {'level': 'medium', 'description': 'Moderate improvements recommended'},
            (8, 9): {'level': 'low', 'description': 'Minor enhancements suggested'},
            (10, 10): {'level': 'minimal', 'description': 'Excellent implementation'}
        }
        
        risk_impact = {'level': 'medium', 'description': 'Assessment needed'}
        
        for score_range, impact_data in risk_levels.items():
            if score_range[0] <= score <= score_range[1]:
                risk_impact = impact_data
                break
        
        # Category-specific risk multipliers
        critical_categories = ['access_management', 'data_sensitivity', 'incident_response']
        if category_id in critical_categories and score <= 5:
            if risk_impact['level'] == 'high':
                risk_impact['level'] = 'critical'
            elif risk_impact['level'] == 'medium':
                risk_impact['level'] = 'high'
        
        # Add business impact assessment
        business_impact = self._calculate_business_impact(score, category_id, metadata)
        risk_impact['business_impact'] = business_impact
        
        return risk_impact
    
    def _calculate_business_impact(self, 
                                  score: int,
                                  category_id: str,
                                  metadata: Dict[str, Any]) -> Dict[str, Any]:
        """Calculate potential business impact"""
        
        company_profile = metadata.get('company_profile', {})
        industry = company_profile.get('industry', '').lower()
        
        impact_factors = {
            'data_sensitivity': {
                'financial_loss': 'High - data breaches can result in significant fines',
                'reputation_damage': 'Critical - customer trust is paramount',
                'regulatory_impact': 'High - compliance violations likely'
            },
            'access_management': {
                'financial_loss': 'Medium to High - unauthorized access can lead to theft',
                'reputation_damage': 'High - security incidents damage credibility',
                'regulatory_impact': 'Medium - depends on industry regulations'
            }
        }
        
        base_impact = impact_factors.get(category_id, {
            'financial_loss': 'Medium - operational disruption likely',
            'reputation_damage': 'Medium - depends on incident severity',
            'regulatory_impact': 'Low to Medium - varies by jurisdiction'
        })
        
        # Adjust based on score
        if score <= 3:
            severity_multiplier = 'Very High'
        elif score <= 5:
            severity_multiplier = 'High'
        elif score <= 7:
            severity_multiplier = 'Medium'
        else:
            severity_multiplier = 'Low'
        
        return {
            'severity': severity_multiplier,
            'potential_impacts': base_impact,
            'timeline_to_impact': '3-6 months' if score <= 5 else '6-12 months'
        }
    
    def _generate_long_term_recommendations(self, score: int, category_id: str) -> List[str]:
        """Generate long-term strategic recommendations"""
        
        recommendations = []
        
        if score <= 4:
            recommendations.extend([
                'Develop comprehensive strategy for foundational improvements',
                'Allocate dedicated resources and budget for security enhancement',
                'Consider bringing in external expertise for rapid improvement'
            ])
        elif score <= 6:
            recommendations.extend([
                'Implement systematic approach to process improvement',
                'Establish metrics and KPIs for continuous monitoring',
                'Plan for gradual automation of manual processes'
            ])
        elif score <= 8:
            recommendations.extend([
                'Focus on optimization and advanced capabilities',
                'Implement predictive and adaptive security measures',
                'Share best practices across organization'
            ])
        
        # Category-specific long-term recommendations
        category_specific = {
            'data_sensitivity': [
                'Implement data governance program',
                'Deploy advanced data classification tools',
                'Establish data privacy center of excellence'
            ],
            'access_management': [
                'Move toward zero-trust architecture',
                'Implement AI-driven access analytics',
                'Establish identity governance program'
            ],
            'incident_response': [
                'Develop threat hunting capabilities',
                'Implement security orchestration platform',
                'Establish threat intelligence program'
            ]
        }
        
        if category_id in category_specific:
            recommendations.extend(category_specific[category_id])
        
        return recommendations[:5]  # Limit to top 5
    
    def _get_industry_best_practices(self, 
                                   category_id: str,
                                   company_profile: Dict[str, Any]) -> List[str]:
        """Get industry-specific best practices"""
        
        industry = company_profile.get('industry', '').lower()
        
        best_practices = {
            'financial services': {
                'access_management': [
                    'Implement privileged access management (PAM)',
                    'Deploy multi-factor authentication for all accounts',
                    'Establish just-in-time access controls'
                ],
                'data_sensitivity': [
                    'Implement data loss prevention (DLP)',
                    'Deploy database activity monitoring',
                    'Establish data retention policies'
                ]
            },
            'healthcare': {
                'data_sensitivity': [
                    'Implement HIPAA-compliant encryption',
                    'Deploy audit logging for all PHI access',
                    'Establish data minimization practices'
                ],
                'access_management': [
                    'Implement role-based access controls',
                    'Deploy break-glass access procedures',
                    'Establish patient data access logging'
                ]
            }
        }
        
        if industry in best_practices and category_id in best_practices[industry]:
            return best_practices[industry][category_id]
        
        # Generic best practices
        generic_practices = {
            'access_management': [
                'Implement principle of least privilege',
                'Deploy regular access reviews',
                'Establish strong authentication methods'
            ],
            'data_sensitivity': [
                'Classify data based on sensitivity',
                'Implement appropriate encryption',
                'Establish data governance framework'
            ],
            'incident_response': [
                'Develop comprehensive response plans',
                'Conduct regular tabletop exercises',
                'Establish communication protocols'
            ]
        }
        
        return generic_practices.get(category_id, [
            'Follow industry-standard frameworks',
            'Implement continuous improvement processes',
            'Establish regular assessment cycles'
        ])
    
    def _calculate_specificity_score(self, text: str) -> float:
        """Calculate how specific and detailed the response is"""
        
        specificity_indicators = [
            'implemented', 'configured', 'deployed', 'established',
            'monitoring', 'automated', 'documented', 'tested',
            'version', 'tool', 'system', 'process', 'procedure'
        ]
        
        text_lower = text.lower()
        specificity_count = sum(1 for indicator in specificity_indicators if indicator in text_lower)
        
        # Normalize by text length and indicator count
        max_possible = min(len(specificity_indicators), len(text.split()) // 5)
        if max_possible == 0:
            return 0.0
        
        return min(1.0, specificity_count / max_possible)

# Global instance
objective_scorer = ObjectiveScorer()