import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import SessionManager from '../components/SessionManager';
import AssessmentProgress from '../components/AssessmentProgress';
import QuestionNavigation from '../components/QuestionNavigation';
import { 
  startAssessment, 
  getAllQuestions, 
  submitResponse, 
  getProgress, 
  completeSection as completeAssessmentSection,
  getSectionQuestions,
  autoSaveAssessment,
  getRiskLevel
} from '../lib/assessment-api';
import { createSession, completeSession } from '../lib/session-api';
import { calculateOverallScore, generateStrategicRecommendations, generateSectionRecommendations } from '../lib/assessment-scoring';

// Mock user ID for demo purposes
const MOCK_USER_ID = 'user-123';

const AssessmentPage: React.FC = () => {
  const router = useRouter();
  const [loading, setLoading] = useState<boolean>(false);
  const [error, setError] = useState<string | null>(null);
  const [currentSession, setCurrentSession] = useState<any>(null);
  const [currentSection, setCurrentSection] = useState<string | null>(null);
  const [currentQuestion, setCurrentQuestion] = useState<string | null>(null);
  const [responses, setResponses] = useState<Record<string, Record<string, any>>>({});
  const [progress, setProgress] = useState<any>(null);
  const [showSessionManager, setShowSessionManager] = useState<boolean>(true);
  const [submittingAssessment, setSubmittingAssessment] = useState<boolean>(false);
  const [sections, setSections] = useState<any[]>([]);
  const [questionsLoaded, setQuestionsLoaded] = useState<boolean>(false);

  // Load questions on component mount
  useEffect(() => {
    loadAssessmentQuestions();
  }, []);

  const loadAssessmentQuestions = async () => {
    try {
      const questionsData = await getAllQuestions();
      setSections(questionsData.sections);
      setQuestionsLoaded(true);
    } catch (err) {
      console.error('Error loading questions:', err);
      setError('Failed to load assessment questions. Please refresh the page.');
    }
  };

  const handleSessionSelected = (sessionData: any) => {
    setCurrentSession(sessionData);
    setShowSessionManager(false);
    
    // Set current section and question from the restored session
    if (sessionData.current_section) {
      setCurrentSection(sessionData.current_section);
    } else {
      setCurrentSection(sections[0].id);
    }
    
    if (sessionData.current_question) {
      setCurrentQuestion(sessionData.current_question);
    } else {
      setCurrentQuestion(sections[0].questions[0].id);
    }
    
    // Set responses from the restored session
    if (sessionData.responses) {
      setResponses(sessionData.responses);
    }
    
    // Set progress from the restored session
    if (sessionData.progress) {
      setProgress(sessionData.progress);
    }
  };

  const handleStartNewSession = async () => {
    try {
      setLoading(true);
      setError(null);
      
      if (!questionsLoaded || sections.length === 0) {
        setError('Assessment questions not loaded. Please refresh the page.');
        return;
      }
      
      // Start a new assessment using the new API
      const result = await startAssessment({
        assessment_name: 'Cybersecurity Risk Assessment',
        user_id: MOCK_USER_ID
      });
      
      // Set the current session
      setCurrentSession({
        session_id: result.session_id,
        assessment_id: result.assessment_id,
        created_at: result.created_at
      });
      
      // Start with the first section and question
      setCurrentSection(sections[0].id);
      setCurrentQuestion(sections[0].questions[0].id);
      
      // Hide the session manager
      setShowSessionManager(false);
    } catch (err) {
      setError('Failed to create a new session');
      console.error('Error creating session:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleSaveResponse = async (questionId: string, sectionId: string, value: any, type: string = 'text') => {
    if (!currentSession) return;
    
    try {
      // Save response locally
      setResponses(prev => ({
        ...prev,
        [sectionId]: {
          ...(prev[sectionId] || {}),
          [questionId]: value
        }
      }));
      
      // Save response to server using the new assessment API
      await submitResponse(currentSession.session_id, {
        question_id: questionId,
        section_id: sectionId,
        response_value: value,
        response_type: type
      });
      
      // Auto-save session state
      await autoSaveAssessment(
        currentSession.session_id,
        questionId,
        sectionId,
        { [questionId]: value }
      );
      
    } catch (err) {
      console.error('Error saving response:', err);
      // Continue anyway - the response is saved locally
    }
  };
  
  const handleNavigateToQuestion = (sectionId: string, questionId: string) => {
    setCurrentSection(sectionId);
    setCurrentQuestion(questionId);
  };

  const handleNavigate = async (direction: 'prev' | 'next') => {
    if (!currentSession || !currentSection || !currentQuestion) return;
    
    const currentSectionIndex = sections.findIndex(s => s.id === currentSection);
    const currentSectionObj = sections[currentSectionIndex];
    const currentQuestionIndex = currentSectionObj.questions.findIndex(q => q.id === currentQuestion);
    
    if (direction === 'next') {
      if (currentQuestionIndex < currentSectionObj.questions.length - 1) {
        // Move to next question in current section
        setCurrentQuestion(currentSectionObj.questions[currentQuestionIndex + 1].id);
      } else if (currentSectionIndex < sections.length - 1) {
        // Move to first question of next section
        const nextSection = sections[currentSectionIndex + 1];
        setCurrentSection(nextSection.id);
        setCurrentQuestion(nextSection.questions[0].id);
        
        // Mark current section as complete
        try {
          await completeAssessmentSection(
            currentSection,
            currentSession.session_id
          );
        } catch (err) {
          console.error('Error completing section:', err);
        }
      } else {
        // Assessment complete - calculate scores and generate recommendations
        try {
          setSubmittingAssessment(true);
          
          await completeAssessmentSection(
            currentSection,
            currentSession.session_id
          );
          
          await completeSession(currentSession.session_id);
          
          // Calculate scores using the new mathematical scoring system
          const overallScore = calculateOverallScore(sections, responses);
          
          // Calculate section scores
          const sectionScores: Record<string, any> = {};
          sections.forEach(section => {
            const sectionId = section.id;
            const sectionResponses = responses[sectionId] || {};
            sectionScores[sectionId] = overallScore.sectionBreakdown.find(s => s.sectionId === sectionId);
          });
          
          // Generate AI-powered feedback using RAG pipeline and local LLM
          let aiFeedback = null;
          try {
            const feedbackResponse = await fetch('/api/assessment/feedback/generate', {
              method: 'POST',
              headers: {
                'Content-Type': 'application/json',
              },
              body: JSON.stringify({
                overall_score: overallScore.percentage,
                risk_level: overallScore.riskLevel,
                section_scores: sectionScores,
                responses: responses,
                completion_rate: overallProgress.answered / overallProgress.total
              })
            });
            
            if (feedbackResponse.ok) {
              aiFeedback = await feedbackResponse.json();
              console.log('AI feedback generated successfully');
            } else {
              console.warn('AI feedback generation failed, using fallback');
            }
          } catch (error) {
            console.warn('Error generating AI feedback:', error);
          }
          
          // Fallback to local recommendations if AI feedback fails
          const sectionRecommendations: Record<string, string[]> = {};
          overallScore.sectionBreakdown.forEach(sectionScore => {
            sectionRecommendations[sectionScore.sectionId] = generateSectionRecommendations(
              sectionScore.sectionId, 
              sectionScore, 
              responses[sectionScore.sectionId] || {}
            );
          });
          
          const strategicRecommendations = generateStrategicRecommendations(responses, overallScore);
          
          // Save results to session storage for the results page
          sessionStorage.setItem('assessmentResults', JSON.stringify({
            overallScore,
            sectionScores,
            sectionRecommendations,
            strategicRecommendations,
            aiFeedback, // Include AI-powered feedback
            responses,
            completedAt: new Date().toISOString()
          }));
          
          // Navigate to results page
          router.push('/reports');
        } catch (err) {
          console.error('Error completing assessment:', err);
          setError('Failed to calculate assessment results. Please try again.');
          setSubmittingAssessment(false);
        }
      }
    } else if (direction === 'prev') {
      if (currentQuestionIndex > 0) {
        // Move to previous question in current section
        setCurrentQuestion(currentSectionObj.questions[currentQuestionIndex - 1].id);
      } else if (currentSectionIndex > 0) {
        // Move to last question of previous section
        const prevSection = sections[currentSectionIndex - 1];
        setCurrentSection(prevSection.id);
        setCurrentQuestion(prevSection.questions[prevSection.questions.length - 1].id);
      }
    }
  };

  const getCurrentQuestion = () => {
    if (!currentSection || !currentQuestion) return null;
    
    const section = sections.find(s => s.id === currentSection);
    if (!section) return null;
    
    return section.questions.find(q => q.id === currentQuestion);
  };

  const getCurrentSectionProgress = () => {
    if (!currentSection) return { completed: 0, total: 0, percentage: 0 };
    
    const section = sections.find(s => s.id === currentSection);
    if (!section) return { completed: 0, total: 0, percentage: 0 };
    
    const sectionResponses = responses[currentSection] || {};
    const completed = Object.keys(sectionResponses).length;
    const total = section.questions.length;
    const percentage = total > 0 ? Math.round((completed / total) * 100) : 0;
    
    return { completed, total, percentage };
  };

  const getOverallProgress = () => {
    const totalQuestions = sections.reduce((sum, section) => sum + section.questions.length, 0);
    const answeredQuestions = Object.values(responses).reduce(
      (sum, sectionResponses) => sum + Object.keys(sectionResponses || {}).length, 
      0
    );
    
    const percentage = totalQuestions > 0 ? Math.round((answeredQuestions / totalQuestions) * 100) : 0;
    
    return { 
      answered: answeredQuestions,
      total: totalQuestions,
      percentage
    };
  };

  const renderQuestionInput = (question: any) => {
    const currentValue = responses[currentSection!]?.[question.id];
    
    switch (question.type) {
      case 'boolean':
        return (
          <div className="space-y-3">
            <div className="flex space-x-4">
              <label className="flex items-center">
                <input
                  type="radio"
                  name={question.id}
                  value="true"
                  checked={currentValue === true}
                  onChange={() => handleSaveResponse(question.id, currentSection!, true, 'boolean')}
                  className="mr-2"
                />
                Yes
              </label>
              <label className="flex items-center">
                <input
                  type="radio"
                  name={question.id}
                  value="false"
                  checked={currentValue === false}
                  onChange={() => handleSaveResponse(question.id, currentSection!, false, 'boolean')}
                  className="mr-2"
                />
                No
              </label>
            </div>
          </div>
        );

      case 'scale':
        return (
          <div className="space-y-3">
            <input
              type="range"
              min={question.min || 1}
              max={question.max || 5}
              value={currentValue || question.min || 1}
              onChange={(e) => handleSaveResponse(question.id, currentSection!, parseInt(e.target.value), 'scale')}
              className="w-full"
            />
            <div className="flex justify-between text-sm text-gray-600">
              <span>{question.min || 1}</span>
              <span className="font-medium">Current: {currentValue || question.min || 1}</span>
              <span>{question.max || 5}</span>
            </div>
          </div>
        );

      case 'select':
        return (
          <select
            value={currentValue || ''}
            onChange={(e) => handleSaveResponse(question.id, currentSection!, e.target.value, 'select')}
            className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="">Select an option...</option>
            {question.options?.map((option: string) => (
              <option key={option} value={option}>
                {option}
              </option>
            ))}
          </select>
        );

      case 'multiselect':
        return (
          <div className="space-y-2">
            {question.options?.map((option: string) => (
              <label key={option} className="flex items-center">
                <input
                  type="checkbox"
                  checked={Array.isArray(currentValue) && currentValue.includes(option)}
                  onChange={(e) => {
                    const currentArray = Array.isArray(currentValue) ? currentValue : [];
                    const newValue = e.target.checked
                      ? [...currentArray, option]
                      : currentArray.filter(item => item !== option);
                    handleSaveResponse(question.id, currentSection!, newValue, 'multiselect');
                  }}
                  className="mr-2"
                />
                {option}
              </label>
            ))}
          </div>
        );

      case 'text':
        return (
          <textarea
            value={currentValue || ''}
            onChange={(e) => handleSaveResponse(question.id, currentSection!, e.target.value, 'text')}
            placeholder="Enter your response..."
            className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            rows={3}
          />
        );

      default:
        return <div>Unsupported question type</div>;
    }
  };

  if (showSessionManager) {
    return (
      <div className="min-h-screen bg-gray-50 py-8">
        <div className="max-w-4xl mx-auto px-4">
          <div className="bg-white rounded-lg shadow-lg p-8">
            <h1 className="text-3xl font-bold text-gray-900 mb-6">
              Cybersecurity Risk Assessment
            </h1>
            <p className="text-lg text-gray-600 mb-8">
              Complete our comprehensive 120-question assessment to evaluate your organization's cybersecurity posture across 12 critical security domains.
            </p>
            
            <SessionManager
              userId={MOCK_USER_ID}
              onSessionSelected={handleSessionSelected}
              onNewSession={handleStartNewSession}
            />
          </div>
        </div>
      </div>
    );
  }

  const currentQuestionObj = getCurrentQuestion();
  const sectionProgress = getCurrentSectionProgress();
  const overallProgress = getOverallProgress();
  const currentSectionObj = sections.find(s => s.id === currentSection);

  if (!currentQuestionObj || !currentSectionObj) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="text-xl text-gray-600">Loading assessment...</div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-4xl mx-auto px-4">
        {/* Enhanced Progress Header */}
        <AssessmentProgress
          currentSection={currentSection}
          currentQuestion={currentQuestion}
          sections={sections}
          responses={responses}
        />

        {/* Question Navigation */}
        <QuestionNavigation
          sections={sections}
          currentSection={currentSection}
          currentQuestion={currentQuestion}
          responses={responses}
          onNavigateToQuestion={handleNavigateToQuestion}
          disabled={submittingAssessment}
        />

        {/* Question Card */}
        <div className="bg-white rounded-lg shadow-lg p-8">
          <div className="mb-6">
            <h2 className="text-xl font-semibold text-gray-900 mb-4">
              {currentQuestionObj.text}
            </h2>
            {currentQuestionObj.category && (
              <div className="text-sm text-gray-500 mb-4">
                Category: {currentQuestionObj.category.replace('_', ' ')}
              </div>
            )}
          </div>

          <div className="mb-8">
            {renderQuestionInput(currentQuestionObj)}
          </div>

          {/* Navigation */}
          <div className="flex justify-between">
            <button
              onClick={() => handleNavigate('prev')}
              disabled={sections.findIndex(s => s.id === currentSection) === 0 && 
                       currentSectionObj.questions.findIndex(q => q.id === currentQuestion) === 0}
              className="px-6 py-2 bg-gray-300 text-gray-700 rounded-lg hover:bg-gray-400 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Previous
            </button>

            <button
              onClick={() => handleNavigate('next')}
              disabled={submittingAssessment}
              className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {submittingAssessment ? 'Submitting...' : 
               (sections.findIndex(s => s.id === currentSection) === sections.length - 1 && 
                currentSectionObj.questions.findIndex(q => q.id === currentQuestion) === currentSectionObj.questions.length - 1) 
                ? 'Complete Assessment' : 'Next'}
            </button>
          </div>
        </div>

        {error && (
          <div className="mt-6 bg-red-50 border border-red-200 rounded-lg p-4">
            <div className="text-red-800">{error}</div>
          </div>
        )}
      </div>
    </div>
  );
};

export default AssessmentPage;