"""
Statistical Analyzer for RiskAI Validation
Performs statistical analysis on validation data to assess generalizability
"""

import logging
import numpy as np
import scipy.stats as stats
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime

from database.models import get_session
from database.validation_models import (
    IndustrySector, SecurityFramework, SecurityDomain, AssessmentQuestion,
    IndustryValidation, ValidationMetric, ValidationResponse, ScoringRubric,
    IndustryBenchmark
)
from validation.validator import validation_data_manager

logger = logging.getLogger(__name__)

class StatisticalAnalyzer:
    """Performs statistical analysis on validation data"""
    
    @staticmethod
    def calculate_confidence_intervals(
        industry_id: Optional[int] = None,
        company_size: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Calculate confidence intervals for validation metrics
        
        Args:
            industry_id: Optional industry sector ID filter
            company_size: Optional company size filter
            
        Returns:
            Dictionary with confidence interval data
        """
        try:
            db = get_session()
            
            # Query validation responses
            query = db.query(ValidationResponse)
            
            if industry_id is not None:
                query = query.filter(ValidationResponse.industry_id == industry_id)
            
            if company_size is not None:
                query = query.filter(ValidationResponse.company_size == company_size)
            
            responses = query.all()
            
            if not responses:
                return {
                    "error": "No validation responses found",
                    "industry_id": industry_id,
                    "company_size": company_size
                }
            
            # Calculate accuracy
            correct_responses = sum(1 for r in responses if r.is_correct)
            total_responses = len(responses)
            accuracy = correct_responses / total_responses if total_responses > 0 else 0
            
            # Calculate confidence interval (95%)
            z = 1.96  # 95% confidence
            p = accuracy
            confidence_interval = z * np.sqrt((p * (1 - p)) / total_responses)
            confidence_lower = max(0, p - confidence_interval)
            confidence_upper = min(1, p + confidence_interval)
            
            # Calculate confidence intervals for different confidence levels
            confidence_intervals = {}
            for confidence_level in [0.90, 0.95, 0.99]:
                z_value = stats.norm.ppf((1 + confidence_level) / 2)
                interval = z_value * np.sqrt((p * (1 - p)) / total_responses)
                confidence_intervals[str(int(confidence_level * 100))] = {
                    "lower": max(0, p - interval),
                    "upper": min(1, p + interval)
                }
            
            return {
                "industry_id": industry_id,
                "company_size": company_size,
                "accuracy": accuracy,
                "total_responses": total_responses,
                "confidence_interval_95": {
                    "lower": confidence_lower,
                    "upper": confidence_upper,
                    "margin_of_error": confidence_interval
                },
                "confidence_intervals": confidence_intervals
            }
            
        except Exception as e:
            logger.error(f"Error calculating confidence intervals: {str(e)}")
            return {
                "error": str(e),
                "industry_id": industry_id,
                "company_size": company_size
            }
        finally:
            db.close()
    
    @staticmethod
    def perform_hypothesis_test(
        industry_id1: int,
        industry_id2: int,
        company_size: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Perform hypothesis test to compare two industries
        
        Args:
            industry_id1: First industry sector ID
            industry_id2: Second industry sector ID
            company_size: Optional company size filter
            
        Returns:
            Dictionary with hypothesis test results
        """
        try:
            db = get_session()
            
            # Query validation responses for first industry
            query1 = db.query(ValidationResponse).filter(
                ValidationResponse.industry_id == industry_id1
            )
            
            if company_size is not None:
                query1 = query1.filter(ValidationResponse.company_size == company_size)
            
            responses1 = query1.all()
            
            # Query validation responses for second industry
            query2 = db.query(ValidationResponse).filter(
                ValidationResponse.industry_id == industry_id2
            )
            
            if company_size is not None:
                query2 = query2.filter(ValidationResponse.company_size == company_size)
            
            responses2 = query2.all()
            
            if not responses1 or not responses2:
                return {
                    "error": "Insufficient validation responses for one or both industries",
                    "industry_id1": industry_id1,
                    "industry_id2": industry_id2,
                    "company_size": company_size
                }
            
            # Calculate accuracies
            correct1 = sum(1 for r in responses1 if r.is_correct)
            total1 = len(responses1)
            accuracy1 = correct1 / total1 if total1 > 0 else 0
            
            correct2 = sum(1 for r in responses2 if r.is_correct)
            total2 = len(responses2)
            accuracy2 = correct2 / total2 if total2 > 0 else 0
            
            # Perform two-proportion z-test
            p1 = accuracy1
            p2 = accuracy2
            n1 = total1
            n2 = total2
            
            # Pooled proportion
            p_pooled = (correct1 + correct2) / (total1 + total2)
            
            # Standard error
            se = np.sqrt(p_pooled * (1 - p_pooled) * (1/n1 + 1/n2))
            
            # Z-statistic
            z = (p1 - p2) / se if se > 0 else 0
            
            # P-value (two-tailed test)
            p_value = 2 * (1 - stats.norm.cdf(abs(z)))
            
            # Get industry names
            industry1 = db.query(IndustrySector).filter(IndustrySector.id == industry_id1).first()
            industry2 = db.query(IndustrySector).filter(IndustrySector.id == industry_id2).first()
            
            industry1_name = industry1.name if industry1 else f"Industry {industry_id1}"
            industry2_name = industry2.name if industry2 else f"Industry {industry_id2}"
            
            # Interpret results
            alpha = 0.05  # Significance level
            significant = p_value < alpha
            
            if significant:
                if accuracy1 > accuracy2:
                    interpretation = f"RiskAI performs significantly better in {industry1_name} compared to {industry2_name}."
                else:
                    interpretation = f"RiskAI performs significantly better in {industry2_name} compared to {industry1_name}."
            else:
                interpretation = f"There is no significant difference in RiskAI's performance between {industry1_name} and {industry2_name}."
            
            return {
                "industry_id1": industry_id1,
                "industry_name1": industry1_name,
                "industry_id2": industry_id2,
                "industry_name2": industry2_name,
                "company_size": company_size,
                "accuracy1": accuracy1,
                "accuracy2": accuracy2,
                "sample_size1": total1,
                "sample_size2": total2,
                "z_statistic": z,
                "p_value": p_value,
                "significant": significant,
                "interpretation": interpretation
            }
            
        except Exception as e:
            logger.error(f"Error performing hypothesis test: {str(e)}")
            return {
                "error": str(e),
                "industry_id1": industry_id1,
                "industry_id2": industry_id2,
                "company_size": company_size
            }
        finally:
            db.close()
    
    @staticmethod
    def analyze_generalizability() -> Dict[str, Any]:
        """
        Analyze generalizability of RiskAI across industries and company sizes
        
        Returns:
            Dictionary with generalizability analysis
        """
        try:
            db = get_session()
            
            # Get all industries
            industries = db.query(IndustrySector).all()
            
            if not industries:
                return {"error": "No industries found"}
            
            # Get all company sizes
            company_sizes = ["small", "medium", "large", "enterprise"]
            
            # Calculate metrics for each industry
            industry_metrics = []
            for industry in industries:
                # Get validation responses for this industry
                responses = db.query(ValidationResponse).filter(
                    ValidationResponse.industry_id == industry.id
                ).all()
                
                if not responses:
                    continue
                
                # Calculate accuracy
                correct = sum(1 for r in responses if r.is_correct)
                total = len(responses)
                accuracy = correct / total if total > 0 else 0
                
                # Calculate confidence interval (95%)
                z = 1.96  # 95% confidence
                p = accuracy
                confidence_interval = z * np.sqrt((p * (1 - p)) / total) if total > 0 else 0
                
                industry_metrics.append({
                    "industry_id": industry.id,
                    "industry_name": industry.name,
                    "accuracy": accuracy,
                    "sample_size": total,
                    "confidence_interval": [max(0, p - confidence_interval), min(1, p + confidence_interval)]
                })
            
            # Calculate metrics for each company size
            company_size_metrics = []
            for size in company_sizes:
                # Get validation responses for this company size
                responses = db.query(ValidationResponse).filter(
                    ValidationResponse.company_size == size
                ).all()
                
                if not responses:
                    continue
                
                # Calculate accuracy
                correct = sum(1 for r in responses if r.is_correct)
                total = len(responses)
                accuracy = correct / total if total > 0 else 0
                
                # Calculate confidence interval (95%)
                z = 1.96  # 95% confidence
                p = accuracy
                confidence_interval = z * np.sqrt((p * (1 - p)) / total) if total > 0 else 0
                
                company_size_metrics.append({
                    "company_size": size,
                    "accuracy": accuracy,
                    "sample_size": total,
                    "confidence_interval": [max(0, p - confidence_interval), min(1, p + confidence_interval)]
                })
            
            # Calculate overall metrics
            all_responses = db.query(ValidationResponse).all()
            
            if not all_responses:
                return {"error": "No validation responses found"}
            
            correct_all = sum(1 for r in all_responses if r.is_correct)
            total_all = len(all_responses)
            accuracy_all = correct_all / total_all if total_all > 0 else 0
            
            # Calculate confidence interval (95%)
            z = 1.96  # 95% confidence
            p = accuracy_all
            confidence_interval_all = z * np.sqrt((p * (1 - p)) / total_all) if total_all > 0 else 0
            
            # Perform ANOVA to test for significant differences between industries
            industry_accuracies = {}
            for industry in industries:
                responses = db.query(ValidationResponse).filter(
                    ValidationResponse.industry_id == industry.id
                ).all()
                
                if responses:
                    industry_accuracies[industry.id] = [1 if r.is_correct else 0 for r in responses]
            
            # Check if we have enough data for ANOVA
            if len(industry_accuracies) >= 2:
                # Perform one-way ANOVA
                samples = list(industry_accuracies.values())
                f_statistic, p_value = stats.f_oneway(*samples)
                
                anova_result = {
                    "f_statistic": f_statistic,
                    "p_value": p_value,
                    "significant": p_value < 0.05
                }
            else:
                anova_result = {
                    "error": "Insufficient data for ANOVA"
                }
            
            # Calculate variance between industries
            if industry_metrics:
                industry_accuracies_list = [m["accuracy"] for m in industry_metrics]
                industry_variance = np.var(industry_accuracies_list)
                industry_std_dev = np.std(industry_accuracies_list)
                industry_min = min(industry_accuracies_list)
                industry_max = max(industry_accuracies_list)
                industry_range = industry_max - industry_min
            else:
                industry_variance = 0
                industry_std_dev = 0
                industry_min = 0
                industry_max = 0
                industry_range = 0
            
            # Calculate variance between company sizes
            if company_size_metrics:
                company_size_accuracies = [m["accuracy"] for m in company_size_metrics]
                company_size_variance = np.var(company_size_accuracies)
                company_size_std_dev = np.std(company_size_accuracies)
                company_size_min = min(company_size_accuracies)
                company_size_max = max(company_size_accuracies)
                company_size_range = company_size_max - company_size_min
            else:
                company_size_variance = 0
                company_size_std_dev = 0
                company_size_min = 0
                company_size_max = 0
                company_size_range = 0
            
            # Interpret generalizability
            if industry_variance < 0.01 and company_size_variance < 0.01:
                generalizability = "Excellent"
                interpretation = "RiskAI demonstrates excellent generalizability across industries and company sizes, with minimal variance in performance."
            elif industry_variance < 0.05 and company_size_variance < 0.05:
                generalizability = "Good"
                interpretation = "RiskAI demonstrates good generalizability across industries and company sizes, with acceptable variance in performance."
            elif industry_variance < 0.1 and company_size_variance < 0.1:
                generalizability = "Moderate"
                interpretation = "RiskAI demonstrates moderate generalizability across industries and company sizes, with some variance in performance."
            else:
                generalizability = "Limited"
                interpretation = "RiskAI demonstrates limited generalizability across industries and company sizes, with significant variance in performance."
            
            return {
                "overall": {
                    "accuracy": accuracy_all,
                    "sample_size": total_all,
                    "confidence_interval": [max(0, p - confidence_interval_all), min(1, p + confidence_interval_all)]
                },
                "industry_metrics": industry_metrics,
                "company_size_metrics": company_size_metrics,
                "industry_variance": {
                    "variance": industry_variance,
                    "std_dev": industry_std_dev,
                    "min": industry_min,
                    "max": industry_max,
                    "range": industry_range
                },
                "company_size_variance": {
                    "variance": company_size_variance,
                    "std_dev": company_size_std_dev,
                    "min": company_size_min,
                    "max": company_size_max,
                    "range": company_size_range
                },
                "anova_result": anova_result,
                "generalizability": generalizability,
                "interpretation": interpretation
            }
            
        except Exception as e:
            logger.error(f"Error analyzing generalizability: {str(e)}")
            return {"error": str(e)}
        finally:
            db.close()
    
    @staticmethod
    def analyze_domain_performance(
        industry_id: Optional[int] = None,
        company_size: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Analyze RiskAI's performance across security domains
        
        Args:
            industry_id: Optional industry sector ID filter
            company_size: Optional company size filter
            
        Returns:
            Dictionary with domain performance analysis
        """
        try:
            db = get_session()
            
            # Get all domains
            domains = db.query(SecurityDomain).all()
            
            if not domains:
                return {"error": "No security domains found"}
            
            # Calculate metrics for each domain
            domain_metrics = []
            for domain in domains:
                # Get questions for this domain
                questions = db.query(AssessmentQuestion).filter(
                    AssessmentQuestion.domain_id == domain.id
                ).all()
                
                if not questions:
                    continue
                
                question_ids = [q.id for q in questions]
                
                # Get validation responses for these questions
                query = db.query(ValidationResponse).filter(
                    ValidationResponse.question_id.in_(question_ids)
                )
                
                if industry_id is not None:
                    query = query.filter(ValidationResponse.industry_id == industry_id)
                
                if company_size is not None:
                    query = query.filter(ValidationResponse.company_size == company_size)
                
                responses = query.all()
                
                if not responses:
                    continue
                
                # Calculate accuracy
                correct = sum(1 for r in responses if r.is_correct)
                total = len(responses)
                accuracy = correct / total if total > 0 else 0
                
                # Calculate confidence interval (95%)
                z = 1.96  # 95% confidence
                p = accuracy
                confidence_interval = z * np.sqrt((p * (1 - p)) / total) if total > 0 else 0
                
                # Get framework
                framework = db.query(SecurityFramework).filter(
                    SecurityFramework.id == domain.framework_id
                ).first()
                
                framework_name = framework.name if framework else "Unknown"
                
                domain_metrics.append({
                    "domain_id": domain.id,
                    "domain_name": domain.name,
                    "framework_id": domain.framework_id,
                    "framework_name": framework_name,
                    "accuracy": accuracy,
                    "sample_size": total,
                    "confidence_interval": [max(0, p - confidence_interval), min(1, p + confidence_interval)]
                })
            
            # Sort domains by accuracy
            domain_metrics.sort(key=lambda x: x["accuracy"], reverse=True)
            
            # Calculate variance between domains
            if domain_metrics:
                domain_accuracies = [m["accuracy"] for m in domain_metrics]
                domain_variance = np.var(domain_accuracies)
                domain_std_dev = np.std(domain_accuracies)
                domain_min = min(domain_accuracies)
                domain_max = max(domain_accuracies)
                domain_range = domain_max - domain_min
            else:
                domain_variance = 0
                domain_std_dev = 0
                domain_min = 0
                domain_max = 0
                domain_range = 0
            
            # Identify strengths and weaknesses
            strengths = domain_metrics[:3] if len(domain_metrics) >= 3 else domain_metrics
            weaknesses = domain_metrics[-3:] if len(domain_metrics) >= 3 else []
            weaknesses.reverse()  # Show worst first
            
            return {
                "industry_id": industry_id,
                "company_size": company_size,
                "domain_metrics": domain_metrics,
                "domain_variance": {
                    "variance": domain_variance,
                    "std_dev": domain_std_dev,
                    "min": domain_min,
                    "max": domain_max,
                    "range": domain_range
                },
                "strengths": strengths,
                "weaknesses": weaknesses
            }
            
        except Exception as e:
            logger.error(f"Error analyzing domain performance: {str(e)}")
            return {"error": str(e)}
        finally:
            db.close()

# Create a global instance
statistical_analyzer = StatisticalAnalyzer()