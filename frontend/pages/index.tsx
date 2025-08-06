import React, { useState, useEffect } from 'react';
import type { NextPage } from 'next';
import { useRouter } from 'next/router';

const HomePage: NextPage = () => {
  const router = useRouter();
  const [activeTab, setActiveTab] = useState<'assessment' | 'demo' | 'chatbot'>('assessment');
  const [demoData, setDemoData] = useState<any>(null);
  const [loading, setLoading] = useState(false);

  const loadDemoData = async () => {
    setLoading(true);
    try {
      const response = await fetch('http://localhost:8000/api/demo/sample-assessment');
      const data = await response.json();
      setDemoData(data);
    } catch (error) {
      console.error('Error loading demo data:', error);
    } finally {
      setLoading(false);
    }
  };

  const getRiskColor = (score: number) => {
    if (score >= 80) return 'text-green-600 bg-green-100';
    if (score >= 65) return 'text-yellow-600 bg-yellow-100';
    if (score >= 45) return 'text-orange-600 bg-orange-100';
    return 'text-red-600 bg-red-100';
  };

  return (
    <div className="min-h-screen bg-gray-50">
      {/* Header */}
      <div className="bg-white border-b border-gray-200">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="py-6">
            <h1 className="text-3xl font-bold text-gray-900">RiskAI Enterprise Platform</h1>
            <p className="mt-2 text-gray-600">
              AI-powered cybersecurity risk assessment with dynamic scoring and industry benchmarks
            </p>
          </div>
        </div>
      </div>

      {/* Tab Navigation */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 pt-6">
        <div className="border-b border-gray-200">
          <nav className="-mb-px flex space-x-8">
            <button
              onClick={() => setActiveTab('assessment')}
              className={`py-2 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'assessment'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              🛡️ Security Assessment
            </button>
            <button
              onClick={() => {
                setActiveTab('demo');
                if (!demoData) loadDemoData();
              }}
              className={`py-2 px-1 border-b-2 font-medium text-sm ${
                activeTab === 'demo'
                  ? 'border-blue-500 text-blue-600'
                  : 'border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300'
              }`}
            >
              📊 Demo Data
            </button>
            <button
              onClick={() => router.push('/chatbot')}
              className="py-2 px-1 border-b-2 border-transparent text-gray-500 hover:text-gray-700 hover:border-gray-300 font-medium text-sm"
            >
              💬 AI Consultant
            </button>
          </nav>
        </div>
      </div>

      {/* Content */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
        {activeTab === 'assessment' && (
          <div className="space-y-6">
            {/* Assessment Card */}
            <div className="bg-white rounded-lg shadow-lg p-6 border border-gray-200">
              <div className="flex items-start justify-between">
                <div className="flex-1">
                  <h2 className="text-2xl font-bold text-gray-900 mb-2">
                    🔍 Enterprise Security Assessment
                  </h2>
                  <p className="text-gray-600 mb-4">
                    Complete cybersecurity risk assessment with dynamic scoring based on industry benchmarks
                  </p>
                  
                  <div className="grid md:grid-cols-2 gap-4 mb-6">
                    <div className="space-y-2">
                      <h3 className="font-semibold text-gray-900">✨ Features:</h3>
                      <ul className="text-sm text-gray-600 space-y-1">
                        <li>• Dynamic scoring based on actual answers</li>
                        <li>• Industry-specific benchmarks (Healthcare, Finance, Tech)</li>
                        <li>• 120 comprehensive enterprise questions</li>
                        <li>• AI-powered recommendations</li>
                        <li>• Statistical confidence intervals</li>
                      </ul>
                    </div>
                    <div className="space-y-2">
                      <h3 className="font-semibold text-gray-900">📋 Assessment Covers:</h3>
                      <ul className="text-sm text-gray-600 space-y-1">
                        <li>• Governance & Risk Management</li>
                        <li>• Access Control & Identity</li>
                        <li>• Data Protection & Privacy</li>
                        <li>• Security Monitoring</li>
                        <li>• Incident Response</li>
                        <li>• Business Continuity</li>
                      </ul>
                    </div>
                  </div>

                  <div className="flex space-x-4">
                    <button
                      onClick={() => router.push('/real-assessment')}
                      className="bg-blue-600 text-white px-6 py-3 rounded-lg font-semibold hover:bg-blue-700 transition-colors"
                    >
                      Start Assessment
                    </button>
                    <a
                      href="http://localhost:8000/api/assessment/enterprise/questions"
                      target="_blank"
                      rel="noopener noreferrer"
                      className="bg-gray-100 text-gray-700 px-6 py-3 rounded-lg font-semibold hover:bg-gray-200 transition-colors"
                    >
                      View API
                    </a>
                  </div>
                </div>
                <div className="ml-6 text-6xl">
                  🛡️
                </div>
              </div>
            </div>

            {/* Quick Stats */}
            <div className="grid md:grid-cols-3 gap-6">
              <div className="bg-white rounded-lg shadow p-6 text-center">
                <div className="text-3xl font-bold text-blue-600">120</div>
                <div className="text-sm text-gray-600">Comprehensive Questions</div>
              </div>
              <div className="bg-white rounded-lg shadow p-6 text-center">
                <div className="text-3xl font-bold text-green-600">8</div>
                <div className="text-sm text-gray-600">Security Domains</div>
              </div>
              <div className="bg-white rounded-lg shadow p-6 text-center">
                <div className="text-3xl font-bold text-purple-600">5</div>
                <div className="text-sm text-gray-600">Maturity Levels</div>
              </div>
            </div>

            {/* Methodology */}
            <div className="bg-white rounded-lg shadow-lg p-6">
              <h3 className="text-xl font-bold mb-4">🧮 Mathematical Scoring Methodology</h3>
              <div className="grid md:grid-cols-2 gap-6">
                <div>
                  <h4 className="font-semibold mb-2">Dynamic Scoring Types:</h4>
                  <ul className="text-sm text-gray-600 space-y-1">
                    <li><strong>Quantitative:</strong> Percentage-based with industry benchmarks</li>
                    <li><strong>Qualitative:</strong> Text analysis with maturity indicators</li>
                    <li><strong>Scale:</strong> 1-10 ratings with normalization</li>
                    <li><strong>Boolean:</strong> Yes/No with confidence scoring</li>
                  </ul>
                </div>
                <div>
                  <h4 className="font-semibold mb-2">Industry Benchmarks:</h4>
                  <ul className="text-sm text-gray-600 space-y-1">
                    <li><strong>Healthcare MFA:</strong> 85% adoption benchmark</li>
                    <li><strong>Finance MFA:</strong> 94% adoption benchmark</li>
                    <li><strong>Tech Encryption:</strong> 88% coverage benchmark</li>
                    <li><strong>Response Time:</strong> Industry-specific SLAs</li>
                  </ul>
                </div>
              </div>
              <div className="mt-4">
                <a
                  href="/MATHEMATICAL_SCORING_METHODOLOGY.md"
                  target="_blank"
                  className="text-blue-600 hover:text-blue-800 text-sm font-medium"
                >
                  📖 View Full Mathematical Methodology →
                </a>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'demo' && (
          <div className="space-y-6">
            <div className="bg-white rounded-lg shadow-lg p-6">
              <div className="flex justify-between items-center mb-6">
                <h2 className="text-2xl font-bold text-gray-900">📊 Demo Assessment Data</h2>
                <button
                  onClick={loadDemoData}
                  disabled={loading}
                  className="bg-blue-600 text-white px-4 py-2 rounded-lg font-semibold hover:bg-blue-700 disabled:opacity-50"
                >
                  {loading ? 'Loading...' : 'Refresh Demo Data'}
                </button>
              </div>

              {demoData ? (
                <div className="space-y-6">
                  {/* Demo Overview */}
                  <div className="grid md:grid-cols-4 gap-4">
                    <div className="bg-gray-50 rounded-lg p-4 text-center">
                      <div className={`text-3xl font-bold ${getRiskColor(demoData.overall_score).split(' ')[0]}`}>
                        {demoData.overall_score}
                      </div>
                      <div className="text-sm text-gray-600">Overall Score</div>
                    </div>
                    <div className="bg-gray-50 rounded-lg p-4 text-center">
                      <div className={`text-lg font-semibold ${getRiskColor(demoData.overall_score).split(' ')[0]}`}>
                        {demoData.risk_level}
                      </div>
                      <div className="text-sm text-gray-600">Risk Level</div>
                    </div>
                    <div className="bg-gray-50 rounded-lg p-4 text-center">
                      <div className="text-lg font-semibold text-blue-600">
                        {demoData.scoring_method || 'Dynamic'}
                      </div>
                      <div className="text-sm text-gray-600">Scoring Method</div>
                    </div>
                    <div className="bg-gray-50 rounded-lg p-4 text-center">
                      <div className="text-lg font-semibold text-green-600">
                        {demoData.industry_adjustments_applied ? 'Yes' : 'No'}
                      </div>
                      <div className="text-sm text-gray-600">Industry Adjusted</div>
                    </div>
                  </div>

                  {/* Company Profile */}
                  <div className="border rounded-lg p-4">
                    <h3 className="font-semibold mb-3">🏢 Company Profile</h3>
                    <div className="grid md:grid-cols-2 gap-4 text-sm">
                      <div><strong>Name:</strong> {demoData.company_profile?.name}</div>
                      <div><strong>Industry:</strong> {demoData.company_profile?.industry}</div>
                      <div><strong>Size:</strong> {demoData.company_profile?.size}</div>
                      <div><strong>Country:</strong> {demoData.company_profile?.country}</div>
                    </div>
                  </div>

                  {/* Section Breakdown */}
                  <div className="border rounded-lg p-4">
                    <h3 className="font-semibold mb-3">📋 Section Breakdown</h3>
                    <div className="space-y-3">
                      {demoData.section_breakdown?.map((section: any, index: number) => (
                        <div key={index} className="flex items-center justify-between p-3 bg-gray-50 rounded">
                          <div>
                            <div className="font-medium">{section.section_name}</div>
                            <div className="text-sm text-gray-600">
                              Weight: {Math.round(section.weight * 100)}% | 
                              Confidence: {Math.round(section.confidence * 100)}% |
                              Evidence: {section.evidence_strength}
                            </div>
                          </div>
                          <div className={`text-xl font-bold px-3 py-1 rounded ${getRiskColor(section.score)}`}>
                            {section.score}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Recommendations */}
                  <div className="border rounded-lg p-4">
                    <h3 className="font-semibold mb-3">💡 AI Recommendations</h3>
                    <div className="space-y-2">
                      {demoData.recommendations?.map((rec: string, index: number) => (
                        <div key={index} className="flex items-start space-x-3">
                          <div className="bg-blue-100 text-blue-600 rounded-full w-6 h-6 flex items-center justify-center text-sm font-semibold">
                            {index + 1}
                          </div>
                          <p className="text-sm">{rec}</p>
                        </div>
                      ))}
                    </div>
                  </div>

                  {/* Confidence Metrics */}
                  {demoData.confidence_metrics && (
                    <div className="border rounded-lg p-4">
                      <h3 className="font-semibold mb-3">🎯 Confidence Metrics</h3>
                      <div className="grid md:grid-cols-4 gap-4 text-sm">
                        <div>
                          <strong>Overall:</strong> {Math.round(demoData.confidence_metrics.overall_confidence * 100)}%
                        </div>
                        <div>
                          <strong>Min:</strong> {Math.round(demoData.confidence_metrics.min_confidence * 100)}%
                        </div>
                        <div>
                          <strong>Max:</strong> {Math.round(demoData.confidence_metrics.max_confidence * 100)}%
                        </div>
                        <div>
                          <strong>Std Dev:</strong> {Math.round(demoData.confidence_metrics.confidence_std * 100)}%
                        </div>
                      </div>
                    </div>
                  )}

                  {/* Demo Note */}
                  <div className="bg-blue-50 border border-blue-200 rounded-lg p-4">
                    <p className="text-sm text-blue-800">
                      <strong>📝 Note:</strong> {demoData.demo_note || 'This is demonstration data showing dynamic scoring capabilities.'}
                    </p>
                  </div>
                </div>
              ) : (
                <div className="text-center py-12">
                  <div className="text-6xl mb-4">📊</div>
                  <p className="text-gray-600">Click "Refresh Demo Data" to load sample assessment results</p>
                </div>
              )}
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default HomePage;