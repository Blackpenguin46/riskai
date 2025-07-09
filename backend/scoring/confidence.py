"""
Confidence Scoring Module

Provides uncertainty quantification for risk scores using statistical methods
including Monte Carlo simulation and Bayesian inference.
"""

import logging
import numpy as np
from typing import Dict, List, Tuple, Any, Optional
from scipy import stats
from dataclasses import dataclass
from enum import Enum
import json

logger = logging.getLogger(__name__)

class ConfidenceLevel(Enum):
    """Confidence levels for interval estimation"""
    LOW = 0.68    # 1 sigma
    MEDIUM = 0.90 # 1.64 sigma
    HIGH = 0.95   # 1.96 sigma
    VERY_HIGH = 0.99  # 2.58 sigma

@dataclass
class ConfidenceScore:
    """Confidence score with uncertainty bounds"""
    point_estimate: float
    confidence_interval: Tuple[float, float]
    confidence_level: float
    uncertainty_source: str
    method: str
    
@dataclass
class UncertaintyAnalysis:
    """Detailed uncertainty analysis for risk assessment"""
    overall_uncertainty: float
    category_uncertainties: Dict[str, float]
    dominant_factors: List[str]
    recommendation: str

class ConfidenceScorer:
    """Main class for calculating confidence scores and uncertainty bounds"""
    
    def __init__(self):
        self.confidence_level = ConfidenceLevel.HIGH.value
        self.monte_carlo_samples = 1000
        self.min_confidence_threshold = 0.5
        
        # Uncertainty sources and their typical ranges
        self.uncertainty_sources = {
            'answer_quality': 0.15,      # 15% uncertainty from answer quality
            'scoring_method': 0.10,      # 10% uncertainty from scoring method
            'model_variance': 0.08,      # 8% uncertainty from model variance
            'data_completeness': 0.12,   # 12% uncertainty from incomplete data
            'expert_disagreement': 0.20  # 20% uncertainty from expert disagreement
        }
    
    def calculate_confidence_score(self, 
                                  risk_score: float,
                                  answer_quality: float,
                                  data_completeness: float,
                                  method: str = "monte_carlo") -> ConfidenceScore:
        """Calculate confidence score with uncertainty bounds"""
        
        try:
            if method == "monte_carlo":
                return self._monte_carlo_confidence(risk_score, answer_quality, data_completeness)
            elif method == "bayesian":
                return self._bayesian_confidence(risk_score, answer_quality, data_completeness)
            else:
                return self._analytical_confidence(risk_score, answer_quality, data_completeness)
                
        except Exception as e:
            logger.error(f"Error calculating confidence score: {str(e)}")
            # Return default confidence score
            return ConfidenceScore(
                point_estimate=risk_score,
                confidence_interval=(max(0, risk_score - 10), min(100, risk_score + 10)),
                confidence_level=self.confidence_level,
                uncertainty_source="error",
                method="default"
            )
    
    def _monte_carlo_confidence(self, 
                              risk_score: float,
                              answer_quality: float,
                              data_completeness: float) -> ConfidenceScore:
        """Use Monte Carlo simulation to estimate confidence bounds"""
        
        # Calculate total uncertainty
        total_uncertainty = self._calculate_total_uncertainty(answer_quality, data_completeness)
        
        # Generate samples using normal distribution
        samples = np.random.normal(
            loc=risk_score,
            scale=total_uncertainty * risk_score,  # Scale uncertainty with score
            size=self.monte_carlo_samples
        )
        
        # Clip samples to valid range [0, 100]
        samples = np.clip(samples, 0, 100)
        
        # Calculate confidence interval
        alpha = 1 - self.confidence_level
        lower_bound = np.percentile(samples, (alpha/2) * 100)
        upper_bound = np.percentile(samples, (1 - alpha/2) * 100)
        
        return ConfidenceScore(
            point_estimate=risk_score,
            confidence_interval=(lower_bound, upper_bound),
            confidence_level=self.confidence_level,
            uncertainty_source="monte_carlo",
            method="monte_carlo"
        )
    
    def _bayesian_confidence(self, 
                           risk_score: float,
                           answer_quality: float,
                           data_completeness: float) -> ConfidenceScore:
        """Use Bayesian inference to estimate confidence bounds"""
        
        # Prior distribution (beta distribution scaled to 0-100)
        prior_alpha = 2.0
        prior_beta = 2.0
        
        # Likelihood based on answer quality and data completeness
        likelihood_strength = (answer_quality * data_completeness) * 10
        
        # Posterior parameters
        posterior_alpha = prior_alpha + likelihood_strength * (risk_score / 100)
        posterior_beta = prior_beta + likelihood_strength * (1 - risk_score / 100)
        
        # Generate samples from posterior
        samples = np.random.beta(posterior_alpha, posterior_beta, self.monte_carlo_samples) * 100
        
        # Calculate confidence interval
        alpha = 1 - self.confidence_level
        lower_bound = np.percentile(samples, (alpha/2) * 100)
        upper_bound = np.percentile(samples, (1 - alpha/2) * 100)
        
        return ConfidenceScore(
            point_estimate=np.mean(samples),
            confidence_interval=(lower_bound, upper_bound),
            confidence_level=self.confidence_level,
            uncertainty_source="bayesian",
            method="bayesian"
        )
    
    def _analytical_confidence(self, 
                             risk_score: float,
                             answer_quality: float,
                             data_completeness: float) -> ConfidenceScore:
        """Use analytical method to estimate confidence bounds"""
        
        # Calculate standard error
        total_uncertainty = self._calculate_total_uncertainty(answer_quality, data_completeness)
        standard_error = total_uncertainty * risk_score
        
        # Calculate confidence interval using normal distribution
        z_score = stats.norm.ppf(1 - (1 - self.confidence_level) / 2)
        margin_of_error = z_score * standard_error
        
        lower_bound = max(0, risk_score - margin_of_error)
        upper_bound = min(100, risk_score + margin_of_error)
        
        return ConfidenceScore(
            point_estimate=risk_score,
            confidence_interval=(lower_bound, upper_bound),
            confidence_level=self.confidence_level,
            uncertainty_source="analytical",
            method="analytical"
        )
    
    def _calculate_total_uncertainty(self, 
                                   answer_quality: float,
                                   data_completeness: float) -> float:
        """Calculate total uncertainty from multiple sources"""
        
        # Base uncertainties
        uncertainties = {
            'answer_quality': self.uncertainty_sources['answer_quality'] * (1 - answer_quality),
            'data_completeness': self.uncertainty_sources['data_completeness'] * (1 - data_completeness),
            'scoring_method': self.uncertainty_sources['scoring_method'],
            'model_variance': self.uncertainty_sources['model_variance']
        }
        
        # Combine uncertainties (assuming independence)
        total_uncertainty = np.sqrt(sum(u**2 for u in uncertainties.values()))
        
        return min(total_uncertainty, 0.5)  # Cap at 50% uncertainty
    
    def calculate_answer_quality(self, answers: Dict[str, str]) -> float:
        """Calculate answer quality score based on completeness and detail"""
        
        if not answers:
            return 0.0
        
        quality_scores = []
        
        for answer in answers.values():
            if not answer or answer.lower() in ['no answer provided', 'n/a', 'unknown']:
                quality_scores.append(0.0)
            else:
                # Score based on length and content
                length_score = min(len(answer) / 200, 1.0)  # Normalize to 200 chars
                
                # Content quality indicators
                quality_indicators = [
                    'implement', 'process', 'policy', 'procedure', 'control',
                    'framework', 'standard', 'compliance', 'audit', 'review',
                    'training', 'monitoring', 'assessment', 'governance'
                ]
                
                content_score = sum(1 for indicator in quality_indicators 
                                  if indicator in answer.lower()) / len(quality_indicators)
                
                # Combine scores
                answer_quality = 0.6 * length_score + 0.4 * content_score
                quality_scores.append(answer_quality)
        
        return np.mean(quality_scores)
    
    def calculate_data_completeness(self, answers: Dict[str, str], 
                                  total_questions: int) -> float:
        """Calculate data completeness score"""
        
        if total_questions == 0:
            return 0.0
        
        answered_questions = sum(1 for answer in answers.values() 
                               if answer and answer.lower() not in ['no answer provided', 'n/a', 'unknown'])
        
        return answered_questions / total_questions
    
    def analyze_uncertainty(self, risk_table: List[Dict[str, Any]], 
                          answers: Dict[str, str]) -> UncertaintyAnalysis:
        """Perform detailed uncertainty analysis"""
        
        try:
            # Calculate category-level uncertainties
            category_uncertainties = {}
            
            for row in risk_table:
                category_id = row['id']
                category_score = row['score']
                
                # Get answer for this category
                answer = answers.get(category_id, '')
                answer_quality = self.calculate_answer_quality({category_id: answer})
                data_completeness = 1.0 if answer else 0.0
                
                # Calculate uncertainty for this category
                uncertainty = self._calculate_total_uncertainty(answer_quality, data_completeness)
                category_uncertainties[category_id] = uncertainty
            
            # Calculate overall uncertainty
            overall_uncertainty = np.mean(list(category_uncertainties.values()))
            
            # Identify dominant uncertainty factors
            dominant_factors = sorted(category_uncertainties.items(), 
                                    key=lambda x: x[1], reverse=True)[:3]
            dominant_factor_names = [factor[0] for factor in dominant_factors]
            
            # Generate recommendation
            recommendation = self._generate_uncertainty_recommendation(overall_uncertainty, 
                                                                     dominant_factor_names)
            
            return UncertaintyAnalysis(
                overall_uncertainty=overall_uncertainty,
                category_uncertainties=category_uncertainties,
                dominant_factors=dominant_factor_names,
                recommendation=recommendation
            )
            
        except Exception as e:
            logger.error(f"Error analyzing uncertainty: {str(e)}")
            return UncertaintyAnalysis(
                overall_uncertainty=0.3,
                category_uncertainties={},
                dominant_factors=[],
                recommendation="Unable to analyze uncertainty. Consider providing more detailed responses."
            )
    
    def _generate_uncertainty_recommendation(self, 
                                           overall_uncertainty: float,
                                           dominant_factors: List[str]) -> str:
        """Generate recommendation based on uncertainty analysis"""
        
        if overall_uncertainty < 0.15:
            return "Excellent confidence in assessment. Results are highly reliable."
        elif overall_uncertainty < 0.25:
            return "Good confidence in assessment. Results are reliable with minor uncertainties."
        elif overall_uncertainty < 0.35:
            return f"Moderate confidence in assessment. Consider improving responses in: {', '.join(dominant_factors[:2])}"
        else:
            return f"Low confidence in assessment. Strongly recommend improving responses in: {', '.join(dominant_factors)}"
    
    def propagate_uncertainty(self, 
                            category_scores: List[ConfidenceScore],
                            weights: List[float]) -> ConfidenceScore:
        """Propagate uncertainty through weighted aggregation"""
        
        if len(category_scores) != len(weights):
            raise ValueError("Number of scores must match number of weights")
        
        # Calculate weighted point estimate
        point_estimate = sum(score.point_estimate * weight 
                           for score, weight in zip(category_scores, weights))
        
        # Propagate uncertainty (assuming independence)
        variance = sum((weight * (score.confidence_interval[1] - score.confidence_interval[0]) / 
                       (2 * stats.norm.ppf(1 - (1 - score.confidence_level) / 2)))**2 
                      for score, weight in zip(category_scores, weights))
        
        standard_error = np.sqrt(variance)
        z_score = stats.norm.ppf(1 - (1 - self.confidence_level) / 2)
        margin_of_error = z_score * standard_error
        
        return ConfidenceScore(
            point_estimate=point_estimate,
            confidence_interval=(max(0, point_estimate - margin_of_error),
                               min(100, point_estimate + margin_of_error)),
            confidence_level=self.confidence_level,
            uncertainty_source="propagated",
            method="uncertainty_propagation"
        )

# Global instance
confidence_scorer = ConfidenceScorer()