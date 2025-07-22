"""
Industry Profiler for RiskAI
Manages industry-specific assessment templates and benchmarks
"""

import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime

from database.models import get_session
from database.validation_models import (
    IndustrySector, SecurityFramework, SecurityDomain, AssessmentQuestion,
    IndustryValidation, ValidationMetric, ValidationResponse, ScoringRubric,
    IndustryBenchmark
)
from validation.validator import validation_data_manager

logger = logging.getLogger(__name__)

class IndustryProfiler:
    """Manages industry-specific assessment templates and benchmarks"""
    
    @staticmethod
    def get_industry_profile(industry_id: int) -> Dict[str, Any]:
        """
        Get a complete profile for an industry
        
        Args:
            industry_id: Industry sector ID
            
        Returns:
            Dictionary with industry profile data
        """
        try:
            db = get_session()
            
            # Get industry details
            industry = db.query(IndustrySector).filter(IndustrySector.id == industry_id).first()
            
            if not industry:
                logger.error(f"Industry {industry_id} not found")
                return {"error": f"Industry {industry_id} not found"}
            
            # Get validation data
            validations = validation_data_manager.get_industry_validations(industry_id=industry_id)
            
            # Get benchmarks
            benchmarks = validation_data_manager.get_industry_benchmarks(industry_id=industry_id)
            
            # Get frameworks associated with this industry
            frameworks = []
            for framework in industry.frameworks:
                framework_data = framework.to_dict()
                
                # Get domains for this framework
                domains = validation_data_manager.get_security_domains(framework_id=framework.id)
                framework_data["domains"] = domains
                
                frameworks.append(framework_data)
            
            # Build profile
            profile = {
                "industry": industry.to_dict(),
                "frameworks": frameworks,
                "validations": validations,
                "benchmarks": benchmarks
            }
            
            return profile
            
        except Exception as e:
            logger.error(f"Error getting industry profile: {str(e)}")
            return {"error": str(e)}
        finally:
            db.close()
    
    @staticmethod
    def get_company_size_profile(company_size: str) -> Dict[str, Any]:
        """
        Get a complete profile for a company size
        
        Args:
            company_size: Company size category
            
        Returns:
            Dictionary with company size profile data
        """
        try:
            # Get validations for this company size
            validations = validation_data_manager.get_industry_validations(company_size=company_size)
            
            # Get benchmarks for this company size
            benchmarks = validation_data_manager.get_industry_benchmarks(company_size=company_size)
            
            # Build profile
            profile = {
                "company_size": company_size,
                "validations": validations,
                "benchmarks": benchmarks
            }
            
            return profile
            
        except Exception as e:
            logger.error(f"Error getting company size profile: {str(e)}")
            return {"error": str(e)}
    
    @staticmethod
    def get_assessment_template(
        industry_id: Optional[int] = None,
        company_size: Optional[str] = None,
        framework_id: Optional[int] = None
    ) -> Dict[str, Any]:
        """
        Get an assessment template for a specific industry and company size
        
        Args:
            industry_id: Optional industry sector ID
            company_size: Optional company size category
            framework_id: Optional framework ID
            
        Returns:
            Dictionary with assessment template data
        """
        try:
            db = get_session()
            
            # Get frameworks
            query = db.query(SecurityFramework)
            
            if framework_id is not None:
                query = query.filter(SecurityFramework.id == framework_id)
            
            frameworks = query.all()
            
            if not frameworks:
                logger.error("No frameworks found")
                return {"error": "No frameworks found"}
            
            # Build template
            template = {
                "industry_id": industry_id,
                "company_size": company_size,
                "frameworks": []
            }
            
            for framework in frameworks:
                framework_data = framework.to_dict()
                
                # Get domains for this framework
                domains = []
                for domain in framework.domains:
                    domain_data = domain.to_dict()
                    
                    # Get questions for this domain
                    questions = []
                    for question in domain.questions:
                        question_data = question.to_dict()
                        
                        # Get scoring rubrics for this domain
                        rubrics = validation_data_manager.get_scoring_rubrics(domain_id=domain.id)
                        question_data["scoring_rubrics"] = rubrics
                        
                        # Get industry-specific benchmarks
                        if industry_id is not None:
                            benchmarks = validation_data_manager.get_industry_benchmarks(
                                industry_id=industry_id,
                                domain_id=domain.id,
                                company_size=company_size
                            )
                            question_data["industry_benchmarks"] = benchmarks
                        
                        questions.append(question_data)
                    
                    domain_data["questions"] = questions
                    domains.append(domain_data)
                
                framework_data["domains"] = domains
                template["frameworks"].append(framework_data)
            
            return template
            
        except Exception as e:
            logger.error(f"Error getting assessment template: {str(e)}")
            return {"error": str(e)}
        finally:
            db.close()
    
    @staticmethod
    def categorize_company_by_size(employee_count: int) -> str:
        """
        Categorize a company by size based on employee count
        
        Args:
            employee_count: Number of employees
            
        Returns:
            Company size category
        """
        if employee_count < 50:
            return "small"
        elif employee_count < 500:
            return "medium"
        elif employee_count < 5000:
            return "large"
        else:
            return "enterprise"
    
    @staticmethod
    def get_industry_specific_questions(industry_id: int) -> List[Dict[str, Any]]:
        """
        Get industry-specific assessment questions
        
        Args:
            industry_id: Industry sector ID
            
        Returns:
            List of industry-specific questions
        """
        try:
            db = get_session()
            
            # Get industry
            industry = db.query(IndustrySector).filter(IndustrySector.id == industry_id).first()
            
            if not industry:
                logger.error(f"Industry {industry_id} not found")
                return []
            
            # Get frameworks associated with this industry
            framework_ids = [framework.id for framework in industry.frameworks]
            
            if not framework_ids:
                logger.warning(f"No frameworks associated with industry {industry_id}")
                return []
            
            # Get domains for these frameworks
            domains = db.query(SecurityDomain).filter(
                SecurityDomain.framework_id.in_(framework_ids)
            ).all()
            
            domain_ids = [domain.id for domain in domains]
            
            # Get questions for these domains
            questions = db.query(AssessmentQuestion).filter(
                AssessmentQuestion.domain_id.in_(domain_ids)
            ).all()
            
            return [question.to_dict() for question in questions]
            
        except Exception as e:
            logger.error(f"Error getting industry-specific questions: {str(e)}")
            return []
        finally:
            db.close()
    
    @staticmethod
    def get_industry_benchmark_comparison(
        industry_id: int,
        domain_id: Optional[int] = None,
        company_size: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Get benchmark comparison for an industry
        
        Args:
            industry_id: Industry sector ID
            domain_id: Optional domain ID filter
            company_size: Optional company size filter
            
        Returns:
            Dictionary with benchmark comparison data
        """
        try:
            # Get benchmarks for this industry
            industry_benchmarks = validation_data_manager.get_industry_benchmarks(
                industry_id=industry_id,
                domain_id=domain_id,
                company_size=company_size
            )
            
            # Get benchmarks for all industries
            all_benchmarks = validation_data_manager.get_industry_benchmarks(
                domain_id=domain_id,
                company_size=company_size
            )
            
            # Group benchmarks by domain
            domain_benchmarks = {}
            for benchmark in all_benchmarks:
                domain_id = benchmark["domain_id"]
                if domain_id not in domain_benchmarks:
                    domain_benchmarks[domain_id] = []
                domain_benchmarks[domain_id].append(benchmark)
            
            # Calculate average scores for each domain
            domain_averages = {}
            for domain_id, benchmarks in domain_benchmarks.items():
                if benchmarks:
                    domain_averages[domain_id] = sum(b["average_score"] for b in benchmarks) / len(benchmarks)
            
            # Build comparison
            comparison = {
                "industry_id": industry_id,
                "company_size": company_size,
                "domain_id": domain_id,
                "industry_benchmarks": industry_benchmarks,
                "domain_averages": domain_averages,
                "comparison": []
            }
            
            # Compare industry benchmarks to overall averages
            for benchmark in industry_benchmarks:
                domain_id = benchmark["domain_id"]
                if domain_id in domain_averages:
                    overall_avg = domain_averages[domain_id]
                    industry_avg = benchmark["average_score"]
                    
                    comparison["comparison"].append({
                        "domain_id": domain_id,
                        "industry_score": industry_avg,
                        "overall_score": overall_avg,
                        "difference": industry_avg - overall_avg,
                        "percentage_difference": ((industry_avg - overall_avg) / overall_avg) * 100 if overall_avg > 0 else 0
                    })
            
            return comparison
            
        except Exception as e:
            logger.error(f"Error getting industry benchmark comparison: {str(e)}")
            return {"error": str(e)}
    
    @staticmethod
    def associate_industry_with_framework(industry_id: int, framework_id: int) -> bool:
        """
        Associate an industry with a security framework
        
        Args:
            industry_id: Industry sector ID
            framework_id: Security framework ID
            
        Returns:
            Success status
        """
        try:
            db = get_session()
            
            # Get industry and framework
            industry = db.query(IndustrySector).filter(IndustrySector.id == industry_id).first()
            framework = db.query(SecurityFramework).filter(SecurityFramework.id == framework_id).first()
            
            if not industry or not framework:
                logger.error(f"Industry {industry_id} or framework {framework_id} not found")
                return False
            
            # Check if association already exists
            if framework in industry.frameworks:
                logger.info(f"Industry {industry_id} already associated with framework {framework_id}")
                return True
            
            # Add association
            industry.frameworks.append(framework)
            db.commit()
            
            logger.info(f"Associated industry {industry_id} with framework {framework_id}")
            return True
            
        except Exception as e:
            logger.error(f"Error associating industry with framework: {str(e)}")
            db.rollback()
            return False
        finally:
            db.close()

# Create a global instance
industry_profiler = IndustryProfiler()