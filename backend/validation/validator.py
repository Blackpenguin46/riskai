"""
Validation Data Manager for RiskAI
Handles storage, retrieval, and validation of cross-industry validation data
"""

import logging
import csv
import json
import numpy as np
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from sqlalchemy.orm import Session as DBSession
from sqlalchemy import func

from database.models import get_session
from database.validation_models import (
    IndustrySector, SecurityFramework, SecurityDomain, AssessmentQuestion,
    IndustryValidation, ValidationMetric, ValidationResponse, ScoringRubric,
    IndustryBenchmark
)

# Create a validation data manager class
class ValidationDataManager:
    def __init__(self):
        self.logger = logging.getLogger(__name__)
    
    def get_industry_sectors(self):
        """Get all industry sectors"""
        try:
            with get_session() as session:
                industries = session.query(IndustrySector).all()
                return [industry.to_dict() for industry in industries]
        except Exception as e:
            self.logger.error(f"Error getting industry sectors: {str(e)}")
            return []
    
    def get_security_frameworks(self):
        """Get all security frameworks"""
        try:
            with get_session() as session:
                frameworks = session.query(SecurityFramework).all()
                return [framework.to_dict() for framework in frameworks]
        except Exception as e:
            self.logger.error(f"Error getting security frameworks: {str(e)}")
            return []
    
    def get_security_domains(self, framework_id=None):
        """Get security domains, optionally filtered by framework"""
        try:
            with get_session() as session:
                query = session.query(SecurityDomain)
                if framework_id:
                    query = query.filter(SecurityDomain.framework_id == framework_id)
                domains = query.all()
                return [domain.to_dict() for domain in domains]
        except Exception as e:
            self.logger.error(f"Error getting security domains: {str(e)}")
            return []
    
    def get_assessment_questions(self, domain_id=None):
        """Get assessment questions, optionally filtered by domain"""
        try:
            with get_session() as session:
                query = session.query(AssessmentQuestion)
                if domain_id:
                    query = query.filter(AssessmentQuestion.domain_id == domain_id)
                questions = query.all()
                return [question.to_dict() for question in questions]
        except Exception as e:
            self.logger.error(f"Error getting assessment questions: {str(e)}")
            return []
    
    def get_industry_validations(self, industry_id=None, company_size=None):
        """Get industry validations, optionally filtered by industry and company size"""
        try:
            with get_session() as session:
                query = session.query(IndustryValidation)
                if industry_id:
                    query = query.filter(IndustryValidation.industry_id == industry_id)
                if company_size:
                    query = query.filter(IndustryValidation.company_size == company_size)
                validations = query.all()
                return [validation.to_dict() for validation in validations]
        except Exception as e:
            self.logger.error(f"Error getting industry validations: {str(e)}")
            return []
    
    def get_validation_metrics(self, validation_id):
        """Get validation metrics for an industry validation"""
        try:
            with get_session() as session:
                metrics = session.query(ValidationMetric).filter(
                    ValidationMetric.validation_id == validation_id
                ).all()
                return [metric.to_dict() for metric in metrics]
        except Exception as e:
            self.logger.error(f"Error getting validation metrics: {str(e)}")
            return []
    
    def get_validation_responses(self, question_id=None, industry_id=None, company_size=None):
        """Get validation responses, optionally filtered by question, industry, and company size"""
        try:
            with get_session() as session:
                query = session.query(ValidationResponse)
                if question_id:
                    query = query.filter(ValidationResponse.question_id == question_id)
                if industry_id:
                    query = query.filter(ValidationResponse.industry_id == industry_id)
                if company_size:
                    query = query.filter(ValidationResponse.company_size == company_size)
                responses = query.all()
                return [response.to_dict() for response in responses]
        except Exception as e:
            self.logger.error(f"Error getting validation responses: {str(e)}")
            return []
    
    def get_scoring_rubrics(self, domain_id=None):
        """Get scoring rubrics, optionally filtered by domain"""
        try:
            with get_session() as session:
                query = session.query(ScoringRubric)
                if domain_id:
                    query = query.filter(ScoringRubric.domain_id == domain_id)
                rubrics = query.all()
                return [rubric.to_dict() for rubric in rubrics]
        except Exception as e:
            self.logger.error(f"Error getting scoring rubrics: {str(e)}")
            return []
    
    def get_industry_benchmarks(self, industry_id=None, domain_id=None, company_size=None):
        """Get industry benchmarks, optionally filtered by industry, domain, and company size"""
        try:
            with get_session() as session:
                query = session.query(IndustryBenchmark)
                if industry_id:
                    query = query.filter(IndustryBenchmark.industry_id == industry_id)
                if domain_id:
                    query = query.filter(IndustryBenchmark.domain_id == domain_id)
                if company_size:
                    query = query.filter(IndustryBenchmark.company_size == company_size)
                benchmarks = query.all()
                return [benchmark.to_dict() for benchmark in benchmarks]
        except Exception as e:
            self.logger.error(f"Error getting industry benchmarks: {str(e)}")
            return []
    
    def calculate_validation_metrics(self, industry_id, company_size=None):
        """Calculate validation metrics for an industry"""
        try:
            # This is a placeholder implementation
            return {
                "industry_id": industry_id,
                "company_size": company_size,
                "metrics": {
                    "accuracy": 0.85,
                    "precision": 0.82,
                    "recall": 0.88,
                    "f1_score": 0.85
                }
            }
        except Exception as e:
            self.logger.error(f"Error calculating validation metrics: {str(e)}")
            return {"error": str(e)}

