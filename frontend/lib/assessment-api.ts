/**
 * Assessment API Client
 * Handles communication with the 120-question assessment API endpoints
 */

// API base URL
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:9000';

// Types
export interface Question {
  id: string;
  text: string;
  type: 'boolean' | 'select' | 'multiselect' | 'scale' | 'text';
  options?: string[];
  min?: number;
  max?: number;
  weight: number;
  category?: string;
}

export interface AssessmentSection {
  id: string;
  name: string;
  description: string;
  weight: number;
  total_questions: number;
  questions: Question[];
}

export interface AssessmentProgress {
  completion_percentage: number;
  sections_completed: number;
  total_sections: number;
  status: string;
  section_progress?: any[];
}

export interface QuestionResponse {
  question_id: string;
  section_id: string;
  response_value: any;
  response_type?: string;
  time_spent_seconds?: number;
}

export interface AssessmentStartRequest {
  assessment_name?: string;
  user_id?: string;
  company_id?: number;
}

/**
 * Start a new 120-question assessment
 * @param request Assessment start parameters
 * @returns Assessment and session details
 */
export async function startAssessment(request: AssessmentStartRequest) {
  const response = await fetch(`${API_URL}/assessment/start`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(request),
  });

  if (!response.ok) {
    throw new Error(`Failed to start assessment: ${response.statusText}`);
  }

  return await response.json();
}

/**
 * Get all 120 questions organized by domain
 * @returns Complete question structure with sections and weights
 */
export async function getAllQuestions() {
  const response = await fetch(`${API_URL}/assessment/questions`);

  if (!response.ok) {
    throw new Error(`Failed to get questions: ${response.statusText}`);
  }

  return await response.json();
}

/**
 * Get questions for a specific domain
 * @param domain Domain/section ID
 * @returns Domain questions and metadata
 */
export async function getDomainQuestions(domain: string) {
  const response = await fetch(`${API_URL}/assessment/questions/${domain}`);

  if (!response.ok) {
    throw new Error(`Failed to get domain questions: ${response.statusText}`);
  }

  return await response.json();
}

/**
 * Submit answer for a specific question
 * @param sessionId Session ID
 * @param questionResponse Question response data
 * @returns Submission status and updated progress
 */
export async function submitResponse(sessionId: string, questionResponse: QuestionResponse) {
  const response = await fetch(`${API_URL}/assessment/response?session_id=${sessionId}`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(questionResponse),
  });

  if (!response.ok) {
    throw new Error(`Failed to submit response: ${response.statusText}`);
  }

  return await response.json();
}

/**
 * Get current progress status
 * @param sessionId Session ID
 * @returns Progress information
 */
export async function getProgress(sessionId: string): Promise<AssessmentProgress> {
  const response = await fetch(`${API_URL}/assessment/progress/${sessionId}`);

  if (!response.ok) {
    throw new Error(`Failed to get progress: ${response.statusText}`);
  }

  return await response.json();
}

/**
 * Update progress and save state
 * @param sessionId Session ID
 * @param updateData Progress update data
 * @returns Updated progress
 */
export async function updateProgress(sessionId: string, updateData: any) {
  const response = await fetch(`${API_URL}/assessment/progress/${sessionId}`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(updateData),
  });

  if (!response.ok) {
    throw new Error(`Failed to update progress: ${response.statusText}`);
  }

  return await response.json();
}

/**
 * Get questions for a specific section with optional session context
 * @param sectionId Section ID
 * @param sessionId Optional session ID for context
 * @returns Section questions with progress if session provided
 */
export async function getSectionQuestions(sectionId: string, sessionId?: string) {
  const url = sessionId 
    ? `${API_URL}/assessment/section/${sectionId}/questions?session_id=${sessionId}`
    : `${API_URL}/assessment/section/${sectionId}/questions`;

  const response = await fetch(url);

  if (!response.ok) {
    throw new Error(`Failed to get section questions: ${response.statusText}`);
  }

  return await response.json();
}

/**
 * Mark a section as complete
 * @param sectionId Section ID
 * @param sessionId Session ID
 * @returns Completion status and updated progress
 */
export async function completeSection(sectionId: string, sessionId: string) {
  const response = await fetch(`${API_URL}/assessment/section/${sectionId}/complete?session_id=${sessionId}`, {
    method: 'POST',
  });

  if (!response.ok) {
    throw new Error(`Failed to complete section: ${response.statusText}`);
  }

  return await response.json();
}

