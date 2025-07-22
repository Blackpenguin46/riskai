import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import Head from 'next/head';

interface Question {
  id: string;
  text: string;
  type: string;
  required: boolean;
  options?: { value: string; label: string; score: number }[];
  scale?: { min: number; max: number };
  description?: string;
  placeholder?: string;
  true_score?: number;
  false_score?: number;
  benchmark?: number;
}

interface Section {
  name: string;
  weight: number;
  description: string;
  questions: Question[];
}

interface CompanyProfile {
  name: string;
  industry: string;
  size: string;
  country: string;
  compliance_requirements: string[];
  technology_adoption: string;
  data_types: string[];
  risk_tolerance: string;
}

const RealAssessmentPage: React.FC = () => {
  const router = useRouter();
  const [currentStep, setCurrentStep] = useState<'profile' | 'assessment' | 'results'>('profile');
  const [companyProfile, setCompanyProfile] = useState<CompanyProfile>({
    name: '',
    industry: '',
    size: '',
    country: 'US',
    compliance_requirements: [],
    technology_adoption: 'medium',
    data_types: [],
    risk_tolerance: 'medium'
  });
  const [sections, setSections] = useState<Record<string, Section>>({});
  const [answers, setAnswers] = useState<Record<string, any>>({});
  const [currentSectionId, setCurrentSectionId] = useState<string>('');
  const [loading, setLoading] = useState(false);
  const [results, setResults] = useState<any>(null);

  useEffect(() => {
    loadAssessmentQuestions();
  }, []);

  const loadAssessmentQuestions = async () => {
    try {
      const response = await fetch('http://localhost:8000/api/assessment/enterprise/questions');
      const data = await response.json();
      setSections(data.sections);
      const firstSection = Object.keys(data.sections)[0];
      setCurrentSectionId(firstSection);
    } catch (error) {
      console.error('Error loading questions:', error);
    }
  };

  const handleProfileSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    if (companyProfile.name && companyProfile.industry && companyProfile.size) {
      setCurrentStep('assessment');
    }
  };

  const handleAnswerChange = (questionId: string, sectionId: string, value: any) => {
    setAnswers(prev => ({
      ...prev,
      [questionId]: value
    }));
  };

  const submitAssessment = async () => {
    setLoading(true);
    try {
      const answersList = Object.entries(answers).map(([questionId, answer]) => {
        // Find section for this question
        const sectionId = Object.keys(sections).find(secId => 
          sections[secId].questions.some(q => q.id === questionId)
        ) || 'unknown';
        
        return {
          question_id: questionId,
          answer: answer,
          section_id: sectionId
        };
      });

      const response = await fetch('http://localhost:8000/api/assessment/enterprise/submit', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify({
          company_profile: companyProfile,
          answers: answersList
        })
      });

      const result = await response.json();
      setResults(result);
      setCurrentStep('results');
    } catch (error) {
      console.error('Error submitting assessment:', error);
    } finally {
      setLoading(false);
    }
  };

  const renderQuestion = (question: Question, sectionId: string) => {
    const value = answers[question.id] || '';

    switch (question.type) {
      case 'multiple_choice':
        return (
          <div className="space-y-4">
            {question.options?.map((option) => (
              <label key={option.value} className={`flex items-center space-x-3 p-3 border-2 rounded-lg cursor-pointer transition-all hover:bg-blue-50 ${
                value === option.value ? 'border-blue-500 bg-blue-50' : 'border-gray-200'
              }`}>
                <input
                  type="radio"
                  name={question.id}
                  value={option.value}
                  checked={value === option.value}
                  onChange={(e) => handleAnswerChange(question.id, sectionId, e.target.value)}
                  className="w-4 h-4 text-blue-600 focus:ring-blue-500"
                />
                <span className="text-gray-800 font-medium">{option.label}</span>
              </label>
            ))}
          </div>
        );

      case 'scale':
        return (
          <div className="space-y-4">
            <div className="bg-gray-50 p-4 rounded-lg">
              <input
                type="range"
                min={question.scale?.min || 1}
                max={question.scale?.max || 10}
                value={value || question.scale?.min || 1}
                onChange={(e) => handleAnswerChange(question.id, sectionId, parseInt(e.target.value))}
                className="w-full h-2 bg-gray-200 rounded-lg appearance-none cursor-pointer slider"
              />
              <div className="flex justify-between text-sm text-gray-600 mt-2">
                <span className="font-medium">{question.scale?.min || 1}</span>
                <span className="text-lg font-bold text-blue-600">Current: {value || question.scale?.min || 1}</span>
                <span className="font-medium">{question.scale?.max || 10}</span>
              </div>
            </div>
            {question.description && (
              <div className="text-sm text-gray-600 bg-blue-50 p-3 rounded-lg">
                💡 {question.description}
              </div>
            )}
          </div>
        );

      case 'boolean':
        return (
          <div className="grid grid-cols-2 gap-4">
            <label className={`flex items-center justify-center space-x-3 p-4 border-2 rounded-lg cursor-pointer transition-all hover:bg-green-50 ${
              value === true || value === 'true' ? 'border-green-500 bg-green-50' : 'border-gray-200'
            }`}>
              <input
                type="radio"
                name={question.id}
                value="true"
                checked={value === true || value === 'true'}
                onChange={() => handleAnswerChange(question.id, sectionId, true)}
                className="w-4 h-4 text-green-600 focus:ring-green-500"
              />
              <span className="text-green-700 font-semibold">✅ Yes</span>
            </label>
            <label className={`flex items-center justify-center space-x-3 p-4 border-2 rounded-lg cursor-pointer transition-all hover:bg-red-50 ${
              value === false || value === 'false' ? 'border-red-500 bg-red-50' : 'border-gray-200'
            }`}>
              <input
                type="radio"
                name={question.id}
                value="false"
                checked={value === false || value === 'false'}
                onChange={() => handleAnswerChange(question.id, sectionId, false)}
                className="w-4 h-4 text-red-600 focus:ring-red-500"
              />
              <span className="text-red-700 font-semibold">❌ No</span>
            </label>
          </div>
        );

      case 'percentage':
        return (
          <div className="space-y-4">
            <div className="relative">
              <input
                type="number"
                min="0"
                max="100"
                value={value || ''}
                onChange={(e) => handleAnswerChange(question.id, sectionId, parseInt(e.target.value))}
                placeholder="Enter percentage (0-100)"
                className="w-full p-4 border-2 border-gray-300 rounded-lg text-lg focus:border-blue-500 focus:ring-2 focus:ring-blue-200"
              />
              <span className="absolute right-3 top-1/2 transform -translate-y-1/2 text-gray-500 font-medium">%</span>
            </div>
            {question.benchmark && (
              <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-3">
                <div className="flex items-center space-x-2">
                  <span className="text-yellow-600">🎯</span>
                  <span className="text-sm font-medium text-yellow-800">
                    Industry benchmark: {question.benchmark}%
                  </span>
                </div>
              </div>
            )}
          </div>
        );

      case 'text':
        return (
          <div className="space-y-2">
            <textarea
              value={value || ''}
              onChange={(e) => handleAnswerChange(question.id, sectionId, e.target.value)}
              placeholder={question.placeholder || 'Enter your response...'}
              rows={4}
              className="w-full p-4 border-2 border-gray-300 rounded-lg focus:border-blue-500 focus:ring-2 focus:ring-blue-200 resize-none"
            />
            <div className="text-xs text-gray-500">
              💡 Optional: Provide additional context to improve assessment accuracy
            </div>
          </div>
        );

      default:
        return (
          <input
            type="text"
            value={value || ''}
            onChange={(e) => handleAnswerChange(question.id, sectionId, e.target.value)}
            placeholder={question.placeholder || 'Enter your response...'}
            className="w-full p-3 border border-gray-300 rounded-lg"
          />
        );
    }
  };

  const getRiskColor = (score: number) => {
    if (score >= 80) return 'text-green-600';
    if (score >= 65) return 'text-yellow-600';
    if (score >= 45) return 'text-orange-600';
    return 'text-red-600';
  };

  if (currentStep === 'profile') {
    return (
      <>
        <Head>
          <title>Security Assessment - Company Profile | RiskAI</title>
          <style jsx global>{`
            .slider::-webkit-slider-thumb {
              appearance: none;
              height: 20px;
              width: 20px;
              border-radius: 50%;
              background: #3B82F6;
              cursor: pointer;
              box-shadow: 0 0 2px 0 #555;
              transition: background .15s ease-in-out;
            }
            .slider::-webkit-slider-thumb:hover {
              background: #2563EB;
            }
            .slider::-moz-range-thumb {
              height: 20px;
              width: 20px;
              border-radius: 50%;
              background: #3B82F6;
              cursor: pointer;
              border: none;
              box-shadow: 0 0 2px 0 #555;
            }
            @media print {
              .no-print { display: none !important; }
            }
          `}</style>
        </Head>
        <div className="min-h-screen bg-gray-50 py-8">
        <div className="max-w-2xl mx-auto px-4">
          <div className="bg-white rounded-xl shadow-xl p-8 border border-gray-200">
            <div className="text-center mb-8">
              <div className="text-6xl mb-4">🏢</div>
              <h1 className="text-3xl font-bold text-gray-900 mb-2">Company Profile Setup</h1>
              <p className="text-gray-600">Tell us about your organization to customize your security assessment</p>
            </div>
            
            <form onSubmit={handleProfileSubmit} className="space-y-6">
              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-3">🏢 Company Name *</label>
                <input
                  type="text"
                  value={companyProfile.name}
                  onChange={(e) => setCompanyProfile(prev => ({...prev, name: e.target.value}))}
                  className="w-full p-4 border-2 border-gray-300 rounded-lg focus:border-blue-500 focus:ring-2 focus:ring-blue-200 transition-all text-lg"
                  placeholder="Enter your company name"
                  required
                />
              </div>

              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-3">🏦 Industry *</label>
                <select
                  value={companyProfile.industry}
                  onChange={(e) => setCompanyProfile(prev => ({...prev, industry: e.target.value}))}
                  className="w-full p-4 border-2 border-gray-300 rounded-lg focus:border-blue-500 focus:ring-2 focus:ring-blue-200 transition-all text-lg"
                  required
                >
                  <option value="">Select Your Industry</option>
                  <option value="healthcare">🏥 Healthcare</option>
                  <option value="finance">🏦 Finance/Banking</option>
                  <option value="technology">💻 Technology</option>
                  <option value="manufacturing">🏭 Manufacturing</option>
                  <option value="government">🏢 Government</option>
                  <option value="education">🎓 Education</option>
                  <option value="retail">🛍️ Retail</option>
                  <option value="other">🏢 Other</option>
                </select>
              </div>

              <div>
                <label className="block text-sm font-semibold text-gray-700 mb-3">👥 Company Size *</label>
                <select
                  value={companyProfile.size}
                  onChange={(e) => setCompanyProfile(prev => ({...prev, size: e.target.value}))}
                  className="w-full p-4 border-2 border-gray-300 rounded-lg focus:border-blue-500 focus:ring-2 focus:ring-blue-200 transition-all text-lg"
                  required
                >
                  <option value="">Select Company Size</option>
                  <option value="small">🏢 Small (1-50 employees)</option>
                  <option value="medium">🏢 Medium (51-500 employees)</option>
                  <option value="large">🏬 Large (501-5000 employees)</option>
                  <option value="enterprise">🏢 Enterprise (5000+ employees)</option>
                </select>
              </div>

              <button
                type="submit"
                className="w-full bg-gradient-to-r from-blue-600 to-indigo-600 text-white py-4 rounded-lg font-bold text-lg hover:from-blue-700 hover:to-indigo-700 transition-all shadow-lg hover:shadow-xl transform hover:scale-105"
              >
                🚀 Start Security Assessment
              </button>
              <p className="text-center text-sm text-gray-500 mt-4">
                🔒 Your information is secure and will only be used for assessment customization
              </p>
            </form>
          </div>
        </div>
      </div>
      </>
    );
  }

  if (currentStep === 'assessment') {
    const sectionIds = Object.keys(sections);
    const currentSection = sections[currentSectionId];
    const currentIndex = sectionIds.indexOf(currentSectionId);
    const totalQuestions = Object.values(sections).reduce((sum, section) => sum + section.questions.length, 0);
    const answeredQuestions = Object.keys(answers).length;

    return (
      <>
        <Head>
          <title>Security Assessment - {currentSection?.name} | RiskAI</title>
        </Head>
        <div className="min-h-screen bg-gray-50 py-8">
        <div className="max-w-4xl mx-auto px-4">
          {/* Progress Bar */}
          <div className="bg-white rounded-lg shadow-lg p-6 mb-6">
            <div className="flex justify-between items-center mb-4">
              <h1 className="text-2xl font-bold">Security Assessment</h1>
              <span className="text-sm text-gray-600">
                {answeredQuestions} of {totalQuestions} questions answered
              </span>
            </div>
            <div className="w-full bg-gray-200 rounded-full h-2">
              <div
                className="bg-blue-600 h-2 rounded-full transition-all"
                style={{ width: `${(answeredQuestions / totalQuestions) * 100}%` }}
              />
            </div>
          </div>

          <div className="grid md:grid-cols-4 gap-6">
            {/* Section Navigation */}
            <div className="bg-white rounded-lg shadow-lg p-6">
              <h3 className="text-lg font-bold mb-6 text-gray-900">📋 Assessment Sections</h3>
              <div className="space-y-3">
                {sectionIds.map((sectionId, index) => {
                  const sectionQuestions = sections[sectionId].questions;
                  const answeredInSection = sectionQuestions.filter(q => answers[q.id] !== undefined).length;
                  const completionPercentage = (answeredInSection / sectionQuestions.length) * 100;
                  
                  return (
                    <button
                      key={sectionId}
                      onClick={() => setCurrentSectionId(sectionId)}
                      className={`w-full text-left p-4 rounded-lg border-2 transition-all ${
                        currentSectionId === sectionId
                          ? 'border-blue-500 bg-blue-50 shadow-md'
                          : 'border-gray-200 hover:border-gray-300 hover:bg-gray-50'
                      }`}
                    >
                      <div className="flex items-center space-x-3">
                        <div className={`w-8 h-8 rounded-full flex items-center justify-center text-sm font-bold ${
                          currentSectionId === sectionId ? 'bg-blue-500 text-white' : 'bg-gray-200 text-gray-600'
                        }`}>
                          {index + 1}
                        </div>
                        <div className="flex-1">
                          <div className="font-medium text-gray-900 text-sm">
                            {sections[sectionId].name}
                          </div>
                          <div className="text-xs text-gray-500">
                            {answeredInSection}/{sectionQuestions.length} questions
                          </div>
                          <div className="w-full bg-gray-200 rounded-full h-1.5 mt-2">
                            <div 
                              className="bg-blue-500 h-1.5 rounded-full transition-all"
                              style={{ width: `${completionPercentage}%` }}
                            />
                          </div>
                        </div>
                      </div>
                    </button>
                  );
                })}
              </div>
            </div>

            {/* Questions */}
            <div className="md:col-span-3 bg-white rounded-lg shadow-lg p-6">
              <div className="mb-8 bg-gradient-to-r from-blue-50 to-indigo-50 rounded-xl p-6 border border-blue-200">
                <h2 className="text-2xl font-bold text-gray-900 mb-2">{currentSection?.name}</h2>
                <p className="text-gray-700 mb-3">{currentSection?.description}</p>
                <div className="flex items-center space-x-4 text-sm">
                  <span className="bg-blue-100 text-blue-800 px-3 py-1 rounded-full font-medium">
                    📊 Weight: {Math.round((currentSection?.weight || 0) * 100)}%
                  </span>
                  <span className="bg-green-100 text-green-800 px-3 py-1 rounded-full font-medium">
                    📝 {currentSection?.questions.length} Questions
                  </span>
                  <span className="bg-purple-100 text-purple-800 px-3 py-1 rounded-full font-medium">
                    ⏱️ Est. {Math.round(currentSection?.questions.length * 1.5)} min
                  </span>
                </div>
              </div>

              <div className="space-y-8">
                {currentSection?.questions.map((question, index) => (
                  <div key={question.id} className="bg-gray-50 border-2 border-gray-200 rounded-xl p-6 hover:shadow-md transition-all">
                    <div className="flex items-start space-x-4 mb-4">
                      <div className="bg-blue-100 text-blue-600 rounded-full w-8 h-8 flex items-center justify-center text-sm font-bold flex-shrink-0">
                        {index + 1}
                      </div>
                      <div className="flex-1">
                        <h3 className="text-lg font-semibold text-gray-900 mb-2">
                          {question.text}
                          {question.required && <span className="text-red-500 ml-2 text-xl">*</span>}
                        </h3>
                        {question.description && (
                          <p className="text-sm text-gray-600 mb-4 bg-blue-50 p-3 rounded-lg">
                            💡 {question.description}
                          </p>
                        )}
                      </div>
                    </div>
                    <div className="ml-12">
                      {renderQuestion(question, currentSectionId)}
                    </div>
                  </div>
                ))}
              </div>

              {/* Navigation */}
              <div className="flex justify-between items-center mt-12 pt-8 border-t border-gray-200">
                <button
                  onClick={() => {
                    const prevIndex = Math.max(0, currentIndex - 1);
                    setCurrentSectionId(sectionIds[prevIndex]);
                  }}
                  disabled={currentIndex === 0}
                  className="flex items-center space-x-2 px-6 py-3 bg-gray-200 text-gray-700 rounded-lg font-medium disabled:opacity-50 hover:bg-gray-300 transition-all"
                >
                  <span>←</span>
                  <span>Previous Section</span>
                </button>

                <div className="text-center">
                  <div className="text-sm text-gray-600 mb-1">
                    Section {currentIndex + 1} of {sectionIds.length}
                  </div>
                  <div className="w-32 bg-gray-200 rounded-full h-2">
                    <div 
                      className="bg-blue-500 h-2 rounded-full transition-all"
                      style={{ width: `${((currentIndex + 1) / sectionIds.length) * 100}%` }}
                    />
                  </div>
                </div>

                {currentIndex === sectionIds.length - 1 ? (
                  <button
                    onClick={submitAssessment}
                    disabled={loading}
                    className="flex items-center space-x-2 px-8 py-3 bg-green-600 text-white rounded-lg font-bold hover:bg-green-700 disabled:opacity-50 transition-all shadow-lg"
                  >
                    {loading ? (
                      <>
                        <div className="animate-spin rounded-full h-5 w-5 border-b-2 border-white"></div>
                        <span>Submitting...</span>
                      </>
                    ) : (
                      <>
                        <span>🎉 Complete Assessment</span>
                      </>
                    )}
                  </button>
                ) : (
                  <button
                    onClick={() => {
                      const nextIndex = Math.min(sectionIds.length - 1, currentIndex + 1);
                      setCurrentSectionId(sectionIds[nextIndex]);
                    }}
                    className="flex items-center space-x-2 px-6 py-3 bg-blue-600 text-white rounded-lg font-medium hover:bg-blue-700 transition-all"
                  >
                    <span>Next Section</span>
                    <span>→</span>
                  </button>
                )}
              </div>
            </div>
          </div>
        </div>
      </div>
      </>
    );
  }

  if (currentStep === 'results' && results) {
    return (
      <>
        <Head>
          <title>Assessment Results - {results.company_profile?.name} | RiskAI</title>
        </Head>
        <div className="min-h-screen bg-gray-50 py-8">
        <div className="max-w-6xl mx-auto px-4">
          {/* Header */}
          <div className="bg-gradient-to-r from-blue-600 to-indigo-600 rounded-lg shadow-xl p-8 mb-8 text-white">
            <h1 className="text-3xl font-bold mb-2">🎆 Assessment Complete!</h1>
            <p className="text-blue-100">Your comprehensive cybersecurity risk assessment results</p>
          </div>

          {/* Key Metrics */}
          <div className="grid md:grid-cols-3 gap-6 mb-8">
            <div className="bg-white rounded-xl shadow-lg p-6 text-center border-2 border-gray-100">
              <div className="mb-3">
                <div className={`text-5xl font-bold ${getRiskColor(results.overall_score)}`}>
                  {results.overall_score}
                </div>
                <div className="text-gray-500 font-medium">Overall Score</div>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-3">
                <div 
                  className={`h-3 rounded-full transition-all ${
                    results.overall_score >= 80 ? 'bg-green-500' :
                    results.overall_score >= 65 ? 'bg-yellow-500' :
                    results.overall_score >= 45 ? 'bg-orange-500' : 'bg-red-500'
                  }`}
                  style={{ width: `${results.overall_score}%` }}
                />
              </div>
            </div>
            <div className="bg-white rounded-xl shadow-lg p-6 text-center border-2 border-gray-100">
              <div className={`text-3xl font-bold mb-2 ${getRiskColor(results.overall_score)}`}>
                {results.risk_level}
              </div>
              <div className="text-gray-500 font-medium">Risk Classification</div>
              <div className="mt-3 text-sm text-gray-600">
                {results.overall_score >= 80 ? '🟢 Excellent security posture' :
                 results.overall_score >= 65 ? '🟡 Good with improvements needed' :
                 results.overall_score >= 45 ? '🟠 Moderate risk - action required' : '🔴 High risk - immediate attention needed'}
              </div>
            </div>
            <div className="bg-white rounded-xl shadow-lg p-6 text-center border-2 border-gray-100">
              <div className="text-3xl font-bold text-blue-600 mb-2">
                {Math.round(results.completion_rate * 100)}%
              </div>
              <div className="text-gray-500 font-medium">Assessment Completion</div>
              <div className="mt-3 text-sm text-gray-600">
                {results.questions_answered} of {results.total_questions} questions answered
              </div>
            </div>
          </div>

          {/* Section Breakdown */}
          <div className="bg-white rounded-xl shadow-lg p-8 mb-8">
            <h2 className="text-2xl font-bold mb-6 text-gray-900">📋 Section Performance Breakdown</h2>
            <div className="grid gap-4">
              {results.section_breakdown?.map((section: any, index: number) => (
                <div key={section.section_id} className="border-2 border-gray-100 rounded-xl p-6 hover:shadow-md transition-all">
                  <div className="flex items-center justify-between mb-4">
                    <div className="flex items-center space-x-4">
                      <div className="bg-blue-100 text-blue-600 rounded-full w-10 h-10 flex items-center justify-center font-bold">
                        {index + 1}
                      </div>
                      <div>
                        <h3 className="text-lg font-bold text-gray-900">{section.section_name}</h3>
                        <div className="flex items-center space-x-4 text-sm text-gray-600">
                          <span className="bg-gray-100 px-2 py-1 rounded">
                            📊 Weight: {Math.round(section.weight * 100)}%
                          </span>
                          <span className="bg-gray-100 px-2 py-1 rounded">
                            📝 {section.questions_answered} Questions
                          </span>
                          <span className="bg-gray-100 px-2 py-1 rounded">
                            🎯 Confidence: {Math.round(section.confidence * 100)}%
                          </span>
                        </div>
                      </div>
                    </div>
                    <div className="text-right">
                      <div className={`text-3xl font-bold ${getRiskColor(section.score)}`}>
                        {section.score}
                      </div>
                      <div className="text-sm text-gray-500">Score</div>
                    </div>
                  </div>
                  <div className="w-full bg-gray-200 rounded-full h-2">
                    <div 
                      className={`h-2 rounded-full transition-all ${
                        section.score >= 80 ? 'bg-green-500' :
                        section.score >= 65 ? 'bg-yellow-500' :
                        section.score >= 45 ? 'bg-orange-500' : 'bg-red-500'
                      }`}
                      style={{ width: `${section.score}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* AI Feedback and Recommendations */}
          {results.ai_feedback && (
            <div className="space-y-6">
              {/* Overall Assessment */}
              <div className="bg-white rounded-xl shadow-lg p-8">
                <h2 className="text-2xl font-bold mb-4 text-gray-900">🤖 AI Assessment Summary</h2>
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
                  <p className="text-gray-800 leading-relaxed">{results.ai_feedback.overall_assessment}</p>
                </div>
              </div>

              {/* Strengths and Gaps */}
              <div className="grid md:grid-cols-2 gap-6">
                <div className="bg-white rounded-xl shadow-lg p-6">
                  <h3 className="text-xl font-bold mb-4 text-green-700">✅ Key Strengths</h3>
                  <div className="space-y-3">
                    {results.ai_feedback.key_strengths?.map((strength: string, index: number) => (
                      <div key={index} className="flex items-start space-x-3">
                        <div className="bg-green-100 text-green-600 rounded-full w-6 h-6 flex items-center justify-center text-sm font-bold flex-shrink-0">
                          ✓
                        </div>
                        <p className="text-gray-700">{strength}</p>
                      </div>
                    ))}
                  </div>
                </div>

                <div className="bg-white rounded-xl shadow-lg p-6">
                  <h3 className="text-xl font-bold mb-4 text-red-700">⚠️ Critical Gaps</h3>
                  <div className="space-y-3">
                    {results.ai_feedback.critical_gaps?.map((gap: string, index: number) => (
                      <div key={index} className="flex items-start space-x-3">
                        <div className="bg-red-100 text-red-600 rounded-full w-6 h-6 flex items-center justify-center text-sm font-bold flex-shrink-0">
                          !
                        </div>
                        <p className="text-gray-700">{gap}</p>
                      </div>
                    ))}
                  </div>
                </div>
              </div>

              {/* AI Recommendations */}
              <div className="bg-white rounded-xl shadow-lg p-8">
                <h2 className="text-2xl font-bold mb-6 text-gray-900">💡 AI-Powered Recommendations</h2>
                <div className="space-y-4">
                  {results.ai_feedback.ai_recommendations?.map((rec: any, index: number) => (
                    <div key={index} className="border-2 border-gray-100 rounded-lg p-6 hover:shadow-md transition-all">
                      <div className="flex items-start justify-between mb-3">
                        <div className="flex items-start space-x-3">
                          <div className={`px-3 py-1 rounded-full text-sm font-bold ${
                            rec.priority === 'critical' ? 'bg-red-100 text-red-700' :
                            rec.priority === 'high' ? 'bg-orange-100 text-orange-700' :
                            rec.priority === 'medium' ? 'bg-yellow-100 text-yellow-700' :
                            'bg-green-100 text-green-700'
                          }`}>
                            {rec.priority.toUpperCase()}
                          </div>
                          <div className="bg-gray-100 text-gray-700 px-3 py-1 rounded-full text-sm font-medium">
                            {rec.timeframe}
                          </div>
                        </div>
                        <div className="text-sm text-gray-500">
                          Confidence: {Math.round(rec.confidence_score * 100)}%
                        </div>
                      </div>
                      <h4 className="text-lg font-bold text-gray-900 mb-2">{rec.title}</h4>
                      <p className="text-gray-700 mb-4">{rec.description}</p>
                      {rec.implementation_steps && rec.implementation_steps.length > 0 && (
                        <div className="mt-4">
                          <h5 className="font-semibold text-gray-800 mb-2">Implementation Steps:</h5>
                          <ol className="list-decimal list-inside space-y-1 text-sm text-gray-600">
                            {rec.implementation_steps.map((step: string, stepIndex: number) => (
                              <li key={stepIndex}>{step}</li>
                            ))}
                          </ol>
                        </div>
                      )}
                    </div>
                  ))}
                </div>
              </div>

              {/* Industry Comparison */}
              <div className="bg-white rounded-xl shadow-lg p-8">
                <h2 className="text-2xl font-bold mb-4 text-gray-900">🎯 Industry Comparison</h2>
                <div className="bg-purple-50 border border-purple-200 rounded-lg p-6">
                  <p className="text-gray-800 leading-relaxed">{results.ai_feedback.industry_comparison}</p>
                </div>
              </div>
            </div>
          ) || (
            <div className="bg-white rounded-xl shadow-lg p-8">
              <h2 className="text-2xl font-bold mb-4 text-gray-900">💡 Basic Recommendations</h2>
              <div className="space-y-4">
                {results.recommendations?.map((rec: string, index: number) => (
                  <div key={index} className="flex items-start space-x-3 p-4 bg-gray-50 rounded-lg">
                    <div className="bg-blue-100 text-blue-600 rounded-full w-8 h-8 flex items-center justify-center text-sm font-bold flex-shrink-0">
                      {index + 1}
                    </div>
                    <p className="text-gray-700">{rec}</p>
                  </div>
                ))}
              </div>
            </div>
          )}

          {/* Action Buttons */}
          <div className="mt-12 flex justify-center space-x-4">
            <button
              onClick={() => window.print()}
              className="px-8 py-3 bg-gray-600 text-white rounded-lg font-semibold hover:bg-gray-700 transition-all flex items-center space-x-2"
            >
              <span>🖨️</span>
              <span>Print Report</span>
            </button>
            <button
              onClick={() => router.push('/')}
              className="px-8 py-3 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-700 transition-all flex items-center space-x-2"
            >
              <span>🏠</span>
              <span>Back to Dashboard</span>
            </button>
            <button
              onClick={() => window.location.reload()}
              className="px-8 py-3 bg-green-600 text-white rounded-lg font-semibold hover:bg-green-700 transition-all flex items-center space-x-2"
            >
              <span>🔁</span>
              <span>Take New Assessment</span>
            </button>
          </div>
        </div>
      </div>
      </>
    );
  }

  return (
    <>
      <Head>
        <title>Loading Assessment | RiskAI</title>
      </Head>
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-blue-600 mx-auto mb-4"></div>
          <p className="text-gray-600 text-lg">Loading assessment...</p>
        </div>
      </div>
    </>
  );
};

export default RealAssessmentPage;