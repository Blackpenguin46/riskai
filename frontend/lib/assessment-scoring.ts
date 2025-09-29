/**
 * Mathematical Assessment Scoring System
 * Aligned with SEET paper's holistic approach to emerging technology risk management
 * 
 * This module provides precise mathematical formulas for scoring assessment responses
 * and generating AI-powered strategic feedback based on the assessment results.
 */

import { ASSESSMENT_SECTIONS, SECTION_WEIGHTS, RISK_LEVELS, Question, AssessmentSection } from './assessment-questions';

// Mathematical scoring formulas aligned with SEET paper requirements
export interface SectionScore {
  sectionId: string;
  sectionName: string;
  score: number;
  maxScore: number;
  percentage: number;
  weight: number;
  riskLevel: string;
  questionsAnswered: number;
  totalQuestions: number;
}

export interface OverallScore {
  totalScore: number;
  maxScore: number;
  percentage: number;
  riskLevel: string;
  riskColor: string;
  confidenceInterval: [number, number];
  sectionBreakdown: SectionScore[];
}

// Question scoring logic with defined mathematical rules
export function scoreQuestion(question: Question, answer: any): number {
  if (answer === null || answer === undefined || answer === '') {
    return 0; // No answer = 0 points
  }

  switch (question.type) {
    case 'boolean':
      // Boolean questions: true = full points, false = 0 points
      return answer === true ? question.weight : 0;

    case 'scale':
      // Scale questions: normalize to question weight
      const min = question.min || 1;
      const max = question.max || 5;
      const normalizedScore = (answer - min) / (max - min);
      return normalizedScore * question.weight;

    case 'select':
      // Select questions: score based on option position (higher = better)
      if (!question.options || !Array.isArray(question.options)) return 0;
      const optionIndex = question.options.indexOf(answer);
      if (optionIndex === -1) return 0;
      
      // Score based on position in options array (last option = highest score)
      const optionScore = optionIndex / (question.options.length - 1);
      return optionScore * question.weight;

    case 'multiselect':
      // Multiselect questions: score based on number of selections
      if (!Array.isArray(answer) || !question.options) return 0;
      
      // Filter out 'None' answers
      const validSelections = answer.filter(selection => 
        selection !== 'None' && selection !== 'No' && question.options!.includes(selection)
      );
      
      if (validSelections.length === 0) return 0;
      
      // Score based on percentage of available options selected
      const selectionRatio = validSelections.length / (question.options.length - 1); // -1 for 'None' option
      return Math.min(selectionRatio, 1) * question.weight;

    case 'text':
      // Text questions: full points if answered, 0 if empty
      return answer.trim().length > 0 ? question.weight : 0;

    default:
      return 0;
  }
}

// Calculate section score using the defined formula:
// Section Score = Σ(Question Score × Question Weight) / Σ(Question Weights) × 100
export function calculateSectionScore(
  sectionId: string, 
  questions: Question[], 
  responses: Record<string, any>
): SectionScore {
  const section = ASSESSMENT_SECTIONS.find(s => s.id === sectionId);
  if (!section) {
    throw new Error(`Section ${sectionId} not found`);
  }

  let totalScore = 0;
  let maxPossibleScore = 0;
  let questionsAnswered = 0;

  questions.forEach(question => {
    const answer = responses[question.id];
    const questionScore = scoreQuestion(question, answer);
    
    totalScore += questionScore;
    maxPossibleScore += question.weight;
    
    if (answer !== null && answer !== undefined && answer !== '') {
      questionsAnswered++;
    }
  });

  // Calculate percentage score
  const percentage = maxPossibleScore > 0 ? (totalScore / maxPossibleScore) * 100 : 0;
  
  // Determine risk level for this section
  const riskLevel = getRiskLevel(percentage);

  return {
    sectionId,
    sectionName: section.name,
    score: totalScore,
    maxScore: maxPossibleScore,
    percentage: Math.round(percentage * 100) / 100, // Round to 2 decimal places
    weight: section.weight,
    riskLevel,
    questionsAnswered,
    totalQuestions: questions.length
  };
}

// Calculate overall score using weighted sections:
// Overall Score = Σ(Section Score × Section Weight)
export function calculateOverallScore(
  sections: AssessmentSection[], 
  responses: Record<string, Record<string, any>>
): OverallScore {
  const sectionBreakdown: SectionScore[] = [];
  let weightedScore = 0;
  let totalWeight = 0;

  sections.forEach(section => {
    const sectionResponses = responses[section.id] || {};
    const sectionScore = calculateSectionScore(section.id, section.questions, sectionResponses);
    
    sectionBreakdown.push(sectionScore);
    
    // Add to weighted score calculation
    weightedScore += (sectionScore.percentage * section.weight) / 100;
    totalWeight += section.weight;
  });

  // Overall percentage score
  const overallPercentage = totalWeight > 0 ? weightedScore : 0;
  
  // Determine overall risk level
  const riskLevel = getRiskLevel(overallPercentage);
  const riskColor = getRiskColor(riskLevel);
  
  // Calculate confidence interval (±5% based on completion rate)
  const totalQuestions = sections.reduce((sum, section) => sum + section.questions.length, 0);
  const answeredQuestions = sectionBreakdown.reduce((sum, section) => sum + section.questionsAnswered, 0);
  const completionRate = answeredQuestions / totalQuestions;
  const confidenceMargin = (1 - completionRate) * 10; // Up to ±10% margin for incomplete assessments
  
  const confidenceInterval: [number, number] = [
    Math.max(0, overallPercentage - confidenceMargin),
    Math.min(100, overallPercentage + confidenceMargin)
  ];

  return {
    totalScore: weightedScore,
    maxScore: 100,
    percentage: Math.round(overallPercentage * 100) / 100,
    riskLevel,
    riskColor,
    confidenceInterval,
    sectionBreakdown
  };
}

