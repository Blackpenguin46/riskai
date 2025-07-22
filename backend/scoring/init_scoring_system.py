#!/usr/bin/env python3
"""
Scoring System Initialization Script
Sets up the scoring system with default data and configurations
"""

import logging
import sys
import os
from datetime import datetime

# Add parent directory to path for imports
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from database.models import get_session, ScoringWeights, ScoringMethodology
from scoring.benchmark_data_loader import BenchmarkDataLoader

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def initialize_default_methodology():
    """Initialize the default scoring methodology"""
    db = get_session()
    try:
        # Check if default methodology exists
        existing = db.query(ScoringMethodology).filter(
            ScoringMethodology.methodology_name == "default"
        ).first()
        
        if existing:
            logger.info("Default methodology already exists")
            return
        
        # Create default methodology
        methodology = ScoringMethodology(
            methodology_name="default",
            version="1.0",
            description="RiskAI Mathematical Scoring System - Default methodology implementing weighted section scoring with statistical confidence intervals",
            mathematical_formula="""
            Question Score = Normalized Answer Value × Question Weight
            Section Score = Σ(Question Score × Question Weight) / Σ(Question Weights) × 100
            Overall Score = Σ(Section Score × Section Weight)
            
            Section Weights:
            - Governance: 20%
            - Technical Controls: 40%
            - Operational: 25%
            - Compliance: 15%
            """,
            implementation_notes="Implements SEET paper recommendations with holistic risk management approach",
            parameters={
                "confidence_level": 0.95,
                "completion_penalty": 0.15,
                "statistical_method": "t_distribution"
            },
            thresholds={
                "critical": {"min": 0, "max": 40},
                "high": {"min": 41, "max": 60},
                "medium": {"min": 61, "max": 80},
                "low": {"min": 81, "max": 100}
            },
            created_by="system",
            approved_by="system",
            approval_date=datetime.utcnow()
        )
        
        db.add(methodology)
        db.commit()
        logger.info("Default methodology created successfully")
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating default methodology: {e}")
        raise
    finally:
        db.close()

def initialize_sample_weights():
    """Initialize sample custom weights for demonstration"""
    db = get_session()
    try:
        # Check if sample weights exist
        existing_count = db.query(ScoringWeights).count()
        if existing_count > 0:
            logger.info(f"Custom weights already exist ({existing_count} records)")
            return
        
        # Sample custom weights for specific questions
        sample_weights = [
            {
                "weight_type": "question",
                "identifier": "gov_001",
                "weight_value": 12.0,
                "max_score": 12.0,
                "description": "Critical governance question - increased weight"
            },
            {
                "weight_type": "question", 
                "identifier": "data_001",
                "weight_value": 15.0,
                "max_score": 15.0,
                "description": "Data protection priority - increased weight"
            },
            {
                "weight_type": "section",
                "identifier": "governance",
                "weight_value": 22.0,
                "max_score": 100.0,
                "description": "Governance section - slightly increased weight"
            }
        ]
        
        for weight_data in sample_weights:
            weight = ScoringWeights(**weight_data)
            db.add(weight)
        
        db.commit()
        logger.info(f"Created {len(sample_weights)} sample custom weights")
        
    except Exception as e:
        db.rollback()
        logger.error(f"Error creating sample weights: {e}")
        raise
    finally:
        db.close()

def verify_scoring_system():
    """Verify that the scoring system is properly initialized"""
    try:
        from scoring.scoring_engine import ScoringEngine
        from assessment.risk_categorization import RiskCategorizationEngine
        
        # Test basic scoring functionality
        test_score = ScoringEngine.score_question(
            question_id="test_001",
            question_type="boolean",
            answer=True
        )
        
        if test_score.percentage > 0:
            logger.info("✓ Scoring engine working correctly")
        else:
            logger.warning("⚠ Scoring engine may have issues")
        
        # Test risk categorization
        risk_assessment = RiskCategorizationEngine.categorize_risk(75.0)
        if risk_assessment.risk_level:
            logger.info("✓ Risk categorization working correctly")
        else:
            logger.warning("⚠ Risk categorization may have issues")
        
        # Check database models
        db = get_session()
        methodology_count = db.query(ScoringMethodology).count()
        benchmark_count = db.query(ScoringWeights).count()
        db.close()
        
        logger.info(f"✓ Database initialized: {methodology_count} methodologies, {benchmark_count} custom weights")
        
        return True
        
    except Exception as e:
        logger.error(f"✗ Scoring system verification failed: {e}")
        return False

def main():
    """Initialize the complete scoring system"""
    print("=" * 60)
    print("RISKAI SCORING SYSTEM INITIALIZATION")
    print("=" * 60)
    
    try:
        # Initialize database tables (should be done by main app)
        logger.info("Initializing database tables...")
        from database.models import init_database
        init_database()
        
        # Load benchmark data
        logger.info("Loading benchmark data...")
        BenchmarkDataLoader.load_benchmark_data()
        
        # Initialize default methodology
        logger.info("Initializing default methodology...")
        initialize_default_methodology()
        
        # Initialize sample weights
        logger.info("Initializing sample weights...")
        initialize_sample_weights()
        
        # Verify system
        logger.info("Verifying scoring system...")
        if verify_scoring_system():
            print("✓ Scoring system initialized successfully!")
        else:
            print("⚠ Scoring system initialized with warnings")
        
        # Print summary
        summary = BenchmarkDataLoader.get_benchmark_summary()
        print(f"\nBenchmark Data Summary:")
        print(f"- Total Records: {summary.get('total_records', 0)}")
        print(f"- Industries: {', '.join(summary.get('industries', []))}")
        print(f"- Company Sizes: {', '.join(summary.get('company_sizes', []))}")
        print(f"- Overall Average Score: {summary.get('overall_average', 0):.1f}%")
        
    except Exception as e:
        logger.error(f"Initialization failed: {e}")
        print(f"✗ Initialization failed: {e}")
        return False
    
    print("=" * 60)
    return True

if __name__ == "__main__":
    main()