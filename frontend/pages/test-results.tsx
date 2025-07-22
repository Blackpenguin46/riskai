import React from 'react';
import Head from 'next/head';

// Test data from our backend test
const testData = {
  "assessment_id": "test-123",
  "company_profile": {
    "name": "Test Corp",
    "industry": "healthcare",
    "size": "medium",
    "country": "US"
  },
  "overall_score": 23.47,
  "risk_level": "Critical Risk",
  "risk_color": "#dc2626",
  "section_breakdown": [
    {
      "section_id": "gov",
      "section_name": "Governance & Risk Management",
      "score": 30,
      "weight": 0.05,
      "confidence": 0.4,
      "evidence_strength": "moderate",
      "maturity_level": "initial",
      "questions_answered": 2
    },
    {
      "section_id": "data",
      "section_name": "Data Protection & Privacy",
      "score": 15,
      "weight": 0.12,
      "confidence": 0.4,
      "evidence_strength": "moderate", 
      "maturity_level": "initial",
      "questions_answered": 2
    }
  ],
  "questions_answered": 12,
  "total_questions": 120,
  "completion_rate": 0.1,
  "ai_feedback": {
    "overall_assessment": "Test Corp demonstrates initial cybersecurity maturity with an overall score of 23.47%. The organization needs immediate attention to establish basic cybersecurity protections.",
    "key_strengths": [
      "Organization shows commitment to cybersecurity improvement"
    ],
    "critical_gaps": [
      "Critical gap in Data Protection & Privacy (15% maturity, 12% weight in overall risk)",
      "Critical gap in Access Control & Identity Management (30% maturity, 12% weight in overall risk)"
    ],
    "ai_recommendations": [
      {
        "priority": "critical",
        "category": "technical",
        "title": "Enhance Data Protection and Privacy Controls",
        "description": "Implement comprehensive data classification, encryption, and loss prevention capabilities. Ensure HIPAA compliance and patient data protection.",
        "implementation_steps": [
          "Deploy data classification and labeling system",
          "Implement encryption for data at rest and in transit",
          "Deploy data loss prevention (DLP) solutions"
        ],
        "estimated_effort": "high",
        "timeframe": "immediate",
        "framework_references": [
          {
            "name": "NIST CSF",
            "control": "PR.DS - Data Security"
          }
        ],
        "risk_impact": "high",
        "confidence_score": 0.85
      },
      {
        "priority": "critical", 
        "category": "technical",
        "title": "Implement Comprehensive Access Control Program",
        "description": "Deploy multi-factor authentication, privileged access management, and regular access reviews.",
        "implementation_steps": [
          "Deploy MFA for all user accounts",
          "Implement privileged access management (PAM) solution",
          "Establish regular access reviews"
        ],
        "estimated_effort": "high",
        "timeframe": "immediate",
        "framework_references": [
          {
            "name": "NIST CSF",
            "control": "PR.AC - Identity Management and Access Control"
          }
        ],
        "risk_impact": "high",
        "confidence_score": 0.85
      }
    ],
    "industry_comparison": "Your organization's cybersecurity maturity score of 23.47% is significantly below the industry benchmark of 75% for medium healthcare organizations.",
    "next_steps": [
      "1. Enhance Data Protection and Privacy Controls (critical priority, immediate)",
      "2. Implement Comprehensive Access Control Program (critical priority, immediate)"
    ],
    "improvement_roadmap": {
      "immediate": [
        "Enhance Data Protection and Privacy Controls",
        "Implement Comprehensive Access Control Program"
      ],
      "short-term": [],
      "medium-term": [],
      "long-term": []
    }
  }
};

