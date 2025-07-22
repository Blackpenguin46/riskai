"""
Standardized Scoring System for RiskAI
Implements a weighted scoring system for security assessments
"""

import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime

from database.models import get_session
from database.validation_models import (
    SecurityDomain, AssessmentQuestion, ScoringRubric, IndustryBenchmark
)
from validation.validator import validation_data_manager

logger = logging.getLogger(__name__)

class ScoringSystem:
    """Implements a standardized scoring system for security assessments"""
    
    @staticmethod
    def calculate_domain_score(
        domain_id: int,
        responses: Dict[str, Any],
        industry_id: Optional[int] = None,
        company_size: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Calculate a score for a security domain based on responses
        
        Args:
            domain_id: Security domain ID
            responses: Dictionary of question_id -> response_value
            industry_id: Optional industry sector ID for industry-specific scoring
            company_size: Optional company size for size-specific scoring
            
        Returns:
            Dictionary with domain score data
        """
        try:
            db = get_session()
            
            # Get domain
            domain = db.query(SecurityDomain).filter(SecurityDomain.id == domain_id).first()
            
            if not domain:
                logger.error(f"Domain {domain_id} not found")
                return {"error": f"Domain {domain_id} not found"}
            
            # Get questions for this domain
            questions = db.query(AssessmentQuestion).filter(
                AssessmentQuestion.domain_id == domain_id
            ).all()
            
            if not questions:
                logger.error(f"No questions found for domain {domain_id}")
                return {"error": f"No questions found for domain {domain_id}"}
            
            # Calculate score
            total_weight = sum(question.weight for question in questions)
            weighted_scores = []
            question_scores = {}
            
            for question in questions:
                if question.id not in responses:
                    continue
                
                response_value = responses[question.id]
                
                # Calculate score based on question type
                score = ScoringSystem._calculate_question_score(
                    question=question,
                    response_value=response_value,
                    domain_id=domain_id
                )
                
                weighted_score = score * (question.weight / total_weight)
                weighted_scores.append(weighted_score)
                
                question_scores[question.id] = {
                    "question_text": question.question_text,
                    "response_value": response_value,
                    "score": score,
                    "weight": question.weight,
                    "weighted_score": weighted_score
                }
            
            # Calculate overall domain score
            if weighted_scores:
                domain_score = sum(weighted_scores)
            else:
                domain_score = 0
            
            # Get industry benchmark for comparison
            benchmark = None
            if industry_id is not None:
                benchmarks = validation_data_manager.get_industry_benchmarks(
                    industry_id=industry_id,
                    domain_id=domain_id,
                    company_size=company_size
                )
                
                if benchmarks:
                    benchmark = benchmarks[0]
            
            # Get scoring rubric for interpretation
            rubrics = validation_data_manager.get_scoring_rubrics(domain_id=domain_id)
            
            # Find the closest rubric
            closest_rubric = None
            if rubrics:
                # Round to nearest integer score
                rounded_score = round(domain_score)
                
                # Find exact match or closest
                exact_match = next((r for r in rubrics if r["score_level"] == rounded_score), None)
                if exact_match:
                    closest_rubric = exact_match
                else:
                    # Find closest
                    rubrics_sorted = sorted(rubrics, key=lambda r: abs(r["score_level"] - domain_score))
                    if rubrics_sorted:
                        closest_rubric = rubrics_sorted[0]
            
            # Build result
            result = {
                "domain_id": domain_id,
                "domain_name": domain.name,
                "domain_score": domain_score,
                "domain_score_rounded": round(domain_score),
                "question_scores": question_scores,
                "questions_answered": len(weighted_scores),
                "total_questions": len(questions),
                "completion_percentage": (len(weighted_scores) / len(questions)) * 100 if questions else 0
            }
            
            # Add benchmark comparison if available
            if benchmark:
                result["benchmark"] = {
                    "industry_average": benchmark["average_score"],
                    "percentile_distribution": benchmark.get("percentile_distribution", {}),
                    "difference": domain_score - benchmark["average_score"],
                    "percentage_difference": ((domain_score - benchmark["average_score"]) / benchmark["average_score"]) * 100 if benchmark["average_score"] > 0 else 0
                }
            
            # Add interpretation if available
            if closest_rubric:
                result["interpretation"] = {
                    "score_level": closest_rubric["score_level"],
                    "description": closest_rubric["description"],
                    "criteria": closest_rubric["criteria"]
                }
                
                # Add industry-specific example if available
                if industry_id is not None and closest_rubric.get("industry_examples"):
                    industry = db.query(IndustrySector).filter(IndustrySector.id == industry_id).first()
                    if industry and industry.name in closest_rubric["industry_examples"]:
                        result["interpretation"]["industry_example"] = closest_rubric["industry_examples"][industry.name]
            
            return result
            
        except Exception as e:
            logger.error(f"Error calculating domain score: {str(e)}")
            return {"error": str(e)}
        finally:
            db.close()
    
    @staticmethod
    def _calculate_question_score(
        question: AssessmentQuestion,
        response_value: Any,
        domain_id: int
    ) -> float:
        """
        Calculate a score for a question based on the response
        
        Args:
            question: Assessment question
            response_value: User's response
            domain_id: Security domain ID
            
        Returns:
            Score (0-10)
        """
        try:
            # Calculate score based on question type
            if question.question_type == "scale":
                # Scale questions are already scored (1-10)
                try:
                    return float(response_value)
                except (ValueError, TypeError):
                    return 0
            
            elif question.question_type == "boolean":
                # Boolean questions are scored as 10 (yes/true) or 0 (no/false)
                if isinstance(response_value, bool):
                    return 10 if response_value else 0
                elif isinstance(response_value, str):
                    return 10 if response_value.lower() in ("yes", "true", "1") else 0
                else:
                    return 0
            
            elif question.question_type == "select":
                # Select questions are scored based on the option selected
                # We need to map options to scores
                if not question.options:
                    return 0
                
                # Get the index of the selected option
                try:
                    if isinstance(response_value, str):
                        option_index = question.options.index(response_value)
                    else:
                        return 0
                except (ValueError, TypeError):
                    return 0
                
                # Calculate score based on position in options list
                # Assuming options are ordered from worst to best
                return (option_index + 1) / len(question.options) * 10
            
            elif question.question_type == "multiselect":
                # Multiselect questions are scored based on the number of options selected
                # More options selected generally means better security posture
                if not question.options or not isinstance(response_value, list):
                    return 0
                
                # Calculate score based on percentage of options selected
                return len(response_value) / len(question.options) * 10
            
            elif question.question_type == "text":
                # Text questions are harder to score automatically
                # We would need NLP or predefined scoring criteria
                # For now, we'll return a neutral score
                return 5
            
            else:
                # Unknown question type
                return 0
                
        except Exception as e:
            logger.error(f"Error calculating question score: {str(e)}")
            return 0
    
    @staticmethod
    def calculate_assessment_score(
        responses: Dict[str, Dict[str, Any]],
        framework_id: Optional[int] = None,
        industry_id: Optional[int] = None,
        company_size: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Calculate an overall assessment score based on responses
        
        Args:
            responses: Dictionary of section_id -> {question_id -> response_value}
            framework_id: Optional framework ID filter
            industry_id: Optional industry sector ID for industry-specific scoring
            company_size: Optional company size for size-specific scoring
            
        Returns:
            Dictionary with assessment score data
        """
        try:
            db = get_session()
            
            # Get domains
            query = db.query(SecurityDomain)
            
            if framework_id is not None:
                query = query.filter(SecurityDomain.framework_id == framework_id)
            
            domains = query.all()
            
            if not domains:
                logger.error("No security domains found")
                return {"error": "No security domains found"}
            
            # Calculate score for each domain
            domain_scores = {}
            weighted_scores = []
            total_weight = sum(domain.weight for domain in domains)
            
            for domain in domains:
                # Find questions for this domain
                questions = db.query(AssessmentQuestion).filter(
                    AssessmentQuestion.domain_id == domain.id
                ).all()
                
                if not questions:
                    continue
                
                # Collect responses for this domain
                domain_responses = {}
                for question in questions:
                    # Find the response for this question
                    for section_id, section_responses in responses.items():
                        if str(question.id) in section_responses:
                            domain_responses[str(question.id)] = section_responses[str(question.id)]
                
                # Calculate domain score
                if domain_responses:
                    domain_score = ScoringSystem.calculate_domain_score(
                        domain_id=domain.id,
                        responses=domain_responses,
                        industry_id=industry_id,
                        company_size=company_size
                    )
                    
                    if "error" not in domain_score:
                        domain_scores[domain.id] = domain_score
                        
                        # Calculate weighted score
                        weighted_score = domain_score["domain_score"] * (domain.weight / total_weight)
                        weighted_scores.append(weighted_score)
            
            # Calculate overall assessment score
            if weighted_scores:
                assessment_score = sum(weighted_scores)
            else:
                assessment_score = 0
            
            # Calculate completion percentage
            total_questions = sum(len(db.query(AssessmentQuestion).filter(
                AssessmentQuestion.domain_id == domain.id
            ).all()) for domain in domains)
            
            answered_questions = sum(score["questions_answered"] for score in domain_scores.values())
            
            completion_percentage = (answered_questions / total_questions) * 100 if total_questions > 0 else 0
            
            # Get framework details
            framework = None
            if framework_id is not None:
                framework = db.query(SecurityFramework).filter(SecurityFramework.id == framework_id).first()
            
            # Build result
            result = {
                "assessment_score": assessment_score,
                "assessment_score_rounded": round(assessment_score),
                "domain_scores": domain_scores,
                "domains_assessed": len(domain_scores),
                "total_domains": len(domains),
                "questions_answered": answered_questions,
                "total_questions": total_questions,
                "completion_percentage": completion_percentage
            }
            
            # Add framework details if available
            if framework:
                result["framework"] = {
                    "id": framework.id,
                    "name": framework.name,
                    "version": framework.version
                }
            
            # Add industry details if available
            if industry_id is not None:
                industry = db.query(IndustrySector).filter(IndustrySector.id == industry_id).first()
                if industry:
                    result["industry"] = {
                        "id": industry.id,
                        "name": industry.name
                    }
            
            # Add company size if available
            if company_size:
                result["company_size"] = company_size
            
            # Add interpretation
            if assessment_score >= 9:
                result["interpretation"] = "Excellent security posture with comprehensive controls and mature practices."
            elif assessment_score >= 8:
                result["interpretation"] = "Very good security posture with strong controls and well-established practices."
            elif assessment_score >= 7:
                result["interpretation"] = "Good security posture with adequate controls and established practices."
            elif assessment_score >= 6:
                result["interpretation"] = "Satisfactory security posture with basic controls in place."
            elif assessment_score >= 5:
                result["interpretation"] = "Moderate security posture with some controls in place but significant gaps."
            elif assessment_score >= 4:
                result["interpretation"] = "Below average security posture with substantial gaps in controls."
            elif assessment_score >= 3:
                result["interpretation"] = "Poor security posture with major gaps in controls and practices."
            elif assessment_score >= 2:
                result["interpretation"] = "Very poor security posture with minimal controls in place."
            else:
                result["interpretation"] = "Critical security posture with severe deficiencies in controls and practices."
            
            return result
            
        except Exception as e:
            logger.error(f"Error calculating assessment score: {str(e)}")
            return {"error": str(e)}
        finally:
            db.close()
    
    @staticmethod
    def generate_recommendations(
        assessment_score: Dict[str, Any],
        industry_id: Optional[int] = None,
        company_size: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Generate recommendations based on assessment score
        
        Args:
            assessment_score: Assessment score data from calculate_assessment_score
            industry_id: Optional industry sector ID for industry-specific recommendations
            company_size: Optional company size for size-specific recommendations
            
        Returns:
            Dictionary with recommendations
        """
        try:
            # Find domains with lowest scores
            domain_scores = assessment_score.get("domain_scores", {})
            
            if not domain_scores:
                return {"error": "No domain scores available"}
            
            # Sort domains by score (ascending)
            sorted_domains = sorted(
                domain_scores.values(),
                key=lambda d: d["domain_score"]
            )
            
            # Get the lowest scoring domains (up to 3)
            lowest_domains = sorted_domains[:3]
            
            # Generate recommendations for each domain
            recommendations = []
            
            for domain in lowest_domains:
                domain_id = domain["domain_id"]
                domain_name = domain["domain_name"]
                domain_score = domain["domain_score"]
                
                # Get domain-specific recommendations
                domain_recommendations = ScoringSystem._generate_domain_recommendations(
                    domain_id=domain_id,
                    domain_score=domain_score,
                    industry_id=industry_id,
                    company_size=company_size
                )
                
                recommendations.append({
                    "domain_id": domain_id,
                    "domain_name": domain_name,
                    "domain_score": domain_score,
                    "recommendations": domain_recommendations
                })
            
            # Generate overall recommendations
            overall_score = assessment_score.get("assessment_score", 0)
            overall_recommendations = []
            
            if overall_score < 3:
                overall_recommendations.append(
                    "Establish a basic security program with fundamental controls and practices."
                )
                overall_recommendations.append(
                    "Prioritize addressing critical vulnerabilities and implementing essential security controls."
                )
                overall_recommendations.append(
                    "Consider engaging security experts to help establish a security roadmap."
                )
            elif overall_score < 5:
                overall_recommendations.append(
                    "Strengthen your security program by addressing significant gaps in controls."
                )
                overall_recommendations.append(
                    "Implement a risk management process to identify and prioritize security risks."
                )
                overall_recommendations.append(
                    "Develop and document security policies and procedures."
                )
            elif overall_score < 7:
                overall_recommendations.append(
                    "Enhance your security program by addressing moderate gaps in controls."
                )
                overall_recommendations.append(
                    "Implement continuous monitoring and regular security assessments."
                )
                overall_recommendations.append(
                    "Provide security awareness training to all employees."
                )
            elif overall_score < 9:
                overall_recommendations.append(
                    "Optimize your security program by addressing minor gaps in controls."
                )
                overall_recommendations.append(
                    "Implement advanced security controls and practices."
                )
                overall_recommendations.append(
                    "Consider pursuing security certifications or compliance frameworks."
                )
            else:
                overall_recommendations.append(
                    "Maintain your excellent security posture through continuous improvement."
                )
                overall_recommendations.append(
                    "Share your security practices and lessons learned with the community."
                )
                overall_recommendations.append(
                    "Explore emerging security technologies and practices."
                )
            
            return {
                "overall_recommendations": overall_recommendations,
                "domain_recommendations": recommendations
            }
            
        except Exception as e:
            logger.error(f"Error generating recommendations: {str(e)}")
            return {"error": str(e)}
    
    @staticmethod
    def _generate_domain_recommendations(
        domain_id: int,
        domain_score: float,
        industry_id: Optional[int] = None,
        company_size: Optional[str] = None
    ) -> List[str]:
        """
        Generate recommendations for a specific domain
        
        Args:
            domain_id: Security domain ID
            domain_score: Domain score
            industry_id: Optional industry sector ID
            company_size: Optional company size
            
        Returns:
            List of recommendations
        """
        try:
            db = get_session()
            
            # Get domain
            domain = db.query(SecurityDomain).filter(SecurityDomain.id == domain_id).first()
            
            if not domain:
                return ["Domain not found"]
            
            # Get framework
            framework = db.query(SecurityFramework).filter(SecurityFramework.id == domain.framework_id).first()
            
            framework_name = framework.name if framework else "Unknown"
            
            # Generate recommendations based on domain and score
            recommendations = []
            
            # Generic recommendations based on domain name and score
            if "identity" in domain.name.lower() or "access" in domain.name.lower():
                if domain_score < 3:
                    recommendations.append("Implement basic identity and access management controls.")
                    recommendations.append("Establish a process for user account management.")
                elif domain_score < 5:
                    recommendations.append("Implement multi-factor authentication for privileged accounts.")
                    recommendations.append("Review and update access control policies.")
                elif domain_score < 7:
                    recommendations.append("Implement role-based access control (RBAC).")
                    recommendations.append("Conduct regular access reviews.")
                elif domain_score < 9:
                    recommendations.append("Implement just-in-time access for privileged accounts.")
                    recommendations.append("Automate access provisioning and deprovisioning.")
                else:
                    recommendations.append("Explore advanced identity and access management technologies.")
                    recommendations.append("Implement continuous access evaluation.")
            
            elif "data" in domain.name.lower() or "information" in domain.name.lower():
                if domain_score < 3:
                    recommendations.append("Identify and classify sensitive data.")
                    recommendations.append("Implement basic data protection controls.")
                elif domain_score < 5:
                    recommendations.append("Implement data encryption for sensitive data.")
                    recommendations.append("Develop and document data handling procedures.")
                elif domain_score < 7:
                    recommendations.append("Implement data loss prevention (DLP) controls.")
                    recommendations.append("Conduct regular data security assessments.")
                elif domain_score < 9:
                    recommendations.append("Implement advanced data protection controls.")
                    recommendations.append("Automate data classification and protection.")
                else:
                    recommendations.append("Explore emerging data protection technologies.")
                    recommendations.append("Implement privacy by design principles.")
            
            elif "network" in domain.name.lower():
                if domain_score < 3:
                    recommendations.append("Implement basic network security controls.")
                    recommendations.append("Segment the network to isolate sensitive systems.")
                elif domain_score < 5:
                    recommendations.append("Implement intrusion detection and prevention systems.")
                    recommendations.append("Conduct regular vulnerability scanning.")
                elif domain_score < 7:
                    recommendations.append("Implement network monitoring and anomaly detection.")
                    recommendations.append("Conduct regular penetration testing.")
                elif domain_score < 9:
                    recommendations.append("Implement zero trust network architecture.")
                    recommendations.append("Automate network security monitoring and response.")
                else:
                    recommendations.append("Explore advanced network security technologies.")
                    recommendations.append("Implement software-defined networking with security controls.")
            
            elif "incident" in domain.name.lower() or "response" in domain.name.lower():
                if domain_score < 3:
                    recommendations.append("Develop an incident response plan.")
                    recommendations.append("Establish an incident response team.")
                elif domain_score < 5:
                    recommendations.append("Conduct regular incident response exercises.")
                    recommendations.append("Implement incident detection and alerting.")
                elif domain_score < 7:
                    recommendations.append("Implement automated incident response for common scenarios.")
                    recommendations.append("Establish relationships with external incident response resources.")
                elif domain_score < 9:
                    recommendations.append("Implement advanced threat hunting capabilities.")
                    recommendations.append("Integrate threat intelligence into incident response.")
                else:
                    recommendations.append("Explore advanced incident response technologies.")
                    recommendations.append("Contribute to industry threat intelligence sharing.")
            
            # Add framework-specific recommendations
            if framework_name == "NIST CSF":
                recommendations.append(f"Review the NIST CSF guidance for the {domain.name} domain.")
            elif framework_name == "ISO 27001":
                recommendations.append(f"Review the ISO 27001 controls related to {domain.name}.")
            elif framework_name == "CIS Controls":
                recommendations.append(f"Implement the CIS Controls related to {domain.name}.")
            
            # Add industry-specific recommendations if available
            if industry_id is not None:
                industry = db.query(IndustrySector).filter(IndustrySector.id == industry_id).first()
                if industry:
                    if industry.name == "Healthcare":
                        recommendations.append(f"Ensure compliance with healthcare regulations for {domain.name}.")
                    elif industry.name == "Finance":
                        recommendations.append(f"Implement financial industry best practices for {domain.name}.")
                    elif industry.name == "Retail":
                        recommendations.append(f"Address retail-specific {domain.name} challenges.")
                    elif industry.name == "Manufacturing":
                        recommendations.append(f"Consider operational technology impacts on {domain.name}.")
            
            # Add company size-specific recommendations
            if company_size == "small":
                recommendations.append("Consider managed security services to address resource constraints.")
            elif company_size == "enterprise":
                recommendations.append("Implement enterprise-scale security automation and orchestration.")
            
            return recommendations
            
        except Exception as e:
            logger.error(f"Error generating domain recommendations: {str(e)}")
            return ["Error generating recommendations"]
        finally:
            db.close()

# Create a global instance
scoring_system = ScoringSystem()