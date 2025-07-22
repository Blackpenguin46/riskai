#!/usr/bin/env python3
"""
Dynamic Scoring Engine

Implements proper dynamic scoring based on actual answer types:
- Multiple choice with defined scores
- Scale questions with quantitative ranges
- Boolean questions with clear values
- Mixed qualitative/quantitative inputs
- Industry-specific adjustments
"""

import logging
import re
from typing import Dict, List, Optional, Any, Union
from dataclasses import dataclass
from enum import Enum
import statistics

logger = logging.getLogger(__name__)

class QuestionType(Enum):
    MULTIPLE_CHOICE = "multiple_choice"
    SCALE = "scale"
    BOOLEAN = "boolean"
    PERCENTAGE = "percentage"
    FREQUENCY = "frequency"
    TEXT = "text"

class MaturityLevel(Enum):
    INITIAL = (1, "No formal processes")
    BASIC = (2, "Basic processes in place")
    DEFINED = (3, "Defined and documented processes")
    MANAGED = (4, "Managed and measured processes")
    OPTIMIZED = (5, "Continuously improving processes")

@dataclass
class ScoringResult:
    raw_score: float
    normalized_score: float  # 0-100
    confidence: float
    evidence_strength: str
    maturity_level: MaturityLevel
    quantitative_support: Optional[float]
    adjustment_reason: str
    recommendations: List[str]

@dataclass
class QuestionDefinition:
    id: str
    text: str
    type: QuestionType
    category: str
    weight: float
    scoring_config: Dict[str, Any]
    quantitative_benchmarks: Optional[Dict[str, float]] = None

