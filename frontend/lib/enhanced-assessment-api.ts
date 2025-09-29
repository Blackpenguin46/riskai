/**
 * Enhanced Assessment API Client
 * Handles 120-question system with industry adaptations
 */

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

export interface IndustryProfile {
  industry?: string;
  compliance_requirements?: string[];
  company_size?: string;
  data_types?: string[];
}

export interface Question {
  id: string;
  domain: string;
  question_text: string;
  question_type: string;
  weight: number;
  options?: string[];
  min_value?: number;
  max_value?: number;
  help_text?: string;
  compliance_frameworks?: string[];
  industry_specific: boolean;
}

export interface AssessmentQuestions {
  total_questions: number;
  industry?: string;
  compliance_requirements?: string[];
  domains: Record<string, Question[]>;
  domain_summary: Record<string, number>;
}

export interface ScoringResult {
  assessment_id: number;
  overall_score: number;
  risk_level: string;
  risk_color: string;
  execution_time_ms: number;
  section_breakdown: Array<{
    section_id: string;
    section_name: string;
    score: number;
    risk_level: string;
    weight: number;
    questions_answered: number;
    total_questions: number;
  }>;
  risk_categorization?: {
    confidence_interval: {
      lower_bound: number;
      upper_bound: number;
      confidence_level: number;
    };
    statistical_significance: number;
    margin_of_error: number;
    industry?: string;
    company_size?: string;
    recommendations: string[];
  };
}

/**
 * Get tailored questions based on industry profile
 */
export async function getTailoredQuestions(profile: IndustryProfile): Promise<AssessmentQuestions> {
  const response = await fetch(`${API_BASE_URL}/assessment/questions`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(profile),
  });

  if (!response.ok) {
    throw new Error(`Failed to get tailored questions: ${response.statusText}`);
  }

  return response.json();
}

/**
 * Get questions for a specific domain
 */
export async function getDomainQuestions(domain: string, industry?: string): Promise<{
  domain: string;
  industry?: string;
  questions: Question[];
}> {
  const url = new URL(`${API_BASE_URL}/assessment/questions/domain/${domain}`);
  if (industry) {
    url.searchParams.append('industry', industry);
  }

  const response = await fetch(url.toString());
  
  if (!response.ok) {
    throw new Error(`Failed to get domain questions: ${response.statusText}`);
  }

  return response.json();
}

/**
 * Get supported industries
 */
export async function getSupportedIndustries(): Promise<{
  industries: string[];
  descriptions: Record<string, string>;
}> {
  const response = await fetch(`${API_BASE_URL}/assessment/industries`);
  
  if (!response.ok) {
    throw new Error(`Failed to get industries: ${response.statusText}`);
  }

  return response.json();
}

/**
 * Get supported compliance frameworks
 */
export async function getComplianceFrameworks(): Promise<{
  frameworks: string[];
  descriptions: Record<string, string>;
}> {
  const response = await fetch(`${API_BASE_URL}/assessment/compliance-frameworks`);
  
  if (!response.ok) {
    throw new Error(`Failed to get compliance frameworks: ${response.statusText}`);
  }

  return response.json();
}

/**
 * Score individual question
 */
export async function scoreQuestion(questionData: {
  question_id: string;
  question_type: string;
  answer: any;
  weight?: number;
  question_options?: string[];
  min_value?: number;
  max_value?: number;
}): Promise<{
  question_id: string;
  raw_score: number;
  max_score: number;
  percentage: number;
}> {
  const response = await fetch(`${API_BASE_URL}/scoring/question`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(questionData),
  });

  if (!response.ok) {
    throw new Error(`Failed to score question: ${response.statusText}`);
  }

  return response.json();
}

/**
 * Calculate comprehensive assessment score
 */
export async function calculateAssessmentScore(assessmentId: number, profile?: IndustryProfile): Promise<ScoringResult> {
  const scoringRequest = {
    assessment_id: assessmentId,
    methodology: 'default',
    include_confidence: true,
    include_benchmarking: !!profile?.industry,
    industry: profile?.industry,
    company_size: profile?.company_size,
  };

  const response = await fetch(`${API_BASE_URL}/scoring/calculate`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(scoringRequest),
  });

  if (!response.ok) {
    throw new Error(`Failed to calculate assessment score: ${response.statusText}`);
  }

  return response.json();
}

/**
 * Get scoring methodology and formulas
 */
export async function getScoringMethodology(): Promise<{
  methodology: {
    name: string;
    version: string;
    description: string;
  };
  formulas: Record<string, string>;
  section_weights: Record<string, number>;
  risk_levels: Record<string, any>;
}> {
  const response = await fetch(`${API_BASE_URL}/scoring/formula`);
  
  if (!response.ok) {
    throw new Error(`Failed to get scoring methodology: ${response.statusText}`);
  }

  return response.json();
}