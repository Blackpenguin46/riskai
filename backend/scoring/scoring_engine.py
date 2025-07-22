"""
Mathematical Scoring Engine for RiskAI
Implements precise mathematical formulas for assessment scoring
"""

import logging
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from dataclasses import dataclass

from database.models import get_session, Assessment, AssessmentResponse, SectionScore, DatabaseManager

logger = logging.getLogger(__name__)

@dataclass
class QuestionScore:
    """Individual question scoring result"""
    question_id: str
    raw_score: float
    weighted_score: float
    max_score: float
    percentage: float

@dataclass
class SectionScoreResult:
    """Section scoring result"""
    section_id: str
    section_name: str
    raw_score: float
    max_score: float
    percentage: float
    weight: float
    risk_level: str
    questions_answered: int
    total_questions: int
    question_scores: List[QuestionScore]

@dataclass
class OverallScoreResult:
    """Overall assessment scoring result"""
    total_score: float
    max_score: float
    percentage: float
    risk_level: str
    risk_color: str
    confidence_interval: Tuple[float, float]
    section_breakdown: List[SectionScoreResult]

# Section weights aligned with SEET paper's holistic risk management approach
SECTION_WEIGHTS = {
    'governance': 20,           # Strategic foundation
    'asset_management': 8,      # Technical visibility
    'data_protection': 12,      # Technical security
    'access_control': 12,       # Technical security
    'security_monitoring': 10,  # Technical detection
    'incident_response': 10,    # Operational resilience
    'business_continuity': 8,   # Operational resilience
    'security_awareness': 6,    # Operational culture
    'compliance': 4,            # Regulatory alignment
    'emerging_tech': 4,         # Innovation risk (SEET focus)
    'third_party': 4,           # Extended ecosystem
    'risk_management': 2        # Process maturity
}

# Risk level categories with mathematical thresholds
RISK_LEVELS = {
    'CRITICAL': {'min': 0, 'max': 40, 'label': 'Critical Risk', 'color': '#dc2626'},
    'HIGH': {'min': 41, 'max': 60, 'label': 'High Risk', 'color': '#ea580c'},
    'MEDIUM': {'min': 61, 'max': 80, 'label': 'Medium Risk', 'color': '#ca8a04'},
    'LOW': {'min': 81, 'max': 100, 'label': 'Low Risk', 'color': '#16a34a'}
}

# Question definitions with weights (simplified version - full version would be imported)
QUESTION_WEIGHTS = {
    # Governance questions
    'gov_001': 10, 'gov_002': 8, 'gov_003': 9, 'gov_004': 10, 'gov_005': 10,
    'gov_006': 9, 'gov_007': 8, 'gov_008': 7, 'gov_009': 6, 'gov_010': 8,
    
    # Asset Management questions
    'asset_001': 12, 'asset_002': 11, 'asset_003': 10, 'asset_004': 10, 'asset_005': 9,
    'asset_006': 9, 'asset_007': 11, 'asset_008': 10, 'asset_009': 9, 'asset_010': 9,
    
    # Data Protection questions
    'data_001': 11, 'data_002': 10, 'data_003': 12, 'data_004': 11, 'data_005': 11,
    'data_006': 9, 'data_007': 8, 'data_008': 8, 'data_009': 9, 'data_010': 11,
    
    # Add more question weights as needed...
}

