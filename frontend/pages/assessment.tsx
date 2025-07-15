import React, { useState, useEffect, useCallback } from 'react';
import type { NextPage } from 'next';
import { useRouter } from 'next/router';

// --- Type Definitions for Modern Assessment ---
interface AssessmentSection {
  id: string;
  name: string;
  description: string;
  estimated_time: string;
  question_count: number;
  weight: number;
  icon: string;
  order: number;
}

interface AssessmentQuestion {
  id: string;
  section_id: string;
  section_name: string;
  category: string;
  question_text: string;
  question_type: string;
  options: string[];
  required: boolean;
  weight: number;
  risk_impact: string;
  help_text?: string;
  maturity_indicators?: Record<string, string>;
}

interface AssessmentOverview {
  assessment_info: {
    title: string;
    description: string;
    total_sections: number;
    total_questions: number;
    estimated_time: string;
    frameworks_covered: string[];
  };
  sections: AssessmentSection[];
}

interface SectionResponse {
  section: AssessmentSection;
  questions: AssessmentQuestion[];
  progress_info: {
    current_section: number;
    total_sections: number;
    questions_in_section: number;
  };
}

interface SectionScore {
  section_id: string;
  section_name: string;
  score: number;
  completion_rate: number;
  maturity_level: string;
  maturity_description: string;
  questions_answered: number;
  total_questions: number;
  recommendations: string[];
}

