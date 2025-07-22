import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import IndustryProfileSetup from '../components/IndustryProfileSetup';
import AssessmentProgress from '../components/AssessmentProgress';
import { 
  getTailoredQuestions, 
  scoreQuestion, 
  calculateAssessmentScore,
  IndustryProfile,
  Question,
  AssessmentQuestions 
} from '../lib/enhanced-assessment-api';

const EnhancedAssessmentPage: React.FC = () => {
  const router = useRouter();
  
  // Setup phase state
  const [showProfileSetup, setShowProfileSetup] = useState(true);
  const [industryProfile, setIndustryProfile] = useState<IndustryProfile>({});
  
  // Assessment state
  const [questions, setQuestions] = useState<AssessmentQuestions | null>(null);
  const [currentDomainIndex, setCurrentDomainIndex] = useState(0);
  const [currentQuestionIndex, setCurrentQuestionIndex] = useState(0);
  const [responses, setResponses] = useState<Record<string, any>>({});
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [submittingAssessment, setSubmittingAssessment] = useState(false);

  // Get current question and domain info
  const domains = questions ? Object.keys(questions.domains) : [];
  const currentDomain = domains[currentDomainIndex];
  const currentDomainQuestions = questions?.domains[currentDomain] || [];
  const currentQuestion = currentDomainQuestions[currentQuestionIndex];
  const totalQuestions = questions?.total_questions || 0;
  const answeredQuestions = Object.keys(responses).length;

  const handleProfileComplete = async (profile: IndustryProfile) => {
    try {
      setLoading(true);
      setError(null);
      setIndustryProfile(profile);
      
      console.log('Getting tailored questions for profile:', profile);
      const questionsData = await getTailoredQuestions(profile);
      console.log('Received questions:', questionsData);
      
      setQuestions(questionsData);
      setShowProfileSetup(false);
    } catch (err) {
      console.error('Error getting tailored questions:', err);
      setError('Failed to load tailored questions. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleSkipProfile = async () => {
    try {
      setLoading(true);
      setError(null);
      
      // Get standard questions without industry customization
      const questionsData = await getTailoredQuestions({});
      setQuestions(questionsData);
      setShowProfileSetup(false);
    } catch (err) {
      console.error('Error getting standard questions:', err);
      setError('Failed to load assessment questions. Please try again.');
    } finally {
      setLoading(false);
    }
  };

  const handleSaveResponse = async (questionId: string, value: any) => {
    // Save response locally
    setResponses(prev => ({
      ...prev,
      [questionId]: value
    }));

    // Score the question in real-time (optional)
    try {
      if (currentQuestion) {
        const scoringData = {
          question_id: questionId,
          question_type: currentQuestion.question_type,
          answer: value,
          weight: currentQuestion.weight,
          question_options: currentQuestion.options,
          min_value: currentQuestion.min_value,
          max_value: currentQuestion.max_value,
        };
        
        const score = await scoreQuestion(scoringData);
        console.log(`Question ${questionId} scored: ${score.percentage}%`);
      }
    } catch (err) {
      console.warn('Error scoring question in real-time:', err);
      // Continue anyway - scoring will happen at the end
    }
  };

  const handleNavigate = (direction: 'prev' | 'next') => {
    if (direction === 'next') {
      if (currentQuestionIndex < currentDomainQuestions.length - 1) {
        // Next question in current domain
        setCurrentQuestionIndex(prev => prev + 1);
      } else if (currentDomainIndex < domains.length - 1) {
        // Next domain
        setCurrentDomainIndex(prev => prev + 1);
        setCurrentQuestionIndex(0);
      } else {
        // Assessment complete
        handleCompleteAssessment();
      }
    } else if (direction === 'prev') {
      if (currentQuestionIndex > 0) {
        // Previous question in current domain
        setCurrentQuestionIndex(prev => prev - 1);
      } else if (currentDomainIndex > 0) {
        // Previous domain
        setCurrentDomainIndex(prev => prev - 1);
        const prevDomainQuestions = questions?.domains[domains[currentDomainIndex - 1]] || [];
        setCurrentQuestionIndex(prevDomainQuestions.length - 1);
      }
    }
  };

  const handleCompleteAssessment = async () => {
    try {
      setSubmittingAssessment(true);
      
      // For demo purposes, create a mock assessment ID
      const mockAssessmentId = Date.now();
      
      // Calculate final scores
      const scoringResult = await calculateAssessmentScore(mockAssessmentId, industryProfile);
      
      // Save results for the reports page
      const assessmentResults = {
        profile: industryProfile,
        questions: questions,
        responses: responses,
        scoring: scoringResult,
        completedAt: new Date().toISOString(),
        totalQuestions: totalQuestions,
        answeredQuestions: answeredQuestions
      };
      
      sessionStorage.setItem('enhancedAssessmentResults', JSON.stringify(assessmentResults));
      
      // Navigate to results
      router.push('/enhanced-reports');
      
    } catch (err) {
      console.error('Error completing assessment:', err);
      setError('Failed to calculate assessment results. Please try again.');
      setSubmittingAssessment(false);
    }
  };

  const renderQuestionInput = (question: Question) => {
    const currentValue = responses[question.id];
    
    switch (question.question_type) {
      case 'boolean':
        return (
          <div className="space-y-3">
            <div className="flex space-x-6">
              <label className="flex items-center">
                <input
                  type="radio"
                  name={question.id}
                  checked={currentValue === true}
                  onChange={() => handleSaveResponse(question.id, true)}
                  className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300"
                />
                <span className="ml-2 text-gray-700">Yes</span>
              </label>
              <label className="flex items-center">
                <input
                  type="radio"
                  name={question.id}
                  checked={currentValue === false}
                  onChange={() => handleSaveResponse(question.id, false)}
                  className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300"
                />
                <span className="ml-2 text-gray-700">No</span>
              </label>
            </div>
          </div>
        );

      case 'scale':
        return (
          <div className="space-y-4">
            <input
              type="range"
              min={question.min_value || 1}
              max={question.max_value || 5}
              value={currentValue || question.min_value || 1}
              onChange={(e) => handleSaveResponse(question.id, parseInt(e.target.value))}
              className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer"
            />
            <div className="flex justify-between text-sm text-gray-600">
              <span>{question.min_value || 1}</span>
              <span className="font-medium bg-blue-100 px-2 py-1 rounded">
                Current: {currentValue || question.min_value || 1}
              </span>
              <span>{question.max_value || 5}</span>
            </div>
          </div>
        );

      case 'select':
        return (
          <select
            value={currentValue || ''}
            onChange={(e) => handleSaveResponse(question.id, e.target.value)}
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
          <div className="space-y-3">
            {question.options?.map((option: string) => (
              <label key={option} className="flex items-center space-x-3 p-2 hover:bg-gray-50 rounded">
                <input
                  type="checkbox"
                  checked={Array.isArray(currentValue) && currentValue.includes(option)}
                  onChange={(e) => {
                    const currentArray = Array.isArray(currentValue) ? currentValue : [];
                    const newValue = e.target.checked
                      ? [...currentArray, option]
                      : currentArray.filter(item => item !== option);
                    handleSaveResponse(question.id, newValue);
                  }}
                  className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                />
                <span className="text-gray-700">{option}</span>
              </label>
            ))}
          </div>
        );

      case 'text':
        return (
          <textarea
            value={currentValue || ''}
            onChange={(e) => handleSaveResponse(question.id, e.target.value)}
            placeholder="Enter your response..."
            className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            rows={4}
          />
        );

      default:
        return <div className="text-red-500">Unsupported question type: {question.question_type}</div>;
    }
  };

  // Show profile setup
  if (showProfileSetup) {
    return (
      <div className="min-h-screen bg-gray-50 py-8">
        <div className="max-w-4xl mx-auto px-4">
          <div className="text-center mb-8">
            <h1 className="text-4xl font-bold text-gray-900 mb-4">
              Enterprise Risk Assessment Platform
            </h1>
            <p className="text-xl text-gray-600">
              Comprehensive 120-question cybersecurity assessment with industry-specific adaptations
            </p>
          </div>
          
          <IndustryProfileSetup
            onProfileComplete={handleProfileComplete}
            onCancel={handleSkipProfile}
          />
          
          {loading && (
            <div className="mt-8 text-center">
              <div className="animate-spin rounded-full h-8 w-8 border-b-2 border-blue-600 mx-auto"></div>
              <p className="mt-2 text-gray-600">Loading your tailored assessment...</p>
            </div>
          )}
          
          {error && (
            <div className="mt-8 bg-red-50 border border-red-200 rounded-lg p-4">
              <div className="text-red-800">{error}</div>
            </div>
          )}
        </div>
      </div>
    );
  }

  // Show assessment
  if (!questions || !currentQuestion) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-xl text-gray-600">Loading assessment...</p>
        </div>
      </div>
    );
  }

  const progressPercentage = Math.round((answeredQuestions / totalQuestions) * 100);
  const isLastQuestion = currentDomainIndex === domains.length - 1 && 
                        currentQuestionIndex === currentDomainQuestions.length - 1;
  const isFirstQuestion = currentDomainIndex === 0 && currentQuestionIndex === 0;

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-4xl mx-auto px-4">
        {/* Progress Header */}
        <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
          <div className="flex justify-between items-center mb-4">
            <div>
              <h1 className="text-2xl font-bold text-gray-900">
                Cybersecurity Risk Assessment
              </h1>
              <p className="text-gray-600">
                {industryProfile.industry && (
                  <span className="capitalize">{industryProfile.industry.replace('_', ' ')} Industry • </span>
                )}
                Domain: {currentDomain?.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())}
              </p>
            </div>
            <div className="text-right">
              <div className="text-2xl font-bold text-blue-600">{progressPercentage}%</div>
              <div className="text-sm text-gray-500">
                {answeredQuestions} of {totalQuestions} questions
              </div>
            </div>
          </div>
          
          <div className="w-full bg-gray-200 rounded-full h-2">
            <div 
              className="bg-blue-600 h-2 rounded-full transition-all duration-300"
              style={{ width: `${progressPercentage}%` }}
            ></div>
          </div>
        </div>

        {/* Question Card */}
        <div className="bg-white rounded-lg shadow-lg p-8">
          <div className="mb-6">
            <div className="flex items-center justify-between mb-4">
              <div className="text-sm text-gray-500">
                Question {answeredQuestions + 1} of {totalQuestions}
              </div>
              {currentQuestion.industry_specific && (
                <span className="px-2 py-1 bg-blue-100 text-blue-800 text-xs rounded-full">
                  Industry Specific
                </span>
              )}
            </div>
            
            <h2 className="text-xl font-semibold text-gray-900 mb-4">
              {currentQuestion.question_text}
            </h2>
            
            {currentQuestion.help_text && (
              <div className="bg-blue-50 border-l-4 border-blue-400 p-4 mb-6">
                <p className="text-blue-800 text-sm">{currentQuestion.help_text}</p>
              </div>
            )}
            
            {currentQuestion.compliance_frameworks && currentQuestion.compliance_frameworks.length > 0 && (
              <div className="mb-4">
                <div className="text-sm text-gray-600">
                  Compliance frameworks: {currentQuestion.compliance_frameworks.map(f => f.toUpperCase()).join(', ')}
                </div>
              </div>
            )}
          </div>

          <div className="mb-8">
            {renderQuestionInput(currentQuestion)}
          </div>

          {/* Navigation */}
          <div className="flex justify-between">
            <button
              onClick={() => handleNavigate('prev')}
              disabled={isFirstQuestion}
              className="px-6 py-3 bg-gray-300 text-gray-700 rounded-lg hover:bg-gray-400 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              Previous
            </button>

            <button
              onClick={() => handleNavigate('next')}
              disabled={submittingAssessment}
              className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {submittingAssessment ? 'Calculating Results...' : 
               isLastQuestion ? 'Complete Assessment' : 'Next'}
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

export default EnhancedAssessmentPage;