// Get risk level based on percentage score
export function getRiskLevel(percentage: number): string {
  if (percentage >= RISK_LEVELS.LOW.min) return RISK_LEVELS.LOW.label;
  if (percentage >= RISK_LEVELS.MEDIUM.min) return RISK_LEVELS.MEDIUM.label;
  if (percentage >= RISK_LEVELS.HIGH.min) return RISK_LEVELS.HIGH.label;
  return RISK_LEVELS.CRITICAL.label;
}

// Get risk color based on risk level
export function getRiskColor(riskLevel: string): string {
  switch (riskLevel) {
    case RISK_LEVELS.LOW.label: return RISK_LEVELS.LOW.color;
    case RISK_LEVELS.MEDIUM.label: return RISK_LEVELS.MEDIUM.color;
    case RISK_LEVELS.HIGH.label: return RISK_LEVELS.HIGH.color;
    case RISK_LEVELS.CRITICAL.label: return RISK_LEVELS.CRITICAL.color;
    default: return '#6b7280';
  }
}

// Generate section-specific recommendations based on score and responses
export function generateSectionRecommendations(
  sectionId: string, 
  sectionScore: SectionScore, 
  responses: Record<string, any>
): string[] {
  const recommendations: string[] = [];
  const section = ASSESSMENT_SECTIONS.find(s => s.id === sectionId);
  
  if (!section) return recommendations;

  // Generate recommendations based on section performance
  if (sectionScore.percentage < 40) {
    recommendations.push(`CRITICAL: ${section.name} requires immediate attention with a score of ${sectionScore.percentage}%`);
  } else if (sectionScore.percentage < 60) {
    recommendations.push(`HIGH PRIORITY: Significant improvements needed in ${section.name} (${sectionScore.percentage}%)`);
  } else if (sectionScore.percentage < 80) {
    recommendations.push(`MEDIUM PRIORITY: Consider enhancements to ${section.name} (${sectionScore.percentage}%)`);
  } else {
    recommendations.push(`GOOD: ${section.name} is performing well (${sectionScore.percentage}%)`);
  }

  // Add specific recommendations based on section type
  switch (sectionId) {
    case 'governance':
      if (sectionScore.percentage < 70) {
        recommendations.push('Establish formal security governance framework with executive support');
        recommendations.push('Implement regular risk assessments using industry-standard methodologies');
      }
      break;
    
    case 'emerging_tech':
      if (sectionScore.percentage < 60) {
        recommendations.push('Develop formal processes for evaluating emerging technology risks');
        recommendations.push('Implement AI/ML security standards including bias detection mechanisms');
        recommendations.push('Create governance frameworks for emerging technology adoption');
      }
      break;
    
    case 'access_control':
      if (sectionScore.percentage < 70) {
        recommendations.push('Implement multi-factor authentication across all critical systems');
        recommendations.push('Enforce principle of least privilege with regular access reviews');
      }
      break;
    
    case 'incident_response':
      if (sectionScore.percentage < 70) {
        recommendations.push('Develop and test incident response plans with regular tabletop exercises');
        recommendations.push('Establish dedicated incident response team with defined roles');
      }
      break;
  }

  return recommendations;
}

// Generate strategic recommendations based on overall assessment
export function generateStrategicRecommendations(
  responses: Record<string, Record<string, any>>, 
  overallScore: OverallScore
): {
  immediate: string[];
  shortTerm: string[];
  strategic: string[];
} {
  const immediate: string[] = [];
  const shortTerm: string[] = [];
  const strategic: string[] = [];

  // Analyze critical areas (sections with < 40% score)
  const criticalSections = overallScore.sectionBreakdown.filter(s => s.percentage < 40);
  const highRiskSections = overallScore.sectionBreakdown.filter(s => s.percentage >= 40 && s.percentage < 60);
  const mediumRiskSections = overallScore.sectionBreakdown.filter(s => s.percentage >= 60 && s.percentage < 80);

  // Immediate actions (0-30 days)
  if (criticalSections.length > 0) {
    immediate.push(`Address critical security gaps in: ${criticalSections.map(s => s.sectionName).join(', ')}`);
  }
  
  if (overallScore.percentage < 40) {
    immediate.push('Conduct emergency security assessment and implement basic security controls');
    immediate.push('Establish incident response procedures and emergency contact protocols');
  }

  // Short-term improvements (1-6 months)
  if (highRiskSections.length > 0) {
    shortTerm.push(`Implement security improvements in: ${highRiskSections.map(s => s.sectionName).join(', ')}`);
  }
  
  shortTerm.push('Develop comprehensive security policies and procedures');
  shortTerm.push('Implement security awareness training program');
  
  if (overallScore.sectionBreakdown.find(s => s.sectionId === 'emerging_tech')?.percentage < 60) {
    shortTerm.push('Establish emerging technology risk assessment processes');
  }

  // Strategic initiatives (6+ months)
  strategic.push('Implement holistic risk management framework aligned with business objectives');
  strategic.push('Develop security metrics and KPIs for continuous improvement');
  
  if (mediumRiskSections.length > 0) {
    strategic.push(`Optimize security practices in: ${mediumRiskSections.map(s => s.sectionName).join(', ')}`);
  }
  
  strategic.push('Establish security center of excellence and governance structure');
  strategic.push('Implement advanced threat detection and response capabilities');

  return {
    immediate,
    shortTerm,
    strategic
  };
}