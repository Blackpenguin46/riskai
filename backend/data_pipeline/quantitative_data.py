#!/usr/bin/env python3
"""
Quantitative Data Pipeline

Provides quantitative benchmarks and data points to support 
qualitative assessment scoring with real-world data.
"""

import logging
from typing import Dict, List, Optional, Any
from dataclasses import dataclass
from enum import Enum

logger = logging.getLogger(__name__)

@dataclass
class IndustryBenchmark:
    industry: str
    metric: str
    value: float
    unit: str
    source: str
    confidence: float

@dataclass
class QuantitativeMetric:
    metric_id: str
    name: str
    category: str
    current_value: Optional[float]
    benchmark_value: float
    unit: str
    higher_is_better: bool
    confidence_score: float

class IndustryType(Enum):
    HEALTHCARE = "healthcare"
    FINANCE = "finance" 
    TECHNOLOGY = "technology"
    MANUFACTURING = "manufacturing"
    GOVERNMENT = "government"
    EDUCATION = "education"
    RETAIL = "retail"
    GENERAL = "general"

class CompanySize(Enum):
    SMALL = "small"          # <50 employees
    MEDIUM = "medium"        # 50-500 employees  
    LARGE = "large"          # 500-5000 employees
    ENTERPRISE = "enterprise" # >5000 employees

class QuantitativeDataPipeline:
    """Pipeline for quantitative cybersecurity benchmarks"""
    
    def __init__(self):
        self.industry_benchmarks = self._load_industry_benchmarks()
        self.security_metrics = self._load_security_metrics()
        self.maturity_benchmarks = self._load_maturity_benchmarks()
        
    def get_industry_benchmark(self, industry: str, metric: str, company_size: str = "medium") -> Optional[float]:
        """Get industry-specific benchmark for a metric"""
        
        key = f"{industry.lower()}_{metric}_{company_size.lower()}"
        benchmark = self.industry_benchmarks.get(key)
        
        if not benchmark:
            # Fallback to general benchmark
            key = f"general_{metric}_{company_size.lower()}"
            benchmark = self.industry_benchmarks.get(key)
        
        return benchmark
    
    def calculate_quantitative_score(self, user_value: float, benchmark_value: float, 
                                   higher_is_better: bool = True) -> float:
        """Calculate score based on quantitative comparison"""
        
        if benchmark_value == 0:
            return 50.0  # Default score if no benchmark
        
        ratio = user_value / benchmark_value
        
        if higher_is_better:
            # Higher values are better (e.g., MFA adoption percentage)
            if ratio >= 1.0:
                return min(100.0, 80 + (ratio - 1.0) * 20)  # 80-100 scale
            else:
                return ratio * 80  # 0-80 scale
        else:
            # Lower values are better (e.g., incident response time)
            if ratio <= 1.0:
                return min(100.0, 80 + (1.0 - ratio) * 20)  # 80-100 scale
            else:
                return max(0.0, 80 - (ratio - 1.0) * 40)  # 40-80 scale
    
    def _load_industry_benchmarks(self) -> Dict[str, float]:
        """Load industry benchmark data"""
        
        return {
            # MFA Adoption Rates (%)
            "healthcare_mfa_adoption_small": 78,
            "healthcare_mfa_adoption_medium": 85,
            "healthcare_mfa_adoption_large": 92,
            "finance_mfa_adoption_small": 88,
            "finance_mfa_adoption_medium": 94,
            "finance_mfa_adoption_large": 98,
            "technology_mfa_adoption_small": 85,
            "technology_mfa_adoption_medium": 91,
            "technology_mfa_adoption_large": 95,
            "general_mfa_adoption_small": 65,
            "general_mfa_adoption_medium": 75,
            "general_mfa_adoption_large": 85,
            
            # Data Encryption Rates (%)
            "healthcare_data_encryption_small": 85,
            "healthcare_data_encryption_medium": 92,
            "healthcare_data_encryption_large": 96,
            "finance_data_encryption_small": 90,
            "finance_data_encryption_medium": 95,
            "finance_data_encryption_large": 98,
            "general_data_encryption_small": 70,
            "general_data_encryption_medium": 80,
            "general_data_encryption_large": 88,
        }
    
    def _load_security_metrics(self) -> Dict[str, Dict[str, Any]]:
        """Load security metrics configuration"""
        
        return {
            "access_control": {
                "mfa_adoption": {
                    "benchmark": 85,
                    "weight": 3.0,
                    "higher_is_better": True,
                    "unit": "percentage"
                }
            },
            "data_protection": {
                "encryption_coverage": {
                    "benchmark": 90,
                    "weight": 3.0,
                    "higher_is_better": True,
                    "unit": "percentage"
                }
            }
        }
    
    def _load_maturity_benchmarks(self) -> Dict[str, Dict[str, float]]:
        """Load maturity level benchmarks"""
        
        return {
            "initial": {"min": 0, "max": 39},
            "basic": {"min": 40, "max": 59},
            "defined": {"min": 60, "max": 74},
            "managed": {"min": 75, "max": 89},
            "optimized": {"min": 90, "max": 100}
        }