const ModernAssessmentPage: NextPage = () => {
  const [currentView, setCurrentView] = useState<'overview' | 'section' | 'results'>('overview');
  const [assessmentOverview, setAssessmentOverview] = useState<AssessmentOverview | null>(null);
  const [currentSection, setCurrentSection] = useState<SectionResponse | null>(null);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [responses, setResponses] = useState<Record<string, Record<string, string | number>>>({});
  const [sectionScores, setSectionScores] = useState<Record<string, SectionScore>>({});
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [isSaving, setIsSaving] = useState(false);
  const [lastSaved, setLastSaved] = useState<Date | null>(null);
  const router = useRouter();

  const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

  const loadAssessmentOverview = useCallback(async () => {
    setIsLoading(true);
    try {
      const response = await fetch(`${apiUrl}/assessment/modern`);
      if (!response.ok) throw new Error('Failed to load assessment');
      const data = await response.json();
      setAssessmentOverview(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load assessment');
    }
    setIsLoading(false);
  }, [apiUrl]);

  // Load assessment overview and check for existing assessment on component mount
  useEffect(() => {
    loadAssessmentOverview();
    loadExistingAssessment();
  }, [loadAssessmentOverview]);

  const loadExistingAssessment = async () => {
    try {
      const response = await fetch(`${apiUrl}/assessment/latest`);
      if (response.ok) {
        const data = await response.json();
        if (data.status === 'in_progress') {
          // Load existing assessment data
          setResponses(data.responses || {});
          setSectionScores(data.section_scores || {});
          console.log('Loaded existing assessment progress:', data);
        }
      }
    } catch (err) {
      console.error('Failed to load existing assessment:', err);
    }
  };

  const loadSection = async (sectionId: string) => {
    setIsLoading(true);
    try {
      const response = await fetch(`${apiUrl}/assessment/modern/section/${sectionId}`);
      if (!response.ok) throw new Error('Failed to load section');
      const data = await response.json();
      setCurrentSection(data);
      setCurrentQuestionIndex(0);
      setCurrentView('section');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load section');
    }
    setIsLoading(false);
  };

  const handleQuestionResponse = (questionId: string, value: string | number) => {
    const sectionId = currentSection?.section.id;
    if (!sectionId) return;

    setResponses(prev => {
      const newResponses = {
        ...prev,
        [sectionId]: {
          ...prev[sectionId],
          [questionId]: value
        }
      };
      
      // Auto-save progress after each response
      saveQuestionProgress(newResponses);
      
      return newResponses;
    });
  };

  const saveQuestionProgress = async (currentResponses: Record<string, Record<string, string | number>>) => {
    try {
      setIsSaving(true);
      const totalQuestions = assessmentOverview?.assessment_info.total_questions || 127;
      const answeredQuestions = Object.values(currentResponses).reduce((total, sectionResponses) => 
        total + Object.keys(sectionResponses).length, 0
      );
      const completionPercentage = (answeredQuestions / totalQuestions) * 100;

      const assessmentData = {
        name: `Security Assessment ${new Date().toLocaleDateString()}`,
        description: "RiskAI Security Assessment - In Progress",
        status: "in_progress",
        completion_percentage: completionPercentage,
        sections_completed: Object.keys(sectionScores).length,
        questions_answered: answeredQuestions,
        total_questions: totalQuestions,
        responses: currentResponses,
        section_scores: sectionScores,
        completed: false
      };

      const response = await fetch(`${apiUrl}/assessment/save`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(assessmentData)
      });

      if (response.ok) {
        setLastSaved(new Date());
        console.log('Assessment progress saved successfully');
      }
    } catch (err) {
      console.error('Failed to save question progress:', err);
    } finally {
      setIsSaving(false);
    }
  };

  const saveAssessmentProgress = async (sectionScores: Record<string, SectionScore>) => {
    try {
      const assessmentData = {
        name: `Security Assessment ${new Date().toLocaleDateString()}`,
        description: "RiskAI Security Assessment - In Progress",
        status: "in_progress",
        completion_percentage: calculateCompletionPercentage(sectionScores),
        sections_completed: Object.keys(sectionScores).length,
        responses: responses,
        section_scores: sectionScores,
        completed: false
      };

      await fetch(`${apiUrl}/assessment/save`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(assessmentData)
      });
    } catch (err) {
      console.error('Failed to save assessment progress:', err);
    }
  };

  const saveAssessmentFinal = async () => {
    try {
      const overallScore = calculateOverallScore();
      const maturityLevel = determineMaturityLevel(overallScore);
      
      const assessmentData = {
        name: `Security Assessment ${new Date().toLocaleDateString()}`,
        description: "RiskAI Security Assessment - Completed",
        status: "completed",
        completion_percentage: 100,
        sections_completed: Object.keys(sectionScores).length,
        overall_score: overallScore,
        maturity_level: maturityLevel,
        risk_level: determineRiskLevel(overallScore),
        responses: responses,
        section_scores: sectionScores,
        completed: true
      };

      const response = await fetch(`${apiUrl}/assessment/save`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(assessmentData)
      });

      if (response.ok) {
        const result = await response.json();
        console.log('Assessment saved successfully:', result);
      }
    } catch (err) {
      console.error('Failed to save final assessment:', err);
    }
  };

  const calculateCompletionPercentage = (sectionScores: Record<string, SectionScore>) => {
    const totalSections = assessmentOverview?.sections.length || 10;
    return (Object.keys(sectionScores).length / totalSections) * 100;
  };

  const calculateOverallScore = () => {
    const completedSections = Object.values(sectionScores);
    if (completedSections.length === 0) return 0;
    return completedSections.reduce((sum, section) => sum + section.score, 0) / completedSections.length;
  };

  const determineMaturityLevel = (score: number) => {
    if (score >= 85) return "Adaptive";
    if (score >= 70) return "Repeatable";
    if (score >= 50) return "Risk-Informed";
    return "Partial";
  };

  const determineRiskLevel = (score: number) => {
    if (score >= 80) return "Low";
    if (score >= 60) return "Medium";
    if (score >= 40) return "High";
    return "Critical";
  };

  const createNewAssessment = async () => {
    try {
      // First, save the current assessment as completed if it has any progress
      if (Object.keys(responses).length > 0 || Object.keys(sectionScores).length > 0) {
        await saveAssessmentFinal();
      }
      
      // Clear current assessment state
      setCurrentView('overview');
      setResponses({});
      setSectionScores({});
      setCurrentSection(null);
      setCurrentQuestionIndex(0);
      
      console.log('New assessment created, previous assessment saved to history');
    } catch (err) {
      console.error('Failed to create new assessment:', err);
    }
  };

  const submitSection = async () => {
    if (!currentSection) return;
    
    const sectionId = currentSection.section.id;
    const sectionResponses = responses[sectionId] || {};
    
    setIsLoading(true);
    try {
      const response = await fetch(`${apiUrl}/assessment/modern/section/${sectionId}/score`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(sectionResponses)
      });
      
      if (!response.ok) throw new Error('Failed to score section');
      const scoreData = await response.json();
      
      setSectionScores(prev => {
        const newSectionScores = {
          ...prev,
          [sectionId]: scoreData
        };
        
        // Save assessment progress after updating section scores
        saveAssessmentProgress(newSectionScores);
        
        return newSectionScores;
      });
      
      // Move to next section or results
      const nextSectionIndex = currentSection.section.order;
      const nextSection = assessmentOverview?.sections.find(s => s.order === nextSectionIndex + 1);
      
      if (nextSection) {
        loadSection(nextSection.id);
      } else {
        // Assessment completed - save final results
        setCurrentView('results');
        saveAssessmentFinal();
      }
      
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to submit section');
    }
    setIsLoading(false);
  };

  const renderOverview = () => {
    if (!assessmentOverview) return null;

    return (
      <div className="max-w-4xl mx-auto p-6">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-indigo-400 mb-4">
            {assessmentOverview.assessment_info.title}
          </h1>
          <p className="text-gray-300 text-lg mb-6">
            {assessmentOverview.assessment_info.description}
          </p>
          
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4 mb-8">
            <div className="bg-gray-800 rounded-lg p-4">
              <div className="text-2xl font-bold text-indigo-400">
                {assessmentOverview.assessment_info.total_sections}
              </div>
              <div className="text-sm text-gray-400">Sections</div>
            </div>
            <div className="bg-gray-800 rounded-lg p-4">
              <div className="text-2xl font-bold text-indigo-400">
                {assessmentOverview.assessment_info.total_questions}
              </div>
              <div className="text-sm text-gray-400">Questions</div>
            </div>
            <div className="bg-gray-800 rounded-lg p-4">
              <div className="text-2xl font-bold text-indigo-400">
                {assessmentOverview.assessment_info.estimated_time}
              </div>
              <div className="text-sm text-gray-400">Est. Time</div>
            </div>
            <div className="bg-gray-800 rounded-lg p-4">
              <div className="text-2xl font-bold text-indigo-400">
                {assessmentOverview.assessment_info.frameworks_covered.length}
              </div>
              <div className="text-sm text-gray-400">Frameworks</div>
            </div>
          </div>
        </div>

        <div className="grid gap-4 mb-8">
          {assessmentOverview.sections.map((section) => (
            <div
              key={section.id}
              className="bg-gray-800 rounded-lg p-6 hover:bg-gray-750 transition-colors cursor-pointer"
              onClick={() => loadSection(section.id)}
            >
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-4">
                  <div className="text-2xl">{section.icon}</div>
                  <div>
                    <h3 className="text-lg font-semibold text-white">
                      {section.name}
                    </h3>
                    <p className="text-gray-400 text-sm">{section.description}</p>
                    <div className="flex gap-4 mt-2 text-xs text-gray-500">
                      <span>{section.question_count} questions</span>
                      <span>{section.estimated_time}</span>
                      <span>Weight: {(section.weight * 100).toFixed(0)}%</span>
                    </div>
                  </div>
                </div>
                <div className="flex items-center gap-2">
                  {sectionScores[section.id] && (
                    <div className="bg-green-600 text-white px-3 py-1 rounded text-sm">
                      ✓ Complete
                    </div>
                  )}
                  <div className="text-indigo-400">→</div>
                </div>
              </div>
            </div>
          ))}
        </div>

        {Object.keys(sectionScores).length > 0 && (
          <div className="text-center">
            <button
              onClick={() => setCurrentView('results')}
              className="bg-gradient-to-r from-indigo-500 to-purple-600 text-white px-8 py-3 rounded-lg font-semibold hover:from-indigo-600 hover:to-purple-700 transition"
            >
              View Results
            </button>
          </div>
        )}
      </div>
    );
  };

  const renderSection = () => {
    if (!currentSection) return null;

    const currentQuestion = currentSection.questions[currentQuestionIndex];
    if (!currentQuestion) return null;

    const sectionResponses = responses[currentSection.section.id] || {};
    const currentResponse = sectionResponses[currentQuestion.id];

    return (
      <div className="max-w-3xl mx-auto p-6">
        {/* Progress bar */}
        <div className="mb-8">
          <div className="flex justify-between text-sm text-gray-400 mb-2">
            <span>{currentSection.section.name}</span>
            <span>
              {currentQuestionIndex + 1} of {currentSection.questions.length}
            </span>
          </div>
          <div className="w-full bg-gray-700 rounded-full h-2 mb-3">
            <div
              className="bg-gradient-to-r from-indigo-500 to-purple-600 h-2 rounded-full transition-all"
              style={{
                width: `${((currentQuestionIndex + 1) / currentSection.questions.length) * 100}%`
              }}
            />
          </div>
          
          {/* Saving indicator */}
          <div className="flex items-center justify-center">
            {isSaving ? (
              <div className="flex items-center text-yellow-400 text-sm">
                <svg className="animate-spin h-4 w-4 mr-2" viewBox="0 0 24 24">
                  <circle cx="12" cy="12" r="10" stroke="currentColor" strokeWidth="4" fill="none" strokeOpacity="0.3"/>
                  <path fill="currentColor" d="M4 12a8 8 0 018-8V0C5.373 0 0 5.373 0 12h4zm2 5.291A7.962 7.962 0 014 12H0c0 3.042 1.135 5.824 3 7.938l3-2.647z"/>
                </svg>
                Saving your answer...
              </div>
            ) : lastSaved && (
              <div className="flex items-center text-green-400 text-sm">
                <svg className="h-4 w-4 mr-2" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                  <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                </svg>
                Saved {lastSaved.toLocaleTimeString()}
              </div>
            )}
          </div>
        </div>

        {/* Question */}
        <div className="bg-gray-800 rounded-lg p-8 mb-6">
          <h2 className="text-xl font-semibold text-white mb-4">
            {currentQuestion.question_text}
          </h2>
          
          {currentQuestion.help_text && (
            <p className="text-gray-400 text-sm mb-6">
              💡 {currentQuestion.help_text}
            </p>
          )}

          {/* Response options based on question type */}
          {currentQuestion.question_type === 'likert_scale' && (
            <div className="space-y-3">
              {currentQuestion.options.map((option, index) => (
                <label
                  key={index}
                  className="flex items-center gap-3 p-4 bg-gray-700 rounded-lg hover:bg-gray-600 cursor-pointer transition"
                >
                  <input
                    type="radio"
                    name={currentQuestion.id}
                    value={index + 1}
                    checked={currentResponse === (index + 1)}
                    onChange={(e) => handleQuestionResponse(currentQuestion.id, parseInt(e.target.value))}
                    className="text-indigo-500"
                  />
                  <span className="text-white">{option}</span>
                </label>
              ))}
            </div>
          )}

          {currentQuestion.question_type === 'dropdown' && (
            <select
              value={currentResponse || ''}
              onChange={(e) => handleQuestionResponse(currentQuestion.id, e.target.value)}
              className="w-full p-4 bg-gray-700 border border-gray-600 rounded-lg text-white focus:ring-2 focus:ring-indigo-500"
            >
              <option value="">Select an option...</option>
              {currentQuestion.options.map((option, index) => (
                <option key={index} value={option}>
                  {option}
                </option>
              ))}
            </select>
          )}

          {currentQuestion.question_type === 'multiple_choice' && (
            <div className="space-y-3">
              {currentQuestion.options.map((option, index) => (
                <label
                  key={index}
                  className="flex items-center gap-3 p-4 bg-gray-700 rounded-lg hover:bg-gray-600 cursor-pointer transition"
                >
                  <input
                    type="radio"
                    name={currentQuestion.id}
                    value={option}
                    checked={currentResponse === option}
                    onChange={(e) => handleQuestionResponse(currentQuestion.id, e.target.value)}
                    className="text-indigo-500"
                  />
                  <span className="text-white">{option}</span>
                </label>
              ))}
            </div>
          )}

          {currentQuestion.question_type === 'short_text' && (
            <textarea
              value={currentResponse || ''}
              onChange={(e) => handleQuestionResponse(currentQuestion.id, e.target.value)}
              placeholder="Enter your response..."
              className="w-full p-4 bg-gray-700 border border-gray-600 rounded-lg text-white focus:ring-2 focus:ring-indigo-500"
              rows={4}
            />
          )}
        </div>

        {/* Navigation */}
        <div className="flex justify-between">
          <button
            onClick={() => {
              if (currentQuestionIndex > 0) {
                setCurrentQuestionIndex(currentQuestionIndex - 1);
              } else {
                setCurrentView('overview');
              }
            }}
            className="px-6 py-3 rounded-lg bg-gray-700 text-white hover:bg-gray-600 transition"
          >
            {currentQuestionIndex === 0 ? 'Back to Overview' : 'Previous'}
          </button>

          <button
            onClick={() => {
              if (currentQuestionIndex < currentSection.questions.length - 1) {
                setCurrentQuestionIndex(currentQuestionIndex + 1);
              } else {
                submitSection();
              }
            }}
            disabled={!currentResponse && currentQuestion.required}
            className="px-6 py-3 rounded-lg bg-gradient-to-r from-indigo-500 to-purple-600 text-white font-semibold hover:from-indigo-600 hover:to-purple-700 transition disabled:opacity-50"
          >
            {currentQuestionIndex < currentSection.questions.length - 1 ? 'Next' : 'Complete Section'}
          </button>
        </div>
      </div>
    );
  };

  const renderResults = () => {
    const completedSections = Object.values(sectionScores);
    if (completedSections.length === 0) return null;

    const overallScore = completedSections.reduce((sum, section) => sum + section.score, 0) / completedSections.length;

    return (
      <div className="max-w-4xl mx-auto p-6">
        <div className="text-center mb-8">
          <h1 className="text-3xl font-bold text-indigo-400 mb-4">
            Assessment Results
          </h1>
          <div className="bg-gray-800 rounded-lg p-8 mb-8">
            <div className="text-4xl font-bold text-white mb-2">
              {overallScore.toFixed(1)}%
            </div>
            <div className="text-gray-400">Overall Security Maturity Score</div>
          </div>
        </div>

        <div className="grid gap-6 mb-8">
          {completedSections.map((section) => (
            <div key={section.section_id} className="bg-gray-800 rounded-lg p-6">
              <div className="flex justify-between items-start mb-4">
                <h3 className="text-lg font-semibold text-white">
                  {section.section_name}
                </h3>
                <div className="text-right">
                  <div className="text-xl font-bold text-indigo-400">
                    {section.score.toFixed(1)}%
                  </div>
                  <div className="text-sm text-gray-400">
                    {section.maturity_level}
                  </div>
                </div>
              </div>
              
              <p className="text-gray-300 text-sm mb-4">
                {section.maturity_description}
              </p>

              {section.recommendations.length > 0 && (
                <div>
                  <h4 className="text-sm font-semibold text-indigo-400 mb-2">
                    Recommendations:
                  </h4>
                  <ul className="text-sm text-gray-300 space-y-1">
                    {section.recommendations.map((rec, index) => (
                      <li key={index} className="flex items-start gap-2">
                        <span className="text-indigo-400">•</span>
                        {rec}
                      </li>
                    ))}
                  </ul>
                </div>
              )}
            </div>
          ))}
        </div>

        <div className="text-center space-y-4">
          <button
            onClick={createNewAssessment}
            className="bg-gradient-to-r from-indigo-500 to-purple-600 text-white px-8 py-3 rounded-lg font-semibold hover:from-indigo-600 hover:to-purple-700 transition"
          >
            Start New Assessment
          </button>
          <div>
            <button
              onClick={() => router.push('/')}
              className="text-indigo-400 hover:text-indigo-300 transition"
            >
              Back to Dashboard
            </button>
          </div>
        </div>
      </div>
    );
  };

  if (isLoading) {
    return (
      <div className="min-h-screen flex items-center justify-center bg-gradient-to-br from-gray-950 to-gray-900">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-indigo-400 mx-auto mb-4"></div>
          <div className="text-white">Loading assessment...</div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-950 to-gray-900 text-white">
      <header className="p-4 bg-gray-900/80 backdrop-blur-md shadow-lg sticky top-0 z-10">
        <div className="flex items-center justify-between max-w-6xl mx-auto">
          <button
            onClick={() => router.push('/')}
            className="text-indigo-400 hover:text-indigo-300 transition flex items-center gap-2"
          >
            ← Back to Dashboard
          </button>
          <h1 className="text-2xl font-bold bg-gradient-to-r from-indigo-400 to-purple-500 bg-clip-text text-transparent">
            Security Assessment
          </h1>
          <div className="w-32"></div>
        </div>
      </header>

      {error && (
        <div className="bg-red-900/50 border border-red-600 text-red-200 p-4 m-4 rounded-lg">
          <div className="flex justify-between items-center">
            <span>Error: {error}</span>
            <button
              onClick={() => setError(null)}
              className="text-red-400 hover:text-red-300"
            >
              ✕
            </button>
          </div>
        </div>
      )}

      <main className="py-8">
        {currentView === 'overview' && renderOverview()}
        {currentView === 'section' && renderSection()}
        {currentView === 'results' && renderResults()}
      </main>
    </div>
  );
};

export default ModernAssessmentPage;