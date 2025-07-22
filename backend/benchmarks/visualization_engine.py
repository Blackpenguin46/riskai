"""
Visualization Engine for RiskAI Benchmarks
Generates visualization data for benchmark comparisons
"""

import logging
import json
from typing import Dict, List, Optional, Any, Union
from datetime import datetime

from benchmarks.comparative_analyzer import comparative_analyzer
from benchmarks.benchmark_collector import benchmark_collector

logger = logging.getLogger(__name__)

class VisualizationEngine:
    """Generates visualization data for benchmark comparisons"""
    
    @staticmethod
    def generate_tool_comparison_chart(
        category: str,
        metric_name: Optional[str] = None,
        industry: Optional[str] = None,
        company_size: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate data for tool comparison chart
        
        Args:
            category: Category to compare
            metric_name: Specific metric to compare (optional)
            industry: Filter by industry (optional)
            company_size: Filter by company size (optional)
            
        Returns:
            Chart data in a format suitable for frontend visualization
        """
        try:
            # Get comparison data
            comparison = comparative_analyzer.compare_tools_by_category(
                category=category,
                industry=industry,
                company_size=company_size
            )
            
            if "error" in comparison:
                return {
                    "error": comparison["error"],
                    "chart_type": "bar",
                    "data": {}
                }
            
            # Prepare chart data
            chart_data = {
                "chart_type": "bar",
                "title": f"Tool Comparison: {category}",
                "subtitle": "",
                "x_axis_label": "Tools",
                "y_axis_label": "Value",
                "series": []
            }
            
            # Add subtitle based on filters
            subtitle_parts = []
            if industry:
                subtitle_parts.append(f"Industry: {industry}")
            if company_size:
                subtitle_parts.append(f"Company Size: {company_size}")
            
            chart_data["subtitle"] = ", ".join(subtitle_parts) if subtitle_parts else "All Industries & Company Sizes"
            
            # If specific metric is provided, create single metric chart
            if metric_name:
                metric_series = {
                    "name": metric_name,
                    "data": []
                }
                
                # Add RiskAI as first tool
                riskai_value = None
                unit = None
                
                # Extract data for each tool
                tool_names = ["RiskAI"]  # Start with RiskAI
                tool_values = []
                
                for tool in comparison["tools"]:
                    tool_names.append(tool["tool_name"])
                    
                    if metric_name in tool["metrics"]:
                        metric_data = tool["metrics"][metric_name]
                        tool_values.append(metric_data["comparison_value"])
                        
                        if riskai_value is None:
                            riskai_value = metric_data["riskai_value"]
                            unit = metric_data["unit"]
                    else:
                        tool_values.append(None)
                
                # Add RiskAI value at the beginning
                if riskai_value is not None:
                    tool_values.insert(0, riskai_value)
                else:
                    tool_values.insert(0, None)
                
                metric_series["data"] = tool_values
                chart_data["series"].append(metric_series)
                chart_data["categories"] = tool_names
                
                if unit:
                    chart_data["y_axis_label"] = f"{chart_data['y_axis_label']} ({unit})"
            
            # If no specific metric, create multi-metric chart with advantage percentages
            else:
                advantage_series = {
                    "name": "RiskAI Advantage (%)",
                    "data": []
                }
                
                tool_names = []
                
                for tool in comparison["tools"]:
                    tool_names.append(tool["tool_name"])
                    
                    # Calculate overall advantage percentage
                    if tool["overall_comparison"]["percentage_difference"] is not None:
                        advantage_series["data"].append(tool["overall_comparison"]["percentage_difference"])
                    else:
                        advantage_series["data"].append(0)
                
                chart_data["series"].append(advantage_series)
                chart_data["categories"] = tool_names
                chart_data["y_axis_label"] = "Advantage Percentage (%)"
            
            return chart_data
            
        except Exception as e:
            logger.error(f"Error generating tool comparison chart: {str(e)}")
            return {
                "error": str(e),
                "chart_type": "bar",
                "data": {}
            }
    
    @staticmethod
    def generate_category_comparison_chart(
        industry: Optional[str] = None,
        company_size: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate data for category comparison chart
        
        Args:
            industry: Filter by industry (optional)
            company_size: Filter by company size (optional)
            
        Returns:
            Chart data in a format suitable for frontend visualization
        """
        try:
            # Get comparison data for all categories
            comparison = comparative_analyzer.compare_all_categories(
                industry=industry,
                company_size=company_size
            )
            
            if "error" in comparison:
                return {
                    "error": comparison["error"],
                    "chart_type": "radar",
                    "data": {}
                }
            
            # Prepare chart data
            chart_data = {
                "chart_type": "radar",
                "title": "RiskAI Performance by Category",
                "subtitle": "",
                "categories": [],
                "series": []
            }
            
            # Add subtitle based on filters
            subtitle_parts = []
            if industry:
                subtitle_parts.append(f"Industry: {industry}")
            if company_size:
                subtitle_parts.append(f"Company Size: {company_size}")
            
            chart_data["subtitle"] = ", ".join(subtitle_parts) if subtitle_parts else "All Industries & Company Sizes"
            
            # Create series for RiskAI advantage
            advantage_series = {
                "name": "RiskAI Advantage (%)",
                "data": []
            }
            
            # Extract data for each category
            for category, category_data in comparison["categories"].items():
                chart_data["categories"].append(category)
                advantage_series["data"].append(category_data["riskai_advantage_percentage"])
            
            chart_data["series"].append(advantage_series)
            
            return chart_data
            
        except Exception as e:
            logger.error(f"Error generating category comparison chart: {str(e)}")
            return {
                "error": str(e),
                "chart_type": "radar",
                "data": {}
            }
    
    @staticmethod
    def generate_roi_chart(company_size: Optional[str] = None) -> Dict[str, Any]:
        """
        Generate data for ROI analysis chart
        
        Args:
            company_size: Filter by company size (optional)
            
        Returns:
            Chart data in a format suitable for frontend visualization
        """
        try:
            # Get ROI metrics
            roi_metrics = comparative_analyzer.calculate_roi_metrics(company_size)
            
            if "error" in roi_metrics:
                return {
                    "error": roi_metrics["error"],
                    "chart_type": "column",
                    "data": {}
                }
            
            # Prepare chart data
            chart_data = {
                "chart_type": "column",
                "title": "RiskAI ROI Analysis",
                "subtitle": company_size if company_size else "All Company Sizes",
                "categories": [],
                "series": [
                    {
                        "name": "ROI (%)",
                        "data": []
                    },
                    {
                        "name": "Cost Savings (%)",
                        "data": []
                    },
                    {
                        "name": "Time Savings (%)",
                        "data": []
                    }
                ]
            }
            
            # Extract data for each company size
            for size_data in roi_metrics["company_sizes"]:
                chart_data["categories"].append(size_data["company_size"])
                chart_data["series"][0]["data"].append(size_data["roi_percentage"])
                chart_data["series"][1]["data"].append(size_data["cost_savings_percentage"])
                chart_data["series"][2]["data"].append(size_data["time_savings_percentage"])
            
            return chart_data
            
        except Exception as e:
            logger.error(f"Error generating ROI chart: {str(e)}")
            return {
                "error": str(e),
                "chart_type": "column",
                "data": {}
            }
    
    @staticmethod
    def generate_strengths_weaknesses_chart() -> Dict[str, Any]:
        """
        Generate data for strengths and weaknesses chart
        
        Returns:
            Chart data in a format suitable for frontend visualization
        """
        try:
            # Get strengths and weaknesses analysis
            analysis = comparative_analyzer.analyze_strengths_and_weaknesses()
            
            if "error" in analysis:
                return {
                    "error": analysis["error"],
                    "chart_type": "column",
                    "data": {}
                }
            
            # Prepare chart data for strengths
            strengths_chart = {
                "chart_type": "column",
                "title": "RiskAI Strengths",
                "subtitle": "Percentage of Comparisons",
                "categories": [],
                "series": [
                    {
                        "name": "Frequency (%)",
                        "data": []
                    }
                ]
            }
            
            # Extract top 5 strengths
            top_strengths = analysis["strengths"][:5] if len(analysis["strengths"]) > 5 else analysis["strengths"]
            
            for strength in top_strengths:
                strengths_chart["categories"].append(strength["strength"])
                strengths_chart["series"][0]["data"].append(strength["percentage"])
            
            # Prepare chart data for weaknesses
            weaknesses_chart = {
                "chart_type": "column",
                "title": "RiskAI Areas for Improvement",
                "subtitle": "Percentage of Comparisons",
                "categories": [],
                "series": [
                    {
                        "name": "Frequency (%)",
                        "data": []
                    }
                ]
            }
            
            # Extract top 5 weaknesses
            top_weaknesses = analysis["weaknesses"][:5] if len(analysis["weaknesses"]) > 5 else analysis["weaknesses"]
            
            for weakness in top_weaknesses:
                weaknesses_chart["categories"].append(weakness["weakness"])
                weaknesses_chart["series"][0]["data"].append(weakness["percentage"])
            
            return {
                "strengths_chart": strengths_chart,
                "weaknesses_chart": weaknesses_chart
            }
            
        except Exception as e:
            logger.error(f"Error generating strengths and weaknesses chart: {str(e)}")
            return {
                "error": str(e),
                "strengths_chart": {},
                "weaknesses_chart": {}
            }
    
    @staticmethod
    def generate_dashboard_data(
        industry: Optional[str] = None,
        company_size: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate comprehensive dashboard data
        
        Args:
            industry: Filter by industry (optional)
            company_size: Filter by company size (optional)
            
        Returns:
            Dashboard data in a format suitable for frontend visualization
        """
        try:
            # Get all chart data
            category_chart = VisualizationEngine.generate_category_comparison_chart(
                industry=industry,
                company_size=company_size
            )
            
            roi_chart = VisualizationEngine.generate_roi_chart(company_size)
            
            strengths_weaknesses_charts = VisualizationEngine.generate_strengths_weaknesses_chart()
            
            # Get overall comparison data
            comparison = comparative_analyzer.compare_all_categories(
                industry=industry,
                company_size=company_size
            )
            
            # Get ROI metrics
            roi_metrics = comparative_analyzer.calculate_roi_metrics(company_size)
            
            # Prepare dashboard data
            dashboard_data = {
                "title": "RiskAI Benchmark Dashboard",
                "generated_at": datetime.utcnow().isoformat(),
                "filters": {
                    "industry": industry,
                    "company_size": company_size
                },
                "summary": {
                    "overall_advantage": comparison.get("overall_riskai_advantage", 0),
                    "average_roi": roi_metrics.get("average_roi", 0),
                    "average_cost_savings": roi_metrics.get("average_cost_savings", 0),
                    "average_time_savings": roi_metrics.get("average_time_savings", 0)
                },
                "charts": {
                    "category_comparison": category_chart,
                    "roi_analysis": roi_chart,
                    "strengths": strengths_weaknesses_charts.get("strengths_chart", {}),
                    "weaknesses": strengths_weaknesses_charts.get("weaknesses_chart", {})
                }
            }
            
            return dashboard_data
            
        except Exception as e:
            logger.error(f"Error generating dashboard data: {str(e)}")
            return {
                "error": str(e),
                "title": "RiskAI Benchmark Dashboard",
                "generated_at": datetime.utcnow().isoformat()
            }
    
    @staticmethod
    def generate_report_data(
        industry: Optional[str] = None,
        company_size: Optional[str] = None,
        format: str = "json"
    ) -> Union[Dict[str, Any], str]:
        """
        Generate comprehensive report data
        
        Args:
            industry: Filter by industry (optional)
            company_size: Filter by company size (optional)
            format: Output format ('json' or 'html')
            
        Returns:
            Report data in the specified format
        """
        try:
            # Get comparative report
            report = comparative_analyzer.generate_comparative_report(
                industry=industry,
                company_size=company_size
            )
            
            # Get dashboard data
            dashboard = VisualizationEngine.generate_dashboard_data(
                industry=industry,
                company_size=company_size
            )
            
            # Combine data
            combined_report = {
                "title": "RiskAI Comparative Analysis Report",
                "generated_at": datetime.utcnow().isoformat(),
                "filters": {
                    "industry": industry,
                    "company_size": company_size
                },
                "executive_summary": report.get("executive_summary", ""),
                "dashboard": dashboard,
                "detailed_analysis": {
                    "category_comparisons": report.get("category_comparisons", {}),
                    "roi_metrics": report.get("roi_metrics", {}),
                    "strengths_weaknesses": report.get("strengths_weaknesses", {})
                }
            }
            
            # Return in requested format
            if format.lower() == "json":
                return combined_report
            elif format.lower() == "html":
                # Simple HTML conversion (in a real implementation, use a template engine)
                html = f"""
                <!DOCTYPE html>
                <html>
                <head>
                    <title>{combined_report["title"]}</title>
                    <style>
                        body {{ font-family: Arial, sans-serif; margin: 20px; }}
                        h1, h2, h3 {{ color: #333; }}
                        .summary {{ background-color: #f5f5f5; padding: 15px; border-radius: 5px; }}
                        .chart-container {{ margin: 20px 0; }}
                    </style>
                </head>
                <body>
                    <h1>{combined_report["title"]}</h1>
                    <p>Generated: {combined_report["generated_at"]}</p>
                    
                    <div class="summary">
                        <h2>Executive Summary</h2>
                        <p>{combined_report["executive_summary"]}</p>
                    </div>
                    
                    <h2>Dashboard</h2>
                    <p>Overall Advantage: {dashboard["summary"]["overall_advantage"]:.1f}%</p>
                    <p>Average ROI: {dashboard["summary"]["average_roi"]:.1f}%</p>
                    <p>Average Cost Savings: {dashboard["summary"]["average_cost_savings"]:.1f}%</p>
                    <p>Average Time Savings: {dashboard["summary"]["average_time_savings"]:.1f}%</p>
                    
                    <h2>Detailed Analysis</h2>
                    <p>Please refer to the interactive dashboard for detailed analysis.</p>
                </body>
                </html>
                """
                return html
            else:
                return {
                    "error": f"Unsupported format: {format}",
                    "supported_formats": ["json", "html"]
                }
            
        except Exception as e:
            logger.error(f"Error generating report data: {str(e)}")
            return {
                "error": str(e),
                "title": "RiskAI Comparative Analysis Report",
                "generated_at": datetime.utcnow().isoformat()
            }

# Create a global instance
visualization_engine = VisualizationEngine()