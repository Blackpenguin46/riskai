"""
Data Analysis and Improvement Tracking System

Provides comprehensive analytics, trend analysis, and improvement tracking
capabilities for continuous security posture enhancement.
"""

import logging
import numpy as np
import pandas as pd
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from sqlalchemy import func, desc, and_, or_
from ..database.models import (
    AssessmentHistory, TrendAnalysis, ImprovementTracking, 
    DataAnalytics, BenchmarkComparison, Assessment, SectionScore,
    get_session
)
from ..data_pipeline.quantitative_data import QuantitativeDataPipeline
from ..benchmarks.case_studies import CaseStudyFramework
import json

logger = logging.getLogger(__name__)

@dataclass
class ImprovementInsight:
    """Individual improvement insight"""
    category: str
    current_score: float
    target_score: float
    improvement_potential: float
    priority: str
    estimated_effort: str
    expected_timeline: str
    success_probability: float
    impact_description: str

@dataclass
class TrendInsight:
    """Trend analysis insight"""
    metric: str
    trend_direction: str
    trend_strength: float
    rate_of_change: float
    prediction: float
    confidence: float
    recommendation: str

@dataclass
class AnalyticsReport:
    """Comprehensive analytics report"""
    report_id: str
    company_id: int
    generation_date: datetime
    overall_score: float
    maturity_level: str
    trend_insights: List[TrendInsight]
    improvement_insights: List[ImprovementInsight]
    benchmark_analysis: Dict[str, Any]
    roi_analysis: Dict[str, Any]
    recommendations: List[str]