class ScoringEngine:
    """Mathematical scoring engine with defined formulas"""
    
    @staticmethod
    def score_question(question_id: str, question_type: str, answer: Any, 
                      question_options: Optional[List[str]] = None,
                      min_value: Optional[int] = None, max_value: Optional[int] = None) -> QuestionScore:
        """
        Score individual question using mathematical rules
        
        Args:
            question_id: Question identifier
            question_type: Type of question (boolean, scale, select, multiselect, text)
            answer: User's answer
            question_options: Available options for select/multiselect questions
            min_value: Minimum value for scale questions
            max_value: Maximum value for scale questions
            
        Returns:
            QuestionScore with raw and weighted scores
        """
        question_weight = QUESTION_WEIGHTS.get(question_id, 5)  # Default weight
        
        if answer is None or answer == '' or answer == []:
            return QuestionScore(
                question_id=question_id,
                raw_score=0.0,
                weighted_score=0.0,
                max_score=question_weight,
                percentage=0.0
            )
        
        raw_score = 0.0
        
        try:
            if question_type == 'boolean':
                # Boolean questions: true = full points, false = 0 points
                raw_score = question_weight if answer is True else 0.0
                
            elif question_type == 'scale':
                # Scale questions: normalize to question weight
                min_val = min_value or 1
                max_val = max_value or 5
                normalized_score = (float(answer) - min_val) / (max_val - min_val)
                raw_score = normalized_score * question_weight
                
            elif question_type == 'select':
                # Select questions: score based on option position (higher = better)
                if question_options and answer in question_options:
                    option_index = question_options.index(answer)
                    # Score based on position in options array (last option = highest score)
                    option_score = option_index / (len(question_options) - 1) if len(question_options) > 1 else 1.0
                    raw_score = option_score * question_weight
                    
            elif question_type == 'multiselect':
                # Multiselect questions: score based on number of valid selections
                if isinstance(answer, list) and question_options:
                    # Filter out 'None' answers and invalid selections
                    valid_selections = [sel for sel in answer 
                                      if sel not in ['None', 'No'] and sel in question_options]
                    
                    if valid_selections:
                        # Score based on percentage of available options selected
                        available_options = len([opt for opt in question_options if opt not in ['None', 'No']])
                        selection_ratio = len(valid_selections) / available_options if available_options > 0 else 0
                        raw_score = min(selection_ratio, 1.0) * question_weight
                        
            elif question_type == 'text':
                # Text questions: full points if answered, 0 if empty
                raw_score = question_weight if str(answer).strip() else 0.0
                
        except (ValueError, TypeError, ZeroDivisionError) as e:
            logger.warning(f"Error scoring question {question_id}: {e}")
            raw_score = 0.0
        
        percentage = (raw_score / question_weight) * 100 if question_weight > 0 else 0.0
        
        return QuestionScore(
            question_id=question_id,
            raw_score=raw_score,
            weighted_score=raw_score,  # Same as raw_score for individual questions
            max_score=question_weight,
            percentage=percentage
        )
    
    @staticmethod
    def calculate_section_score(section_id: str, question_scores: List[QuestionScore]) -> SectionScoreResult:
        """
        Calculate section score using the formula:
        Section Score = Σ(Question Score × Question Weight) / Σ(Question Weights) × 100
        
        Args:
            section_id: Section identifier
            question_scores: List of individual question scores
            
        Returns:
            SectionScoreResult with calculated scores
        """
        if not question_scores:
            return SectionScoreResult(
                section_id=section_id,
                section_name=section_id.replace('_', ' ').title(),
                raw_score=0.0,
                max_score=0.0,
                percentage=0.0,
                weight=SECTION_WEIGHTS.get(section_id, 5),
                risk_level='Critical Risk',
                questions_answered=0,
                total_questions=0,
                question_scores=[]
            )
        
        total_score = sum(qs.raw_score for qs in question_scores)
        max_possible_score = sum(qs.max_score for qs in question_scores)
        questions_answered = sum(1 for qs in question_scores if qs.raw_score > 0)
        
        # Calculate percentage score
        percentage = (total_score / max_possible_score) * 100 if max_possible_score > 0 else 0.0
        
        # Determine risk level
        risk_level = ScoringEngine.get_risk_level(percentage)
        
        # Get section name
        section_names = {
            'governance': 'Governance & Risk Management',
            'asset_management': 'Asset Management',
            'data_protection': 'Data Protection',
            'access_control': 'Access Control',
            'security_monitoring': 'Security Monitoring & Detection',
            'incident_response': 'Incident Response',
            'business_continuity': 'Business Continuity & Disaster Recovery',
            'security_awareness': 'Security Awareness & Training',
            'compliance': 'Regulatory Compliance',
            'emerging_tech': 'Emerging Technologies Risk Management',
            'third_party': 'Third-Party Risk Management',
            'risk_management': 'Risk Management Process'
        }
        
        return SectionScoreResult(
            section_id=section_id,
            section_name=section_names.get(section_id, section_id.replace('_', ' ').title()),
            raw_score=total_score,
            max_score=max_possible_score,
            percentage=round(percentage, 2),
            weight=SECTION_WEIGHTS.get(section_id, 5),
            risk_level=risk_level,
            questions_answered=questions_answered,
            total_questions=len(question_scores),
            question_scores=question_scores
        )
    
    @staticmethod
    def calculate_overall_score(section_scores: List[SectionScoreResult]) -> OverallScoreResult:
        """
        Calculate overall score using weighted sections:
        Overall Score = Σ(Section Score × Section Weight)
        
        Where Section Weights:
        - Governance: 20%
        - Technical Controls (Asset Mgmt + Data Protection + Access Control + Monitoring): 40%
        - Operational (Incident Response + Business Continuity + Awareness): 25%
        - Compliance (Compliance + Emerging Tech + Third Party + Risk Mgmt): 15%
        
        Args:
            section_scores: List of section scoring results
            
        Returns:
            OverallScoreResult with calculated overall score
        """
        if not section_scores:
            return OverallScoreResult(
                total_score=0.0,
                max_score=100.0,
                percentage=0.0,
                risk_level='Critical Risk',
                risk_color='#dc2626',
                confidence_interval=(0.0, 0.0),
                section_breakdown=[]
            )
        
        weighted_score = 0.0
        total_weight = 0.0
        
        for section_score in section_scores:
            section_weight = section_score.weight
            weighted_score += (section_score.percentage * section_weight) / 100
            total_weight += section_weight
        
        # Overall percentage score
        overall_percentage = weighted_score if total_weight > 0 else 0.0
        
        # Determine overall risk level and color
        risk_level = ScoringEngine.get_risk_level(overall_percentage)
        risk_color = ScoringEngine.get_risk_color(risk_level)
        
        # Calculate confidence interval based on completion rate
        total_questions = sum(section.total_questions for section in section_scores)
        answered_questions = sum(section.questions_answered for section in section_scores)
        completion_rate = answered_questions / total_questions if total_questions > 0 else 0
        
        # Confidence margin: up to ±10% for incomplete assessments
        confidence_margin = (1 - completion_rate) * 10
        confidence_interval = (
            max(0.0, overall_percentage - confidence_margin),
            min(100.0, overall_percentage + confidence_margin)
        )
        
        return OverallScoreResult(
            total_score=weighted_score,
            max_score=100.0,
            percentage=round(overall_percentage, 2),
            risk_level=risk_level,
            risk_color=risk_color,
            confidence_interval=confidence_interval,
            section_breakdown=section_scores
        )
    
    @staticmethod
    def get_risk_level(percentage: float) -> str:
        """Get risk level based on percentage score"""
        if percentage >= RISK_LEVELS['LOW']['min']:
            return RISK_LEVELS['LOW']['label']
        elif percentage >= RISK_LEVELS['MEDIUM']['min']:
            return RISK_LEVELS['MEDIUM']['label']
        elif percentage >= RISK_LEVELS['HIGH']['min']:
            return RISK_LEVELS['HIGH']['label']
        else:
            return RISK_LEVELS['CRITICAL']['label']
    
    @staticmethod
    def get_risk_color(risk_level: str) -> str:
        """Get risk color based on risk level"""
        for level_data in RISK_LEVELS.values():
            if level_data['label'] == risk_level:
                return level_data['color']
        return '#6b7280'  # Default gray
    
    @staticmethod
    def score_assessment(assessment_id: int) -> OverallScoreResult:
        """
        Score a complete assessment using mathematical formulas
        
        Args:
            assessment_id: Assessment ID to score
            
        Returns:
            OverallScoreResult with complete scoring breakdown
        """
        db = get_session()
        try:
            # Get assessment responses
            responses = db.query(AssessmentResponse).filter(
                AssessmentResponse.assessment_id == assessment_id
            ).all()
            
            if not responses:
                logger.warning(f"No responses found for assessment {assessment_id}")
                return ScoringEngine.calculate_overall_score([])
            
            # Group responses by section
            section_responses = {}
            for response in responses:
                if response.section_id not in section_responses:
                    section_responses[response.section_id] = []
                section_responses[response.section_id].append(response)
            
            # Score each section
            section_scores = []
            for section_id, section_responses_list in section_responses.items():
                question_scores = []
                
                for response in section_responses_list:
                    # Parse response value
                    response_value = response.response_value
                    if response.response_type == 'boolean':
                        response_value = response_value.lower() == 'true' if isinstance(response_value, str) else bool(response_value)
                    elif response.response_type == 'scale':
                        response_value = float(response_value) if response_value else 0
                    elif response.response_type == 'multiselect':
                        # Handle multiselect responses (stored as JSON string or list)
                        if isinstance(response_value, str):
                            try:
                                import json
                                response_value = json.loads(response_value)
                            except:
                                response_value = [response_value] if response_value else []
                    
                    # Score the question
                    question_score = ScoringEngine.score_question(
                        question_id=response.question_id,
                        question_type=response.response_type or 'text',
                        answer=response_value
                    )
                    question_scores.append(question_score)
                
                # Calculate section score
                section_score = ScoringEngine.calculate_section_score(section_id, question_scores)
                section_scores.append(section_score)
            
            # Calculate overall score
            overall_score = ScoringEngine.calculate_overall_score(section_scores)
            
            # Save section scores to database
            ScoringEngine._save_section_scores(db, assessment_id, section_scores)
            
            # Update assessment with overall score
            assessment = db.query(Assessment).filter(Assessment.id == assessment_id).first()
            if assessment:
                assessment.overall_score = overall_score.percentage
                assessment.risk_level = overall_score.risk_level
                assessment.updated_at = datetime.utcnow()
                if overall_score.percentage == 100:
                    assessment.status = 'completed'
                    assessment.completed_at = datetime.utcnow()
            
            db.commit()
            
            logger.info(f"Scored assessment {assessment_id}: {overall_score.percentage}% ({overall_score.risk_level})")
            return overall_score
            
        except Exception as e:
            logger.error(f"Error scoring assessment {assessment_id}: {str(e)}")
            db.rollback()
            raise
        finally:
            db.close()
    
    @staticmethod
    def _save_section_scores(db, assessment_id: int, section_scores: List[SectionScoreResult]) -> None:
        """Save section scores to database"""
        # Delete existing section scores
        db.query(SectionScore).filter(SectionScore.assessment_id == assessment_id).delete()
        
        # Save new section scores
        for section_score in section_scores:
            db_section_score = SectionScore(
                assessment_id=assessment_id,
                section_id=section_score.section_id,
                score=section_score.percentage,
                maturity_level=section_score.risk_level,
                maturity_description=f"Section scored {section_score.percentage}% with {section_score.questions_answered}/{section_score.total_questions} questions answered",
                questions_answered=section_score.questions_answered,
                total_questions=section_score.total_questions,
                completion_rate=section_score.percentage,
                risk_breakdown={'risk_level': section_score.risk_level, 'percentage': section_score.percentage},
                recommendations=[]  # Will be populated by recommendation engine
            )
            db.add(db_section_score)

# Create a global instance
scoring_engine = ScoringEngine()