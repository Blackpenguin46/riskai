"""
Validation Module

Provides cross-validation against industry benchmarks, statistical validation,
and performance assessment for the risk assessment system.
"""

import logging
import numpy as np
from typing import Dict, List, Tuple, Any, Optional
from scipy import stats
from sklearn.model_selection import cross_val_score, KFold
from sklearn.metrics import mean_squared_error, mean_absolute_error, r2_score
from dataclasses import dataclass
from enum import Enum
import json

logger = logging.getLogger(__name__)

class ValidationMethod(Enum):
    """Available validation methods"""
    CROSS_VALIDATION = "cross_validation"
    BENCHMARK_COMPARISON = "benchmark_comparison"
    STATISTICAL_SIGNIFICANCE = "statistical_significance"
    CONVERGENCE_ANALYSIS = "convergence_analysis"

@dataclass
class ValidationResult:
    """Result of a validation test"""
    method: str
    score: float
    confidence_interval: Tuple[float, float]
    p_value: Optional[float]
    status: str  # 'pass', 'warning', 'fail'
    details: Dict[str, Any]

@dataclass
class BenchmarkScore:
    """Industry benchmark score"""
    industry: str
    framework: str
    category: str
    mean_score: float
    std_score: float
    percentile_25: float
    percentile_75: float
    sample_size: int