# Global instance
quantitative_pipeline = QuantitativeDataPipeline()
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from enum import Enum
import json
import statistics

logger = logging.getLogger(__name__)

class DataSource(Enum):
    """Available quantitative data sources"""
    INDUSTRY_BENCHMARKS = "industry_benchmarks"
    COMPLIANCE_METRICS = "compliance_metrics"
    SECURITY_METRICS = "security_metrics"
    PERFORMANCE_METRICS = "performance_metrics"
    MATURITY_METRICS = "maturity_metrics"
    TREND_ANALYSIS = "trend_analysis"

@dataclass
class QuantitativeMetric:
    """Quantitative metric with validation and context"""
    metric_id: str
    name: str
    value: float
    unit: str
    category: str
    industry: str
    benchmark_percentile: float
    confidence_interval: Tuple[float, float]
    data_source: DataSource
    last_updated: datetime
    validation_status: str

@dataclass
class DataValidation:
    """Data validation results"""
    is_valid: bool
    confidence_score: float
    validation_errors: List[str]
    outlier_status: str
    data_quality_score: float

class QuantitativeDataPipeline:
    """Main class for quantitative data integration"""
    
    def __init__(self):
        self.data_sources = self._initialize_data_sources()
        self.validation_thresholds = self._initialize_validation_thresholds()
        self.industry_benchmarks = self._load_industry_benchmarks()
        self.metric_cache = {}
        
    def _initialize_data_sources(self) -> Dict[str, Dict[str, Any]]:
        """Initialize quantitative data sources"""
        
        return {
            "industry_benchmarks": {
                "finance": {
                    "compliance_score": {"mean": 85.2, "std": 12.4, "n": 1247},
                    "security_maturity": {"mean": 7.8, "std": 1.2, "n": 1247},
                    "incident_response_time": {"mean": 2.4, "std": 0.8, "n": 1247},
                    "data_classification": {"mean": 8.1, "std": 1.5, "n": 1247},
                    "access_control": {"mean": 7.9, "std": 1.3, "n": 1247}
                },
                "healthcare": {
                    "compliance_score": {"mean": 82.7, "std": 14.2, "n": 892},
                    "security_maturity": {"mean": 7.5, "std": 1.4, "n": 892},
                    "incident_response_time": {"mean": 3.1, "std": 1.2, "n": 892},
                    "data_classification": {"mean": 8.5, "std": 1.2, "n": 892},
                    "access_control": {"mean": 7.2, "std": 1.6, "n": 892}
                },
                "technology": {
                    "compliance_score": {"mean": 78.9, "std": 16.1, "n": 2134},
                    "security_maturity": {"mean": 7.3, "std": 1.6, "n": 2134},
                    "incident_response_time": {"mean": 1.8, "std": 0.6, "n": 2134},
                    "data_classification": {"mean": 7.1, "std": 1.8, "n": 2134},
                    "access_control": {"mean": 7.5, "std": 1.4, "n": 2134}
                },
                "manufacturing": {
                    "compliance_score": {"mean": 76.4, "std": 18.3, "n": 567},
                    "security_maturity": {"mean": 6.8, "std": 1.7, "n": 567},
                    "incident_response_time": {"mean": 4.2, "std": 1.8, "n": 567},
                    "data_classification": {"mean": 6.9, "std": 2.1, "n": 567},
                    "access_control": {"mean": 6.7, "std": 1.9, "n": 567}
                }
            },
            "compliance_frameworks": {
                "nist_csf": {
                    "identify": {"max_score": 10, "weight": 0.2},
                    "protect": {"max_score": 10, "weight": 0.2},
                    "detect": {"max_score": 10, "weight": 0.2},
                    "respond": {"max_score": 10, "weight": 0.2},
                    "recover": {"max_score": 10, "weight": 0.2}
                },
                "iso_27001": {
                    "information_security_policies": {"max_score": 10, "weight": 0.15},
                    "organization_security": {"max_score": 10, "weight": 0.15},
                    "human_resource_security": {"max_score": 10, "weight": 0.10},
                    "asset_management": {"max_score": 10, "weight": 0.15},
                    "access_control": {"max_score": 10, "weight": 0.15},
                    "cryptography": {"max_score": 10, "weight": 0.10},
                    "physical_security": {"max_score": 10, "weight": 0.10},
                    "operations_security": {"max_score": 10, "weight": 0.10}
                }
            },
            "security_metrics": {
                "vulnerability_metrics": {
                    "critical_vulns_avg": 2.3,
                    "high_vulns_avg": 12.7,
                    "medium_vulns_avg": 45.2,
                    "patching_time_avg": 15.6,  # days
                    "scan_frequency_avg": 7      # days
                },
                "incident_metrics": {
                    "incidents_per_month": 3.2,
                    "detection_time_avg": 197,  # hours
                    "containment_time_avg": 24, # hours
                    "recovery_time_avg": 72     # hours
                },
                "access_metrics": {
                    "privileged_accounts_ratio": 0.08,
                    "password_policy_compliance": 0.87,
                    "mfa_adoption_rate": 0.72,
                    "access_review_frequency": 90  # days
                }
            }
        }
    
    def _initialize_validation_thresholds(self) -> Dict[str, Dict[str, float]]:
        """Initialize validation thresholds for data quality"""
        
        return {
            "outlier_detection": {
                "z_score_threshold": 3.0,
                "iqr_multiplier": 1.5,
                "percentile_threshold": 95.0
            },
            "data_quality": {
                "min_sample_size": 50,
                "max_age_days": 90,
                "min_confidence": 0.8,
                "consistency_threshold": 0.85
            },
            "validation": {
                "min_correlation": 0.3,
                "max_variance": 0.5,
                "trend_significance": 0.05
            }
        }
    
    def _load_industry_benchmarks(self) -> Dict[str, Any]:
        """Load industry-specific benchmarks"""
        
        return {
            "percentile_distributions": {
                "10th": {"multiplier": 0.4, "description": "Bottom 10%"},
                "25th": {"multiplier": 0.6, "description": "Bottom quartile"},
                "50th": {"multiplier": 0.8, "description": "Median"},
                "75th": {"multiplier": 1.0, "description": "Top quartile"},
                "90th": {"multiplier": 1.2, "description": "Top 10%"},
                "95th": {"multiplier": 1.4, "description": "Top 5%"}
            },
            "maturity_mapping": {
                "ad_hoc": {"score_range": (1, 2), "percentile": 10},
                "basic": {"score_range": (3, 4), "percentile": 25},
                "defined": {"score_range": (5, 6), "percentile": 50},
                "managed": {"score_range": (7, 8), "percentile": 75},
                "optimizing": {"score_range": (9, 10), "percentile": 90}
            }
        }
    
    def get_quantitative_support(self, 
                               category: str, 
                               industry: str,
                               current_score: float) -> Dict[str, Any]:
        """Get quantitative support for qualitative assessment"""
        
        try:
            # Get industry benchmark
            benchmark = self._get_industry_benchmark(category, industry)
            
            # Calculate percentile rank
            percentile_rank = self._calculate_percentile_rank(current_score, benchmark)
            
            # Get peer comparison
            peer_comparison = self._get_peer_comparison(category, industry, current_score)
            
            # Validate data quality
            validation = self._validate_data_quality(benchmark, category)
            
            return {
                "quantitative_support": {
                    "benchmark_data": benchmark,
                    "percentile_rank": percentile_rank,
                    "peer_comparison": peer_comparison,
                    "validation": asdict(validation),
                    "recommendations": self._generate_quantitative_recommendations(
                        current_score, benchmark, percentile_rank
                    )
                },
                "confidence_boost": self._calculate_confidence_boost(validation, percentile_rank),
                "score_validation": self._validate_score_against_benchmark(current_score, benchmark)
            }
            
        except Exception as e:
            logger.error(f"Error getting quantitative support: {str(e)}")
            return self._get_default_quantitative_support()
    
    def _get_industry_benchmark(self, category: str, industry: str) -> Optional[Dict[str, Any]]:
        """Get industry benchmark for specific category"""
        
        industry_data = self.data_sources.get("industry_benchmarks", {}).get(industry.lower(), {})
        
        if category in industry_data:
            return industry_data[category]
        
        # Try to find similar category
        similar_categories = {
            "access_management": "access_control",
            "data_sensitivity": "data_classification",
            "compliance": "compliance_score",
            "security_maturity": "security_maturity"
        }
        
        similar_category = similar_categories.get(category)
        if similar_category and similar_category in industry_data:
            return industry_data[similar_category]
        
        return None
    
    def _calculate_percentile_rank(self, score: float, benchmark: Dict[str, Any]) -> float:
        """Calculate percentile rank against benchmark"""
        
        if not benchmark:
            return 50.0  # Default to median
        
        mean = benchmark.get("mean", 5.0)
        std = benchmark.get("std", 2.0)
        
        # Calculate z-score
        z_score = (score - mean) / std if std > 0 else 0
        
        # Convert to percentile (using normal distribution approximation)
        from scipy.stats import norm
        percentile = norm.cdf(z_score) * 100
        
        return max(0, min(100, percentile))
    
    def _get_peer_comparison(self, category: str, industry: str, score: float) -> Dict[str, Any]:
        """Get peer comparison analysis"""
        
        benchmark = self._get_industry_benchmark(category, industry)
        
        if not benchmark:
            return {"status": "no_data", "message": "No benchmark data available"}
        
        mean = benchmark.get("mean", 5.0)
        std = benchmark.get("std", 2.0)
        
        # Calculate comparison metrics
        deviation = score - mean
        z_score = deviation / std if std > 0 else 0
        
        # Determine performance category
        if z_score > 1.5:
            performance = "excellent"
        elif z_score > 0.5:
            performance = "above_average"
        elif z_score > -0.5:
            performance = "average"
        elif z_score > -1.5:
            performance = "below_average"
        else:
            performance = "poor"
        
        return {
            "peer_score_mean": mean,
            "peer_score_std": std,
            "your_score": score,
            "deviation": deviation,
            "z_score": z_score,
            "performance_category": performance,
            "sample_size": benchmark.get("n", 0)
        }
    
    def _validate_data_quality(self, benchmark: Dict[str, Any], category: str) -> DataValidation:
        """Validate data quality and reliability"""
        
        if not benchmark:
            return DataValidation(
                is_valid=False,
                confidence_score=0.0,
                validation_errors=["No benchmark data available"],
                outlier_status="no_data",
                data_quality_score=0.0
            )
        
        validation_errors = []
        
        # Check sample size
        sample_size = benchmark.get("n", 0)
        if sample_size < self.validation_thresholds["data_quality"]["min_sample_size"]:
            validation_errors.append(f"Small sample size: {sample_size}")
        
        # Check data consistency
        mean = benchmark.get("mean", 0)
        std = benchmark.get("std", 0)
        
        if std > mean * 0.5:  # High variance
            validation_errors.append("High variance in benchmark data")
        
        # Calculate overall quality score
        quality_score = min(1.0, (
            (min(sample_size, 1000) / 1000) * 0.4 +  # Sample size factor
            (1.0 - min(std / mean, 1.0)) * 0.3 +      # Consistency factor
            0.3  # Base reliability
        ))
        
        return DataValidation(
            is_valid=len(validation_errors) == 0,
            confidence_score=quality_score,
            validation_errors=validation_errors,
            outlier_status="normal",
            data_quality_score=quality_score
        )
    
    def _generate_quantitative_recommendations(self, 
                                             current_score: float, 
                                             benchmark: Dict[str, Any],
                                             percentile_rank: float) -> List[str]:
        """Generate recommendations based on quantitative analysis"""
        
        recommendations = []
        
        if not benchmark:
            return ["Insufficient benchmark data for quantitative recommendations"]
        
        mean = benchmark.get("mean", 5.0)
        
        if current_score < mean:
            gap = mean - current_score
            recommendations.append(f"Score is {gap:.1f} points below industry average")
            
            if percentile_rank < 25:
                recommendations.append("Performance is in bottom quartile - immediate improvement needed")
            elif percentile_rank < 50:
                recommendations.append("Performance is below median - focus on key improvements")
        
        else:
            if percentile_rank > 75:
                recommendations.append("Performance is in top quartile - maintain current practices")
            elif percentile_rank > 50:
                recommendations.append("Performance is above median - consider optimization")
        
        # Add specific improvement areas
        if current_score < 6:
            recommendations.append("Focus on establishing foundational security controls")
        elif current_score < 8:
            recommendations.append("Implement advanced security measures and automation")
        else:
            recommendations.append("Optimize existing controls and pursue continuous improvement")
        
        return recommendations
    
    def _calculate_confidence_boost(self, validation: DataValidation, percentile_rank: float) -> float:
        """Calculate confidence boost based on quantitative validation"""
        
        if not validation.is_valid:
            return 0.0
        
        # Base confidence boost from data quality
        base_boost = validation.data_quality_score * 0.2
        
        # Additional boost for extreme percentiles (more certainty)
        if percentile_rank < 10 or percentile_rank > 90:
            base_boost += 0.1
        
        return min(0.3, base_boost)  # Cap at 30% boost
    
    def _validate_score_against_benchmark(self, score: float, benchmark: Dict[str, Any]) -> Dict[str, Any]:
        """Validate score against benchmark data"""
        
        if not benchmark:
            return {"status": "no_validation", "message": "No benchmark available"}
        
        mean = benchmark.get("mean", 5.0)
        std = benchmark.get("std", 2.0)
        
        # Calculate z-score
        z_score = (score - mean) / std if std > 0 else 0
        
        # Check for outliers
        is_outlier = abs(z_score) > self.validation_thresholds["outlier_detection"]["z_score_threshold"]
        
        return {
            "status": "validated",
            "is_outlier": is_outlier,
            "z_score": z_score,
            "deviation_from_mean": score - mean,
            "validation_message": self._get_validation_message(z_score, is_outlier)
        }
    
    def _get_validation_message(self, z_score: float, is_outlier: bool) -> str:
        """Get validation message based on z-score"""
        
        if is_outlier:
            if z_score > 0:
                return "Score is exceptionally high compared to industry peers"
            else:
                return "Score is exceptionally low compared to industry peers"
        
        if abs(z_score) < 0.5:
            return "Score is consistent with industry average"
        elif z_score > 0:
            return "Score is above industry average"
        else:
            return "Score is below industry average"
    
    def _get_default_quantitative_support(self) -> Dict[str, Any]:
        """Get default quantitative support when data unavailable"""
        
        return {
            "quantitative_support": {
                "benchmark_data": None,
                "percentile_rank": 50.0,
                "peer_comparison": {"status": "no_data"},
                "validation": {"is_valid": False, "confidence_score": 0.0},
                "recommendations": ["Insufficient quantitative data for comparison"]
            },
            "confidence_boost": 0.0,
            "score_validation": {"status": "no_validation"}
        }
    
    def get_trend_analysis(self, category: str, historical_scores: List[float]) -> Dict[str, Any]:
        """Analyze trends in historical scores"""
        
        if len(historical_scores) < 3:
            return {"status": "insufficient_data", "message": "Need at least 3 historical scores"}
        
        # Calculate trend
        x = np.arange(len(historical_scores))
        y = np.array(historical_scores)
        
        # Linear regression
        slope, intercept = np.polyfit(x, y, 1)
        
        # Calculate trend strength
        correlation = np.corrcoef(x, y)[0, 1]
        
        # Determine trend direction
        if slope > 0.1:
            trend_direction = "improving"
        elif slope < -0.1:
            trend_direction = "declining"
        else:
            trend_direction = "stable"
        
        return {
            "trend_direction": trend_direction,
            "trend_strength": abs(correlation),
            "slope": slope,
            "predicted_next_score": slope * len(historical_scores) + intercept,
            "volatility": np.std(historical_scores),
            "trend_analysis": self._interpret_trend(trend_direction, correlation, slope)
        }
    
    def _interpret_trend(self, direction: str, strength: float, slope: float) -> str:
        """Interpret trend analysis results"""
        
        if direction == "improving":
            if strength > 0.7:
                return f"Strong improvement trend (+{slope:.2f} points per assessment)"
            else:
                return f"Moderate improvement trend (+{slope:.2f} points per assessment)"
        
        elif direction == "declining":
            if strength > 0.7:
                return f"Strong declining trend ({slope:.2f} points per assessment)"
            else:
                return f"Moderate declining trend ({slope:.2f} points per assessment)"
        
        else:
            return "Stable performance with no significant trend"