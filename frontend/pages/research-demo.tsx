import React, { useState, useEffect } from 'react';
import ScoringVisualization from '../components/ScoringVisualization';
import FeedbackVisualization from '../components/FeedbackVisualization';
import RealTimeScoringDisplay from '../components/RealTimeScoringDisplay';

const ResearchDemoPage: React.FC = () => {
  const [demoData, setDemoData] = useState<any>(null);
  const [activeDemo, setActiveDemo] = useState<'scoring' | 'feedback' | 'realtime'>('scoring');
  const [loading, setLoading] = useState(true);

  useEffect(() => {
    loadDemoData();
  }, []);

  const loadDemoData = async () => {
    try {
      // Load sample data for demonstration
      const response = await fetch('http://localhost:8000/api/demo/sample-assessment');
      const data = await response.json();
      setDemoData(data);
    } catch (error) {
      console.error('Error loading demo data:', error);
      // Fallback to static demo data
      setDemoData(getStaticDemoData());
    } finally {
      setLoading(false);
    }
  };

  const getStaticDemoData = () => ({
    assessment_id: 1,
    profile: {
      industry: "healthcare",
      company_size: "medium",
      compliance_requirements: ["HIPAA", "SOC2"],
      data_types: ["patient_data", "financial_data"]
    },
    scoring: {
      overall_score: 72.5,
      risk_level: "Medium Risk",
      risk_color: "#ca8a04",
      section_breakdown: [
        {
          section_id: "governance",
          section_name: "Governance & Risk Management",
          score: 78.0,
          risk_level: "Medium Risk",
          weight: 20,
          questions_answered: 10,
          total_questions: 10
        },
        {
          section_id: "data_protection",
          section_name: "Data Protection",
          score: 85.0,
          risk_level: "Low Risk",
          weight: 12,
          questions_answered: 10,
          total_questions: 10
        },
        {
          section_id: "access_control",
          section_name: "Access Control",
          score: 65.0,
          risk_level: "Medium Risk",
          weight: 12,
          questions_answered: 10,
          total_questions: 10
        }
      ],
      risk_categorization: {
        confidence_interval: {
          lower_bound: 68.2,
          upper_bound: 76.8
        },
        recommendations: [
          "Implement multi-factor authentication across all systems",
          "Establish formal incident response procedures",
          "Enhance security awareness training program"
        ]
      }
    },
    recommendations: [
      {
        recommendation_id: "rec_001",
        category: "immediate",
        text: "Implement multi-factor authentication (MFA) for all administrative accounts to reduce unauthorized access risk.",
        confidence_score: 0.92,
        implementation_difficulty: "Medium",
        expected_impact: "High",
        timeframe: "0-30 days",
        primary_sources: [
          {
            framework: "NIST Cybersecurity Framework",
            control_id: "PR.AC-1",
            control_title: "Identities and credentials are issued, managed, verified, revoked, and audited",
            relevance_score: 0.95
          }
        ],
        bias_score: 0.15,
        fairness_metrics: {
          demographic_parity: 0.88,
          individual_fairness: 0.92,
          group_fairness: 0.85,
          overall_fairness: 0.88
        },
        review_required: false
      },
      {
        recommendation_id: "rec_002",
        category: "short_term",
        text: "Establish a comprehensive incident response plan with defined roles, responsibilities, and communication procedures.",
        confidence_score: 0.89,
        implementation_difficulty: "Hard",
        expected_impact: "High",
        timeframe: "1-6 months",
        primary_sources: [
          {
            framework: "ISO 27001",
            control_id: "A.16.1.1",
            control_title: "Responsibilities and procedures",
            relevance_score: 0.90
          }
        ],
        bias_score: 0.22,
        fairness_metrics: {
          demographic_parity: 0.85,
          individual_fairness: 0.88,
          group_fairness: 0.82,
          overall_fairness: 0.85
        },
        review_required: false
      },
      {
        recommendation_id: "rec_003",
        category: "strategic",
        text: "Implement a holistic risk management framework that integrates cybersecurity with business objectives and emerging technology adoption.",
        confidence_score: 0.78,
        implementation_difficulty: "Hard",
        expected_impact: "High",
        timeframe: "6+ months",
        primary_sources: [
          {
            framework: "NIST Cybersecurity Framework",
            control_id: "ID.GV-1",
            control_title: "Organizational cybersecurity policy is established and communicated",
            relevance_score: 0.85
          }
        ],
        bias_score: 0.18,
        fairness_metrics: {
          demographic_parity: 0.90,
          individual_fairness: 0.87,
          group_fairness: 0.89,
          overall_fairness: 0.89
        },
        review_required: false
      }
    ],
    quality_metrics: {
      total_recommendations: 3,
      high_confidence_count: 2,
      average_confidence: 0.86,
      review_required_count: 0
    }
  });

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-xl text-gray-600">Loading research demonstration...</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4">
        {/* Header */}
        <div className="mb-8 text-center">
          <h1 className="text-4xl font-bold text-gray-900 mb-4">
            RiskAI Enhanced Platform
          </h1>
          <p className="text-xl text-gray-600 mb-6">
            Research Demonstration: AI-Powered Cybersecurity Risk Assessment with Mathematical Scoring and Bias Detection
          </p>
          
          {/* Key Features */}
          <div className="grid grid-cols-1 md:grid-cols-4 gap-6 mb-8">
            <div className="bg-gradient-to-br from-blue-50 to-blue-100 border border-blue-200 p-6 rounded-xl shadow-lg hover:shadow-xl transition-all duration-300 hover:scale-105">
              <div className="text-3xl font-bold text-blue-700 mb-2">120</div>
              <div className="text-base font-semibold text-blue-900">Question Assessment</div>
              <div className="text-sm text-blue-600 mt-1">Comprehensive evaluation</div>
            </div>
            <div className="bg-gradient-to-br from-green-50 to-green-100 border border-green-200 p-6 rounded-xl shadow-lg hover:shadow-xl transition-all duration-300 hover:scale-105">
              <div className="text-3xl font-bold text-green-700 mb-2">12</div>
              <div className="text-base font-semibold text-green-900">Security Domains</div>
              <div className="text-sm text-green-600 mt-1">Multi-domain coverage</div>
            </div>
            <div className="bg-gradient-to-br from-purple-50 to-purple-100 border border-purple-200 p-6 rounded-xl shadow-lg hover:shadow-xl transition-all duration-300 hover:scale-105">
              <div className="text-3xl font-bold text-purple-700 mb-2">AI</div>
              <div className="text-base font-semibold text-purple-900">Powered Feedback</div>
              <div className="text-sm text-purple-600 mt-1">Intelligent recommendations</div>
            </div>
            <div className="bg-gradient-to-br from-red-50 to-red-100 border border-red-200 p-6 rounded-xl shadow-lg hover:shadow-xl transition-all duration-300 hover:scale-105">
              <div className="text-3xl font-bold text-red-700 mb-2">Bias</div>
              <div className="text-base font-semibold text-red-900">Detection & Mitigation</div>
              <div className="text-sm text-red-600 mt-1">Fairness monitoring</div>
            </div>
          </div>
        </div>

        {/* Demo Navigation */}
        <div className="mb-6">
          <div className="bg-white rounded-xl shadow-lg border border-gray-200 p-6">
            <div className="flex items-center justify-center space-x-4">
              <span className="text-base font-semibold text-gray-800">Research Components:</span>
              <div className="flex space-x-3">
                <button
                  onClick={() => setActiveDemo('scoring')}
                  className={`px-6 py-3 rounded-lg text-sm font-semibold transition-all duration-200 ${
                    activeDemo === 'scoring'
                      ? 'bg-blue-600 text-white shadow-lg transform scale-105'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200 hover:shadow-md'
                  }`}
                >
                  Mathematical Scoring
                </button>
                <button
                  onClick={() => setActiveDemo('feedback')}
                  className={`px-6 py-3 rounded-lg text-sm font-semibold transition-all duration-200 ${
                    activeDemo === 'feedback'
                      ? 'bg-blue-600 text-white shadow-lg transform scale-105'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200 hover:shadow-md'
                  }`}
                >
                  AI Feedback & Attribution
                </button>
                <button
                  onClick={() => setActiveDemo('realtime')}
                  className={`px-6 py-3 rounded-lg text-sm font-semibold transition-all duration-200 ${
                    activeDemo === 'realtime'
                      ? 'bg-blue-600 text-white shadow-lg transform scale-105'
                      : 'bg-gray-100 text-gray-700 hover:bg-gray-200 hover:shadow-md'
                  }`}
                >
                  Real-time Analysis
                </button>
              </div>
            </div>
          </div>
        </div>

        {/* Demo Content */}
        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Main Content */}
          <div className="lg:col-span-2">
            {activeDemo === 'scoring' && demoData && (
              <ScoringVisualization
                overallScore={{
                  totalScore: demoData.scoring.overall_score,
                  maxScore: 100,
                  percentage: demoData.scoring.overall_score,
                  riskLevel: demoData.scoring.risk_level,
                  riskColor: demoData.scoring.risk_color,
                  confidenceInterval: [
                    demoData.scoring.risk_categorization.confidence_interval.lower_bound,
                    demoData.scoring.risk_categorization.confidence_interval.upper_bound
                  ],
                  sectionBreakdown: demoData.scoring.section_breakdown.map((section: any) => ({
                    sectionId: section.section_id,
                    sectionName: section.section_name,
                    score: section.score,
                    maxScore: 100,
                    percentage: section.score,
                    weight: section.weight,
                    riskLevel: section.risk_level,
                    questionsAnswered: section.questions_answered,
                    totalQuestions: section.total_questions
                  }))
                }}
                showMathematicalDetails={true}
              />
            )}

            {activeDemo === 'feedback' && demoData && (
              <FeedbackVisualization
                assessmentId={demoData.assessment_id}
                recommendations={demoData.recommendations}
                qualityMetrics={demoData.quality_metrics}
              />
            )}

            {activeDemo === 'realtime' && demoData && (
              <div className="space-y-6">
                <div className="bg-white rounded-lg shadow-lg p-6">
                  <h3 className="text-xl font-bold text-gray-900 mb-4">Real-time Scoring Demonstration</h3>
                  <p className="text-gray-600 mb-4">
                    This component shows how scores update in real-time as users answer assessment questions.
                  </p>
                  <RealTimeScoringDisplay
                    responses={{
                      governance: { q1: true, q2: 4, q3: "Implemented" },
                      data_protection: { q1: true, q2: 5, q3: "Advanced" },
                      access_control: { q1: false, q2: 3, q3: "Basic" }
                    }}
                    currentSection="governance"
                    currentQuestion="q4"
                    showProjectedScore={true}
                  />
                </div>
              </div>
            )}
          </div>

          {/* Sidebar */}
          <div className="space-y-6">
            {/* Research Highlights */}
            <div className="bg-gradient-to-br from-slate-50 to-slate-100 border border-slate-200 rounded-xl shadow-lg p-6 hover:shadow-xl transition-shadow duration-300">
              <h3 className="text-xl font-bold text-slate-900 mb-5 flex items-center">
                <span className="w-3 h-3 bg-blue-500 rounded-full mr-3"></span>
                Research Contributions
              </h3>
              <ul className="space-y-4 text-sm">
                <li className="flex items-start p-3 bg-white rounded-lg shadow-sm hover:shadow-md transition-shadow duration-200">
                  <span className="w-3 h-3 bg-blue-500 rounded-full mt-1.5 mr-3 flex-shrink-0"></span>
                  <span className="text-gray-800 font-medium">Mathematical scoring with defined formulas and confidence intervals</span>
                </li>
                <li className="flex items-start p-3 bg-white rounded-lg shadow-sm hover:shadow-md transition-shadow duration-200">
                  <span className="w-3 h-3 bg-green-500 rounded-full mt-1.5 mr-3 flex-shrink-0"></span>
                  <span className="text-gray-800 font-medium">AI-powered recommendations with framework source attribution</span>
                </li>
                <li className="flex items-start p-3 bg-white rounded-lg shadow-sm hover:shadow-md transition-shadow duration-200">
                  <span className="w-3 h-3 bg-purple-500 rounded-full mt-1.5 mr-3 flex-shrink-0"></span>
                  <span className="text-gray-800 font-medium">Comprehensive bias detection and fairness monitoring</span>
                </li>
                <li className="flex items-start p-3 bg-white rounded-lg shadow-sm hover:shadow-md transition-shadow duration-200">
                  <span className="w-3 h-3 bg-red-500 rounded-full mt-1.5 mr-3 flex-shrink-0"></span>
                  <span className="text-gray-800 font-medium">Industry-specific adaptations for emerging technologies</span>
                </li>
                <li className="flex items-start p-3 bg-white rounded-lg shadow-sm hover:shadow-md transition-shadow duration-200">
                  <span className="w-3 h-3 bg-yellow-500 rounded-full mt-1.5 mr-3 flex-shrink-0"></span>
                  <span className="text-gray-800 font-medium">Real-time scoring with transparent methodology</span>
                </li>
              </ul>
            </div>

            {/* Technical Specifications */}
            <div className="bg-gradient-to-br from-indigo-50 to-indigo-100 border border-indigo-200 rounded-xl shadow-lg p-6 hover:shadow-xl transition-shadow duration-300">
              <h3 className="text-xl font-bold text-indigo-900 mb-5 flex items-center">
                <span className="w-3 h-3 bg-indigo-500 rounded-full mr-3"></span>
                Technical Specifications
              </h3>
              <div className="space-y-3">
                <div className="flex justify-between items-center p-3 bg-white rounded-lg shadow-sm">
                  <span className="text-gray-700 font-medium">Assessment Questions:</span>
                  <span className="font-bold text-indigo-700 bg-indigo-100 px-3 py-1 rounded-full text-sm">120 (10 per domain)</span>
                </div>
                <div className="flex justify-between items-center p-3 bg-white rounded-lg shadow-sm">
                  <span className="text-gray-700 font-medium">Security Domains:</span>
                  <span className="font-bold text-indigo-700 bg-indigo-100 px-3 py-1 rounded-full text-sm">12 domains</span>
                </div>
                <div className="flex justify-between items-center p-3 bg-white rounded-lg shadow-sm">
                  <span className="text-gray-700 font-medium">Frameworks Supported:</span>
                  <span className="font-bold text-indigo-700 bg-indigo-100 px-3 py-1 rounded-full text-sm">8+ standards</span>
                </div>
                <div className="flex justify-between items-center p-3 bg-white rounded-lg shadow-sm">
                  <span className="text-gray-700 font-medium">Bias Detection Types:</span>
                  <span className="font-bold text-indigo-700 bg-indigo-100 px-3 py-1 rounded-full text-sm">7 categories</span>
                </div>
                <div className="flex justify-between items-center p-3 bg-white rounded-lg shadow-sm">
                  <span className="text-gray-700 font-medium">Industry Adaptations:</span>
                  <span className="font-bold text-indigo-700 bg-indigo-100 px-3 py-1 rounded-full text-sm">Healthcare, Finance, Tech</span>
                </div>
              </div>
            </div>

            {/* Assessment Profile */}
            {demoData && (
              <div className="bg-gradient-to-br from-emerald-50 to-emerald-100 border border-emerald-200 rounded-xl shadow-lg p-6 hover:shadow-xl transition-shadow duration-300">
                <h3 className="text-xl font-bold text-emerald-900 mb-5 flex items-center">
                  <span className="w-3 h-3 bg-emerald-500 rounded-full mr-3"></span>
                  Demo Profile
                </h3>
                <div className="space-y-3">
                  <div className="flex justify-between items-center p-3 bg-white rounded-lg shadow-sm">
                    <span className="text-gray-700 font-medium">Industry:</span>
                    <span className="font-bold text-emerald-700 bg-emerald-100 px-3 py-1 rounded-full text-sm capitalize">{demoData.profile.industry}</span>
                  </div>
                  <div className="flex justify-between items-center p-3 bg-white rounded-lg shadow-sm">
                    <span className="text-gray-700 font-medium">Company Size:</span>
                    <span className="font-bold text-emerald-700 bg-emerald-100 px-3 py-1 rounded-full text-sm capitalize">{demoData.profile.company_size}</span>
                  </div>
                  <div className="flex justify-between items-center p-3 bg-white rounded-lg shadow-sm">
                    <span className="text-gray-700 font-medium">Compliance:</span>
                    <span className="font-bold text-emerald-700 bg-emerald-100 px-3 py-1 rounded-full text-sm">{demoData.profile.compliance_requirements.join(', ')}</span>
                  </div>
                  <div className="flex justify-between items-center p-3 bg-white rounded-lg shadow-sm">
                    <span className="text-gray-700 font-medium">Overall Score:</span>
                    <span className="font-bold text-2xl px-4 py-2 rounded-full text-white shadow-md" style={{ backgroundColor: demoData.scoring.risk_color }}>
                      {demoData.scoring.overall_score}%
                    </span>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Footer */}
        <div className="mt-12 text-center text-gray-500 text-sm">
          <p>RiskAI Enhanced Platform - Research Demonstration</p>
          <p>Mathematical Scoring • AI Feedback • Bias Detection • Source Attribution</p>
        </div>
      </div>
    </div>
  );
};

export default ResearchDemoPage;