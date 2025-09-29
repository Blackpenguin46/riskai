/**
 * Session Management API Client
 * Handles communication with the session management API endpoints
 */

// API base URL
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:9000';

/**
 * Create a new assessment session
 * @param assessmentId Assessment ID
 * @param userId Optional user ID
 * @returns Session ID and status
 */
export async function createSession(assessmentId: number, userId?: string) {
  const response = await fetch(`${API_URL}/assessment/session/create`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      assessment_id: assessmentId,
      user_id: userId,
    }),
  });

  if (!response.ok) {
    throw new Error(`Failed to create session: ${response.statusText}`);
  }

  return await response.json();
}

/**
 * Get session details
 * @param sessionId Session ID
 * @returns Session details
 */
export async function getSession(sessionId: string) {
  const response = await fetch(`${API_URL}/assessment/session/${sessionId}`);

  if (!response.ok) {
    throw new Error(`Failed to get session: ${response.statusText}`);
  }

  return await response.json();
}

/**
 * Update session details
 * @param sessionId Session ID
 * @param updateData Update data
 * @returns Update status
 */
export async function updateSession(sessionId: string, updateData: any) {
  const response = await fetch(`${API_URL}/assessment/session/${sessionId}/update`, {
    method: 'PUT',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify(updateData),
  });

  if (!response.ok) {
    throw new Error(`Failed to update session: ${response.statusText}`);
  }

  return await response.json();
}

/**
 * Save a question response
 * @param sessionId Session ID
 * @param questionId Question ID
 * @param sectionId Section ID
 * @param responseValue Response value
 * @param responseType Response type
 * @param timeSpentSeconds Time spent in seconds
 * @returns Save status
 */
export async function saveResponse(
  sessionId: string,
  questionId: string,
  sectionId: string,
  responseValue: any,
  responseType?: string,
  timeSpentSeconds?: number
) {
  const response = await fetch(`${API_URL}/assessment/session/${sessionId}/response`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      question_id: questionId,
      section_id: sectionId,
      response_value: responseValue,
      response_type: responseType,
      time_spent_seconds: timeSpentSeconds,
    }),
  });

  if (!response.ok) {
    throw new Error(`Failed to save response: ${response.statusText}`);
  }

  return await response.json();
}

/**
 * Mark a section as complete
 * @param sessionId Session ID
 * @param sectionId Section ID
 * @param totalQuestions Total number of questions
 * @returns Completion status
 */
export async function completeSection(sessionId: string, sectionId: string, totalQuestions: number) {
  const response = await fetch(`${API_URL}/assessment/session/${sessionId}/section/complete`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      section_id: sectionId,
      total_questions: totalQuestions,
    }),
  });

  if (!response.ok) {
    throw new Error(`Failed to complete section: ${response.statusText}`);
  }

  return await response.json();
}

/**
 * Get all sessions for a user
 * @param userId User ID
 * @returns User sessions
 */
export async function getUserSessions(userId: string) {
  const response = await fetch(`${API_URL}/assessment/sessions/user/${userId}`);

  if (!response.ok) {
    throw new Error(`Failed to get user sessions: ${response.statusText}`);
  }

  return await response.json();
}

/**
 * Get all incomplete sessions
 * @param userId Optional user ID
 * @returns Incomplete sessions
 */
export async function getIncompleteSessions(userId?: string) {
  const url = userId
    ? `${API_URL}/assessment/sessions/incomplete?user_id=${userId}`
    : `${API_URL}/assessment/sessions/incomplete`;

  const response = await fetch(url);

  if (!response.ok) {
    throw new Error(`Failed to get incomplete sessions: ${response.statusText}`);
  }

  return await response.json();
}

/**
 * Resume an existing session
 * @param sessionId Session ID
 * @returns Restored session state
 */
export async function resumeSession(sessionId: string) {
  const response = await fetch(`${API_URL}/assessment/session/${sessionId}/resume`, {
    method: 'POST',
  });

  if (!response.ok) {
    throw new Error(`Failed to resume session: ${response.statusText}`);
  }

  return await response.json();
}