class ImprovementTracker:
    """Main class for data analysis and improvement tracking"""
    
    def __init__(self):
        self.quantitative_pipeline = QuantitativeDataPipeline()
        self.case_study_framework = CaseStudyFramework()
        self.analysis_cache = {}
        
    def analyze_improvement_opportunities(self, company_id: int) -> List[ImprovementInsight]:
        """Analyze and identify improvement opportunities"""
        
        db = get_session()
        try:
            # Get recent assessment data
            latest_assessment = db.query(Assessment).filter(
                Assessment.company_id == company_id
            ).order_by(Assessment.created_at.desc()).first()
            
            if not latest_assessment:
                return []
            
            # Get section scores
            section_scores = db.query(SectionScore).filter(
                SectionScore.assessment_id == latest_assessment.id
            ).all()
            
            insights = []
            
            for section in section_scores:
                # Calculate improvement potential
                improvement_potential = min(10.0, section.score + 2.0) - section.score
                
                # Determine priority based on score and impact
                if section.score < 5.0:
                    priority = "high"
                elif section.score < 7.0:
                    priority = "medium"
                else:
                    priority = "low"
                
                # Estimate effort and timeline
                effort, timeline = self._estimate_effort_timeline(section.score, improvement_potential)
                
                # Calculate success probability
                success_prob = self._calculate_success_probability(
                    section.score, improvement_potential, company_id
                )
                
                insight = ImprovementInsight(
                    category=section.section_id,
                    current_score=section.score,
                    target_score=min(10.0, section.score + improvement_potential),
                    improvement_potential=improvement_potential,
                    priority=priority,
                    estimated_effort=effort,
                    expected_timeline=timeline,
                    success_probability=success_prob,
                    impact_description=self._generate_impact_description(
                        section.section_id, improvement_potential
                    )
                )
                
                insights.append(insight)
            
            # Sort by priority and impact
            insights.sort(key=lambda x: (
                {"high": 0, "medium": 1, "low": 2}[x.priority],
                -x.improvement_potential
            ))
            
            return insights
            
        except Exception as e:
            logger.error(f"Error analyzing improvement opportunities: {e}")
            return []
        finally:
            db.close()
    
    def _estimate_effort_timeline(self, current_score: float, improvement: float) -> Tuple[str, str]:
        """Estimate effort and timeline for improvement"""
        
        if improvement <= 1.0:
            return "Low", "1-2 months"
        elif improvement <= 2.0:
            return "Medium", "2-4 months"
        else:
            return "High", "4-6 months"
    
    def _calculate_success_probability(self, current_score: float, improvement: float, company_id: int) -> float:
        """Calculate probability of successful improvement"""
        
        # Base probability based on current score
        if current_score < 3.0:
            base_prob = 0.6  # Easier to improve from low baseline
        elif current_score < 6.0:
            base_prob = 0.8  # Moderate improvement potential
        else:
            base_prob = 0.9  # High baseline, incremental improvements
        
        # Adjust based on improvement magnitude
        if improvement > 2.0:
            base_prob *= 0.7  # Large improvements are harder
        elif improvement > 1.0:
            base_prob *= 0.85
        
        # Historical success rate (simplified)
        historical_factor = 0.75  # Assume 75% historical success rate
        
        return min(1.0, base_prob * historical_factor)
    
    def _generate_impact_description(self, section_id: str, improvement: float) -> str:
        """Generate impact description for improvement"""
        
        impact_templates = {
            "access_management": "Improved access controls reduce unauthorized access risk by {:.0f}%",
            "data_sensitivity": "Enhanced data protection reduces data breach risk by {:.0f}%",
            "incident_response": "Faster incident response reduces recovery time by {:.0f}%",
            "security_awareness": "Better security training reduces human error incidents by {:.0f}%",
            "compliance": "Improved compliance reduces regulatory risk by {:.0f}%"
        }
        
        template = impact_templates.get(section_id, "Improvement reduces overall risk by {:.0f}%")
        impact_percentage = improvement * 10  # Convert to percentage
        
        return template.format(impact_percentage)
    
    def perform_trend_analysis(self, company_id: int, days_back: int = 180) -> List[TrendInsight]:
        """Perform comprehensive trend analysis"""
        
        db = get_session()
        try:
            # Get historical data
            cutoff_date = datetime.utcnow() - timedelta(days=days_back)
            history = db.query(AssessmentHistory).filter(
                AssessmentHistory.company_id == company_id,
                AssessmentHistory.snapshot_date >= cutoff_date
            ).order_by(AssessmentHistory.snapshot_date).all()
            
            if len(history) < 3:
                return []
            
            insights = []
            
            # Overall score trend
            overall_scores = [h.overall_score for h in history]
            overall_trend = self._analyze_trend(overall_scores)
            
            insights.append(TrendInsight(
                metric="Overall Security Score",
                trend_direction=overall_trend['direction'],
                trend_strength=overall_trend['strength'],
                rate_of_change=overall_trend['slope'],
                prediction=overall_trend['prediction'],
                confidence=overall_trend['confidence'],
                recommendation=self._generate_trend_recommendation(overall_trend)
            ))
            
            # Section-level trends
            section_trends = self._analyze_section_trends(history)
            
            for section_id, trend_data in section_trends.items():
                if trend_data['strength'] > 0.3:  # Only significant trends
                    insights.append(TrendInsight(
                        metric=f"{section_id} Score",
                        trend_direction=trend_data['direction'],
                        trend_strength=trend_data['strength'],
                        rate_of_change=trend_data['slope'],
                        prediction=trend_data['prediction'],
                        confidence=trend_data['confidence'],
                        recommendation=self._generate_section_trend_recommendation(
                            section_id, trend_data
                        )
                    ))
            
            return insights
            
        except Exception as e:
            logger.error(f"Error performing trend analysis: {e}")
            return []
        finally:
            db.close()
    
    def _analyze_trend(self, values: List[float]) -> Dict[str, Any]:
        """Analyze trend for a series of values"""
        
        if len(values) < 3:
            return {
                'direction': 'insufficient_data',
                'strength': 0.0,
                'slope': 0.0,
                'prediction': values[-1] if values else 0.0,
                'confidence': 0.0
            }
        
        # Linear regression
        x = np.arange(len(values))
        y = np.array(values)
        
        slope, intercept = np.polyfit(x, y, 1)
        correlation = np.corrcoef(x, y)[0, 1] if len(values) > 1 else 0.0
        
        # Determine direction
        if slope > 0.05:
            direction = "improving"
        elif slope < -0.05:
            direction = "declining"
        else:
            direction = "stable"
        
        # Predict next value
        next_prediction = slope * len(values) + intercept
        
        # Calculate confidence
        variance = np.var(values)
        confidence = max(0.0, min(1.0, abs(correlation) * (1 - variance/10)))
        
        return {
            'direction': direction,
            'strength': abs(correlation),
            'slope': slope,
            'prediction': next_prediction,
            'confidence': confidence
        }
    
    def _analyze_section_trends(self, history: List) -> Dict[str, Dict[str, Any]]:
        """Analyze trends for each section"""
        
        section_trends = {}
        
        # Extract section scores from history
        for record in history:
            if record.section_scores:
                for section_id, score in record.section_scores.items():
                    if section_id not in section_trends:
                        section_trends[section_id] = []
                    section_trends[section_id].append(score)
        
        # Analyze each section
        trends = {}
        for section_id, scores in section_trends.items():
            if len(scores) >= 3:
                trends[section_id] = self._analyze_trend(scores)
        
        return trends
    
    def _generate_trend_recommendation(self, trend_data: Dict[str, Any]) -> str:
        """Generate recommendation based on trend analysis"""
        
        direction = trend_data['direction']
        strength = trend_data['strength']
        
        if direction == "improving":
            if strength > 0.7:
                return "Strong positive trend - continue current initiatives"
            else:
                return "Moderate improvement - consider accelerating efforts"
        elif direction == "declining":
            if strength > 0.7:
                return "Strong negative trend - immediate intervention required"
            else:
                return "Moderate decline - review and adjust current practices"
        else:
            return "Stable performance - focus on maintaining current levels"
    
    def _generate_section_trend_recommendation(self, section_id: str, trend_data: Dict[str, Any]) -> str:
        """Generate section-specific trend recommendation"""
        
        direction = trend_data['direction']
        section_actions = {
            "access_management": {
                "improving": "Expand access control automation",
                "declining": "Review access policies and enforcement",
                "stable": "Maintain current access management practices"
            },
            "data_sensitivity": {
                "improving": "Enhance data classification automation",
                "declining": "Strengthen data protection measures",
                "stable": "Continue data governance practices"
            },
            "incident_response": {
                "improving": "Optimize incident response procedures",
                "declining": "Review incident response capabilities",
                "stable": "Maintain incident response readiness"
            }
        }
        
        default_actions = {
            "improving": f"Continue improving {section_id}",
            "declining": f"Address declining {section_id}",
            "stable": f"Maintain {section_id} practices"
        }
        
        return section_actions.get(section_id, default_actions)[direction]
    
    def track_improvement_initiative(self, 
                                   company_id: int,
                                   initiative_name: str,
                                   description: str,
                                   category: str,
                                   target_score: float,
                                   timeline: datetime,
                                   assigned_to: str = "",
                                   budget: float = 0.0) -> int:
        """Track a new improvement initiative"""
        
        db = get_session()
        try:
            # Get baseline score
            latest_assessment = db.query(Assessment).filter(
                Assessment.company_id == company_id
            ).order_by(Assessment.created_at.desc()).first()
            
            baseline_score = latest_assessment.overall_score if latest_assessment else 0.0
            
            # Create improvement tracking record
            improvement = ImprovementTracking(
                company_id=company_id,
                initiative_name=initiative_name,
                description=description,
                category=category,
                baseline_score=baseline_score,
                target_score=target_score,
                target_date=timeline,
                assigned_to=assigned_to,
                budget_allocated=budget
            )
            
            db.add(improvement)
            db.commit()
            db.refresh(improvement)
            
            logger.info(f"Started tracking improvement initiative: {initiative_name}")
            return improvement.id
            
        except Exception as e:
            logger.error(f"Error tracking improvement initiative: {e}")
            db.rollback()
            return -1
        finally:
            db.close()
    
    def update_improvement_progress(self, 
                                  improvement_id: int,
                                  current_score: float,
                                  status: str,
                                  budget_spent: float = 0.0) -> bool:
        """Update progress on an improvement initiative"""
        
        db = get_session()
        try:
            improvement = db.query(ImprovementTracking).filter(
                ImprovementTracking.id == improvement_id
            ).first()
            
            if not improvement:
                return False
            
            improvement.current_score = current_score
            improvement.status = status
            improvement.budget_spent = budget_spent
            
            # Calculate impact percentage
            if improvement.baseline_score and improvement.target_score:
                total_improvement = improvement.target_score - improvement.baseline_score
                current_improvement = current_score - improvement.baseline_score
                improvement.impact_percentage = (current_improvement / total_improvement) * 100
            
            # Set completion date if completed
            if status == "completed":
                improvement.completion_date = datetime.utcnow()
            
            db.commit()
            return True
            
        except Exception as e:
            logger.error(f"Error updating improvement progress: {e}")
            db.rollback()
            return False
        finally:
            db.close()
    
    def get_improvement_dashboard(self, company_id: int) -> Dict[str, Any]:
        """Get improvement tracking dashboard data"""
        
        db = get_session()
        try:
            # Get all improvements
            improvements = db.query(ImprovementTracking).filter(
                ImprovementTracking.company_id == company_id
            ).all()
            
            # Calculate statistics
            total_improvements = len(improvements)
            completed_improvements = len([i for i in improvements if i.status == "completed"])
            in_progress_improvements = len([i for i in improvements if i.status == "in_progress"])
            
            # Calculate ROI
            total_budget = sum(i.budget_allocated or 0 for i in improvements)
            total_spent = sum(i.budget_spent or 0 for i in improvements)
            
            # Get recent trends
            recent_trends = self.perform_trend_analysis(company_id, days_back=90)
            
            # Get improvement opportunities
            opportunities = self.analyze_improvement_opportunities(company_id)
            
            return {
                "summary": {
                    "total_initiatives": total_improvements,
                    "completed": completed_improvements,
                    "in_progress": in_progress_improvements,
                    "completion_rate": (completed_improvements / total_improvements) * 100 if total_improvements > 0 else 0,
                    "budget_utilization": (total_spent / total_budget) * 100 if total_budget > 0 else 0
                },
                "active_initiatives": [
                    {
                        "id": i.id,
                        "name": i.initiative_name,
                        "category": i.category,
                        "status": i.status,
                        "progress": i.impact_percentage or 0,
                        "target_date": i.target_date.isoformat() if i.target_date else None,
                        "assigned_to": i.assigned_to
                    }
                    for i in improvements if i.status != "completed"
                ],
                "recent_trends": [asdict(trend) for trend in recent_trends[:5]],
                "improvement_opportunities": [asdict(opp) for opp in opportunities[:5]]
            }
            
        except Exception as e:
            logger.error(f"Error getting improvement dashboard: {e}")
            return {"error": "Failed to load dashboard data"}
        finally:
            db.close()
    
    def generate_comprehensive_report(self, company_id: int) -> AnalyticsReport:
        """Generate comprehensive analytics report"""
        
        db = get_session()
        try:
            # Get latest assessment
            latest_assessment = db.query(Assessment).filter(
                Assessment.company_id == company_id
            ).order_by(Assessment.created_at.desc()).first()
            
            if not latest_assessment:
                raise ValueError("No assessment data available")
            
            # Generate report components
            trend_insights = self.perform_trend_analysis(company_id)
            improvement_insights = self.analyze_improvement_opportunities(company_id)
            
            # Get benchmark analysis
            benchmark_data = self.quantitative_pipeline.get_quantitative_support(
                "overall_score", 
                "technology",  # Default industry
                latest_assessment.overall_score
            )
            
            # Calculate ROI analysis
            roi_analysis = self._calculate_roi_analysis(company_id)
            
            # Generate recommendations
            recommendations = self._generate_comprehensive_recommendations(
                trend_insights, improvement_insights, benchmark_data
            )
            
            report = AnalyticsReport(
                report_id=f"report_{company_id}_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}",
                company_id=company_id,
                generation_date=datetime.utcnow(),
                overall_score=latest_assessment.overall_score,
                maturity_level=latest_assessment.maturity_level,
                trend_insights=trend_insights,
                improvement_insights=improvement_insights,
                benchmark_analysis=benchmark_data,
                roi_analysis=roi_analysis,
                recommendations=recommendations
            )
            
            return report
            
        except Exception as e:
            logger.error(f"Error generating comprehensive report: {e}")
            raise
        finally:
            db.close()
    
    def _calculate_roi_analysis(self, company_id: int) -> Dict[str, Any]:
        """Calculate ROI analysis for improvements"""
        
        db = get_session()
        try:
            improvements = db.query(ImprovementTracking).filter(
                ImprovementTracking.company_id == company_id,
                ImprovementTracking.status == "completed"
            ).all()
            
            if not improvements:
                return {"message": "No completed improvements for ROI analysis"}
            
            total_investment = sum(i.budget_spent or 0 for i in improvements)
            total_improvement = sum(
                (i.current_score - i.baseline_score) for i in improvements
                if i.current_score and i.baseline_score
            )
            
            # Estimate value of improvements (simplified)
            estimated_value = total_improvement * 10000  # $10k per point improvement
            
            roi_percentage = ((estimated_value - total_investment) / total_investment) * 100 if total_investment > 0 else 0
            
            return {
                "total_investment": total_investment,
                "estimated_value": estimated_value,
                "roi_percentage": roi_percentage,
                "improvement_score": total_improvement,
                "completed_initiatives": len(improvements)
            }
            
        except Exception as e:
            logger.error(f"Error calculating ROI analysis: {e}")
            return {"error": "Failed to calculate ROI"}
        finally:
            db.close()
    
    def _generate_comprehensive_recommendations(self, 
                                              trends: List[TrendInsight],
                                              improvements: List[ImprovementInsight],
                                              benchmark: Dict[str, Any]) -> List[str]:
        """Generate comprehensive recommendations"""
        
        recommendations = []
        
        # Trend-based recommendations
        declining_trends = [t for t in trends if t.trend_direction == "declining"]
        if declining_trends:
            recommendations.append(f"Address {len(declining_trends)} declining trend(s) immediately")
        
        # Improvement-based recommendations
        high_priority_improvements = [i for i in improvements if i.priority == "high"]
        if high_priority_improvements:
            recommendations.append(f"Focus on {len(high_priority_improvements)} high-priority improvement areas")
        
        # Benchmark-based recommendations
        benchmark_recommendations = benchmark.get("quantitative_support", {}).get("recommendations", [])
        recommendations.extend(benchmark_recommendations[:2])
        
        # Generic recommendations
        recommendations.extend([
            "Implement continuous monitoring for sustained improvement",
            "Regular assessment cycles to track progress",
            "Invest in security awareness training",
            "Consider automation for repetitive security tasks"
        ])
        
        return recommendations[:8]  # Limit to 8 recommendations