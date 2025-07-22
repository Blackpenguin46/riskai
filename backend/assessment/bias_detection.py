#!/usr/bin/env python3
"""
AI Bias Detection and Mitigation System
Implements comprehensive bias detection and fairness monitoring for LLM recommendations
"""

import logging
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
from enum import Enum
import re
import json
from datetime import datetime
import statistics
from collections import Counter

logger = logging.getLogger(__name__)

class BiasType(Enum):
    DEMOGRAPHIC = "demographic"
    INDUSTRY = "industry"
    COMPANY_SIZE = "company_size"
    GEOGRAPHIC = "geographic"
    LANGUAGE = "language"
    CULTURAL = "cultural"
    TECHNICAL = "technical"
    TEMPORAL = "temporal"

class SeverityLevel(Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

@dataclass
class BiasDetection:
    """Individual bias detection result"""
    bias_type: BiasType
    severity: SeverityLevel
    confidence: float
    description: str
    evidence: List[str]
    affected_groups: List[str]
    mitigation_suggestions: List[str]

@dataclass
class FairnessMetrics:
    """Fairness metrics for recommendations"""
    demographic_parity: float
    equalized_odds: float
    calibration: float
    individual_fairness: float
    group_fairness: float
    overall_fairness_score: float

@dataclass
class BiasAnalysisResult:
    """Complete bias analysis result"""
    recommendation_id: str
    overall_bias_score: float
    detected_biases: List[BiasDetection]
    fairness_metrics: FairnessMetrics
    transparency_score: float
    mitigation_actions: List[Dict[str, Any]]
    review_required: bool
    timestamp: datetime

class BiasDetector:
    """Main class for detecting and mitigating AI bias"""
    
    def __init__(self):
        self.bias_patterns = self._load_bias_patterns()
        self.fairness_thresholds = self._load_fairness_thresholds()
        self.demographic_terms = self._load_demographic_terms()
        
    def _load_bias_patterns(self) -> Dict[BiasType, List[Dict[str, Any]]]:
        """Load patterns that indicate potential bias"""
        return {
            BiasType.DEMOGRAPHIC: [
                {
                    "pattern": r"\b(men|women|male|female|gender|age|elderly|young|senior)\b",
                    "severity": SeverityLevel.HIGH,
                    "description": "Gender or age-based assumptions"
                },
                {
                    "pattern": r"\b(race|ethnicity|nationality|religion|culture)\b",
                    "severity": SeverityLevel.CRITICAL,
                    "description": "Race, ethnicity, or religious bias"
                }
            ],
            BiasType.INDUSTRY: [
                {
                    "pattern": r"\b(startup|enterprise|small business|corporation)\b.*\b(should|must|always|never)\b",
                    "severity": SeverityLevel.MEDIUM,
                    "description": "Industry size assumptions"
                },
                {
                    "pattern": r"\b(healthcare|finance|tech|government)\b.*\b(typically|usually|generally)\b",
                    "severity": SeverityLevel.MEDIUM,
                    "description": "Industry-specific generalizations"
                }
            ],
            BiasType.COMPANY_SIZE: [
                {
                    "pattern": r"\b(small companies|large organizations|enterprises)\b.*\b(cannot|unable|lack)\b",
                    "severity": SeverityLevel.MEDIUM,
                    "description": "Company size capability assumptions"
                }
            ],
            BiasType.GEOGRAPHIC: [
                {
                    "pattern": r"\b(developing countries|third world|western|eastern)\b",
                    "severity": SeverityLevel.HIGH,
                    "description": "Geographic or economic development bias"
                }
            ],
            BiasType.LANGUAGE: [
                {
                    "pattern": r"\b(native speakers|non-native|foreign|accent)\b",
                    "severity": SeverityLevel.MEDIUM,
                    "description": "Language proficiency assumptions"
                }
            ],
            BiasType.TECHNICAL: [
                {
                    "pattern": r"\b(technical users|non-technical|IT savvy|computer literate)\b",
                    "severity": SeverityLevel.MEDIUM,
                    "description": "Technical skill assumptions"
                }
            ]
        }
    
    def _load_fairness_thresholds(self) -> Dict[str, float]:
        """Load thresholds for fairness metrics"""
        return {
            "demographic_parity": 0.8,
            "equalized_odds": 0.8,
            "calibration": 0.9,
            "individual_fairness": 0.85,
            "group_fairness": 0.8,
            "overall_fairness": 0.8
        }
    
    def _load_demographic_terms(self) -> Dict[str, List[str]]:
        """Load demographic terms for analysis"""
        return {
            "gender": ["male", "female", "man", "woman", "men", "women", "gender"],
            "age": ["young", "old", "elderly", "senior", "youth", "age", "aged"],
            "race": ["race", "racial", "ethnicity", "ethnic", "nationality"],
            "religion": ["religion", "religious", "faith", "belief", "spiritual"],
            "disability": ["disability", "disabled", "impaired", "handicapped"],
            "socioeconomic": ["poor", "rich", "wealthy", "income", "class", "status"]
        }
    
    def analyze_bias(self, recommendation_text: str, 
                    context: Optional[Dict[str, Any]] = None,
                    historical_data: Optional[List[Dict[str, Any]]] = None) -> BiasAnalysisResult:
        """
        Comprehensive bias analysis of a recommendation
        
        Args:
            recommendation_text: The recommendation to analyze
            context: Optional context about the assessment
            historical_data: Optional historical recommendation data for comparison
            
        Returns:
            BiasAnalysisResult with detected biases and mitigation suggestions
        """
        recommendation_id = f"bias_{datetime.now().strftime('%Y%m%d_%H%M%S')}"
        
        # Detect individual biases
        detected_biases = self._detect_biases(recommendation_text, context)
        
        # Calculate fairness metrics
        fairness_metrics = self._calculate_fairness_metrics(
            recommendation_text, context, historical_data
        )
        
        # Calculate overall bias score
        overall_bias_score = self._calculate_overall_bias_score(detected_biases, fairness_metrics)
        
        # Calculate transparency score
        transparency_score = self._calculate_transparency_score(recommendation_text)
        
        # Generate mitigation actions
        mitigation_actions = self._generate_mitigation_actions(detected_biases, fairness_metrics)
        
        # Determine if review is required
        review_required = self._requires_review(overall_bias_score, detected_biases)
        
        return BiasAnalysisResult(
            recommendation_id=recommendation_id,
            overall_bias_score=overall_bias_score,
            detected_biases=detected_biases,
            fairness_metrics=fairness_metrics,
            transparency_score=transparency_score,
            mitigation_actions=mitigation_actions,
            review_required=review_required,
            timestamp=datetime.utcnow()
        )
    
    def _detect_biases(self, text: str, context: Optional[Dict[str, Any]] = None) -> List[BiasDetection]:
        """Detect specific types of bias in the text"""
        detected_biases = []
        text_lower = text.lower()
        
        for bias_type, patterns in self.bias_patterns.items():
            for pattern_info in patterns:
                matches = re.findall(pattern_info["pattern"], text_lower, re.IGNORECASE)
                
                if matches:
                    # Calculate confidence based on number of matches and context
                    confidence = min(0.9, len(matches) * 0.3 + 0.4)
                    
                    # Identify affected groups
                    affected_groups = self._identify_affected_groups(matches, bias_type)
                    
                    # Generate evidence
                    evidence = [f"Pattern match: '{match}'" for match in matches[:3]]
                    
                    # Generate mitigation suggestions
                    mitigation_suggestions = self._generate_bias_mitigation(bias_type, matches)
                    
                    bias_detection = BiasDetection(
                        bias_type=bias_type,
                        severity=pattern_info["severity"],
                        confidence=confidence,
                        description=pattern_info["description"],
                        evidence=evidence,
                        affected_groups=affected_groups,
                        mitigation_suggestions=mitigation_suggestions
                    )
                    
                    detected_biases.append(bias_detection)
        
        # Additional contextual bias detection
        if context:
            contextual_biases = self._detect_contextual_biases(text, context)
            detected_biases.extend(contextual_biases)
        
        return detected_biases
    
    def _identify_affected_groups(self, matches: List[str], bias_type: BiasType) -> List[str]:
        """Identify groups that might be affected by the bias"""
        affected_groups = []
        
        if bias_type == BiasType.DEMOGRAPHIC:
            for match in matches:
                for category, terms in self.demographic_terms.items():
                    if any(term in match.lower() for term in terms):
                        affected_groups.append(category)
        
        elif bias_type == BiasType.INDUSTRY:
            affected_groups = ["industry-specific groups"]
        
        elif bias_type == BiasType.COMPANY_SIZE:
            affected_groups = ["small businesses", "large enterprises"]
        
        elif bias_type == BiasType.GEOGRAPHIC:
            affected_groups = ["geographic regions", "developing nations"]
        
        return list(set(affected_groups))
    
    def _generate_bias_mitigation(self, bias_type: BiasType, matches: List[str]) -> List[str]:
        """Generate specific mitigation suggestions for detected bias"""
        suggestions = []
        
        if bias_type == BiasType.DEMOGRAPHIC:
            suggestions.extend([
                "Use inclusive language that doesn't assume demographic characteristics",
                "Focus on role-based or skill-based recommendations rather than personal attributes",
                "Consider diverse perspectives when making recommendations"
            ])
        
        elif bias_type == BiasType.INDUSTRY:
            suggestions.extend([
                "Provide industry-agnostic alternatives where possible",
                "Acknowledge industry-specific variations in recommendations",
                "Avoid overgeneralization about industry capabilities"
            ])
        
        elif bias_type == BiasType.COMPANY_SIZE:
            suggestions.extend([
                "Provide scalable recommendations suitable for different organization sizes",
                "Acknowledge resource constraints without making assumptions",
                "Offer alternative approaches for different organizational contexts"
            ])
        
        elif bias_type == BiasType.TECHNICAL:
            suggestions.extend([
                "Provide explanations for technical concepts",
                "Offer both technical and non-technical implementation approaches",
                "Avoid assumptions about technical expertise levels"
            ])
        
        return suggestions
    
    def _detect_contextual_biases(self, text: str, context: Dict[str, Any]) -> List[BiasDetection]:
        """Detect biases based on assessment context"""
        contextual_biases = []
        
        # Check for industry bias
        if "industry" in context:
            industry = context["industry"]
            industry_assumptions = self._check_industry_assumptions(text, industry)
            if industry_assumptions:
                contextual_biases.append(industry_assumptions)
        
        # Check for company size bias
        if "company_size" in context:
            size_bias = self._check_company_size_bias(text, context["company_size"])
            if size_bias:
                contextual_biases.append(size_bias)
        
        return contextual_biases
    
    def _check_industry_assumptions(self, text: str, industry: str) -> Optional[BiasDetection]:
        """Check for industry-specific assumptions"""
        # Industry-specific assumption patterns
        assumption_patterns = {
            "healthcare": ["HIPAA compliance", "patient data", "medical records"],
            "finance": ["PCI compliance", "financial data", "banking regulations"],
            "technology": ["agile development", "DevOps", "cloud-native"]
        }
        
        if industry in assumption_patterns:
            assumptions = assumption_patterns[industry]
            found_assumptions = [term for term in assumptions if term.lower() in text.lower()]
            
            if found_assumptions:
                return BiasDetection(
                    bias_type=BiasType.INDUSTRY,
                    severity=SeverityLevel.MEDIUM,
                    confidence=0.7,
                    description=f"Industry-specific assumptions for {industry}",
                    evidence=[f"Assumption: {assumption}" for assumption in found_assumptions],
                    affected_groups=[f"{industry} industry"],
                    mitigation_suggestions=[
                        "Provide general security principles alongside industry-specific guidance",
                        "Acknowledge that recommendations may vary by industry context"
                    ]
                )
        
        return None
    
    def _check_company_size_bias(self, text: str, company_size: str) -> Optional[BiasDetection]:
        """Check for company size bias"""
        size_assumptions = {
            "small": ["limited resources", "cannot afford", "lack expertise"],
            "large": ["enterprise-grade", "complex infrastructure", "dedicated teams"]
        }
        
        for size, assumptions in size_assumptions.items():
            if size != company_size.lower():
                found_assumptions = [term for term in assumptions if term.lower() in text.lower()]
                
                if found_assumptions:
                    return BiasDetection(
                        bias_type=BiasType.COMPANY_SIZE,
                        severity=SeverityLevel.MEDIUM,
                        confidence=0.6,
                        description=f"Company size assumptions for {size} companies",
                        evidence=[f"Assumption: {assumption}" for assumption in found_assumptions],
                        affected_groups=[f"{size} companies"],
                        mitigation_suggestions=[
                            "Provide scalable recommendations for different organization sizes",
                            "Avoid assumptions about organizational capabilities based on size"
                        ]
                    )
        
        return None
    
    def _calculate_fairness_metrics(self, text: str, context: Optional[Dict[str, Any]] = None,
                                  historical_data: Optional[List[Dict[str, Any]]] = None) -> FairnessMetrics:
        """Calculate fairness metrics for the recommendation"""
        
        # Demographic parity: equal recommendation rates across groups
        demographic_parity = self._calculate_demographic_parity(text, historical_data)
        
        # Equalized odds: equal true positive rates across groups
        equalized_odds = self._calculate_equalized_odds(text, historical_data)
        
        # Calibration: equal prediction accuracy across groups
        calibration = self._calculate_calibration(text, historical_data)
        
        # Individual fairness: similar individuals get similar recommendations
        individual_fairness = self._calculate_individual_fairness(text, context)
        
        # Group fairness: fair treatment of different groups
        group_fairness = self._calculate_group_fairness(text, context)
        
        # Overall fairness score
        overall_fairness_score = statistics.mean([
            demographic_parity, equalized_odds, calibration,
            individual_fairness, group_fairness
        ])
        
        return FairnessMetrics(
            demographic_parity=demographic_parity,
            equalized_odds=equalized_odds,
            calibration=calibration,
            individual_fairness=individual_fairness,
            group_fairness=group_fairness,
            overall_fairness_score=overall_fairness_score
        )
    
    def _calculate_demographic_parity(self, text: str, 
                                    historical_data: Optional[List[Dict[str, Any]]] = None) -> float:
        """Calculate demographic parity score"""
        # Simplified calculation - in practice would use historical data
        demographic_terms_found = 0
        total_demographic_terms = sum(len(terms) for terms in self.demographic_terms.values())
        
        for terms in self.demographic_terms.values():
            for term in terms:
                if term.lower() in text.lower():
                    demographic_terms_found += 1
        
        # Higher score means less demographic bias
        return max(0.0, 1.0 - (demographic_terms_found / max(total_demographic_terms, 1)))
    
    def _calculate_equalized_odds(self, text: str,
                                historical_data: Optional[List[Dict[str, Any]]] = None) -> float:
        """Calculate equalized odds score"""
        # Simplified calculation - would use actual prediction outcomes in practice
        bias_indicators = ["always", "never", "all", "none", "every", "no one"]
        found_indicators = sum(1 for indicator in bias_indicators if indicator in text.lower())
        
        return max(0.0, 1.0 - (found_indicators / len(bias_indicators)))
    
    def _calculate_calibration(self, text: str,
                             historical_data: Optional[List[Dict[str, Any]]] = None) -> float:
        """Calculate calibration score"""
        # Check for confidence expressions that might indicate miscalibration
        confidence_terms = ["definitely", "certainly", "absolutely", "guaranteed", "impossible"]
        found_terms = sum(1 for term in confidence_terms if term in text.lower())
        
        return max(0.0, 1.0 - (found_terms / len(confidence_terms)))
    
    def _calculate_individual_fairness(self, text: str, context: Optional[Dict[str, Any]] = None) -> float:
        """Calculate individual fairness score"""
        # Check for personalization vs. generalization
        personal_terms = ["you", "your", "specific", "particular", "individual"]
        general_terms = ["everyone", "all organizations", "companies", "users"]
        
        personal_count = sum(1 for term in personal_terms if term in text.lower())
        general_count = sum(1 for term in general_terms if term in text.lower())
        
        # Balance between personalization and generalization
        if personal_count + general_count == 0:
            return 0.8  # Neutral
        
        balance = abs(personal_count - general_count) / (personal_count + general_count)
        return max(0.0, 1.0 - balance)
    
    def _calculate_group_fairness(self, text: str, context: Optional[Dict[str, Any]] = None) -> float:
        """Calculate group fairness score"""
        # Check for group-specific recommendations
        group_terms = ["type of organization", "industry", "sector", "category"]
        exclusionary_terms = ["only", "exclusively", "just", "merely"]
        
        group_count = sum(1 for term in group_terms if term in text.lower())
        exclusionary_count = sum(1 for term in exclusionary_terms if term in text.lower())
        
        # Penalize exclusionary language
        fairness_score = 0.9 - (exclusionary_count * 0.2)
        
        # Reward inclusive group considerations
        if group_count > 0:
            fairness_score += 0.1
        
        return max(0.0, min(1.0, fairness_score))
    
    def _calculate_overall_bias_score(self, detected_biases: List[BiasDetection],
                                    fairness_metrics: FairnessMetrics) -> float:
        """Calculate overall bias score (0 = no bias, 1 = high bias)"""
        if not detected_biases:
            bias_component = 0.0
        else:
            # Weight biases by severity
            severity_weights = {
                SeverityLevel.LOW: 0.1,
                SeverityLevel.MEDIUM: 0.3,
                SeverityLevel.HIGH: 0.6,
                SeverityLevel.CRITICAL: 1.0
            }
            
            weighted_bias = sum(
                severity_weights[bias.severity] * bias.confidence
                for bias in detected_biases
            ) / len(detected_biases)
            
            bias_component = min(1.0, weighted_bias)
        
        # Combine with fairness metrics (inverted since lower fairness = higher bias)
        fairness_component = 1.0 - fairness_metrics.overall_fairness_score
        
        # Weighted combination
        overall_bias = (bias_component * 0.6) + (fairness_component * 0.4)
        
        return min(1.0, overall_bias)
    
    def _calculate_transparency_score(self, text: str) -> float:
        """Calculate transparency score for the recommendation"""
        transparency_indicators = [
            "because", "due to", "based on", "according to", "research shows",
            "studies indicate", "evidence suggests", "framework recommends"
        ]
        
        found_indicators = sum(1 for indicator in transparency_indicators 
                             if indicator in text.lower())
        
        # Normalize to 0-1 scale
        transparency_score = min(1.0, found_indicators / 3.0)  # 3 indicators = full transparency
        
        return transparency_score
    
    def _generate_mitigation_actions(self, detected_biases: List[BiasDetection],
                                   fairness_metrics: FairnessMetrics) -> List[Dict[str, Any]]:
        """Generate specific mitigation actions"""
        actions = []
        
        # Actions for detected biases
        for bias in detected_biases:
            for suggestion in bias.mitigation_suggestions:
                actions.append({
                    "type": "bias_mitigation",
                    "bias_type": bias.bias_type.value,
                    "action": suggestion,
                    "priority": bias.severity.value,
                    "impact_score": bias.confidence
                })
        
        # Actions for fairness improvements
        if fairness_metrics.demographic_parity < self.fairness_thresholds["demographic_parity"]:
            actions.append({
                "type": "fairness_improvement",
                "metric": "demographic_parity",
                "action": "Review recommendation for demographic assumptions",
                "priority": "medium",
                "impact_score": 0.7
            })
        
        if fairness_metrics.individual_fairness < self.fairness_thresholds["individual_fairness"]:
            actions.append({
                "type": "fairness_improvement",
                "metric": "individual_fairness",
                "action": "Balance personalization with general applicability",
                "priority": "medium",
                "impact_score": 0.6
            })
        
        # Sort by priority and impact
        priority_order = {"critical": 4, "high": 3, "medium": 2, "low": 1}
        actions.sort(key=lambda x: (priority_order.get(x["priority"], 0), x["impact_score"]), reverse=True)
        
        return actions
    
    def _requires_review(self, overall_bias_score: float, detected_biases: List[BiasDetection]) -> bool:
        """Determine if human review is required"""
        # Review required if overall bias is high
        if overall_bias_score > 0.7:
            return True
        
        # Review required if any critical biases detected
        if any(bias.severity == SeverityLevel.CRITICAL for bias in detected_biases):
            return True
        
        # Review required if multiple high-severity biases
        high_severity_count = sum(1 for bias in detected_biases 
                                if bias.severity == SeverityLevel.HIGH)
        if high_severity_count >= 2:
            return True
        
        return False

# Global instance
bias_detector = BiasDetector()