const TestResultsPage: React.FC = () => {
  const getRiskColor = (score: number) => {
    if (score >= 80) return 'text-green-600';
    if (score >= 65) return 'text-yellow-600';
    if (score >= 45) return 'text-orange-600';
    return 'text-red-600';
  };

  return (
    <>
      <Head>
        <title>Test Results Display | RiskAI</title>
      </Head>
      <div className="min-h-screen bg-gray-50 py-8">
        <div className="max-w-6xl mx-auto px-4">
          {/* Header */}
          <div className="bg-gradient-to-r from-blue-600 to-indigo-600 rounded-lg shadow-xl p-8 mb-8 text-white">
            <h1 className="text-3xl font-bold mb-2">🧪 Assessment Results Test Page</h1>
            <p className="text-blue-100">Testing the display of assessment results and AI feedback</p>
          </div>

          {/* Key Metrics */}
          <div className="grid md:grid-cols-3 gap-6 mb-8">
            <div className="bg-white rounded-xl shadow-lg p-6 text-center border-2 border-gray-100">
              <div className="mb-3">
                <div className={`text-5xl font-bold ${getRiskColor(testData.overall_score)}`}>
                  {testData.overall_score}
                </div>
                <div className="text-gray-500 font-medium">Overall Score</div>
              </div>
              <div className="w-full bg-gray-200 rounded-full h-3">
                <div 
                  className="bg-red-500 h-3 rounded-full transition-all"
                  style={{ width: `${testData.overall_score}%` }}
                />
              </div>
            </div>
            <div className="bg-white rounded-xl shadow-lg p-6 text-center border-2 border-gray-100">
              <div className={`text-3xl font-bold mb-2 ${getRiskColor(testData.overall_score)}`}>
                {testData.risk_level}
              </div>
              <div className="text-gray-500 font-medium">Risk Classification</div>
              <div className="mt-3 text-sm text-gray-600">
                🔴 High risk - immediate attention needed
              </div>
            </div>
            <div className="bg-white rounded-xl shadow-lg p-6 text-center border-2 border-gray-100">
              <div className="text-3xl font-bold text-blue-600 mb-2">
                {Math.round(testData.completion_rate * 100)}%
              </div>
              <div className="text-gray-500 font-medium">Assessment Completion</div>
              <div className="mt-3 text-sm text-gray-600">
                {testData.questions_answered} of {testData.total_questions} questions answered
              </div>
            </div>
          </div>

          {/* Section Breakdown */}
          <div className="bg-white rounded-xl shadow-lg p-8 mb-8">
            <h2 className="text-2xl font-bold mb-6 text-gray-900">📋 Section Performance Breakdown</h2>
            <div className="grid gap-4">
              {testData.section_breakdown?.map((section: any, index: number) => (
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
                      className="bg-red-500 h-2 rounded-full transition-all"
                      style={{ width: `${section.score}%` }}
                    />
                  </div>
                </div>
              ))}
            </div>
          </div>

          {/* AI Feedback Test */}
          {testData.ai_feedback && (
            <div className="space-y-6">
              {/* Overall Assessment */}
              <div className="bg-white rounded-xl shadow-lg p-8">
                <h2 className="text-2xl font-bold mb-4 text-gray-900">🤖 AI Assessment Summary</h2>
                <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
                  <p className="text-gray-800 leading-relaxed">{testData.ai_feedback.overall_assessment}</p>
                </div>
              </div>

              {/* Strengths and Gaps */}
              <div className="grid md:grid-cols-2 gap-6">
                <div className="bg-white rounded-xl shadow-lg p-6">
                  <h3 className="text-xl font-bold mb-4 text-green-700">✅ Key Strengths</h3>
                  <div className="space-y-3">
                    {testData.ai_feedback.key_strengths?.map((strength: string, index: number) => (
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
                    {testData.ai_feedback.critical_gaps?.map((gap: string, index: number) => (
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
                  {testData.ai_feedback.ai_recommendations?.map((rec: any, index: number) => (
                    <div key={index} className="border-2 border-gray-100 rounded-lg p-6 hover:shadow-md transition-all">
                      <div className="flex items-start justify-between mb-3">
                        <div className="flex items-start space-x-3">
                          <div className="bg-red-100 text-red-700 px-3 py-1 rounded-full text-sm font-bold">
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
                  <p className="text-gray-800 leading-relaxed">{testData.ai_feedback.industry_comparison}</p>
                </div>
              </div>
            </div>
          )}

          {/* Back Button */}
          <div className="mt-12 flex justify-center">
            <button
              onClick={() => window.history.back()}
              className="px-8 py-3 bg-blue-600 text-white rounded-lg font-semibold hover:bg-blue-700 transition-all flex items-center space-x-2"
            >
              <span>🏠</span>
              <span>Back to Dashboard</span>
            </button>
          </div>
        </div>
      </div>
    </>
  );
};

export default TestResultsPage;