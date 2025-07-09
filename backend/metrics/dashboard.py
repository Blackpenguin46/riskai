"""
Metrics Dashboard Module

Provides performance tracking, validation metrics, and statistical analysis
for the risk assessment system.
"""

import logging
import json
from datetime import datetime, timedelta
from typing import Dict, List, Optional, Tuple, Any
from dataclasses import dataclass, asdict
from collections import defaultdict
import numpy as np
from scipy import stats
from sklearn.metrics import mean_squared_error, mean_absolute_error

logger = logging.getLogger(__name__)

@dataclass
class AssessmentMetrics:
    """Metrics for a single risk assessment"""
    assessment_id: str
    timestamp: datetime
    overall_score: float
    confidence_interval: Tuple[float, float]
    category_scores: Dict[str, float]
    processing_time: float
    company_profile: Dict[str, Any]
    
@dataclass
class SystemMetrics:
    """Aggregated system-wide metrics"""
    total_assessments: int
    avg_processing_time: float
    avg_overall_score: float
    score_variance: float
    consistency_score: float
    reliability_score: float
    last_updated: datetime

class MetricsDashboard:
    """Main class for tracking and analyzing system metrics"""
    
    def __init__(self):
        self.assessment_history: List[AssessmentMetrics] = []
        self.industry_benchmarks: Dict[str, Dict[str, float]] = {}
        self.performance_thresholds = {
            'processing_time_max': 30.0,  # seconds
            'consistency_min': 0.8,       # correlation coefficient
            'reliability_min': 0.85,      # test-retest reliability
            'score_variance_max': 15.0    # maximum acceptable variance
        }
        
    def record_assessment(self, assessment_data: Dict[str, Any]) -> None:
        """Record a new assessment for metrics tracking"""
        try:
            metrics = AssessmentMetrics(
                assessment_id=assessment_data.get('id', f"assessment_{datetime.now().timestamp()}"),
                timestamp=datetime.now(),
                overall_score=assessment_data.get('overall_weighted_score', 0.0),
                confidence_interval=assessment_data.get('confidence_interval', (0.0, 0.0)),
                category_scores={
                    row['id']: row['score'] for row in assessment_data.get('risk_table', [])
                },
                processing_time=assessment_data.get('processing_time', 0.0),
                company_profile=assessment_data.get('company_profile', {})
            )
            
            self.assessment_history.append(metrics)
            
            # Keep only last 1000 assessments for performance
            if len(self.assessment_history) > 1000:
                self.assessment_history = self.assessment_history[-1000:]
                
            logger.info(f"Recorded assessment metrics for {metrics.assessment_id}")
            
        except Exception as e:
            logger.error(f"Error recording assessment metrics: {str(e)}")
    
    def calculate_system_metrics(self) -> SystemMetrics:
        """Calculate aggregated system-wide metrics"""
        if not self.assessment_history:
            return SystemMetrics(
                total_assessments=0,
                avg_processing_time=0.0,
                avg_overall_score=0.0,
                score_variance=0.0,
                consistency_score=0.0,
                reliability_score=0.0,
                last_updated=datetime.now()
            )
        
        # Basic statistics
        scores = [a.overall_score for a in self.assessment_history]
        processing_times = [a.processing_time for a in self.assessment_history]
        
        # Calculate consistency (correlation between similar assessments)
        consistency_score = self._calculate_consistency_score()
        
        # Calculate reliability (test-retest reliability)
        reliability_score = self._calculate_reliability_score()
        
        return SystemMetrics(
            total_assessments=len(self.assessment_history),
            avg_processing_time=np.mean(processing_times),
            avg_overall_score=np.mean(scores),
            score_variance=np.var(scores),
            consistency_score=consistency_score,
            reliability_score=reliability_score,
            last_updated=datetime.now()
        )
    
    def _calculate_consistency_score(self) -> float:
        """Calculate consistency score based on similar company profiles"""
        if len(self.assessment_history) < 10:
            return 0.0
        
        try:
            # Group assessments by industry and size
            industry_groups = defaultdict(list)
            for assessment in self.assessment_history:
                industry = assessment.company_profile.get('industry', 'unknown')
                size = assessment.company_profile.get('size', 'unknown')
                key = f"{industry}_{size}"
                industry_groups[key].append(assessment.overall_score)
            
            # Calculate within-group consistency
            consistency_scores = []
            for group_scores in industry_groups.values():
                if len(group_scores) >= 3:
                    # Calculate coefficient of variation (std/mean)
                    cv = np.std(group_scores) / np.mean(group_scores) if np.mean(group_scores) > 0 else 0
                    consistency_scores.append(1 - min(cv, 1.0))  # Convert to consistency score
            
            return np.mean(consistency_scores) if consistency_scores else 0.0
            
        except Exception as e:
            logger.error(f"Error calculating consistency score: {str(e)}")
            return 0.0
    
    def _calculate_reliability_score(self) -> float:
        """Calculate reliability score based on repeat assessments"""
        if len(self.assessment_history) < 5:
            return 0.0
        
        try:
            # Find assessments with similar profiles (simple heuristic)
            similar_pairs = []
            for i, assessment1 in enumerate(self.assessment_history):
                for j, assessment2 in enumerate(self.assessment_history[i+1:], i+1):
                    if self._are_similar_profiles(assessment1.company_profile, assessment2.company_profile):
                        similar_pairs.append((assessment1.overall_score, assessment2.overall_score))
            
            if len(similar_pairs) >= 3:
                scores1, scores2 = zip(*similar_pairs)
                correlation, _ = stats.pearsonr(scores1, scores2)
                return max(0.0, correlation)
            
            return 0.0
            
        except Exception as e:
            logger.error(f"Error calculating reliability score: {str(e)}")
            return 0.0
    
    def _are_similar_profiles(self, profile1: Dict[str, Any], profile2: Dict[str, Any]) -> bool:
        """Check if two company profiles are similar"""
        key_fields = ['industry', 'size', 'tech_adoption']
        matches = sum(1 for field in key_fields if profile1.get(field) == profile2.get(field))
        return matches >= 2
    
    def get_industry_benchmarks(self, industry: str) -> Dict[str, float]:
        """Get benchmark scores for a specific industry"""
        if industry not in self.industry_benchmarks:
            # Calculate benchmarks from historical data
            industry_assessments = [
                a for a in self.assessment_history 
                if a.company_profile.get('industry') == industry
            ]
            
            if industry_assessments:
                scores = [a.overall_score for a in industry_assessments]
                self.industry_benchmarks[industry] = {
                    'mean': np.mean(scores),
                    'median': np.median(scores),
                    'std': np.std(scores),
                    'percentile_25': np.percentile(scores, 25),
                    'percentile_75': np.percentile(scores, 75),
                    'sample_size': len(scores)
                }
            else:
                # Default benchmarks if no data available
                self.industry_benchmarks[industry] = {
                    'mean': 65.0,
                    'median': 65.0,
                    'std': 10.0,
                    'percentile_25': 55.0,
                    'percentile_75': 75.0,
                    'sample_size': 0
                }
        
        return self.industry_benchmarks[industry]
    
    def validate_assessment_quality(self, assessment_data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate the quality of an assessment"""
        quality_report = {
            'overall_quality': 'good',
            'warnings': [],
            'recommendations': []
        }
        
        try:
            # Check processing time
            processing_time = assessment_data.get('processing_time', 0.0)
            if processing_time > self.performance_thresholds['processing_time_max']:
                quality_report['warnings'].append(f"Processing time ({processing_time:.2f}s) exceeds threshold")
                quality_report['overall_quality'] = 'warning'
            
            # Check score variance
            risk_table = assessment_data.get('risk_table', [])
            if risk_table:
                scores = [row['score'] for row in risk_table]
                score_variance = np.var(scores)
                if score_variance > self.performance_thresholds['score_variance_max']:
                    quality_report['warnings'].append(f"Score variance ({score_variance:.2f}) is high")
                    quality_report['overall_quality'] = 'warning'
            
            # Check confidence intervals
            confidence_interval = assessment_data.get('confidence_interval')
            if confidence_interval:
                interval_width = confidence_interval[1] - confidence_interval[0]
                if interval_width > 20.0:  # More than 20 points uncertainty
                    quality_report['warnings'].append(f"Confidence interval too wide ({interval_width:.2f})")
                    quality_report['recommendations'].append("Consider gathering more detailed responses")
            
            # Check system consistency
            system_metrics = self.calculate_system_metrics()
            if system_metrics.consistency_score < self.performance_thresholds['consistency_min']:
                quality_report['warnings'].append("System consistency below threshold")
                quality_report['overall_quality'] = 'warning'
            
            # Set overall quality based on warnings
            if len(quality_report['warnings']) > 3:
                quality_report['overall_quality'] = 'poor'
            elif len(quality_report['warnings']) > 0:
                quality_report['overall_quality'] = 'warning'
            
        except Exception as e:
            logger.error(f"Error validating assessment quality: {str(e)}")
            quality_report['overall_quality'] = 'error'
            quality_report['warnings'].append(f"Validation error: {str(e)}")
        
        return quality_report
    
    def get_performance_trends(self, days: int = 30) -> Dict[str, Any]:
        """Get performance trends over specified time period"""
        cutoff_date = datetime.now() - timedelta(days=days)
        recent_assessments = [
            a for a in self.assessment_history 
            if a.timestamp >= cutoff_date
        ]
        
        if not recent_assessments:
            return {'error': 'No recent assessments found'}
        
        # Calculate trends
        timestamps = [a.timestamp for a in recent_assessments]
        scores = [a.overall_score for a in recent_assessments]
        processing_times = [a.processing_time for a in recent_assessments]
        
        # Simple linear regression for trends
        time_numeric = [(t - timestamps[0]).total_seconds() / 3600 for t in timestamps]  # hours
        
        score_slope, score_intercept, score_r_value, _, _ = stats.linregress(time_numeric, scores)
        time_slope, time_intercept, time_r_value, _, _ = stats.linregress(time_numeric, processing_times)
        
        return {
            'period_days': days,
            'total_assessments': len(recent_assessments),
            'score_trend': {
                'slope': score_slope,
                'direction': 'improving' if score_slope > 0 else 'declining' if score_slope < 0 else 'stable',
                'correlation': score_r_value
            },
            'processing_time_trend': {
                'slope': time_slope,
                'direction': 'improving' if time_slope < 0 else 'declining' if time_slope > 0 else 'stable',
                'correlation': time_r_value
            },
            'avg_score': np.mean(scores),
            'avg_processing_time': np.mean(processing_times)
        }
    
    def export_metrics(self) -> Dict[str, Any]:
        """Export all metrics for API consumption"""
        system_metrics = self.calculate_system_metrics()
        
        return {
            'system_metrics': asdict(system_metrics),
            'performance_trends': self.get_performance_trends(),
            'industry_benchmarks': self.industry_benchmarks,
            'recent_assessments': [
                asdict(a) for a in self.assessment_history[-10:]  # Last 10 assessments
            ],
            'thresholds': self.performance_thresholds
        }

# Global instance
metrics_dashboard = MetricsDashboard()