# Create an instance of the validation data manager
validation_data_manager = ValidationDataManager()

logger = logging.getLogger(__name__)

class ValidationDataManager:
    """Manages validation data for cross-industry validation"""
    
    @staticmethod
    def add_industry_sector(name: str, description: Optional[str] = None) -> Optional[int]:
        """
        Add a new industry sector
        
        Args:
            name: Industry sector name
            description: Optional description
            
        Returns:
            ID of the created industry sector or None if failed
        """
        try:
            db = get_session()
            
            # Check if industry already exists
            existing = db.query(IndustrySector).filter(IndustrySector.name == name).first()
            if existing:
                logger.info(f"Industry sector {name} already exists with ID {existing.id}")
                return existing.id
            
            industry = IndustrySector(
                name=name,
                description=description
            )
            
            db.add(industry)
            db.commit()
            db.refresh(industry)
            
            logger.info(f"Added industry sector {name} with ID {industry.id}")
            return industry.id
            
        except Exception as e:
            logger.error(f"Error adding industry sector: {str(e)}")
            db.rollback()
            return None
        finally:
            db.close() 
   
    @staticmethod
    def add_security_framework(
        name: str,
        version: Optional[str] = None,
        description: Optional[str] = None,
        source_url: Optional[str] = None
    ) -> Optional[int]:
        """
        Add a new security framework
        
        Args:
            name: Framework name
            version: Optional version
            description: Optional description
            source_url: Optional source URL
            
        Returns:
            ID of the created framework or None if failed
        """
        try:
            db = get_session()
            
            # Check if framework already exists
            existing = db.query(SecurityFramework).filter(
                SecurityFramework.name == name,
                SecurityFramework.version == version
            ).first()
            
            if existing:
                logger.info(f"Security framework {name} {version} already exists with ID {existing.id}")
                return existing.id
            
            framework = SecurityFramework(
                name=name,
                version=version,
                description=description,
                source_url=source_url
            )
            
            db.add(framework)
            db.commit()
            db.refresh(framework)
            
            logger.info(f"Added security framework {name} {version} with ID {framework.id}")
            return framework.id
            
        except Exception as e:
            logger.error(f"Error adding security framework: {str(e)}")
            db.rollback()
            return None
        finally:
            db.close()
    
    @staticmethod
    def add_security_domain(
        framework_id: int,
        name: str,
        description: Optional[str] = None,
        weight: float = 1.0
    ) -> Optional[int]:
        """
        Add a new security domain to a framework
        
        Args:
            framework_id: Framework ID
            name: Domain name
            description: Optional description
            weight: Domain weight for scoring
            
        Returns:
            ID of the created domain or None if failed
        """
        try:
            db = get_session()
            
            # Check if domain already exists in this framework
            existing = db.query(SecurityDomain).filter(
                SecurityDomain.framework_id == framework_id,
                SecurityDomain.name == name
            ).first()
            
            if existing:
                logger.info(f"Security domain {name} already exists in framework {framework_id} with ID {existing.id}")
                return existing.id
            
            domain = SecurityDomain(
                framework_id=framework_id,
                name=name,
                description=description,
                weight=weight
            )
            
            db.add(domain)
            db.commit()
            db.refresh(domain)
            
            logger.info(f"Added security domain {name} to framework {framework_id} with ID {domain.id}")
            return domain.id
            
        except Exception as e:
            logger.error(f"Error adding security domain: {str(e)}")
            db.rollback()
            return None
        finally:
            db.close()    
  
  @staticmethod
    def add_assessment_question(
        domain_id: int,
        question_text: str,
        question_type: str,
        options: Optional[List[str]] = None,
        weight: float = 1.0,
        guidance: Optional[str] = None,
        evidence_required: bool = False
    ) -> Optional[int]:
        """
        Add a new assessment question to a domain
        
        Args:
            domain_id: Domain ID
            question_text: Question text
            question_type: Question type (text, select, multiselect, scale, boolean)
            options: Optional list of options for select/multiselect questions
            weight: Question weight for scoring
            guidance: Optional guidance for answering
            evidence_required: Whether evidence is required
            
        Returns:
            ID of the created question or None if failed
        """
        try:
            db = get_session()
            
            # Check if question already exists in this domain
            existing = db.query(AssessmentQuestion).filter(
                AssessmentQuestion.domain_id == domain_id,
                AssessmentQuestion.question_text == question_text
            ).first()
            
            if existing:
                logger.info(f"Assessment question already exists in domain {domain_id} with ID {existing.id}")
                return existing.id
            
            question = AssessmentQuestion(
                domain_id=domain_id,
                question_text=question_text,
                question_type=question_type,
                options=options,
                weight=weight,
                guidance=guidance,
                evidence_required=evidence_required
            )
            
            db.add(question)
            db.commit()
            db.refresh(question)
            
            logger.info(f"Added assessment question to domain {domain_id} with ID {question.id}")
            return question.id
            
        except Exception as e:
            logger.error(f"Error adding assessment question: {str(e)}")
            db.rollback()
            return None
        finally:
            db.close()
    
    @staticmethod
    def add_industry_validation(
        industry_id: int,
        company_size: str,
        company_count: int,
        average_accuracy: Optional[float] = None,
        confidence_interval: Optional[Tuple[float, float]] = None,
        precision_score: Optional[float] = None,
        recall_score: Optional[float] = None,
        f1_score: Optional[float] = None,
        validation_methodology: Optional[str] = None
    ) -> Optional[int]:
        """
        Add validation data for an industry sector
        
        Args:
            industry_id: Industry sector ID
            company_size: Company size category
            company_count: Number of companies assessed
            average_accuracy: Optional average accuracy
            confidence_interval: Optional confidence interval (lower, upper)
            precision_score: Optional precision score
            recall_score: Optional recall score
            f1_score: Optional F1 score
            validation_methodology: Optional validation methodology
            
        Returns:
            ID of the created validation or None if failed
        """
        try:
            db = get_session()
            
            # Check if validation already exists for this industry and company size
            existing = db.query(IndustryValidation).filter(
                IndustryValidation.industry_id == industry_id,
                IndustryValidation.company_size == company_size
            ).first()
            
            if existing:
                # Update existing validation
                existing.company_count = company_count
                if average_accuracy is not None:
                    existing.average_accuracy = average_accuracy
                if confidence_interval is not None:
                    existing.confidence_interval_lower = confidence_interval[0]
                    existing.confidence_interval_upper = confidence_interval[1]
                if precision_score is not None:
                    existing.precision_score = precision_score
                if recall_score is not None:
                    existing.recall_score = recall_score
                if f1_score is not None:
                    existing.f1_score = f1_score
                if validation_methodology is not None:
                    existing.validation_methodology = validation_methodology
                existing.validation_date = datetime.utcnow()
                
                db.commit()
                logger.info(f"Updated industry validation for industry {industry_id}, company size {company_size}")
                return existing.id
            
            # Create new validation
            validation = IndustryValidation(
                industry_id=industry_id,
                company_size=company_size,
                company_count=company_count,
                average_accuracy=average_accuracy,
                confidence_interval_lower=confidence_interval[0] if confidence_interval else None,
                confidence_interval_upper=confidence_interval[1] if confidence_interval else None,
                precision_score=precision_score,
                recall_score=recall_score,
                f1_score=f1_score,
                validation_methodology=validation_methodology,
                validation_date=datetime.utcnow()
            )
            
            db.add(validation)
            db.commit()
            db.refresh(validation)
            
            logger.info(f"Added industry validation for industry {industry_id}, company size {company_size} with ID {validation.id}")
            return validation.id
            
        except Exception as e:
            logger.error(f"Error adding industry validation: {str(e)}")
            db.rollback()
            return None
        finally:
            db.close()    

    @staticmethod
    def add_validation_metric(
        validation_id: int,
        metric_name: str,
        metric_value: float,
        metric_description: Optional[str] = None
    ) -> Optional[int]:
        """
        Add a validation metric to an industry validation
        
        Args:
            validation_id: Industry validation ID
            metric_name: Metric name
            metric_value: Metric value
            metric_description: Optional metric description
            
        Returns:
            ID of the created metric or None if failed
        """
        try:
            db = get_session()
            
            # Check if metric already exists for this validation
            existing = db.query(ValidationMetric).filter(
                ValidationMetric.validation_id == validation_id,
                ValidationMetric.metric_name == metric_name
            ).first()
            
            if existing:
                # Update existing metric
                existing.metric_value = metric_value
                if metric_description is not None:
                    existing.metric_description = metric_description
                
                db.commit()
                logger.info(f"Updated validation metric {metric_name} for validation {validation_id}")
                return existing.id
            
            # Create new metric
            metric = ValidationMetric(
                validation_id=validation_id,
                metric_name=metric_name,
                metric_value=metric_value,
                metric_description=metric_description
            )
            
            db.add(metric)
            db.commit()
            db.refresh(metric)
            
            logger.info(f"Added validation metric {metric_name} to validation {validation_id} with ID {metric.id}")
            return metric.id
            
        except Exception as e:
            logger.error(f"Error adding validation metric: {str(e)}")
            db.rollback()
            return None
        finally:
            db.close()
    
    @staticmethod
    def add_validation_response(
        question_id: int,
        industry_id: int,
        company_size: str,
        expert_response: str,
        riskai_response: str,
        is_correct: bool,
        confidence_score: Optional[float] = None,
        validator_id: Optional[str] = None
    ) -> Optional[int]:
        """
        Add a validation response for an assessment question
        
        Args:
            question_id: Assessment question ID
            industry_id: Industry sector ID
            company_size: Company size category
            expert_response: Expert's response
            riskai_response: RiskAI's response
            is_correct: Whether RiskAI's response is correct
            confidence_score: Optional confidence score
            validator_id: Optional validator ID
            
        Returns:
            ID of the created response or None if failed
        """
        try:
            db = get_session()
            
            response = ValidationResponse(
                question_id=question_id,
                industry_id=industry_id,
                company_size=company_size,
                expert_response=expert_response,
                riskai_response=riskai_response,
                is_correct=is_correct,
                confidence_score=confidence_score,
                validation_date=datetime.utcnow(),
                validator_id=validator_id
            )
            
            db.add(response)
            db.commit()
            db.refresh(response)
            
            logger.info(f"Added validation response for question {question_id}, industry {industry_id} with ID {response.id}")
            return response.id
            
        except Exception as e:
            logger.error(f"Error adding validation response: {str(e)}")
            db.rollback()
            return None
        finally:
            db.close() 
   
    @staticmethod
    def add_scoring_rubric(
        domain_id: int,
        score_level: int,
        description: str,
        criteria: Optional[List[str]] = None,
        industry_examples: Optional[Dict[str, str]] = None
    ) -> Optional[int]:
        """
        Add a scoring rubric for a security domain
        
        Args:
            domain_id: Security domain ID
            score_level: Score level (1-10)
            description: Rubric description
            criteria: Optional list of criteria
            industry_examples: Optional dict of industry -> example
            
        Returns:
            ID of the created rubric or None if failed
        """
        try:
            db = get_session()
            
            # Check if rubric already exists for this domain and score level
            existing = db.query(ScoringRubric).filter(
                ScoringRubric.domain_id == domain_id,
                ScoringRubric.score_level == score_level
            ).first()
            
            if existing:
                # Update existing rubric
                existing.description = description
                if criteria is not None:
                    existing.criteria = criteria
                if industry_examples is not None:
                    existing.industry_examples = industry_examples
                
                db.commit()
                logger.info(f"Updated scoring rubric for domain {domain_id}, score level {score_level}")
                return existing.id
            
            # Create new rubric
            rubric = ScoringRubric(
                domain_id=domain_id,
                score_level=score_level,
                description=description,
                criteria=criteria,
                industry_examples=industry_examples
            )
            
            db.add(rubric)
            db.commit()
            db.refresh(rubric)
            
            logger.info(f"Added scoring rubric for domain {domain_id}, score level {score_level} with ID {rubric.id}")
            return rubric.id
            
        except Exception as e:
            logger.error(f"Error adding scoring rubric: {str(e)}")
            db.rollback()
            return None
        finally:
            db.close()
    
    @staticmethod
    def add_industry_benchmark(
        industry_id: int,
        domain_id: int,
        company_size: str,
        average_score: float,
        percentile_distribution: Optional[Dict[str, float]] = None,
        sample_size: Optional[int] = None
    ) -> Optional[int]:
        """
        Add a benchmark score for an industry and domain
        
        Args:
            industry_id: Industry sector ID
            domain_id: Security domain ID
            company_size: Company size category
            average_score: Average score
            percentile_distribution: Optional dict of percentile -> score
            sample_size: Optional sample size
            
        Returns:
            ID of the created benchmark or None if failed
        """
        try:
            db = get_session()
            
            # Check if benchmark already exists
            existing = db.query(IndustryBenchmark).filter(
                IndustryBenchmark.industry_id == industry_id,
                IndustryBenchmark.domain_id == domain_id,
                IndustryBenchmark.company_size == company_size
            ).first()
            
            if existing:
                # Update existing benchmark
                existing.average_score = average_score
                if percentile_distribution:
                    existing.percentile_10 = percentile_distribution.get("10")
                    existing.percentile_25 = percentile_distribution.get("25")
                    existing.percentile_50 = percentile_distribution.get("50")
                    existing.percentile_75 = percentile_distribution.get("75")
                    existing.percentile_90 = percentile_distribution.get("90")
                if sample_size is not None:
                    existing.sample_size = sample_size
                existing.last_updated = datetime.utcnow()
                
                db.commit()
                logger.info(f"Updated industry benchmark for industry {industry_id}, domain {domain_id}, company size {company_size}")
                return existing.id
            
            # Create new benchmark
            benchmark = IndustryBenchmark(
                industry_id=industry_id,
                domain_id=domain_id,
                company_size=company_size,
                average_score=average_score,
                percentile_10=percentile_distribution.get("10") if percentile_distribution else None,
                percentile_25=percentile_distribution.get("25") if percentile_distribution else None,
                percentile_50=percentile_distribution.get("50") if percentile_distribution else None,
                percentile_75=percentile_distribution.get("75") if percentile_distribution else None,
                percentile_90=percentile_distribution.get("90") if percentile_distribution else None,
                sample_size=sample_size,
                last_updated=datetime.utcnow()
            )
            
            db.add(benchmark)
            db.commit()
            db.refresh(benchmark)
            
            logger.info(f"Added industry benchmark for industry {industry_id}, domain {domain_id}, company size {company_size} with ID {benchmark.id}")
            return benchmark.id
            
        except Exception as e:
            logger.error(f"Error adding industry benchmark: {str(e)}")
            db.rollback()
            return None
        finally:
            db.close() 
   
    @staticmethod
    def get_industry_sectors() -> List[Dict[str, Any]]:
        """
        Get all industry sectors
        
        Returns:
            List of industry sector dictionaries
        """
        try:
            db = get_session()
            
            industries = db.query(IndustrySector).all()
            
            return [industry.to_dict() for industry in industries]
            
        except Exception as e:
            logger.error(f"Error getting industry sectors: {str(e)}")
            return []
        finally:
            db.close()
    
    @staticmethod
    def get_security_frameworks() -> List[Dict[str, Any]]:
        """
        Get all security frameworks
        
        Returns:
            List of security framework dictionaries
        """
        try:
            db = get_session()
            
            frameworks = db.query(SecurityFramework).all()
            
            return [framework.to_dict() for framework in frameworks]
            
        except Exception as e:
            logger.error(f"Error getting security frameworks: {str(e)}")
            return []
        finally:
            db.close()
    
    @staticmethod
    def get_security_domains(framework_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get security domains, optionally filtered by framework
        
        Args:
            framework_id: Optional framework ID filter
            
        Returns:
            List of security domain dictionaries
        """
        try:
            db = get_session()
            
            query = db.query(SecurityDomain)
            
            if framework_id is not None:
                query = query.filter(SecurityDomain.framework_id == framework_id)
            
            domains = query.all()
            
            return [domain.to_dict() for domain in domains]
            
        except Exception as e:
            logger.error(f"Error getting security domains: {str(e)}")
            return []
        finally:
            db.close()
    
    @staticmethod
    def get_assessment_questions(domain_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get assessment questions, optionally filtered by domain
        
        Args:
            domain_id: Optional domain ID filter
            
        Returns:
            List of assessment question dictionaries
        """
        try:
            db = get_session()
            
            query = db.query(AssessmentQuestion)
            
            if domain_id is not None:
                query = query.filter(AssessmentQuestion.domain_id == domain_id)
            
            questions = query.all()
            
            return [question.to_dict() for question in questions]
            
        except Exception as e:
            logger.error(f"Error getting assessment questions: {str(e)}")
            return []
        finally:
            db.close() 
   
    @staticmethod
    def get_industry_validations(
        industry_id: Optional[int] = None,
        company_size: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get industry validations, optionally filtered by industry and company size
        
        Args:
            industry_id: Optional industry ID filter
            company_size: Optional company size filter
            
        Returns:
            List of industry validation dictionaries
        """
        try:
            db = get_session()
            
            query = db.query(IndustryValidation)
            
            if industry_id is not None:
                query = query.filter(IndustryValidation.industry_id == industry_id)
            
            if company_size is not None:
                query = query.filter(IndustryValidation.company_size == company_size)
            
            validations = query.all()
            
            return [validation.to_dict() for validation in validations]
            
        except Exception as e:
            logger.error(f"Error getting industry validations: {str(e)}")
            return []
        finally:
            db.close()
    
    @staticmethod
    def get_validation_metrics(validation_id: int) -> List[Dict[str, Any]]:
        """
        Get validation metrics for an industry validation
        
        Args:
            validation_id: Industry validation ID
            
        Returns:
            List of validation metric dictionaries
        """
        try:
            db = get_session()
            
            metrics = db.query(ValidationMetric).filter(
                ValidationMetric.validation_id == validation_id
            ).all()
            
            return [metric.to_dict() for metric in metrics]
            
        except Exception as e:
            logger.error(f"Error getting validation metrics: {str(e)}")
            return []
        finally:
            db.close()
    
    @staticmethod
    def get_validation_responses(
        question_id: Optional[int] = None,
        industry_id: Optional[int] = None,
        company_size: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get validation responses, optionally filtered by question, industry, and company size
        
        Args:
            question_id: Optional question ID filter
            industry_id: Optional industry ID filter
            company_size: Optional company size filter
            
        Returns:
            List of validation response dictionaries
        """
        try:
            db = get_session()
            
            query = db.query(ValidationResponse)
            
            if question_id is not None:
                query = query.filter(ValidationResponse.question_id == question_id)
            
            if industry_id is not None:
                query = query.filter(ValidationResponse.industry_id == industry_id)
            
            if company_size is not None:
                query = query.filter(ValidationResponse.company_size == company_size)
            
            responses = query.all()
            
            return [response.to_dict() for response in responses]
            
        except Exception as e:
            logger.error(f"Error getting validation responses: {str(e)}")
            return []
        finally:
            db.close()    
    @
staticmethod
    def get_scoring_rubrics(domain_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Get scoring rubrics, optionally filtered by domain
        
        Args:
            domain_id: Optional domain ID filter
            
        Returns:
            List of scoring rubric dictionaries
        """
        try:
            db = get_session()
            
            query = db.query(ScoringRubric)
            
            if domain_id is not None:
                query = query.filter(ScoringRubric.domain_id == domain_id)
            
            rubrics = query.order_by(ScoringRubric.domain_id, ScoringRubric.score_level).all()
            
            return [rubric.to_dict() for rubric in rubrics]
            
        except Exception as e:
            logger.error(f"Error getting scoring rubrics: {str(e)}")
            return []
        finally:
            db.close()
    
    @staticmethod
    def get_industry_benchmarks(
        industry_id: Optional[int] = None,
        domain_id: Optional[int] = None,
        company_size: Optional[str] = None
    ) -> List[Dict[str, Any]]:
        """
        Get industry benchmarks, optionally filtered by industry, domain, and company size
        
        Args:
            industry_id: Optional industry ID filter
            domain_id: Optional domain ID filter
            company_size: Optional company size filter
            
        Returns:
            List of industry benchmark dictionaries
        """
        try:
            db = get_session()
            
            query = db.query(IndustryBenchmark)
            
            if industry_id is not None:
                query = query.filter(IndustryBenchmark.industry_id == industry_id)
            
            if domain_id is not None:
                query = query.filter(IndustryBenchmark.domain_id == domain_id)
            
            if company_size is not None:
                query = query.filter(IndustryBenchmark.company_size == company_size)
            
            benchmarks = query.all()
            
            return [benchmark.to_dict() for benchmark in benchmarks]
            
        except Exception as e:
            logger.error(f"Error getting industry benchmarks: {str(e)}")
            return []
        finally:
            db.close()    

    @staticmethod
    def calculate_validation_metrics(
        industry_id: int,
        company_size: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Calculate validation metrics for an industry
        
        Args:
            industry_id: Industry sector ID
            company_size: Optional company size filter
            
        Returns:
            Dictionary with validation metrics
        """
        try:
            db = get_session()
            
            # Query validation responses
            query = db.query(ValidationResponse).filter(
                ValidationResponse.industry_id == industry_id
            )
            
            if company_size is not None:
                query = query.filter(ValidationResponse.company_size == company_size)
            
            responses = query.all()
            
            if not responses:
                return {
                    "industry_id": industry_id,
                    "company_size": company_size,
                    "error": "No validation responses found"
                }
            
            # Calculate metrics
            total_responses = len(responses)
            correct_responses = sum(1 for r in responses if r.is_correct)
            accuracy = correct_responses / total_responses if total_responses > 0 else 0
            
            # Calculate confidence interval (95%)
            if total_responses > 0:
                z = 1.96  # 95% confidence
                p = accuracy
                confidence_interval = z * np.sqrt((p * (1 - p)) / total_responses)
                confidence_lower = max(0, p - confidence_interval)
                confidence_upper = min(1, p + confidence_interval)
            else:
                confidence_lower = 0
                confidence_upper = 0
            
            # Calculate precision, recall, and F1 score
            # (simplified calculation assuming binary classification)
            true_positives = sum(1 for r in responses if r.is_correct and r.riskai_response == "yes")
            false_positives = sum(1 for r in responses if not r.is_correct and r.riskai_response == "yes")
            false_negatives = sum(1 for r in responses if not r.is_correct and r.riskai_response == "no")
            
            precision = true_positives / (true_positives + false_positives) if (true_positives + false_positives) > 0 else 0
            recall = true_positives / (true_positives + false_negatives) if (true_positives + false_negatives) > 0 else 0
            f1_score = 2 * (precision * recall) / (precision + recall) if (precision + recall) > 0 else 0
            
            # Calculate average confidence score
            confidence_scores = [r.confidence_score for r in responses if r.confidence_score is not None]
            avg_confidence = sum(confidence_scores) / len(confidence_scores) if confidence_scores else 0
            
            # Save metrics to database
            validation_id = ValidationDataManager.add_industry_validation(
                industry_id=industry_id,
                company_size=company_size or "all",
                company_count=len(set(r.validator_id for r in responses if r.validator_id)),
                average_accuracy=accuracy,
                confidence_interval=(confidence_lower, confidence_upper),
                precision_score=precision,
                recall_score=recall,
                f1_score=f1_score,
                validation_methodology="Automated calculation based on expert validation responses"
            )
            
            if validation_id:
                # Add additional metrics
                ValidationDataManager.add_validation_metric(
                    validation_id=validation_id,
                    metric_name="average_confidence_score",
                    metric_value=avg_confidence,
                    metric_description="Average confidence score for RiskAI responses"
                )
                
                ValidationDataManager.add_validation_metric(
                    validation_id=validation_id,
                    metric_name="total_responses",
                    metric_value=total_responses,
                    metric_description="Total number of validation responses"
                )
            
            return {
                "industry_id": industry_id,
                "company_size": company_size,
                "total_responses": total_responses,
                "accuracy": accuracy,
                "confidence_interval": [confidence_lower, confidence_upper],
                "precision": precision,
                "recall": recall,
                "f1_score": f1_score,
                "average_confidence_score": avg_confidence
            }
            
        except Exception as e:
            logger.error(f"Error calculating validation metrics: {str(e)}")
            return {
                "industry_id": industry_id,
                "company_size": company_size,
                "error": str(e)
            }
        finally:
            db.close()    

    @staticmethod
    def import_validation_data_from_csv(file_path: str) -> Dict[str, Any]:
        """
        Import validation data from a CSV file
        
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
                        # Get or create industry
                        industry_name = row.get('industry')
                        if not industry_name:
                            raise ValueError("Missing industry name")
                        
                        industry_id = ValidationDataManager.add_industry_sector(
                            name=industry_name,
                            description=row.get('industry_description')
                        )
                        
                        if not industry_id:
                            raise ValueError(f"Failed to add industry: {industry_name}")
                        
                        # Get or create framework
                        framework_name = row.get('framework')
                        if not framework_name:
                            raise ValueError("Missing framework name")
                        
                        framework_id = ValidationDataManager.add_security_framework(
                            name=framework_name,
                            version=row.get('framework_version'),
                            description=row.get('framework_description'),
                            source_url=row.get('framework_url')
                        )
                        
                        if not framework_id:
                            raise ValueError(f"Failed to add framework: {framework_name}")
                        
                        # Get or create domain
                        domain_name = row.get('domain')
                        if not domain_name:
                            raise ValueError("Missing domain name")
                        
                        domain_id = ValidationDataManager.add_security_domain(
                            framework_id=framework_id,
                            name=domain_name,
                            description=row.get('domain_description'),
                            weight=float(row.get('domain_weight', 1.0))
                        )
                        
                        if not domain_id:
                            raise ValueError(f"Failed to add domain: {domain_name}")
                        
                        # Get or create question
                        question_text = row.get('question')
                        if not question_text:
                            raise ValueError("Missing question text")
                        
                        question_type = row.get('question_type', 'text')
                        options = row.get('options', '').split('|') if row.get('options') else None
                        
                        question_id = ValidationDataManager.add_assessment_question(
                            domain_id=domain_id,
                            question_text=question_text,
                            question_type=question_type,
                            options=options,
                            weight=float(row.get('question_weight', 1.0)),
                            guidance=row.get('guidance'),
                            evidence_required=row.get('evidence_required', '').lower() in ('true', 'yes', '1')
                        )
                        
                        if not question_id:
                            raise ValueError(f"Failed to add question: {question_text}")
                        
                        # Add validation response
                        company_size = row.get('company_size', 'medium')
                        expert_response = row.get('expert_response')
                        riskai_response = row.get('riskai_response')
                        is_correct = row.get('is_correct', '').lower() in ('true', 'yes', '1')
                        confidence_score = float(row.get('confidence_score', 0)) if row.get('confidence_score') else None
                        
                        if expert_response and riskai_response:
                            response_id = ValidationDataManager.add_validation_response(
                                question_id=question_id,
                                industry_id=industry_id,
                                company_size=company_size,
                                expert_response=expert_response,
                                riskai_response=riskai_response,
                                is_correct=is_correct,
                                confidence_score=confidence_score,
                                validator_id=row.get('validator_id')
                            )
                            
                            if not response_id:
                                raise ValueError(f"Failed to add validation response for question {question_id}")
                        
                        results["successful"] += 1
                    
                    except Exception as e:
                        results["failed"] += 1
                        results["errors"].append(f"Error processing row: {str(e)}")
            
            logger.info(f"Imported {results['successful']} validation data points from CSV")
            return results
            
        except Exception as e:
            logger.error(f"Error importing validation data from CSV: {str(e)}")
            return {
                "total": 0,
                "successful": 0,
                "failed": 0,
                "errors": [str(e)]
            }    

    @staticmethod
    def import_scoring_rubrics_from_csv(file_path: str) -> Dict[str, Any]:
        """
        Import scoring rubrics from a CSV file
        
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
                        # Get domain
                        domain_id = int(row.get('domain_id', 0))
                        if not domain_id:
                            # Try to find domain by name and framework
                            framework_name = row.get('framework')
                            domain_name = row.get('domain')
                            
                            if not framework_name or not domain_name:
                                raise ValueError("Missing domain_id or framework/domain name")
                            
                            # Get framework ID
                            db = get_session()
                            framework = db.query(SecurityFramework).filter(
                                SecurityFramework.name == framework_name
                            ).first()
                            
                            if not framework:
                                raise ValueError(f"Framework not found: {framework_name}")
                            
                            # Get domain ID
                            domain = db.query(SecurityDomain).filter(
                                SecurityDomain.framework_id == framework.id,
                                SecurityDomain.name == domain_name
                            ).first()
                            
                            if not domain:
                                raise ValueError(f"Domain not found: {domain_name} in framework {framework_name}")
                            
                            domain_id = domain.id
                            db.close()
                        
                        # Get score level
                        score_level = int(row.get('score_level', 0))
                        if not score_level or score_level < 1 or score_level > 10:
                            raise ValueError(f"Invalid score level: {score_level}")
                        
                        # Get description
                        description = row.get('description')
                        if not description:
                            raise ValueError("Missing rubric description")
                        
                        # Get criteria
                        criteria = row.get('criteria', '').split('|') if row.get('criteria') else None
                        
                        # Get industry examples
                        industry_examples = {}
                        for key in row.keys():
                            if key.startswith('example_'):
                                industry = key[8:]  # Remove 'example_' prefix
                                if row[key]:
                                    industry_examples[industry] = row[key]
                        
                        # Add scoring rubric
                        rubric_id = ValidationDataManager.add_scoring_rubric(
                            domain_id=domain_id,
                            score_level=score_level,
                            description=description,
                            criteria=criteria,
                            industry_examples=industry_examples
                        )
                        
                        if not rubric_id:
                            raise ValueError(f"Failed to add scoring rubric for domain {domain_id}, score level {score_level}")
                        
                        results["successful"] += 1
                    
                    except Exception as e:
                        results["failed"] += 1
                        results["errors"].append(f"Error processing row: {str(e)}")
            
            logger.info(f"Imported {results['successful']} scoring rubrics from CSV")
            return results
            
        except Exception as e:
            logger.error(f"Error importing scoring rubrics from CSV: {str(e)}")
            return {
                "total": 0,
                "successful": 0,
                "failed": 0,
                "errors": [str(e)]
            }
        finally:
            try:
                db.close()
            except:
                pass   
 
    @staticmethod
    def import_industry_benchmarks_from_csv(file_path: str) -> Dict[str, Any]:
        """
        Import industry benchmarks from a CSV file
        
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
                        # Get industry
                        industry_id = int(row.get('industry_id', 0))
                        if not industry_id:
                            industry_name = row.get('industry')
                            if not industry_name:
                                raise ValueError("Missing industry_id or industry name")
                            
                            # Get industry ID
                            db = get_session()
                            industry = db.query(IndustrySector).filter(
                                IndustrySector.name == industry_name
                            ).first()
                            
                            if not industry:
                                raise ValueError(f"Industry not found: {industry_name}")
                            
                            industry_id = industry.id
                            db.close()
                        
                        # Get domain
                        domain_id = int(row.get('domain_id', 0))
                        if not domain_id:
                            domain_name = row.get('domain')
                            framework_name = row.get('framework')
                            
                            if not domain_name or not framework_name:
                                raise ValueError("Missing domain_id or domain/framework name")
                            
                            # Get framework and domain ID
                            db = get_session()
                            framework = db.query(SecurityFramework).filter(
                                SecurityFramework.name == framework_name
                            ).first()
                            
                            if not framework:
                                raise ValueError(f"Framework not found: {framework_name}")
                            
                            domain = db.query(SecurityDomain).filter(
                                SecurityDomain.framework_id == framework.id,
                                SecurityDomain.name == domain_name
                            ).first()
                            
                            if not domain:
                                raise ValueError(f"Domain not found: {domain_name} in framework {framework_name}")
                            
                            domain_id = domain.id
                            db.close()
                        
                        # Get company size
                        company_size = row.get('company_size', 'medium')
                        
                        # Get average score
                        average_score = float(row.get('average_score', 0))
                        if average_score < 0 or average_score > 10:
                            raise ValueError(f"Invalid average score: {average_score}")
                        
                        # Get percentile distribution
                        percentile_distribution = {}
                        for percentile in ['10', '25', '50', '75', '90']:
                            if row.get(f'percentile_{percentile}'):
                                percentile_distribution[percentile] = float(row.get(f'percentile_{percentile}'))
                        
                        # Get sample size
                        sample_size = int(row.get('sample_size', 0)) if row.get('sample_size') else None
                        
                        # Add industry benchmark
                        benchmark_id = ValidationDataManager.add_industry_benchmark(
                            industry_id=industry_id,
                            domain_id=domain_id,
                            company_size=company_size,
                            average_score=average_score,
                            percentile_distribution=percentile_distribution,
                            sample_size=sample_size
                        )
                        
                        if not benchmark_id:
                            raise ValueError(f"Failed to add industry benchmark for industry {industry_id}, domain {domain_id}")
                        
                        results["successful"] += 1
                    
                    except Exception as e:
                        results["failed"] += 1
                        results["errors"].append(f"Error processing row: {str(e)}")
            
            logger.info(f"Imported {results['successful']} industry benchmarks from CSV")
            return results
            
        except Exception as e:
            logger.error(f"Error importing industry benchmarks from CSV: {str(e)}")
            return {
                "total": 0,
                "successful": 0,
                "failed": 0,
                "errors": [str(e)]
            }
        finally:
            try:
                db.close()
            except:
                pass

# Create a global instance
validation_data_manager = ValidationDataManager()