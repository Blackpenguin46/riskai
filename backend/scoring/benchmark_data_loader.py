#!/usr/bin/env python3
"""
Benchmark Data Loader
Loads sample industry benchmark data into the database
"""

import logging
import sys
import os
from datetime import datetime, timedelta

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.models import get_session, IndustryBenchmarks

logger = logging.getLogger(__name__)

class BenchmarkDataLoader:
    """Loads benchmark data into the database"""
    
    # Sample industry benchmark data
    SAMPLE_BENCHMARKS = [
        {
            "industry": "financial_services",
            "company_size": "large",
            "average_score": 72.5,
            "standard_deviation": 12.3,
            "sample_size": 245,
            "percentile_10": 55.2,
            "percentile_25": 63.8,
            "percentile_50": 72.5,
            "percentile_75": 81.7,
            "percentile_90": 89.3,
            "data_source": "Industry Security Survey 2024",
            "collection_method": "Anonymous survey of CISO community",
            "data_quality_score": 0.92
        },
        {
            "industry": "healthcare",
            "company_size": "large",
            "average_score": 68.9,
            "standard_deviation": 14.1,
            "sample_size": 189,
            "percentile_10": 51.3,
            "percentile_25": 59.2,
            "percentile_50": 68.9,
            "percentile_75": 78.6,
            "percentile_90": 86.4,
            "data_source": "Healthcare Security Benchmark 2024",
            "collection_method": "HIPAA compliance assessment data",
            "data_quality_score": 0.88
        },
        {
            "industry": "technology",
            "company_size": "large",
            "average_score": 75.8,
            "standard_deviation": 11.7,
            "sample_size": 312,
            "percentile_10": 61.2,
            "percentile_25": 67.9,
            "percentile_50": 75.8,
            "percentile_75": 83.7,
            "percentile_90": 90.1,
            "data_source": "Tech Industry Security Report 2024",
            "collection_method": "Voluntary security maturity assessment",
            "data_quality_score": 0.95
        },
        {
            "industry": "manufacturing",
            "company_size": "medium",
            "average_score": 64.3,
            "standard_deviation": 15.8,
            "sample_size": 156,
            "percentile_10": 45.7,
            "percentile_25": 53.1,
            "percentile_50": 64.3,
            "percentile_75": 75.9,
            "percentile_90": 84.2,
            "data_source": "Manufacturing Cybersecurity Study 2024",
            "collection_method": "ICS/OT security assessment survey",
            "data_quality_score": 0.85
        },
        {
            "industry": "government",
            "company_size": "large",
            "average_score": 71.2,
            "standard_deviation": 13.5,
            "sample_size": 98,
            "percentile_10": 54.8,
            "percentile_25": 61.7,
            "percentile_50": 71.2,
            "percentile_75": 80.6,
            "percentile_90": 87.9,
            "data_source": "Public Sector Security Assessment 2024",
            "collection_method": "Government agency security audit data",
            "data_quality_score": 0.90
        },
        {
            "industry": "financial_services",
            "company_size": "medium",
            "average_score": 69.8,
            "standard_deviation": 13.1,
            "sample_size": 178,
            "percentile_10": 52.4,
            "percentile_25": 60.2,
            "percentile_50": 69.8,
            "percentile_75": 79.1,
            "percentile_90": 86.7,
            "data_source": "Regional Bank Security Survey 2024",
            "collection_method": "Community bank security assessment",
            "data_quality_score": 0.89
        },
        {
            "industry": "healthcare",
            "company_size": "medium",
            "average_score": 65.4,
            "standard_deviation": 15.2,
            "sample_size": 134,
            "percentile_10": 47.8,
            "percentile_25": 55.6,
            "percentile_50": 65.4,
            "percentile_75": 75.9,
            "percentile_90": 83.2,
            "data_source": "Regional Healthcare Security Study 2024",
            "collection_method": "Hospital and clinic security survey",
            "data_quality_score": 0.86
        },
        {
            "industry": "technology",
            "company_size": "small",
            "average_score": 71.2,
            "standard_deviation": 16.4,
            "sample_size": 89,
            "percentile_10": 51.3,
            "percentile_25": 59.8,
            "percentile_50": 71.2,
            "percentile_75": 82.6,
            "percentile_90": 91.4,
            "data_source": "Startup Security Assessment 2024",
            "collection_method": "Tech startup security maturity survey",
            "data_quality_score": 0.82
        }
    ]
    
    @staticmethod
    def load_benchmark_data():
        """Load sample benchmark data into the database"""
        db = get_session()
        try:
            # Check if data already exists
            existing_count = db.query(IndustryBenchmarks).count()
            if existing_count > 0:
                logger.info(f"Benchmark data already exists ({existing_count} records). Skipping load.")
                return existing_count
            
            # Load sample data
            loaded_count = 0
            data_date = datetime.utcnow() - timedelta(days=30)  # 30 days ago
            
            for benchmark_data in BenchmarkDataLoader.SAMPLE_BENCHMARKS:
                benchmark = IndustryBenchmarks(
                    industry=benchmark_data["industry"],
                    company_size=benchmark_data["company_size"],
                    average_score=benchmark_data["average_score"],
                    standard_deviation=benchmark_data["standard_deviation"],
                    sample_size=benchmark_data["sample_size"],
                    percentile_10=benchmark_data["percentile_10"],
                    percentile_25=benchmark_data["percentile_25"],
                    percentile_50=benchmark_data["percentile_50"],
                    percentile_75=benchmark_data["percentile_75"],
                    percentile_90=benchmark_data["percentile_90"],
                    data_source=benchmark_data["data_source"],
                    collection_method=benchmark_data["collection_method"],
                    data_quality_score=benchmark_data["data_quality_score"],
                    data_date=data_date
                )
                
                db.add(benchmark)
                loaded_count += 1
            
            db.commit()
            logger.info(f"Successfully loaded {loaded_count} benchmark records")
            return loaded_count
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error loading benchmark data: {e}")
            raise
        finally:
            db.close()
    
    @staticmethod
    def update_benchmark_data(industry: str, company_size: str, benchmark_data: dict):
        """Update specific benchmark data"""
        db = get_session()
        try:
            # Find existing benchmark
            benchmark = db.query(IndustryBenchmarks).filter(
                IndustryBenchmarks.industry == industry,
                IndustryBenchmarks.company_size == company_size
            ).first()
            
            if benchmark:
                # Update existing
                for key, value in benchmark_data.items():
                    if hasattr(benchmark, key):
                        setattr(benchmark, key, value)
                benchmark.updated_at = datetime.utcnow()
            else:
                # Create new
                benchmark = IndustryBenchmarks(
                    industry=industry,
                    company_size=company_size,
                    data_date=datetime.utcnow(),
                    **benchmark_data
                )
                db.add(benchmark)
            
            db.commit()
            logger.info(f"Updated benchmark for {industry}/{company_size}")
            
        except Exception as e:
            db.rollback()
            logger.error(f"Error updating benchmark data: {e}")
            raise
        finally:
            db.close()
    
    @staticmethod
    def get_benchmark_summary():
        """Get summary of loaded benchmark data"""
        db = get_session()
        try:
            benchmarks = db.query(IndustryBenchmarks).all()
            
            summary = {
                "total_records": len(benchmarks),
                "industries": set(),
                "company_sizes": set(),
                "average_scores": [],
                "data_sources": set()
            }
            
            for benchmark in benchmarks:
                summary["industries"].add(benchmark.industry)
                summary["company_sizes"].add(benchmark.company_size)
                summary["average_scores"].append(benchmark.average_score)
                summary["data_sources"].add(benchmark.data_source)
            
            # Convert sets to lists for JSON serialization
            summary["industries"] = list(summary["industries"])
            summary["company_sizes"] = list(summary["company_sizes"])
            summary["data_sources"] = list(summary["data_sources"])
            
            # Calculate overall statistics
            if summary["average_scores"]:
                summary["overall_average"] = sum(summary["average_scores"]) / len(summary["average_scores"])
                summary["score_range"] = {
                    "min": min(summary["average_scores"]),
                    "max": max(summary["average_scores"])
                }
            
            return summary
            
        except Exception as e:
            logger.error(f"Error getting benchmark summary: {e}")
            return {"error": str(e)}
        finally:
            db.close()

def main():
    """Load benchmark data if run directly"""
    print("Loading benchmark data...")
    try:
        count = BenchmarkDataLoader.load_benchmark_data()
        print(f"Loaded {count} benchmark records")
        
        summary = BenchmarkDataLoader.get_benchmark_summary()
        print(f"Summary: {summary}")
        
    except Exception as e:
        print(f"Error: {e}")

if __name__ == "__main__":
    main()