"""
Benchmark Data Collector for RiskAI
Handles collection, import, and validation of benchmark data for GRC tool comparisons
"""

import logging
import csv
import json
from typing import Dict, List, Optional, Any, Union
from datetime import datetime
from sqlalchemy.orm import Session as DBSession

from database.models import get_session
from database.benchmark_models import BenchmarkData, ToolComparison, ROIAnalysis, BenchmarkMethodology

logger = logging.getLogger(__name__)

class BenchmarkDataCollector:
    """Collects and manages benchmark data for GRC tool comparisons"""
    
    @staticmethod
    def add_benchmark_data(
        tool_name: str,
        category: str,
        metric_name: str,
        metric_value: float,
        unit: Optional[str] = None,
        measurement_methodology: Optional[str] = None,
        source_reference: Optional[str] = None
    ) -> Optional[int]:
        """
        Add a new benchmark data point
        
        Args:
            tool_name: Name of the GRC tool
            category: Category of the metric (e.g., 'performance', 'cost', 'coverage')
            metric_name: Name of the metric
            metric_value: Value of the metric
            unit: Unit of measurement (optional)
            measurement_methodology: Description of how the data was collected (optional)
            source_reference: Reference to the data source (optional)
            
        Returns:
            ID of the created benchmark data or None if failed
        """
        try:
            db = get_session()
            
            benchmark = BenchmarkData(
                tool_name=tool_name,
                category=category,
                metric_name=metric_name,
                metric_value=metric_value,
                unit=unit,
                measurement_date=datetime.utcnow(),
                measurement_methodology=measurement_methodology,
                source_reference=source_reference
            )
            
            db.add(benchmark)
            db.commit()
            db.refresh(benchmark)
            
            logger.info(f"Added benchmark data for {tool_name}, {metric_name}: {metric_value}")
            return benchmark.id
            
        except Exception as e:
            logger.error(f"Error adding benchmark data: {str(e)}")
            db.rollback()
            return None
        finally:
            db.close()
    
    @staticmethod
    def add_tool_comparison(
        benchmark_id: int,
        riskai_value: float,
        comparison_value: float,
        industry: Optional[str] = None,
        company_size: Optional[str] = None,
        strengths: Optional[List[str]] = None,
        weaknesses: Optional[List[str]] = None,
        notes: Optional[str] = None
    ) -> Optional[int]:
        """
        Add a comparison between RiskAI and another tool
        
        Args:
            benchmark_id: ID of the benchmark data
            riskai_value: Value for RiskAI
            comparison_value: Value for the comparison tool
            industry: Industry sector (optional)
            company_size: Company size category (optional)
            strengths: List of RiskAI strengths (optional)
            weaknesses: List of RiskAI weaknesses (optional)
            notes: Additional notes (optional)
            
        Returns:
            ID of the created comparison or None if failed
        """
        try:
            db = get_session()
            
            # Calculate percentage difference and determine if RiskAI is better
            percentage_difference = None
            is_better = None
            
            if comparison_value != 0:
                percentage_difference = ((riskai_value - comparison_value) / comparison_value) * 100
                
                # Determine if higher or lower is better based on the metric
                benchmark = db.query(BenchmarkData).filter(BenchmarkData.id == benchmark_id).first()
                if benchmark:
                    # For these categories, lower is better
                    lower_is_better = ["cost", "time", "complexity", "implementation_time"]
                    
                    # Check if the category indicates lower is better
                    if any(term in benchmark.category.lower() for term in lower_is_better):
                        is_better = riskai_value < comparison_value
                    else:
                        # For most metrics, higher is better
                        is_better = riskai_value > comparison_value
            
            comparison = ToolComparison(
                benchmark_id=benchmark_id,
                industry=industry,
                company_size=company_size,
                riskai_value=riskai_value,
                comparison_value=comparison_value,
                percentage_difference=percentage_difference,
                is_better=is_better,
                strengths=strengths,
                weaknesses=weaknesses,
                notes=notes
            )
            
            db.add(comparison)
            db.commit()
            db.refresh(comparison)
            
            logger.info(f"Added tool comparison for benchmark {benchmark_id}")
            return comparison.id
            
        except Exception as e:
            logger.error(f"Error adding tool comparison: {str(e)}")
            db.rollback()
            return None
        finally:
            db.close()
    
    @staticmethod
    def add_roi_analysis(
        company_size: str,
        riskai_cost: float,
        traditional_cost: float,
        riskai_time: float,
        traditional_time: float,
        riskai_effectiveness: float,
        traditional_effectiveness: float,
        assessment_frequency: Optional[int] = None,
        methodology: Optional[str] = None,
        assumptions: Optional[List[str]] = None
    ) -> Optional[int]:
        """
        Add ROI analysis data
        
        Args:
            company_size: Company size category
            riskai_cost: Cost of using RiskAI
            traditional_cost: Cost of traditional GRC approach
            riskai_time: Time spent using RiskAI (hours)
            traditional_time: Time spent using traditional approach (hours)
            riskai_effectiveness: Effectiveness score for RiskAI (0-100)
            traditional_effectiveness: Effectiveness score for traditional approach (0-100)
            assessment_frequency: Number of assessments per year (optional)
            methodology: Description of ROI calculation methodology (optional)
            assumptions: List of assumptions made (optional)
            
        Returns:
            ID of the created ROI analysis or None if failed
        """
        try:
            db = get_session()
            
            # Calculate derived metrics
            cost_savings = traditional_cost - riskai_cost
            cost_savings_percentage = (cost_savings / traditional_cost) * 100 if traditional_cost > 0 else 0
            
            time_savings = traditional_time - riskai_time
            time_savings_percentage = (time_savings / traditional_time) * 100 if traditional_time > 0 else 0
            
            effectiveness_improvement = riskai_effectiveness - traditional_effectiveness
            
            # Calculate ROI
            # ROI = (Gain from Investment - Cost of Investment) / Cost of Investment
            roi_percentage = ((cost_savings + (time_savings * 100)) / riskai_cost) * 100 if riskai_cost > 0 else 0
            
            # Payback period in months
            payback_period = (riskai_cost / (cost_savings + (time_savings * 100))) * 12 if (cost_savings + (time_savings * 100)) > 0 else None
            
            roi_analysis = ROIAnalysis(
                company_size=company_size,
                assessment_frequency=assessment_frequency,
                riskai_cost=riskai_cost,
                traditional_cost=traditional_cost,
                cost_savings=cost_savings,
                cost_savings_percentage=cost_savings_percentage,
                riskai_time=riskai_time,
                traditional_time=traditional_time,
                time_savings=time_savings,
                time_savings_percentage=time_savings_percentage,
                riskai_effectiveness=riskai_effectiveness,
                traditional_effectiveness=traditional_effectiveness,
                effectiveness_improvement=effectiveness_improvement,
                roi_percentage=roi_percentage,
                payback_period=payback_period,
                analysis_date=datetime.utcnow(),
                methodology=methodology,
                assumptions=assumptions
            )
            
            db.add(roi_analysis)
            db.commit()
            db.refresh(roi_analysis)
            
            logger.info(f"Added ROI analysis for {company_size} company")
            return roi_analysis.id
            
        except Exception as e:
            logger.error(f"Error adding ROI analysis: {str(e)}")
            db.rollback()
            return None
        finally:
            db.close()
    
    @staticmethod
    def add_benchmark_methodology(
        name: str,
        description: str,
        data_collection_method: str,
        sample_size: Optional[int] = None,
        date_range: Optional[str] = None,
        limitations: Optional[List[str]] = None,
        sources: Optional[List[str]] = None
    ) -> Optional[int]:
        """
        Add benchmark methodology information
        
        Args:
            name: Name of the methodology
            description: Description of the methodology
            data_collection_method: Method used to collect data
            sample_size: Size of the sample (optional)
            date_range: Date range of the data (optional)
            limitations: List of limitations (optional)
            sources: List of sources (optional)
            
        Returns:
            ID of the created methodology or None if failed
        """
        try:
            db = get_session()
            
            methodology = BenchmarkMethodology(
                name=name,
                description=description,
                data_collection_method=data_collection_method,
                sample_size=sample_size,
                date_range=date_range,
                limitations=limitations,
                sources=sources,
                created_at=datetime.utcnow(),
                updated_at=datetime.utcnow()
            )
            
            db.add(methodology)
            db.commit()
            db.refresh(methodology)
            
            logger.info(f"Added benchmark methodology: {name}")
            return methodology.id
            
        except Exception as e:
            logger.error(f"Error adding benchmark methodology: {str(e)}")
            db.rollback()
            return None
        finally:
            db.close()
    
    @staticmethod
    def import_benchmark_data_from_csv(file_path: str) -> Dict[str, Any]:
        """
        Import benchmark data from a CSV file
        
        Args:
            file_path: Path to the CSV file
            
        Returns:
            Dictionary with import results
        """
        try:
            db = get_session()
            
            results = {
                "total": 0,
                "successful": 0,
                "failed": 0,
                "errors": []
            }
            
            with open(file_path, 'r', newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                
                for row in reader:
                    results["total"] += 1
                    
                    try:
                        # Extract and validate required fields
                        tool_name = row.get('tool_name')
                        category = row.get('category')
                        metric_name = row.get('metric_name')
                        metric_value = float(row.get('metric_value', 0))
                        
                        if not all([tool_name, category, metric_name]):
                            raise ValueError("Missing required fields")
                        
                        # Extract optional fields
                        unit = row.get('unit')
                        methodology = row.get('methodology')
                        source = row.get('source')
                        
                        # Add benchmark data
                        benchmark_id = BenchmarkDataCollector.add_benchmark_data(
                            tool_name=tool_name,
                            category=category,
                            metric_name=metric_name,
                            metric_value=metric_value,
                            unit=unit,
                            measurement_methodology=methodology,
                            source_reference=source
                        )
                        
                        if benchmark_id:
                            # Check if comparison data is available
                            if 'riskai_value' in row and row['riskai_value']:
                                riskai_value = float(row.get('riskai_value', 0))
                                
                                # Add tool comparison
                                BenchmarkDataCollector.add_tool_comparison(
                                    benchmark_id=benchmark_id,
                                    riskai_value=riskai_value,
                                    comparison_value=metric_value,
                                    industry=row.get('industry'),
                                    company_size=row.get('company_size'),
                                    strengths=row.get('strengths', '').split('|') if row.get('strengths') else None,
                                    weaknesses=row.get('weaknesses', '').split('|') if row.get('weaknesses') else None,
                                    notes=row.get('notes')
                                )
                            
                            results["successful"] += 1
                        else:
                            results["failed"] += 1
                            results["errors"].append(f"Failed to add benchmark data for {tool_name}, {metric_name}")
                    
                    except Exception as e:
                        results["failed"] += 1
                        results["errors"].append(f"Error processing row: {str(e)}")
            
            logger.info(f"Imported {results['successful']} benchmark data points from CSV")
            return results
            
        except Exception as e:
            logger.error(f"Error importing benchmark data from CSV: {str(e)}")
            return {
                "total": 0,
                "successful": 0,
                "failed": 0,
                "errors": [str(e)]
            }
        finally:
            db.close()
    
    @staticmethod
    def import_roi_analysis_from_csv(file_path: str) -> Dict[str, Any]:
        """
        Import ROI analysis data from a CSV file
        
        Args:
            file_path: Path to the CSV file
            
        Returns:
            Dictionary with import results
        """
        try:
            results = {
                "total": 0,
                "successful": 0,
                "failed": 0,
                "errors": []
            }
            
            with open(file_path, 'r', newline='', encoding='utf-8') as csvfile:
                reader = csv.DictReader(csvfile)
                
                for row in reader:
                    results["total"] += 1
                    
                    try:
                        # Extract and validate required fields
                        company_size = row.get('company_size')
                        riskai_cost = float(row.get('riskai_cost', 0))
                        traditional_cost = float(row.get('traditional_cost', 0))
                        riskai_time = float(row.get('riskai_time', 0))
                        traditional_time = float(row.get('traditional_time', 0))
                        riskai_effectiveness = float(row.get('riskai_effectiveness', 0))
                        traditional_effectiveness = float(row.get('traditional_effectiveness', 0))
                        
                        if not company_size:
                            raise ValueError("Missing required field: company_size")
                        
                        # Extract optional fields
                        assessment_frequency = int(row.get('assessment_frequency')) if row.get('assessment_frequency') else None
                        methodology = row.get('methodology')
                        assumptions = row.get('assumptions', '').split('|') if row.get('assumptions') else None
                        
                        # Add ROI analysis
                        roi_id = BenchmarkDataCollector.add_roi_analysis(
                            company_size=company_size,
                            riskai_cost=riskai_cost,
                            traditional_cost=traditional_cost,
                            riskai_time=riskai_time,
                            traditional_time=traditional_time,
                            riskai_effectiveness=riskai_effectiveness,
                            traditional_effectiveness=traditional_effectiveness,
                            assessment_frequency=assessment_frequency,
                            methodology=methodology,
                            assumptions=assumptions
                        )
                        
                        if roi_id:
                            results["successful"] += 1
                        else:
                            results["failed"] += 1
                            results["errors"].append(f"Failed to add ROI analysis for {company_size}")
                    
                    except Exception as e:
                        results["failed"] += 1
                        results["errors"].append(f"Error processing row: {str(e)}")
            
            logger.info(f"Imported {results['successful']} ROI analysis records from CSV")
            return results
            
        except Exception as e:
            logger.error(f"Error importing ROI analysis from CSV: {str(e)}")
            return {
                "total": 0,
                "successful": 0,
                "failed": 0,
                "errors": [str(e)]
            }
    
    @staticmethod
    def get_benchmark_data(
        tool_name: Optional[str] = None,
        category: Optional[str] = None,
        metric_name: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get benchmark data with optional filters
        
        Args:
            tool_name: Filter by tool name (optional)
            category: Filter by category (optional)
            metric_name: Filter by metric name (optional)
            
        Returns:
            List of benchmark data dictionaries
        """
        try:
            db = get_session()
            
            query = db.query(BenchmarkData)
            
            if tool_name:
                query = query.filter(BenchmarkData.tool_name == tool_name)
            
            if category:
                query = query.filter(BenchmarkData.category == category)
            
            if metric_name:
                query = query.filter(BenchmarkData.metric_name == metric_name)
            
            benchmarks = query.all()
            
            return [benchmark.to_dict() for benchmark in benchmarks]
            
        except Exception as e:
            logger.error(f"Error getting benchmark data: {str(e)}")
            return []
        finally:
            db.close()
    
    @staticmethod
    def get_tool_comparisons(
        tool_name: Optional[str] = None,
        category: Optional[str] = None,
        industry: Optional[str] = None,
        company_size: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get tool comparisons with optional filters
        
        Args:
            tool_name: Filter by tool name (optional)
            category: Filter by category (optional)
            industry: Filter by industry (optional)
            company_size: Filter by company size (optional)
            
        Returns:
            List of tool comparison dictionaries
        """
        try:
            db = get_session()
            
            query = db.query(ToolComparison).join(BenchmarkData)
            
            if tool_name:
                query = query.filter(BenchmarkData.tool_name == tool_name)
            
            if category:
                query = query.filter(BenchmarkData.category == category)
            
            if industry:
                query = query.filter(ToolComparison.industry == industry)
            
            if company_size:
                query = query.filter(ToolComparison.company_size == company_size)
            
            comparisons = query.all()
            
            return [comparison.to_dict() for comparison in comparisons]
            
        except Exception as e:
            logger.error(f"Error getting tool comparisons: {str(e)}")
            return []
        finally:
            db.close()
    
    @staticmethod
    def get_roi_analysis(company_size: Optional[str] = None) -> List[Dict[str, Any]]:
        """
        Get ROI analysis data with optional filter
        
        Args:
            company_size: Filter by company size (optional)
            
        Returns:
            List of ROI analysis dictionaries
        """
        try:
            db = get_session()
            
            query = db.query(ROIAnalysis)
            
            if company_size:
                query = query.filter(ROIAnalysis.company_size == company_size)
            
            analyses = query.all()
            
            return [analysis.to_dict() for analysis in analyses]
            
        except Exception as e:
            logger.error(f"Error getting ROI analysis: {str(e)}")
            return []
        finally:
            db.close()
    
    @staticmethod
    def get_benchmark_methodologies() -> List[Dict[str, Any]]:
        """
        Get all benchmark methodologies
        
        Returns:
            List of benchmark methodology dictionaries
        """
        try:
            db = get_session()
            
            methodologies = db.query(BenchmarkMethodology).all()
            
            return [methodology.to_dict() for methodology in methodologies]
            
        except Exception as e:
            logger.error(f"Error getting benchmark methodologies: {str(e)}")
            return []
        finally:
            db.close()
    
    @staticmethod
    def validate_benchmark_data() -> Dict[str, Any]:
        """
        Validate benchmark data for consistency and completeness
        
        Returns:
            Dictionary with validation results
        """
        try:
            db = get_session()
            
            results = {
                "total_benchmarks": 0,
                "total_comparisons": 0,
                "total_roi_analyses": 0,
                "issues": []
            }
            
            # Count records
            results["total_benchmarks"] = db.query(BenchmarkData).count()
            results["total_comparisons"] = db.query(ToolComparison).count()
            results["total_roi_analyses"] = db.query(ROIAnalysis).count()
            
            # Check for benchmarks without comparisons
            benchmarks_without_comparisons = db.query(BenchmarkData).outerjoin(
                ToolComparison
            ).filter(
                ToolComparison.id == None
            ).all()
            
            if benchmarks_without_comparisons:
                results["issues"].append({
                    "type": "benchmarks_without_comparisons",
                    "count": len(benchmarks_without_comparisons),
                    "details": [b.to_dict() for b in benchmarks_without_comparisons]
                })
            
            # Check for missing tool coverage
            tools = db.query(BenchmarkData.tool_name).distinct().all()
            tool_names = [t[0] for t in tools]
            
            categories = db.query(BenchmarkData.category).distinct().all()
            category_names = [c[0] for c in categories]
            
            for tool in tool_names:
                for category in category_names:
                    count = db.query(BenchmarkData).filter(
                        BenchmarkData.tool_name == tool,
                        BenchmarkData.category == category
                    ).count()
                    
                    if count == 0:
                        results["issues"].append({
                            "type": "missing_category_for_tool",
                            "tool": tool,
                            "category": category
                        })
            
            # Check for ROI analysis coverage
            company_sizes = ["small", "medium", "large", "enterprise"]
            for size in company_sizes:
                count = db.query(ROIAnalysis).filter(
                    ROIAnalysis.company_size == size
                ).count()
                
                if count == 0:
                    results["issues"].append({
                        "type": "missing_roi_analysis",
                        "company_size": size
                    })
            
            return results
            
        except Exception as e:
            logger.error(f"Error validating benchmark data: {str(e)}")
            return {
                "error": str(e),
                "total_benchmarks": 0,
                "total_comparisons": 0,
                "total_roi_analyses": 0,
                "issues": []
            }
        finally:
            db.close()

# Create a global instance
benchmark_collector = BenchmarkDataCollector()