class RiskAssessmentValidator:
    """Main validator class for risk assessment system"""
    
    def __init__(self):
        self.validation_thresholds = {
            'cross_validation_r2': 0.7,        # Minimum R² score
            'benchmark_deviation': 2.0,        # Max standard deviations from benchmark
            'statistical_significance': 0.05,  # p-value threshold
            'convergence_tolerance': 0.02      # Convergence tolerance
        }
        
        # Industry benchmarks (would typically be loaded from database)
        self.industry_benchmarks = self._load_industry_benchmarks()
        
        # NIST CSF framework mappings
        self.nist_csf_mappings = self._load_nist_csf_mappings()
        
        # Multi-industry validation datasets
        self.multi_industry_datasets = self._initialize_multi_industry_datasets()
        
        # Case studies for validation
        self.case_studies = self._load_case_studies()
    
    def _load_industry_benchmarks(self) -> Dict[str, List[BenchmarkScore]]:
        """Load industry benchmarks (placeholder - would load from database)"""
        return {
            'healthcare': [
                BenchmarkScore('healthcare', 'NIST_CSF', 'data_sensitivity', 7.5, 1.2, 6.8, 8.5, 150),
                BenchmarkScore('healthcare', 'NIST_CSF', 'access_management', 7.2, 1.5, 6.2, 8.2, 150),
                BenchmarkScore('healthcare', 'NIST_CSF', 'regulatory_compliance', 8.1, 1.0, 7.5, 8.8, 150)
            ],
            'finance': [
                BenchmarkScore('finance', 'NIST_CSF', 'data_sensitivity', 8.2, 1.1, 7.5, 8.9, 200),
                BenchmarkScore('finance', 'NIST_CSF', 'access_management', 7.8, 1.3, 6.9, 8.6, 200),
                BenchmarkScore('finance', 'NIST_CSF', 'regulatory_compliance', 8.5, 0.9, 7.9, 9.1, 200)
            ],
            'technology': [
                BenchmarkScore('technology', 'NIST_CSF', 'innovation_culture', 7.9, 1.4, 7.0, 8.7, 180),
                BenchmarkScore('technology', 'NIST_CSF', 'emerging_tech_adoption', 7.5, 1.6, 6.5, 8.5, 180),
                BenchmarkScore('technology', 'NIST_CSF', 'secure_sdlc', 7.3, 1.8, 6.2, 8.4, 180)
            ]
        }
    
    def _load_nist_csf_mappings(self) -> Dict[str, str]:
        """Load NIST CSF framework mappings"""
        return {
            'asset_visibility': 'ID.AM',
            'data_sensitivity': 'ID.GV',
            'access_management': 'PR.AC',
            'network_security': 'PR.AC',
            'cloud_security': 'PR.AC',
            'third_party_risk': 'ID.SC',
            'incident_response': 'RS.RP',
            'security_awareness': 'PR.AT',
            'grc': 'ID.GV',
            'secure_sdlc': 'PR.IP',
            'business_continuity': 'RC.CO',
            'security_monitoring': 'DE.CM',
            'app_security': 'PR.IP'
        }
    
    def validate_assessment(self, 
                          risk_table: List[Dict[str, Any]],
                          company_profile: Dict[str, Any],
                          answers: Dict[str, str]) -> Dict[str, ValidationResult]:
        """Perform comprehensive validation of risk assessment"""
        
        validation_results = {}
        
        # 1. Cross-validation
        validation_results['cross_validation'] = self._perform_cross_validation(
            risk_table, company_profile, answers
        )
        
        # 2. Benchmark comparison
        validation_results['benchmark_comparison'] = self._compare_with_benchmarks(
            risk_table, company_profile
        )
        
        # 3. Statistical significance testing
        validation_results['statistical_significance'] = self._test_statistical_significance(
            risk_table, answers
        )
        
        # 4. Convergence analysis
        validation_results['convergence_analysis'] = self._analyze_convergence(
            risk_table, answers
        )
        
        # 5. NIST CSF alignment
        validation_results['nist_csf_alignment'] = self._validate_nist_csf_alignment(
            risk_table
        )
        
        return validation_results
    
    def _perform_cross_validation(self, 
                                 risk_table: List[Dict[str, Any]],
                                 company_profile: Dict[str, Any],
                                 answers: Dict[str, str]) -> ValidationResult:
        """Perform cross-validation on risk scoring"""
        
        try:
            # Extract features and scores
            scores = [row['score'] for row in risk_table]
            weights = [row['weight'] for row in risk_table]
            
            # Create feature matrix (simplified for demonstration)
            features = self._create_feature_matrix(answers, company_profile)
            
            if len(features) < 5:  # Need minimum samples for cross-validation
                return ValidationResult(
                    method="cross_validation",
                    score=0.0,
                    confidence_interval=(0.0, 0.0),
                    p_value=None,
                    status="warning",
                    details={"error": "Insufficient data for cross-validation"}
                )
            
            # Perform k-fold cross-validation
            kfold = KFold(n_splits=min(5, len(features)), shuffle=True, random_state=42)
            
            # Calculate mean squared error and R²
            mse_scores = []
            r2_scores = []
            
            for train_idx, test_idx in kfold.split(features):
                # Simple linear regression for demonstration
                train_features = np.array(features)[train_idx]
                train_scores = np.array(scores)[train_idx]
                test_features = np.array(features)[test_idx]
                test_scores = np.array(scores)[test_idx]
                
                # Fit model (simplified)
                coeffs = np.polyfit(train_features.flatten(), train_scores, 1)
                predictions = np.polyval(coeffs, test_features.flatten())
                
                mse = mean_squared_error(test_scores, predictions)
                r2 = r2_score(test_scores, predictions)
                
                mse_scores.append(mse)
                r2_scores.append(r2)
            
            # Calculate statistics
            mean_r2 = np.mean(r2_scores)
            std_r2 = np.std(r2_scores)
            
            # Determine status
            status = "pass" if mean_r2 >= self.validation_thresholds['cross_validation_r2'] else "warning"
            
            return ValidationResult(
                method="cross_validation",
                score=mean_r2,
                confidence_interval=(mean_r2 - 1.96 * std_r2, mean_r2 + 1.96 * std_r2),
                p_value=None,
                status=status,
                details={
                    "mean_r2": mean_r2,
                    "std_r2": std_r2,
                    "mean_mse": np.mean(mse_scores),
                    "n_folds": len(mse_scores)
                }
            )
            
        except Exception as e:
            logger.error(f"Error in cross-validation: {str(e)}")
            return ValidationResult(
                method="cross_validation",
                score=0.0,
                confidence_interval=(0.0, 0.0),
                p_value=None,
                status="fail",
                details={"error": str(e)}
            )
    
    def _compare_with_benchmarks(self, 
                               risk_table: List[Dict[str, Any]],
                               company_profile: Dict[str, Any]) -> ValidationResult:
        """Compare assessment scores with industry benchmarks"""
        
        try:
            industry = company_profile.get('industry', 'unknown').lower()
            
            if industry not in self.industry_benchmarks:
                return ValidationResult(
                    method="benchmark_comparison",
                    score=0.0,
                    confidence_interval=(0.0, 0.0),
                    p_value=None,
                    status="warning",
                    details={"error": f"No benchmarks available for industry: {industry}"}
                )
            
            benchmarks = self.industry_benchmarks[industry]
            benchmark_dict = {b.category: b for b in benchmarks}
            
            deviations = []
            comparisons = []
            
            for row in risk_table:
                category_id = row['id']
                score = row['score']
                
                if category_id in benchmark_dict:
                    benchmark = benchmark_dict[category_id]
                    
                    # Calculate z-score (standard deviations from benchmark)
                    z_score = (score - benchmark.mean_score) / benchmark.std_score
                    deviations.append(abs(z_score))
                    
                    # Calculate percentile
                    percentile = stats.norm.cdf(z_score) * 100
                    
                    comparisons.append({
                        'category': category_id,
                        'score': score,
                        'benchmark_mean': benchmark.mean_score,
                        'z_score': z_score,
                        'percentile': percentile,
                        'status': 'normal' if abs(z_score) <= 2.0 else 'outlier'
                    })
            
            # Calculate overall deviation
            mean_deviation = np.mean(deviations) if deviations else 0.0
            
            # Determine status
            status = "pass" if mean_deviation <= self.validation_thresholds['benchmark_deviation'] else "warning"
            
            return ValidationResult(
                method="benchmark_comparison",
                score=1.0 - (mean_deviation / 3.0),  # Normalize to 0-1 scale
                confidence_interval=(0.0, 1.0),
                p_value=None,
                status=status,
                details={
                    "mean_deviation": mean_deviation,
                    "comparisons": comparisons,
                    "industry": industry,
                    "categories_compared": len(comparisons)
                }
            )
            
        except Exception as e:
            logger.error(f"Error in benchmark comparison: {str(e)}")
            return ValidationResult(
                method="benchmark_comparison",
                score=0.0,
                confidence_interval=(0.0, 0.0),
                p_value=None,
                status="fail",
                details={"error": str(e)}
            )
    
    def _test_statistical_significance(self, 
                                     risk_table: List[Dict[str, Any]],
                                     answers: Dict[str, str]) -> ValidationResult:
        """Test statistical significance of risk scores"""
        
        try:
            scores = [row['score'] for row in risk_table]
            
            # Test if scores are significantly different from random (5.0 midpoint)
            t_stat, p_value = stats.ttest_1samp(scores, 5.0)
            
            # Test for normality
            shapiro_stat, shapiro_p = stats.shapiro(scores)
            
            # Calculate effect size (Cohen's d)
            effect_size = (np.mean(scores) - 5.0) / np.std(scores)
            
            # Determine status
            status = "pass" if p_value < self.validation_thresholds['statistical_significance'] else "warning"
            
            return ValidationResult(
                method="statistical_significance",
                score=1.0 - p_value,  # Higher score for lower p-value
                confidence_interval=(0.0, 1.0),
                p_value=p_value,
                status=status,
                details={
                    "t_statistic": t_stat,
                    "p_value": p_value,
                    "effect_size": effect_size,
                    "shapiro_statistic": shapiro_stat,
                    "shapiro_p_value": shapiro_p,
                    "normality_test": "pass" if shapiro_p > 0.05 else "fail"
                }
            )
            
        except Exception as e:
            logger.error(f"Error in statistical significance test: {str(e)}")
            return ValidationResult(
                method="statistical_significance",
                score=0.0,
                confidence_interval=(0.0, 0.0),
                p_value=None,
                status="fail",
                details={"error": str(e)}
            )
    
    def _analyze_convergence(self, 
                           risk_table: List[Dict[str, Any]],
                           answers: Dict[str, str]) -> ValidationResult:
        """Analyze convergence of risk assessment"""
        
        try:
            # Simulate iterative scoring process
            scores = [row['score'] for row in risk_table]
            weights = [row['weight'] for row in risk_table]
            
            # Calculate weighted score
            weighted_score = sum(s * w for s, w in zip(scores, weights))
            
            # Simulate convergence by adding small perturbations
            iterations = 10
            convergence_scores = []
            
            for i in range(iterations):
                # Add small random perturbations
                perturbed_scores = [s + np.random.normal(0, 0.1) for s in scores]
                perturbed_weighted = sum(s * w for s, w in zip(perturbed_scores, weights))
                convergence_scores.append(perturbed_weighted)
            
            # Calculate convergence statistics
            convergence_std = np.std(convergence_scores)
            convergence_range = max(convergence_scores) - min(convergence_scores)
            
            # Determine convergence status
            converged = convergence_std <= self.validation_thresholds['convergence_tolerance']
            status = "pass" if converged else "warning"
            
            return ValidationResult(
                method="convergence_analysis",
                score=1.0 - min(convergence_std, 1.0),  # Higher score for better convergence
                confidence_interval=(min(convergence_scores), max(convergence_scores)),
                p_value=None,
                status=status,
                details={
                    "convergence_std": convergence_std,
                    "convergence_range": convergence_range,
                    "iterations": iterations,
                    "converged": converged
                }
            )
            
        except Exception as e:
            logger.error(f"Error in convergence analysis: {str(e)}")
            return ValidationResult(
                method="convergence_analysis",
                score=0.0,
                confidence_interval=(0.0, 0.0),
                p_value=None,
                status="fail",
                details={"error": str(e)}
            )
    
    def _validate_nist_csf_alignment(self, 
                                   risk_table: List[Dict[str, Any]]) -> ValidationResult:
        """Validate alignment with NIST Cybersecurity Framework"""
        
        try:
            # Check coverage of NIST CSF categories
            nist_categories = set(self.nist_csf_mappings.values())
            assessed_categories = set()
            
            alignment_scores = []
            
            for row in risk_table:
                category_id = row['id']
                score = row['score']
                
                if category_id in self.nist_csf_mappings:
                    nist_category = self.nist_csf_mappings[category_id]
                    assessed_categories.add(nist_category)
                    
                    # Score alignment (higher scores indicate better alignment)
                    alignment_score = score / 10.0  # Normalize to 0-1
                    alignment_scores.append(alignment_score)
            
            # Calculate coverage
            coverage = len(assessed_categories) / len(nist_categories)
            
            # Calculate average alignment
            avg_alignment = np.mean(alignment_scores) if alignment_scores else 0.0
            
            # Overall NIST CSF score
            nist_score = 0.6 * avg_alignment + 0.4 * coverage
            
            # Determine status
            status = "pass" if nist_score >= 0.7 else "warning"
            
            return ValidationResult(
                method="nist_csf_alignment",
                score=nist_score,
                confidence_interval=(0.0, 1.0),
                p_value=None,
                status=status,
                details={
                    "coverage": coverage,
                    "avg_alignment": avg_alignment,
                    "assessed_categories": list(assessed_categories),
                    "total_nist_categories": len(nist_categories),
                    "alignment_scores": alignment_scores
                }
            )
            
        except Exception as e:
            logger.error(f"Error in NIST CSF alignment validation: {str(e)}")
            return ValidationResult(
                method="nist_csf_alignment",
                score=0.0,
                confidence_interval=(0.0, 0.0),
                p_value=None,
                status="fail",
                details={"error": str(e)}
            )
    
    def _create_feature_matrix(self, 
                              answers: Dict[str, str],
                              company_profile: Dict[str, Any]) -> List[float]:
        """Create feature matrix for validation (simplified)"""
        
        features = []
        
        # Answer-based features
        for answer in answers.values():
            if answer and answer.lower() not in ['no answer provided', 'n/a']:
                features.append(len(answer))  # Answer length
                features.append(answer.count(','))  # Complexity indicator
            else:
                features.extend([0, 0])
        
        # Profile-based features
        industry_map = {'finance': 1, 'healthcare': 2, 'technology': 3}
        size_map = {'startup': 1, 'small': 2, 'medium': 3, 'large': 4}
        
        features.append(industry_map.get(company_profile.get('industry', '').lower(), 0))
        features.append(size_map.get(company_profile.get('size', '').lower(), 0))
        
        return features
    
    def generate_validation_report(self, 
                                 validation_results: Dict[str, ValidationResult]) -> Dict[str, Any]:
        """Generate comprehensive validation report"""
        
        # Calculate overall validation score
        scores = [result.score for result in validation_results.values() if result.score is not None]
        overall_score = np.mean(scores) if scores else 0.0
        
        # Count status types
        status_counts = {}
        for result in validation_results.values():
            status_counts[result.status] = status_counts.get(result.status, 0) + 1
        
        # Generate recommendations
        recommendations = []
        for method, result in validation_results.items():
            if result.status == "warning" or result.status == "fail":
                recommendations.append(f"Address issues in {method}: {result.details}")
        
        return {
            "overall_score": overall_score,
            "overall_status": "pass" if overall_score >= 0.7 else "warning",
            "validation_results": {k: {
                "method": v.method,
                "score": v.score,
                "confidence_interval": v.confidence_interval,
                "p_value": v.p_value,
                "status": v.status,
                "details": v.details
            } for k, v in validation_results.items()},
            "status_summary": status_counts,
            "recommendations": recommendations,
            "timestamp": np.datetime64('now').isoformat()
        }
    
    def _initialize_multi_industry_datasets(self) -> Dict[str, Any]:
        """Initialize multi-industry validation datasets"""
        return {
            "healthcare": {
                "compliance_standards": ["HIPAA", "FDA", "CDC"],
                "risk_thresholds": {"high": 7.5, "medium": 5.0, "low": 2.5}
            },
            "finance": {
                "compliance_standards": ["SOX", "PCI-DSS", "GDPR"],
                "risk_thresholds": {"high": 8.0, "medium": 5.5, "low": 3.0}
            },
            "technology": {
                "compliance_standards": ["ISO27001", "NIST", "SOC2"],
                "risk_thresholds": {"high": 7.0, "medium": 4.5, "low": 2.0}
            },
            "manufacturing": {
                "compliance_standards": ["ISO27001", "NIST", "IEC62443"],
                "risk_thresholds": {"high": 6.5, "medium": 4.0, "low": 2.0}
            }
        }
    
    def _load_case_studies(self) -> List[Dict[str, Any]]:
        """Load case studies for validation"""
        return [
            {
                "id": "healthcare_hospital",
                "industry": "healthcare", 
                "organization_size": "large",
                "expected_score_range": {"min": 6.5, "max": 8.5},
                "key_controls": ["access_control", "encryption", "audit_logging"]
            },
            {
                "id": "finance_bank",
                "industry": "finance",
                "organization_size": "large", 
                "expected_score_range": {"min": 7.0, "max": 9.0},
                "key_controls": ["multi_factor_auth", "transaction_monitoring", "fraud_detection"]
            },
            {
                "id": "tech_startup",
                "industry": "technology",
                "organization_size": "small",
                "expected_score_range": {"min": 5.0, "max": 7.5},
                "key_controls": ["code_review", "vulnerability_scanning", "incident_response"]
            }
        ]

# Global instance
risk_validator = RiskAssessmentValidator()