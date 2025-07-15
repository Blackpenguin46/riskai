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
    
    def get_real_time_dashboard(self) -> Dict[str, Any]:
        """Get comprehensive real-time dashboard data"""
        
        try:
            current_time = datetime.now()
            system_metrics = self.calculate_system_metrics()
            
            # Real-time statistics
            last_24h = [a for a in self.assessment_history 
                       if (current_time - a.timestamp).total_seconds() < 86400]
            last_hour = [a for a in self.assessment_history 
                        if (current_time - a.timestamp).total_seconds() < 3600]
            
            # Calculate real-time metrics
            real_time_metrics = {
                'assessments_last_24h': len(last_24h),
                'assessments_last_hour': len(last_hour),
                'avg_score_24h': np.mean([a.overall_score for a in last_24h]) if last_24h else 0,
                'avg_processing_time_24h': np.mean([a.processing_time for a in last_24h]) if last_24h else 0,
                'current_throughput': len(last_hour),  # assessments per hour
                'system_health': self._calculate_system_health()
            }
            
            # Performance alerts
            alerts = self._generate_performance_alerts()
            
            # Usage patterns
            usage_patterns = self._analyze_usage_patterns()
            
            # Scoring analytics
            scoring_analytics = self._generate_scoring_analytics()
            
            # Industry insights
            industry_insights = self._generate_industry_insights()
            
            return {
                'dashboard_timestamp': current_time.isoformat(),
                'real_time_metrics': real_time_metrics,
                'system_metrics': asdict(system_metrics),
                'performance_alerts': alerts,
                'usage_patterns': usage_patterns,
                'scoring_analytics': scoring_analytics,
                'industry_insights': industry_insights,
                'historical_trends': self.get_performance_trends(7),  # Last 7 days
                'capacity_metrics': self._calculate_capacity_metrics()
            }
            
        except Exception as e:
            logger.error(f"Error generating real-time dashboard: {str(e)}")
            return {'error': str(e), 'dashboard_timestamp': current_time.isoformat()}
    
    def _calculate_system_health(self) -> Dict[str, Any]:
        """Calculate overall system health indicators"""
        
        health_score = 100.0
        health_issues = []
        
        try:
            # Check recent performance
            recent_assessments = self.assessment_history[-50:] if len(self.assessment_history) >= 50 else self.assessment_history
            
            if recent_assessments:
                # Processing time health
                avg_processing_time = np.mean([a.processing_time for a in recent_assessments])
                if avg_processing_time > self.performance_thresholds['processing_time_max']:
                    health_score -= 20
                    health_issues.append("Processing time above threshold")
                
                # Score variance health
                scores = [a.overall_score for a in recent_assessments]
                score_variance = np.var(scores)
                if score_variance > self.performance_thresholds['score_variance_max']:
                    health_score -= 15
                    health_issues.append("High score variance detected")
                
                # Consistency health
                consistency = self._calculate_consistency_score()
                if consistency < self.performance_thresholds['consistency_min']:
                    health_score -= 20
                    health_issues.append("Low consistency detected")
                
                # Reliability health
                reliability = self._calculate_reliability_score()
                if reliability < self.performance_thresholds['reliability_min']:
                    health_score -= 15
                    health_issues.append("Low reliability detected")
            
            # Determine health status
            if health_score >= 90:
                status = "excellent"
            elif health_score >= 75:
                status = "good"
            elif health_score >= 60:
                status = "warning"
            else:
                status = "critical"
            
            return {
                'score': max(0, health_score),
                'status': status,
                'issues': health_issues,
                'last_check': datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Error calculating system health: {str(e)}")
            return {
                'score': 0,
                'status': 'error',
                'issues': [f"Health check failed: {str(e)}"],
                'last_check': datetime.now().isoformat()
            }
    
    def _generate_performance_alerts(self) -> List[Dict[str, Any]]:
        """Generate performance alerts based on thresholds"""
        
        alerts = []
        current_time = datetime.now()
        
        try:
            # Check recent assessments for issues
            recent_assessments = [a for a in self.assessment_history 
                                if (current_time - a.timestamp).total_seconds() < 3600]  # Last hour
            
            if recent_assessments:
                # Processing time alerts
                slow_assessments = [a for a in recent_assessments 
                                  if a.processing_time > self.performance_thresholds['processing_time_max']]
                
                if slow_assessments:
                    alerts.append({
                        'type': 'performance',
                        'severity': 'warning',
                        'message': f"{len(slow_assessments)} assessments with slow processing time in last hour",
                        'timestamp': current_time.isoformat(),
                        'details': {
                            'threshold': self.performance_thresholds['processing_time_max'],
                            'max_time': max(a.processing_time for a in slow_assessments)
                        }
                    })
                
                # Consistency alerts
                if len(recent_assessments) >= 5:
                    scores = [a.overall_score for a in recent_assessments]
                    score_range = max(scores) - min(scores)
                    if score_range > 40:  # More than 40 points difference
                        alerts.append({
                            'type': 'consistency',
                            'severity': 'warning',
                            'message': f"High score variation ({score_range:.1f} points) in recent assessments",
                            'timestamp': current_time.isoformat(),
                            'details': {
                                'score_range': score_range,
                                'min_score': min(scores),
                                'max_score': max(scores)
                            }
                        })
            
            # System capacity alerts
            capacity_metrics = self._calculate_capacity_metrics()
            if capacity_metrics['cpu_usage'] > 80:
                alerts.append({
                    'type': 'capacity',
                    'severity': 'critical',
                    'message': f"High CPU usage detected ({capacity_metrics['cpu_usage']:.1f}%)",
                    'timestamp': current_time.isoformat(),
                    'details': capacity_metrics
                })
            
            return alerts
            
        except Exception as e:
            logger.error(f"Error generating performance alerts: {str(e)}")
            return [{
                'type': 'system',
                'severity': 'error',
                'message': f"Alert generation failed: {str(e)}",
                'timestamp': current_time.isoformat()
            }]
    
    def _analyze_usage_patterns(self) -> Dict[str, Any]:
        """Analyze usage patterns and trends"""
        
        try:
            if not self.assessment_history:
                return {'error': 'No assessment data available'}
            
            current_time = datetime.now()
            
            # Time-based patterns
            hourly_counts = defaultdict(int)
            daily_counts = defaultdict(int)
            industry_counts = defaultdict(int)
            
            for assessment in self.assessment_history:
                hour = assessment.timestamp.hour
                day = assessment.timestamp.strftime('%A')
                industry = assessment.company_profile.get('industry', 'Unknown')
                
                hourly_counts[hour] += 1
                daily_counts[day] += 1
                industry_counts[industry] += 1
            
            # Find peak usage times
            peak_hour = max(hourly_counts.items(), key=lambda x: x[1]) if hourly_counts else (0, 0)
            peak_day = max(daily_counts.items(), key=lambda x: x[1]) if daily_counts else ('Unknown', 0)
            
            # Calculate usage trends
            last_7_days = [a for a in self.assessment_history 
                          if (current_time - a.timestamp).days <= 7]
            last_30_days = [a for a in self.assessment_history 
                           if (current_time - a.timestamp).days <= 30]
            
            return {
                'peak_usage': {
                    'hour': peak_hour[0],
                    'hour_count': peak_hour[1],
                    'day': peak_day[0],
                    'day_count': peak_day[1]
                },
                'volume_trends': {
                    'last_7_days': len(last_7_days),
                    'last_30_days': len(last_30_days),
                    'daily_average': len(last_7_days) / 7 if last_7_days else 0,
                    'growth_rate': self._calculate_growth_rate()
                },
                'industry_distribution': dict(industry_counts),
                'hourly_distribution': dict(hourly_counts),
                'daily_distribution': dict(daily_counts)
            }
            
        except Exception as e:
            logger.error(f"Error analyzing usage patterns: {str(e)}")
            return {'error': str(e)}
    
    def _generate_scoring_analytics(self) -> Dict[str, Any]:
        """Generate comprehensive scoring analytics"""
        
        try:
            if not self.assessment_history:
                return {'error': 'No assessment data available'}
            
            # Score distribution analysis
            all_scores = [a.overall_score for a in self.assessment_history]
            
            # Category-wise analysis
            category_stats = defaultdict(list)
            for assessment in self.assessment_history:
                for category, score in assessment.category_scores.items():
                    category_stats[category].append(score)
            
            category_analysis = {}
            for category, scores in category_stats.items():
                if scores:
                    category_analysis[category] = {
                        'mean': np.mean(scores),
                        'median': np.median(scores),
                        'std': np.std(scores),
                        'min': min(scores),
                        'max': max(scores),
                        'count': len(scores)
                    }
            
            # Confidence analysis
            confidence_widths = []
            for assessment in self.assessment_history:
                if assessment.confidence_interval[1] > assessment.confidence_interval[0]:
                    width = assessment.confidence_interval[1] - assessment.confidence_interval[0]
                    confidence_widths.append(width)
            
            return {
                'score_distribution': {
                    'mean': np.mean(all_scores),
                    'median': np.median(all_scores),
                    'std': np.std(all_scores),
                    'percentiles': {
                        '10th': np.percentile(all_scores, 10),
                        '25th': np.percentile(all_scores, 25),
                        '75th': np.percentile(all_scores, 75),
                        '90th': np.percentile(all_scores, 90)
                    }
                },
                'category_analysis': category_analysis,
                'confidence_analysis': {
                    'avg_interval_width': np.mean(confidence_widths) if confidence_widths else 0,
                    'median_interval_width': np.median(confidence_widths) if confidence_widths else 0,
                    'high_uncertainty_count': sum(1 for w in confidence_widths if w > 20)
                },
                'scoring_trends': self._calculate_scoring_trends()
            }
            
        except Exception as e:
            logger.error(f"Error generating scoring analytics: {str(e)}")
            return {'error': str(e)}
    
    def _generate_industry_insights(self) -> Dict[str, Any]:
        """Generate industry-specific insights"""
        
        try:
            industry_data = defaultdict(lambda: {
                'assessments': [],
                'scores': [],
                'processing_times': []
            })
            
            for assessment in self.assessment_history:
                industry = assessment.company_profile.get('industry', 'Unknown')
                industry_data[industry]['assessments'].append(assessment)
                industry_data[industry]['scores'].append(assessment.overall_score)
                industry_data[industry]['processing_times'].append(assessment.processing_time)
            
            insights = {}
            for industry, data in industry_data.items():
                if len(data['scores']) >= 3:  # Minimum data for meaningful insights
                    insights[industry] = {
                        'count': len(data['assessments']),
                        'avg_score': np.mean(data['scores']),
                        'score_trend': self._calculate_industry_trend(data['assessments']),
                        'avg_processing_time': np.mean(data['processing_times']),
                        'risk_profile': self._determine_industry_risk_profile(data['scores']),
                        'top_categories': self._get_top_categories_by_industry(data['assessments'])
                    }
            
            return {
                'industry_insights': insights,
                'cross_industry_comparison': self._compare_industries(insights),
                'recommendations': self._generate_industry_recommendations(insights)
            }
            
        except Exception as e:
            logger.error(f"Error generating industry insights: {str(e)}")
            return {'error': str(e)}
    
    def _calculate_capacity_metrics(self) -> Dict[str, Any]:
        """Calculate system capacity and resource utilization metrics"""
        
        try:
            import psutil
            import os
            
            # System resource metrics
            cpu_percent = psutil.cpu_percent(interval=1)
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # Assessment processing metrics
            current_time = datetime.now()
            recent_load = len([a for a in self.assessment_history 
                              if (current_time - a.timestamp).total_seconds() < 300])  # Last 5 minutes
            
            return {
                'cpu_usage': cpu_percent,
                'memory_usage': memory.percent,
                'disk_usage': disk.percent,
                'available_memory_gb': memory.available / (1024**3),
                'recent_assessment_load': recent_load,
                'estimated_capacity': 100 - max(cpu_percent, memory.percent),
                'last_updated': current_time.isoformat()
            }
            
        except ImportError:
            # Fallback if psutil not available
            return {
                'cpu_usage': 0,
                'memory_usage': 0,
                'disk_usage': 0,
                'available_memory_gb': 0,
                'recent_assessment_load': 0,
                'estimated_capacity': 100,
                'last_updated': datetime.now().isoformat(),
                'note': 'Resource monitoring unavailable'
            }
        except Exception as e:
            logger.error(f"Error calculating capacity metrics: {str(e)}")
            return {
                'error': str(e),
                'last_updated': datetime.now().isoformat()
            }
    
    def _calculate_growth_rate(self) -> float:
        """Calculate assessment volume growth rate"""
        
        try:
            current_time = datetime.now()
            last_week = [a for a in self.assessment_history 
                        if (current_time - a.timestamp).days <= 7]
            prev_week = [a for a in self.assessment_history 
                        if 7 < (current_time - a.timestamp).days <= 14]
            
            if len(prev_week) == 0:
                return 0.0
            
            current_rate = len(last_week) / 7
            previous_rate = len(prev_week) / 7
            
            if previous_rate == 0:
                return 100.0 if current_rate > 0 else 0.0
            
            growth_rate = ((current_rate - previous_rate) / previous_rate) * 100
            return growth_rate
            
        except Exception as e:
            logger.error(f"Error calculating growth rate: {str(e)}")
            return 0.0
    
    def _calculate_scoring_trends(self) -> Dict[str, Any]:
        """Calculate scoring trends over time"""
        
        try:
            if len(self.assessment_history) < 10:
                return {'insufficient_data': True}
            
            # Sort by timestamp
            sorted_assessments = sorted(self.assessment_history, key=lambda x: x.timestamp)
            
            # Calculate moving averages
            window_size = min(10, len(sorted_assessments) // 4)
            moving_averages = []
            
            for i in range(window_size, len(sorted_assessments)):
                window = sorted_assessments[i-window_size:i]
                avg_score = np.mean([a.overall_score for a in window])
                moving_averages.append(avg_score)
            
            # Calculate trend direction
            if len(moving_averages) >= 2:
                trend_slope = (moving_averages[-1] - moving_averages[0]) / len(moving_averages)
                trend_direction = 'improving' if trend_slope > 0.5 else 'declining' if trend_slope < -0.5 else 'stable'
            else:
                trend_slope = 0
                trend_direction = 'stable'
            
            return {
                'trend_direction': trend_direction,
                'trend_slope': trend_slope,
                'recent_average': np.mean(moving_averages[-5:]) if len(moving_averages) >= 5 else 0,
                'historical_average': np.mean(moving_averages) if moving_averages else 0
            }
            
        except Exception as e:
            logger.error(f"Error calculating scoring trends: {str(e)}")
            return {'error': str(e)}
    
    def _calculate_industry_trend(self, assessments: List[AssessmentMetrics]) -> str:
        """Calculate trend for specific industry"""
        
        if len(assessments) < 5:
            return 'insufficient_data'
        
        sorted_assessments = sorted(assessments, key=lambda x: x.timestamp)
        recent_scores = [a.overall_score for a in sorted_assessments[-5:]]
        older_scores = [a.overall_score for a in sorted_assessments[-10:-5]] if len(sorted_assessments) >= 10 else []
        
        if not older_scores:
            return 'stable'
        
        recent_avg = np.mean(recent_scores)
        older_avg = np.mean(older_scores)
        
        difference = recent_avg - older_avg
        
        if difference > 2:
            return 'improving'
        elif difference < -2:
            return 'declining'
        else:
            return 'stable'
    
    def _determine_industry_risk_profile(self, scores: List[float]) -> str:
        """Determine risk profile for industry based on scores"""
        
        avg_score = np.mean(scores)
        
        if avg_score >= 80:
            return 'low_risk'
        elif avg_score >= 65:
            return 'moderate_risk'
        elif avg_score >= 50:
            return 'high_risk'
        else:
            return 'critical_risk'
    
    def _get_top_categories_by_industry(self, assessments: List[AssessmentMetrics]) -> List[Dict[str, Any]]:
        """Get top performing categories for an industry"""
        
        category_scores = defaultdict(list)
        for assessment in assessments:
            for category, score in assessment.category_scores.items():
                category_scores[category].append(score)
        
        category_averages = [
            {'category': category, 'avg_score': np.mean(scores)}
            for category, scores in category_scores.items()
        ]
        
        return sorted(category_averages, key=lambda x: x['avg_score'], reverse=True)[:5]
    
    def _compare_industries(self, insights: Dict[str, Any]) -> Dict[str, Any]:
        """Compare performance across industries"""
        
        if len(insights) < 2:
            return {'insufficient_data': True}
        
        industries = list(insights.keys())
        scores = [insights[industry]['avg_score'] for industry in industries]
        
        best_industry = industries[scores.index(max(scores))]
        worst_industry = industries[scores.index(min(scores))]
        
        return {
            'best_performing': {
                'industry': best_industry,
                'avg_score': max(scores)
            },
            'worst_performing': {
                'industry': worst_industry,
                'avg_score': min(scores)
            },
            'score_gap': max(scores) - min(scores),
            'industry_count': len(industries)
        }
    
    def _generate_industry_recommendations(self, insights: Dict[str, Any]) -> List[str]:
        """Generate recommendations based on industry insights"""
        
        recommendations = []
        
        for industry, data in insights.items():
            if data['risk_profile'] == 'critical_risk':
                recommendations.append(f"{industry} industry requires immediate attention - critical risk level")
            elif data['risk_profile'] == 'high_risk':
                recommendations.append(f"{industry} industry shows high risk - consider targeted interventions")
            
            if data['score_trend'] == 'declining':
                recommendations.append(f"{industry} industry shows declining scores - investigate causes")
            elif data['score_trend'] == 'improving':
                recommendations.append(f"{industry} industry is improving - share best practices")
        
        return recommendations[:5]  # Limit to top 5

# Global instance
metrics_dashboard = MetricsDashboard()