/**
 * Get all sessions that can be resumed
 * @param userId Optional user ID
 * @returns Resumable sessions
 */
export async function getResumableSessions(userId?: string) {
  const url = userId
    ? `${API_URL}/assessment/sessions/resumable?user_id=${userId}`
    : `${API_URL}/assessment/sessions/resumable`;

  const response = await fetch(url);

  if (!response.ok) {
    throw new Error(`Failed to get resumable sessions: ${response.statusText}`);
  }

  return await response.json();
}

/**
 * Mark a session as complete
 * @param sessionId Session ID
 * @returns Completion status
 */
export async function completeSession(sessionId: string) {
  const response = await fetch(`${API_URL}/assessment/session/${sessionId}/complete`, {
    method: 'POST',
  });

  if (!response.ok) {
    throw new Error(`Failed to complete session: ${response.statusText}`);
  }

  return await response.json();
}

/**
 * Get overall progress for an assessment
 * @param sessionId Session ID
 * @returns Assessment progress
 */
export async function getAssessmentProgress(sessionId: string) {
  const response = await fetch(`${API_URL}/assessment/session/${sessionId}/progress`);

  if (!response.ok) {
    throw new Error(`Failed to get assessment progress: ${response.statusText}`);
  }

  return await response.json();
}

/**
 * Get progress for a specific section
 * @param sessionId Session ID
 * @param sectionId Section ID
 * @returns Section progress
 */
export async function getSectionProgress(sessionId: string, sectionId: string) {
  const response = await fetch(`${API_URL}/assessment/session/${sessionId}/section/${sectionId}/progress`);

  if (!response.ok) {
    throw new Error(`Failed to get section progress: ${response.statusText}`);
  }

  return await response.json();
}

/**
 * Get all responses for a section
 * @param sessionId Session ID
 * @param sectionId Section ID
 * @returns Section responses
 */
export async function getSectionResponses(sessionId: string, sectionId: string) {
  const response = await fetch(`${API_URL}/assessment/session/${sessionId}/section/${sectionId}/responses`);

  if (!response.ok) {
    throw new Error(`Failed to get section responses: ${response.statusText}`);
  }

  return await response.json();
}

/**
 * Get all responses for a session
 * @param sessionId Session ID
 * @returns All responses
 */
export async function getAllResponses(sessionId: string) {
  const response = await fetch(`${API_URL}/assessment/session/${sessionId}/responses`);

  if (!response.ok) {
    throw new Error(`Failed to get all responses: ${response.statusText}`);
  }

  return await response.json();
}

/**
 * Get list of completed section IDs
 * @param sessionId Session ID
 * @returns Completed section IDs
 */
export async function getCompletedSections(sessionId: string) {
  const response = await fetch(`${API_URL}/assessment/session/${sessionId}/completed-sections`);

  if (!response.ok) {
    throw new Error(`Failed to get completed sections: ${response.statusText}`);
  }

  return await response.json();
}

/**
 * Auto-save session state for recovery
 * @param sessionId Session ID
 * @param currentQuestion Current question ID
 * @param currentSection Current section ID
 * @param stateData Additional state data
 * @returns Auto-save status
 */
export async function autoSaveSession(
  sessionId: string,
  currentQuestion?: string,
  currentSection?: string,
  stateData?: any
) {
  const response = await fetch(`${API_URL}/assessment/session/${sessionId}/auto-save`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      current_question: currentQuestion,
      current_section: currentSection,
      state_data: stateData,
    }),
  });

  if (!response.ok) {
    throw new Error(`Failed to auto-save session: ${response.statusText}`);
  }

  return await response.json();
}

/**
 * Clean up expired sessions
 * @param hours Number of hours of inactivity before cleanup
 * @returns Cleanup status
 */
export async function cleanupExpiredSessions(hours: number = 24) {
  const response = await fetch(`${API_URL}/assessment/sessions/cleanup`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ hours }),
  });

  if (!response.ok) {
    throw new Error(`Failed to cleanup sessions: ${response.statusText}`);
  }

  return await response.json();
}