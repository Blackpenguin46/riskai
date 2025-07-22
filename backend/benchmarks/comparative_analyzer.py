"""
Comparative Analyzer for RiskAI
Analyzes and compares benchmark data between RiskAI and other GRC tools
"""

import logging
import numpy as np
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime

from database.models import get_session
from database.benchmark_models import BenchmarkData, ToolComparison, ROIAnalysis
from benchmarks.benchmark_collector import benchmark_collector

logger = logging.getLogger(__name__)

class ComparativeAnalyzer:
    """Analyzes and compares benchmark data between RiskAI and other GRC tools"""
    
    @staticmethod
    def compare_tools_by_category(
        category: str,
        industry: Optional[str] = None,
        company_size: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Compare RiskAI with other tools for a specific category
        
        Args:
            category: Category to compare (e.g., 'performance', 'cost', 'coverage')
            industry: Filter by industry (optional)
            company_size: Filter by company size (optional)
            
        Returns:
            Dictionary with comparison results
        """
        try:
            db = get_session()
            
            # Get all benchmark data for the category
            query = db.query(BenchmarkData).filter(
                BenchmarkData.category == category
            )
            
            benchmarks = query.all()
            
            # Get all tool names
            tool_names = set([b.tool_name for b in benchmarks])
            
            # Get all metric names for this category
            metric_names = set([b.metric_name for b in benchmarks])
            
            # Build comparison data
            comparison = {
                "category": category,
                "industry": industry,
                "company_size": company_size,
                "tools": [],
                "metrics": list(metric_names),
                "riskai_advantage_percentage": 0,
                "summary": ""
            }
            
            riskai_better_count = 0
            total_comparisons = 0
            
            # For each tool, collect metrics
            for tool_name in tool_names:
                if tool_name == "RiskAI":
                    continue
                
                tool_data = {
                    "tool_name": tool_name,
                    "metrics": {},
                    "overall_comparison": {
                        "better_than_riskai": 0,
                        "worse_than_riskai": 0,
                        "equal_to_riskai": 0,
                        "percentage_difference": 0
                    }
                }
                
                # Get comparisons for this tool
                comparisons = db.query(ToolComparison).join(BenchmarkData).filter(
                    BenchmarkData.tool_name == tool_name,
                    BenchmarkData.category == category
                )
                
                if industry:
                    comparisons = comparisons.filter(ToolComparison.industry == industry)
                
                if company_size:
                    comparisons = comparisons.filter(ToolComparison.company_size == company_size)
                
                comparisons = comparisons.all()
                
                # Process each comparison
                for comparison_item in comparisons:
                    benchmark = db.query(BenchmarkData).filter(
                        BenchmarkData.id == comparison_item.benchmark_id
                    ).first()
                    
                    if not benchmark:
                        continue
                    
                    metric_name = benchmark.metric_name
                    
                    tool_data["metrics"][metric_name] = {
                        "tool_value": comparison_item.comparison_value,
                        "riskai_value": comparison_item.riskai_value,
                        "percentage_difference": comparison_item.percentage_difference,
                        "is_riskai_better": comparison_item.is_better,
                        "unit": benchmark.unit
                    }
                    
                    # Update overall comparison
                    if comparison_item.is_better:
                        tool_data["overall_comparison"]["better_than_riskai"] += 1
                        riskai_better_count += 1
                    elif comparison_item.is_better is False:
                        tool_data["overall_comparison"]["worse_than_riskai"] += 1
                    else:
                        tool_data["overall_comparison"]["equal_to_riskai"] += 1
                    
                    total_comparisons += 1
                
                # Calculate overall percentage difference
                if tool_data["metrics"]:
                    avg_percentage_diff = sum(
                        m["percentage_difference"] for m in tool_data["metrics"].values() if m["percentage_difference"] is not None
                    ) / len(tool_data["metrics"])
                    
                    tool_data["overall_comparison"]["percentage_difference"] = avg_percentage_diff
                
                comparison["tools"].append(tool_data)
            
            # Calculate overall RiskAI advantage
            if total_comparisons > 0:
                comparison["riskai_advantage_percentage"] = (riskai_better_count / total_comparisons) * 100
            
            # Generate summary
            if comparison["riskai_advantage_percentage"] > 75:
                comparison["summary"] = f"RiskAI significantly outperforms other tools in {category}, with a {comparison['riskai_advantage_percentage']:.1f}% advantage."
            elif comparison["riskai_advantage_percentage"] > 50:
                comparison["summary"] = f"RiskAI performs better than most tools in {category}, with a {comparison['riskai_advantage_percentage']:.1f}% advantage."
            elif comparison["riskai_advantage_percentage"] > 25:
                comparison["summary"] = f"RiskAI performs moderately well in {category}, with a {comparison['riskai_advantage_percentage']:.1f}% advantage."
            else:
                comparison["summary"] = f"RiskAI has opportunities for improvement in {category}, with only a {comparison['riskai_advantage_percentage']:.1f}% advantage."
            
            return comparison
            
        except Exception as e:
            logger.error(f"Error comparing tools by category: {str(e)}")
            return {
                "category": category,
                "error": str(e),
                "tools": []
            }
        finally:
            db.close()
    
    @staticmethod
    def compare_all_categories(
        industry: Optional[str] = None,
        company_size: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Compare RiskAI with other tools across all categories
        
        Args:
            industry: Filter by industry (optional)
            company_size: Filter by company size (optional)
            
        Returns:
            Dictionary with comparison results for all categories
        """
        try:
            db = get_session()
            
            # Get all categories
            categories = db.query(BenchmarkData.category).distinct().all()
            category_names = [c[0] for c in categories]
            
            # Compare each category
            results = {
                "industry": industry,
                "company_size": company_size,
                "categories": {},
                "overall_riskai_advantage": 0,
                "summary": ""
            }
            
            total_advantage = 0
            
            for category in category_names:
                category_result = ComparativeAnalyzer.compare_tools_by_category(
                    category=category,
                    industry=industry,
                    company_size=company_size
                )
                
                results["categories"][category] = category_result
                total_advantage += category_result["riskai_advantage_percentage"]
            
            # Calculate overall advantage
            if category_names:
                results["overall_riskai_advantage"] = total_advantage / len(category_names)
            
            # Generate summary
            if results["overall_riskai_advantage"] > 75:
                results["summary"] = f"RiskAI significantly outperforms other GRC tools across all categories, with a {results['overall_riskai_advantage']:.1f}% overall advantage."
            elif results["overall_riskai_advantage"] > 50:
                results["summary"] = f"RiskAI performs better than most GRC tools across categories, with a {results['overall_riskai_advantage']:.1f}% overall advantage."
            elif results["overall_riskai_advantage"] > 25:
                results["summary"] = f"RiskAI performs moderately well compared to other GRC tools, with a {results['overall_riskai_advantage']:.1f}% overall advantage."
            else:
                results["summary"] = f"RiskAI has opportunities for improvement compared to other GRC tools, with only a {results['overall_riskai_advantage']:.1f}% overall advantage."
            
            return results
            
        except Exception as e:
            logger.error(f"Error comparing all categories: {str(e)}")
            return {
                "error": str(e),
                "categories": {}
            }
        finally:
            db.close()
    
    @staticmethod
    def calculate_roi_metrics(company_size: Optional[str] = None) -> Dict[str, Any]:
        """
        Calculate ROI metrics for RiskAI
        
        Args:
            company_size: Filter by company size (optional)
            
        Returns:
            Dictionary with ROI metrics
        """
        try:
            # Get ROI analysis data
            roi_data = benchmark_collector.get_roi_analysis(company_size)
            
            if not roi_data:
                return {
                    "error": "No ROI data available",
                    "company_sizes": []
                }
            
            # Group by company size
            results = {
                "company_sizes": [],
                "average_roi": 0,
                "average_payback_period": 0,
                "average_cost_savings": 0,
                "average_time_savings": 0,
                "summary": ""
            }
            
            company_sizes = set([r["company_size"] for r in roi_data])
            
            total_roi = 0
            total_payback = 0
            total_cost_savings = 0
            total_time_savings = 0
            count = 0
            
            for size in company_sizes:
                size_data = [r for r in roi_data if r["company_size"] == size]
                
                if not size_data:
                    continue
                
                # Calculate averages for this company size
                avg_roi = sum(r["roi_percentage"] for r in size_data if r["roi_percentage"] is not None) / len(size_data)
                avg_payback = sum(r["payback_period"] for r in size_data if r["payback_period"] is not None) / len(size_data) if any(r["payback_period"] is not None for r in size_data) else None
                avg_cost_savings = sum(r["cost_savings_percentage"] for r in size_data) / len(size_data)
                avg_time_savings = sum(r["time_savings_percentage"] for r in size_data) / len(size_data)
                
                size_result = {
                    "company_size": size,
                    "roi_percentage": avg_roi,
                    "payback_period": avg_payback,
                    "cost_savings_percentage": avg_cost_savings,
                    "time_savings_percentage": avg_time_savings,
                    "sample_size": len(size_data)
                }
                
                results["company_sizes"].append(size_result)
                
                total_roi += avg_roi
                if avg_payback is not None:
                    total_payback += avg_payback
                total_cost_savings += avg_cost_savings
                total_time_savings += avg_time_savings
                count += 1
            
            # Calculate overall averages
            if count > 0:
                results["average_roi"] = total_roi / count
                results["average_payback_period"] = total_payback / count if total_payback > 0 else None
                results["average_cost_savings"] = total_cost_savings / count
                results["average_time_savings"] = total_time_savings / count
            
            # Generate summary
            if results["average_roi"] > 200:
                results["summary"] = f"RiskAI provides exceptional ROI with an average return of {results['average_roi']:.1f}%, cost savings of {results['average_cost_savings']:.1f}%, and time savings of {results['average_time_savings']:.1f}%."
            elif results["average_roi"] > 100:
                results["summary"] = f"RiskAI delivers strong ROI with an average return of {results['average_roi']:.1f}%, cost savings of {results['average_cost_savings']:.1f}%, and time savings of {results['average_time_savings']:.1f}%."
            elif results["average_roi"] > 50:
                results["summary"] = f"RiskAI offers good ROI with an average return of {results['average_roi']:.1f}%, cost savings of {results['average_cost_savings']:.1f}%, and time savings of {results['average_time_savings']:.1f}%."
            else:
                results["summary"] = f"RiskAI provides positive ROI with an average return of {results['average_roi']:.1f}%, cost savings of {results['average_cost_savings']:.1f}%, and time savings of {results['average_time_savings']:.1f}%."
            
            if results["average_payback_period"] is not None:
                results["summary"] += f" Average payback period is {results['average_payback_period']:.1f} months."
            
            return results
            
        except Exception as e:
            logger.error(f"Error calculating ROI metrics: {str(e)}")
            return {
                "error": str(e),
                "company_sizes": []
            }
    
    @staticmethod
    def analyze_strengths_and_weaknesses() -> Dict[str, Any]:
        """
        Analyze RiskAI's strengths and weaknesses compared to other tools
        
        Returns:
            Dictionary with strengths and weaknesses analysis
        """
        try:
            db = get_session()
            
            # Get all tool comparisons
            comparisons = db.query(ToolComparison).all()
            
            if not comparisons:
                return {
                    "error": "No comparison data available",
                    "strengths": [],
                    "weaknesses": []
                }
            
            # Collect all strengths and weaknesses
            all_strengths = []
            all_weaknesses = []
            
            for comparison in comparisons:
                if comparison.strengths:
                    all_strengths.extend(comparison.strengths)
                
                if comparison.weaknesses:
                    all_weaknesses.extend(comparison.weaknesses)
            
            # Count occurrences
            strength_counts = {}
            for strength in all_strengths:
                if strength in strength_counts:
                    strength_counts[strength] += 1
                else:
                    strength_counts[strength] = 1
            
            weakness_counts = {}
            for weakness in all_weaknesses:
                if weakness in weakness_counts:
                    weakness_counts[weakness] += 1
                else:
                    weakness_counts[weakness] = 1
            
            # Sort by frequency
            sorted_strengths = sorted(
                strength_counts.items(),
                key=lambda x: x[1],
                reverse=True
            )
            
            sorted_weaknesses = sorted(
                weakness_counts.items(),
                key=lambda x: x[1],
                reverse=True
            )
            
            # Format results
            results = {
                "strengths": [
                    {"strength": s[0], "count": s[1], "percentage": (s[1] / len(comparisons)) * 100}
                    for s in sorted_strengths
                ],
                "weaknesses": [
                    {"weakness": w[0], "count": w[1], "percentage": (w[1] / len(comparisons)) * 100}
                    for w in sorted_weaknesses
                ],
                "total_comparisons": len(comparisons)
            }
            
            # Generate summary
            top_strengths = [s["strength"] for s in results["strengths"][:3]] if results["strengths"] else []
            top_weaknesses = [w["weakness"] for w in results["weaknesses"][:3]] if results["weaknesses"] else []
            
            summary = "RiskAI's key strengths include "
            if top_strengths:
                summary += ", ".join(top_strengths[:-1])
                if len(top_strengths) > 1:
                    summary += f", and {top_strengths[-1]}"
                else:
                    summary += top_strengths[0]
            else:
                summary += "no identified strengths"
            
            summary += ". Areas for improvement include "
            if top_weaknesses:
                summary += ", ".join(top_weaknesses[:-1])
                if len(top_weaknesses) > 1:
                    summary += f", and {top_weaknesses[-1]}"
                else:
                    summary += top_weaknesses[0]
            else:
                summary += "no identified weaknesses"
            
            summary += "."
            
            results["summary"] = summary
            
            return results
            
        except Exception as e:
            logger.error(f"Error analyzing strengths and weaknesses: {str(e)}")
            return {
                "error": str(e),
                "strengths": [],
                "weaknesses": []
            }
        finally:
            db.close()
    
    @staticmethod
    def generate_comparative_report(
        industry: Optional[str] = None,
        company_size: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate a comprehensive comparative report
        
        Args:
            industry: Filter by industry (optional)
            company_size: Filter by company size (optional)
            
        Returns:
            Dictionary with comprehensive report data
        """
        try:
            # Get category comparisons
            category_comparisons = ComparativeAnalyzer.compare_all_categories(
                industry=industry,
                company_size=company_size
            )
            
            # Get ROI metrics
            roi_metrics = ComparativeAnalyzer.calculate_roi_metrics(company_size)
            
            # Get strengths and weaknesses
            strengths_weaknesses = ComparativeAnalyzer.analyze_strengths_and_weaknesses()
            
            # Build comprehensive report
            report = {
                "title": "RiskAI Comparative Analysis Report",
                "generated_at": datetime.utcnow().isoformat(),
                "filters": {
                    "industry": industry,
                    "company_size": company_size
                },
                "executive_summary": "",
                "category_comparisons": category_comparisons,
                "roi_metrics": roi_metrics,
                "strengths_weaknesses": strengths_weaknesses
            }
            
            # Generate executive summary
            executive_summary = f"RiskAI demonstrates a {category_comparisons.get('overall_riskai_advantage', 0):.1f}% overall advantage compared to other GRC tools"
            
            if industry:
                executive_summary += f" in the {industry} industry"
            
            if company_size:
                executive_summary += f" for {company_size} companies"
            
            executive_summary += f". {roi_metrics.get('summary', '')}"
            
            report["executive_summary"] = executive_summary
            
            return report
            
        except Exception as e:
            logger.error(f"Error generating comparative report: {str(e)}")
            return {
                "error": str(e),
                "title": "RiskAI Comparative Analysis Report",
                "generated_at": datetime.utcnow().isoformat()
            }

# Create a global instance
comparative_analyzer = ComparativeAnalyzer()