class DynamicScoringEngine:
    """Advanced scoring engine with proper dynamic scoring"""
    
    def __init__(self):
        self.industry_benchmarks = self._load_industry_benchmarks()
        self.question_definitions = self._initialize_question_definitions()
        self.maturity_indicators = self._load_maturity_indicators()
        
    def score_assessment(self, answers: Dict[str, Any], company_profile: Dict[str, Any]) -> Dict[str, Any]:
        """Score complete assessment with dynamic scoring"""
        
        section_scores = {}
        total_weighted_score = 0.0
        total_weight = 0.0
        
        # Group answers by section
        answer_groups = self._group_answers_by_section(answers)
        
        for section_id, section_answers in answer_groups.items():
            section_result = self._score_section(section_id, section_answers, company_profile)
            section_scores[section_id] = section_result
            
            # Add to weighted total
            section_weight = section_result.get('weight', 0.1)
            total_weighted_score += section_result['score'] * section_weight
            total_weight += section_weight
        
        # Calculate overall score
        overall_score = total_weighted_score / total_weight if total_weight > 0 else 0
        
        # Generate insights and recommendations
        insights = self._generate_insights(section_scores, company_profile)
        recommendations = self._generate_recommendations(section_scores, company_profile)
        
        return {
            'overall_score': round(overall_score, 2),
            'section_scores': section_scores,
            'insights': insights,
            'recommendations': recommendations,
            'confidence_metrics': self._calculate_confidence_metrics(section_scores)
        }
    
    def score_question(self, question_id: str, answer: Any, company_profile: Dict[str, Any]) -> ScoringResult:
        """Score individual question with dynamic logic"""
        
        question_def = self.question_definitions.get(question_id)
        if not question_def:
            return self._fallback_scoring(answer)
        
        # Base scoring by question type
        if question_def.type == QuestionType.MULTIPLE_CHOICE:
            result = self._score_multiple_choice(question_def, answer)
        elif question_def.type == QuestionType.SCALE:
            result = self._score_scale_question(question_def, answer)
        elif question_def.type == QuestionType.BOOLEAN:
            result = self._score_boolean_question(question_def, answer)
        elif question_def.type == QuestionType.PERCENTAGE:
            result = self._score_percentage_question(question_def, answer)
        elif question_def.type == QuestionType.FREQUENCY:
            result = self._score_frequency_question(question_def, answer)
        else:
            result = self._score_text_question(question_def, answer)
        
        # Apply industry adjustments
        result = self._apply_industry_adjustments(result, question_def, company_profile)
        
        # Add quantitative support
        result = self._add_quantitative_support(result, question_def, company_profile)
        
        return result
    
    def _score_multiple_choice(self, question_def: QuestionDefinition, answer: str) -> ScoringResult:
        """Score multiple choice question"""
        
        scoring_config = question_def.scoring_config
        options = scoring_config.get('options', [])
        
        # Find selected option
        selected_option = None
        for option in options:
            if option['value'] == answer:
                selected_option = option
                break
        
        if not selected_option:
            return ScoringResult(
                raw_score=1.0,
                normalized_score=20.0,
                confidence=0.3,
                evidence_strength="weak",
                maturity_level=MaturityLevel.INITIAL,
                quantitative_support=None,
                adjustment_reason="Unknown option selected",
                recommendations=["Please review and provide a valid response"]
            )
        
        raw_score = selected_option.get('score', 1)
        max_score = max(opt.get('score', 1) for opt in options)
        normalized_score = (raw_score / max_score) * 100
        
        # Determine maturity level
        maturity_level = self._determine_maturity_level(normalized_score)
        
        # Generate recommendations
        recommendations = []
        if normalized_score < 60:
            recommendations.append(f"Consider upgrading to higher maturity practices")
        
        return ScoringResult(
            raw_score=float(raw_score),
            normalized_score=normalized_score,
            confidence=0.9,
            evidence_strength="strong",
            maturity_level=maturity_level,
            quantitative_support=None,
            adjustment_reason="Direct multiple choice scoring",
            recommendations=recommendations
        )
    
    def _score_scale_question(self, question_def: QuestionDefinition, answer: Union[int, float, str]) -> ScoringResult:
        """Score scale question (1-5, 1-10, etc.)"""
        
        try:
            numeric_value = float(answer)
        except (ValueError, TypeError):
            return self._fallback_scoring(answer)
        
        scoring_config = question_def.scoring_config
        scale_min = scoring_config.get('min', 1)
        scale_max = scoring_config.get('max', 5)
        
        # Validate range
        if numeric_value < scale_min or numeric_value > scale_max:
            numeric_value = max(scale_min, min(scale_max, numeric_value))
        
        # Normalize to 0-100
        normalized_score = ((numeric_value - scale_min) / (scale_max - scale_min)) * 100
        
        # Determine evidence strength based on score
        if normalized_score >= 80:
            evidence_strength = "very_strong"
        elif normalized_score >= 60:
            evidence_strength = "strong"
        elif normalized_score >= 40:
            evidence_strength = "moderate"
        else:
            evidence_strength = "weak"
        
        maturity_level = self._determine_maturity_level(normalized_score)
        
        # Generate recommendations
        recommendations = []
        if normalized_score < 70:
            recommendations.append("Consider implementing additional controls to improve this area")
        
        return ScoringResult(
            raw_score=numeric_value,
            normalized_score=normalized_score,
            confidence=0.8,
            evidence_strength=evidence_strength,
            maturity_level=maturity_level,
            quantitative_support=numeric_value,
            adjustment_reason="Scale question scoring",
            recommendations=recommendations
        )
    
    def _score_boolean_question(self, question_def: QuestionDefinition, answer: Union[bool, str]) -> ScoringResult:
        """Score boolean question"""
        
        # Convert string answers to boolean
        if isinstance(answer, str):
            answer = answer.lower() in ['yes', 'true', '1', 'enabled', 'implemented']
        
        scoring_config = question_def.scoring_config
        true_score = scoring_config.get('true_score', 100)
        false_score = scoring_config.get('false_score', 0)
        
        raw_score = true_score if answer else false_score
        normalized_score = float(raw_score)
        
        evidence_strength = "strong" if answer else "weak"
        maturity_level = MaturityLevel.MANAGED if answer else MaturityLevel.INITIAL
        
        recommendations = []
        if not answer:
            recommendations.append("Implement this control to improve security posture")
        
        return ScoringResult(
            raw_score=raw_score,
            normalized_score=normalized_score,
            confidence=0.95,
            evidence_strength=evidence_strength,
            maturity_level=maturity_level,
            quantitative_support=1.0 if answer else 0.0,
            adjustment_reason="Boolean question scoring",
            recommendations=recommendations
        )
    
    def _score_percentage_question(self, question_def: QuestionDefinition, answer: Union[int, float, str]) -> ScoringResult:
        """Score percentage-based question"""
        
        try:
            # Extract percentage from string if needed
            if isinstance(answer, str):
                # Look for percentage in string
                percentage_match = re.search(r'(\d+(?:\.\d+)?)%?', answer)
                if percentage_match:
                    numeric_value = float(percentage_match.group(1))
                else:
                    raise ValueError("No percentage found")
            else:
                numeric_value = float(answer)
        except (ValueError, TypeError):
            return self._fallback_scoring(answer)
        
        # Ensure percentage is in valid range
        numeric_value = max(0, min(100, numeric_value))
        
        # For percentage questions, the percentage directly maps to score
        normalized_score = numeric_value
        
        # Determine evidence strength
        if normalized_score >= 90:
            evidence_strength = "very_strong"
        elif normalized_score >= 75:
            evidence_strength = "strong"
        elif normalized_score >= 50:
            evidence_strength = "moderate"
        else:
            evidence_strength = "weak"
        
        maturity_level = self._determine_maturity_level(normalized_score)
        
        recommendations = []
        if normalized_score < 80:
            recommendations.append(f"Increase coverage to reach industry best practice of 90%+")
        
        return ScoringResult(
            raw_score=numeric_value,
            normalized_score=normalized_score,
            confidence=0.85,
            evidence_strength=evidence_strength,
            maturity_level=maturity_level,
            quantitative_support=numeric_value / 100,
            adjustment_reason="Percentage-based scoring",
            recommendations=recommendations
        )
    
    def _score_frequency_question(self, question_def: QuestionDefinition, answer: str) -> ScoringResult:
        """Score frequency-based question"""
        
        frequency_scores = {
            'never': 0,
            'rarely': 20,
            'sometimes': 40,
            'often': 60,
            'always': 80,
            'continuously': 100,
            'real-time': 100,
            'daily': 90,
            'weekly': 80,
            'monthly': 70,
            'quarterly': 60,
            'semi-annually': 50,
            'annually': 40,
            'ad-hoc': 30
        }
        
        answer_lower = answer.lower()
        normalized_score = 20  # Default low score
        
        # Find best match
        for freq_term, score in frequency_scores.items():
            if freq_term in answer_lower:
                normalized_score = max(normalized_score, score)
        
        evidence_strength = "strong" if normalized_score >= 60 else "moderate" if normalized_score >= 40 else "weak"
        maturity_level = self._determine_maturity_level(normalized_score)
        
        recommendations = []
        if normalized_score < 60:
            recommendations.append("Increase frequency of this activity for better security posture")
        
        return ScoringResult(
            raw_score=normalized_score,
            normalized_score=normalized_score,
            confidence=0.75,
            evidence_strength=evidence_strength,
            maturity_level=maturity_level,
            quantitative_support=normalized_score / 100,
            adjustment_reason="Frequency-based scoring",
            recommendations=recommendations
        )
    
    def _score_text_question(self, question_def: QuestionDefinition, answer: str) -> ScoringResult:
        """Score open text question using advanced analysis"""
        
        if not answer or answer.lower() in ['no', 'none', 'n/a', 'not applicable']:
            return ScoringResult(
                raw_score=0.0,
                normalized_score=0.0,
                confidence=0.7,
                evidence_strength="weak",
                maturity_level=MaturityLevel.INITIAL,
                quantitative_support=None,
                adjustment_reason="No implementation indicated",
                recommendations=["Implement basic controls in this area"]
            )
        
        # Analyze text for security maturity indicators
        maturity_score = self._analyze_text_maturity(answer)
        evidence_strength = self._analyze_text_evidence_strength(answer)
        
        # Base score on text quality and content
        base_score = self._calculate_text_base_score(answer)
        
        # Apply maturity adjustments
        normalized_score = min(100, base_score + maturity_score)
        
        maturity_level = self._determine_maturity_level(normalized_score)
        
        recommendations = self._generate_text_recommendations(answer, normalized_score)
        
        return ScoringResult(
            raw_score=base_score,
            normalized_score=normalized_score,
            confidence=0.6,  # Lower confidence for text analysis
            evidence_strength=evidence_strength,
            maturity_level=maturity_level,
            quantitative_support=None,
            adjustment_reason="Text analysis with maturity indicators",
            recommendations=recommendations
        )
    
    def _analyze_text_maturity(self, text: str) -> float:
        """Analyze text for maturity indicators"""
        
        text_lower = text.lower()
        maturity_score = 0
        
        # Advanced maturity indicators
        advanced_indicators = [
            'automated', 'continuous', 'real-time', 'integrated', 'comprehensive',
            'enterprise-wide', 'standardized', 'measured', 'optimized', 'best practice'
        ]
        
        # Basic maturity indicators
        basic_indicators = [
            'documented', 'formal', 'policy', 'procedure', 'process',
            'regular', 'scheduled', 'monitored', 'reviewed'
        ]
        
        # Count indicators
        for indicator in advanced_indicators:
            if indicator in text_lower:
                maturity_score += 5
        
        for indicator in basic_indicators:
            if indicator in text_lower:
                maturity_score += 2
        
        return min(30, maturity_score)  # Cap at 30 points
    
    def _analyze_text_evidence_strength(self, text: str) -> str:
        """Analyze evidence strength in text"""
        
        word_count = len(text.split())
        text_lower = text.lower()
        
        # Strong evidence indicators
        strong_indicators = ['implemented', 'deployed', 'operational', 'measured', 'tested']
        moderate_indicators = ['planned', 'documented', 'defined', 'scheduled']
        weak_indicators = ['considering', 'evaluating', 'future', 'planned for']
        
        strong_count = sum(1 for indicator in strong_indicators if indicator in text_lower)
        moderate_count = sum(1 for indicator in moderate_indicators if indicator in text_lower)
        weak_count = sum(1 for indicator in weak_indicators if indicator in text_lower)
        
        if word_count >= 50 and strong_count >= 2:
            return "very_strong"
        elif word_count >= 30 and (strong_count >= 1 or moderate_count >= 2):
            return "strong"
        elif word_count >= 15 and (moderate_count >= 1 or weak_count >= 1):
            return "moderate"
        else:
            return "weak"
    
    def _calculate_text_base_score(self, text: str) -> float:
        """Calculate base score for text response"""
        
        word_count = len(text.split())
        
        # Base score on content quality
        if word_count < 5:
            return 10
        elif word_count < 15:
            return 25
        elif word_count < 30:
            return 40
        elif word_count < 50:
            return 55
        else:
            return 70
    
    def _determine_maturity_level(self, score: float) -> MaturityLevel:
        """Determine maturity level from score"""
        
        if score >= 90:
            return MaturityLevel.OPTIMIZED
        elif score >= 75:
            return MaturityLevel.MANAGED
        elif score >= 60:
            return MaturityLevel.DEFINED
        elif score >= 40:
            return MaturityLevel.BASIC
        else:
            return MaturityLevel.INITIAL
    
    def _apply_industry_adjustments(self, result: ScoringResult, question_def: QuestionDefinition, 
                                  company_profile: Dict[str, Any]) -> ScoringResult:
        """Apply industry-specific scoring adjustments"""
        
        industry = company_profile.get('industry', '').lower()
        category = question_def.category
        
        # Industry-specific adjustments
        adjustment = 0
        adjustment_reason = result.adjustment_reason
        
        # High-regulation industries
        if industry in ['healthcare', 'finance', 'banking', 'government']:
            if category in ['governance', 'compliance', 'data_protection']:
                # Higher standards expected
                if result.normalized_score < 80:
                    adjustment = -5
                    adjustment_reason += " (High-regulation industry penalty)"
            elif category == 'incident_response':
                # Critical for regulated industries
                if result.normalized_score >= 80:
                    adjustment = +3
                    adjustment_reason += " (Regulated industry bonus)"
        
        # Technology companies
        elif industry in ['technology', 'software', 'saas']:
            if category in ['emerging_tech', 'innovation']:
                # Higher expectations for tech companies
                if result.normalized_score >= 70:
                    adjustment = +5
                    adjustment_reason += " (Tech industry bonus)"
        
        # Small companies
        company_size = company_profile.get('size', '').lower()
        if company_size in ['small', 'startup']:
            if category in ['governance', 'compliance']:
                # More lenient for small companies
                adjustment = +3
                adjustment_reason += " (Small company adjustment)"
        
        # Apply adjustment
        adjusted_score = max(0, min(100, result.normalized_score + adjustment))
        
        return ScoringResult(
            raw_score=result.raw_score,
            normalized_score=adjusted_score,
            confidence=result.confidence,
            evidence_strength=result.evidence_strength,
            maturity_level=self._determine_maturity_level(adjusted_score),
            quantitative_support=result.quantitative_support,
            adjustment_reason=adjustment_reason,
            recommendations=result.recommendations
        )
    
    def _add_quantitative_support(self, result: ScoringResult, question_def: QuestionDefinition,
                                company_profile: Dict[str, Any]) -> ScoringResult:
        """Add quantitative benchmarking support"""
        
        benchmarks = question_def.quantitative_benchmarks
        if not benchmarks:
            return result
        
        industry = company_profile.get('industry', 'general')
        company_size = company_profile.get('size', 'medium')
        
        # Get industry benchmark
        benchmark_key = f"{industry}_{company_size}"
        if benchmark_key not in benchmarks:
            benchmark_key = f"general_{company_size}"
        if benchmark_key not in benchmarks:
            benchmark_key = "general_medium"
        
        benchmark_score = benchmarks.get(benchmark_key, 50)
        
        # Add quantitative support
        quantitative_support = result.normalized_score / benchmark_score if benchmark_score > 0 else 1.0
        
        return ScoringResult(
            raw_score=result.raw_score,
            normalized_score=result.normalized_score,
            confidence=min(1.0, result.confidence + 0.1),  # Boost confidence with quantitative support
            evidence_strength=result.evidence_strength,
            maturity_level=result.maturity_level,
            quantitative_support=quantitative_support,
            adjustment_reason=result.adjustment_reason + f" (Benchmark: {benchmark_score})",
            recommendations=result.recommendations
        )
    
    def _fallback_scoring(self, answer: Any) -> ScoringResult:
        """Fallback scoring for unknown question types"""
        
        if not answer:
            score = 0
        elif isinstance(answer, str) and len(answer) > 20:
            score = min(60, 20 + len(answer) // 10)
        else:
            score = 30
        
        return ScoringResult(
            raw_score=score,
            normalized_score=score,
            confidence=0.4,
            evidence_strength="moderate",
            maturity_level=MaturityLevel.BASIC,
            quantitative_support=None,
            adjustment_reason="Fallback scoring method",
            recommendations=["Provide more specific information for better assessment"]
        )
    
    def _group_answers_by_section(self, answers: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
        """Group answers by section for scoring"""
        
        sections = {}
        
        for question_id, answer in answers.items():
            # Extract section from question ID (assumes format: section_number)
            section_id = question_id.split('_')[0] if '_' in question_id else 'general'
            
            if section_id not in sections:
                sections[section_id] = {}
            
            sections[section_id][question_id] = answer
        
        return sections
    
    def _score_section(self, section_id: str, answers: Dict[str, Any], 
                      company_profile: Dict[str, Any]) -> Dict[str, Any]:
        """Score a complete section"""
        
        question_scores = []
        total_confidence = 0
        evidence_strengths = []
        
        for question_id, answer in answers.items():
            result = self.score_question(question_id, answer, company_profile)
            question_scores.append(result.normalized_score)
            total_confidence += result.confidence
            evidence_strengths.append(result.evidence_strength)
        
        if not question_scores:
            return {
                'score': 0,
                'confidence': 0,
                'evidence_strength': 'weak',
                'maturity_level': 'initial',
                'weight': 0.1
            }
        
        # Calculate section metrics
        section_score = statistics.mean(question_scores)
        avg_confidence = total_confidence / len(question_scores)
        
        # Determine overall evidence strength
        if evidence_strengths.count('very_strong') >= len(evidence_strengths) // 2:
            overall_strength = 'very_strong'
        elif evidence_strengths.count('strong') >= len(evidence_strengths) // 2:
            overall_strength = 'strong'
        elif evidence_strengths.count('moderate') >= len(evidence_strengths) // 2:
            overall_strength = 'moderate'
        else:
            overall_strength = 'weak'
        
        return {
            'score': round(section_score, 2),
            'confidence': round(avg_confidence, 2),
            'evidence_strength': overall_strength,
            'maturity_level': self._determine_maturity_level(section_score).name.lower(),
            'questions_answered': len(answers),
            'weight': self._get_section_weight(section_id)
        }
    
    def _get_section_weight(self, section_id: str) -> float:
        """Get weight for section"""
        
        weights = {
            'governance': 0.20,
            'access': 0.12,
            'data': 0.12,
            'monitor': 0.10,
            'incident': 0.10,
            'business': 0.08,
            'asset': 0.08,
            'awareness': 0.06,
            'compliance': 0.04,
            'emerging': 0.04,
            'vendor': 0.04,
            'risk': 0.02
        }
        
        return weights.get(section_id, 0.05)
    
    def _generate_insights(self, section_scores: Dict[str, Any], 
                          company_profile: Dict[str, Any]) -> List[str]:
        """Generate insights from assessment results"""
        
        insights = []
        
        # Find strongest and weakest areas
        scores = [(section, data['score']) for section, data in section_scores.items()]
        scores.sort(key=lambda x: x[1])
        
        weakest = scores[:2]
        strongest = scores[-2:]
        
        insights.append(f"Strongest areas: {', '.join([s[0] for s in strongest])}")
        insights.append(f"Areas needing attention: {', '.join([s[0] for s in weakest])}")
        
        # Industry-specific insights
        industry = company_profile.get('industry', '')
        if industry.lower() in ['healthcare', 'finance']:
            insights.append("As a regulated industry, focus on compliance and governance improvements")
        
        return insights
    
    def _generate_recommendations(self, section_scores: Dict[str, Any],
                                company_profile: Dict[str, Any]) -> List[str]:
        """Generate prioritized recommendations"""
        
        recommendations = []
        
        # Sort sections by score (lowest first)
        sorted_sections = sorted(section_scores.items(), key=lambda x: x[1]['score'])
        
        for section_id, section_data in sorted_sections[:3]:  # Top 3 priorities
            score = section_data['score']
            
            if score < 40:
                recommendations.append(f"Critical: Implement basic {section_id} controls immediately")
            elif score < 60:
                recommendations.append(f"High priority: Improve {section_id} maturity")
            elif score < 80:
                recommendations.append(f"Medium priority: Enhance {section_id} capabilities")
        
        return recommendations
    
    def _calculate_confidence_metrics(self, section_scores: Dict[str, Any]) -> Dict[str, float]:
        """Calculate overall confidence metrics"""
        
        confidences = [section['confidence'] for section in section_scores.values()]
        
        return {
            'overall_confidence': statistics.mean(confidences) if confidences else 0,
            'confidence_std': statistics.stdev(confidences) if len(confidences) > 1 else 0,
            'min_confidence': min(confidences) if confidences else 0,
            'max_confidence': max(confidences) if confidences else 0
        }
    
    def _generate_text_recommendations(self, text: str, score: float) -> List[str]:
        """Generate recommendations based on text analysis"""
        
        recommendations = []
        
        if score < 40:
            recommendations.append("Implement formal processes and documentation")
        elif score < 60:
            recommendations.append("Enhance existing processes with automation")
        elif score < 80:
            recommendations.append("Add measurement and continuous improvement")
        
        return recommendations
    
    def _load_industry_benchmarks(self) -> Dict[str, Dict[str, float]]:
        """Load industry benchmark data"""
        
        # This would typically load from a database or file
        return {
            'healthcare': {'governance': 85, 'data_protection': 90, 'access_control': 80},
            'finance': {'governance': 90, 'compliance': 95, 'access_control': 85},
            'technology': {'emerging_tech': 85, 'innovation': 80, 'monitoring': 85},
            'general': {'governance': 70, 'access_control': 75, 'data_protection': 70}
        }
    
    def _initialize_question_definitions(self) -> Dict[str, QuestionDefinition]:
        """Initialize question definitions with scoring configs"""
        
        # This would typically load from configuration
        return {}
    
    def _load_maturity_indicators(self) -> Dict[str, List[str]]:
        """Load maturity indicators for text analysis"""
        
        return {
            'advanced': ['automated', 'continuous', 'real-time', 'ai-powered', 'machine learning'],
            'managed': ['measured', 'monitored', 'tracked', 'reported', 'dashboard'],
            'defined': ['documented', 'formal', 'standardized', 'procedure', 'policy'],
            'basic': ['implemented', 'deployed', 'operational', 'functional', 'working']
        }

# Global instance
dynamic_scoring_engine = DynamicScoringEngine()