/**
 * Get assessment summary with all responses and progress
 * @param assessmentId Assessment ID
 * @returns Complete assessment summary
 */
export async function getAssessmentSummary(assessmentId: number) {
  const response = await fetch(`${API_URL}/assessment/${assessmentId}/summary`);

  if (!response.ok) {
    throw new Error(`Failed to get assessment summary: ${response.statusText}`);
  }

  return await response.json();
}

/**
 * Get list of all assessment domains/sections
 * @returns Domain list with metadata
 */
export async function getAssessmentDomains() {
  const response = await fetch(`${API_URL}/assessment/domains`);

  if (!response.ok) {
    throw new Error(`Failed to get assessment domains: ${response.statusText}`);
  }

  return await response.json();
}

/**
 * Auto-save assessment progress
 * @param sessionId Session ID
 * @param currentQuestion Current question ID
 * @param currentSection Current section ID
 * @param formData Additional form data to save
 * @returns Auto-save status
 */
export async function autoSaveAssessment(
  sessionId: string,
  currentQuestion?: string,
  currentSection?: string,
  formData?: any
) {
  const response = await fetch(`${API_URL}/assessment/session/${sessionId}/auto-save`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      current_question: currentQuestion,
      current_section: currentSection,
      state_data: formData,
    }),
  });

  if (!response.ok) {
    throw new Error(`Failed to auto-save assessment: ${response.statusText}`);
  }

  return await response.json();
}

/**
 * Calculate section score based on responses
 * @param sectionId Section ID
 * @param responses Section responses
 * @returns Section score and analysis
 */
export async function calculateSectionScore(sectionId: string, responses: Record<string, any>) {
  // This would integrate with the mathematical scoring system
  // For now, return a placeholder implementation
  const totalQuestions = Object.keys(responses).length;
  const completedQuestions = Object.values(responses).filter(r => r !== null && r !== undefined).length;
  const completionRate = totalQuestions > 0 ? (completedQuestions / totalQuestions) * 100 : 0;
  
  return {
    section_id: sectionId,
    completion_rate: completionRate,
    completed_questions: completedQuestions,
    total_questions: totalQuestions,
    score: completionRate, // Placeholder - would use actual scoring algorithm
    calculated_at: new Date().toISOString()
  };
}

/**
 * Get risk level based on score
 * @param score Numerical score (0-100)
 * @returns Risk level information
 */
export function getRiskLevel(score: number) {
  if (score >= 0 && score <= 40) {
    return { level: 'CRITICAL', label: 'Critical Risk', color: '#dc2626' };
  } else if (score >= 41 && score <= 60) {
    return { level: 'HIGH', label: 'High Risk', color: '#ea580c' };
  } else if (score >= 61 && score <= 80) {
    return { level: 'MEDIUM', label: 'Medium Risk', color: '#ca8a04' };
  } else {
    return { level: 'LOW', label: 'Low Risk', color: '#16a34a' };
  }
}

/**
 * Validate question response
 * @param question Question definition
 * @param response User response
 * @returns Validation result
 */
export function validateResponse(question: Question, response: any): { isValid: boolean; error?: string } {
  if (response === null || response === undefined || response === '') {
    return { isValid: false, error: 'Response is required' };
  }

  switch (question.type) {
    case 'boolean':
      if (typeof response !== 'boolean') {
        return { isValid: false, error: 'Response must be true or false' };
      }
      break;
    
    case 'select':
      if (!question.options?.includes(response)) {
        return { isValid: false, error: 'Response must be one of the provided options' };
      }
      break;
    
    case 'multiselect':
      if (!Array.isArray(response) || !response.every(r => question.options?.includes(r))) {
        return { isValid: false, error: 'Response must be an array of valid options' };
      }
      break;
    
    case 'scale':
      const num = Number(response);
      if (isNaN(num) || num < (question.min || 1) || num > (question.max || 5)) {
        return { isValid: false, error: `Response must be a number between ${question.min || 1} and ${question.max || 5}` };
      }
      break;
    
    case 'text':
      if (typeof response !== 'string' || response.trim().length === 0) {
        return { isValid: false, error: 'Response must be a non-empty text' };
      }
      break;
    
    default:
      return { isValid: false, error: 'Unknown question type' };
  }

  return { isValid: true };
}