import React, { useState, useEffect } from 'react';
import type { NextPage } from 'next';
import { useRouter } from 'next/router';

interface ScoringCategory {
  id: string;
  name: string;
  description: string;
  weight: number;
  current_score: number;
  max_score: number;
  confidence_level: number;
  last_updated: string;
  guidance_available: boolean;
}

interface EvidenceItem {
  id: string;
  category: string;
  description: string;
  evidence_type: string;
  confidence_score: number;
  impact_weight: number;
  source: string;
  date_collected: string;
}

interface ScoringGuidance {
  category_id: string;
  category_name: string;
  description: string;
  scoring_criteria: Array<{
    criterion: string;
    weight: number;
    description: string;
    examples: string[];
  }>;
  improvement_recommendations: string[];
  industry_benchmarks: {
    average_score: number;
    top_quartile: number;
    your_percentile: number;
  };
}

const ScoringPage: NextPage = () => {
  const router = useRouter();
  const [categories, setCategories] = useState<ScoringCategory[]>([]);
  const [selectedCategory, setSelectedCategory] = useState<string | null>(null);
  const [guidance, setGuidance] = useState<ScoringGuidance | null>(null);
  const [evidence, setEvidence] = useState<EvidenceItem[]>([]);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'overview' | 'guidance' | 'evidence'>('overview');

  useEffect(() => {
    fetchScoringData();
  }, []);

  useEffect(() => {
    if (selectedCategory) {
      fetchCategoryGuidance(selectedCategory);
      fetchCategoryEvidence(selectedCategory);
    }
  }, [selectedCategory]);

  const fetchScoringData = async () => {
    try {
      setIsLoading(true);
      // const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      
      // Mock data for demonstration
      const mockCategories: ScoringCategory[] = [
        {
          id: 'governance',
          name: 'Governance',
          description: 'Risk governance and management framework',
          weight: 20,
          current_score: 75,
          max_score: 100,
          confidence_level: 85,
          last_updated: '2025-07-15',
          guidance_available: true
        },
        {
          id: 'identify',
          name: 'Identify',
          description: 'Asset management and risk assessment',
          weight: 15,
          current_score: 68,
          max_score: 100,
          confidence_level: 78,
          last_updated: '2025-07-15',
          guidance_available: true
        },
        {
          id: 'protect',
          name: 'Protect',
          description: 'Access control and data security',
          weight: 25,
          current_score: 82,
          max_score: 100,
          confidence_level: 92,
          last_updated: '2025-07-15',
          guidance_available: true
        },
        {
          id: 'detect',
          name: 'Detect',
          description: 'Monitoring and anomaly detection',
          weight: 20,
          current_score: 71,
          max_score: 100,
          confidence_level: 81,
          last_updated: '2025-07-15',
          guidance_available: true
        },
        {
          id: 'respond',
          name: 'Respond',
          description: 'Incident response and communication',
          weight: 15,
          current_score: 65,
          max_score: 100,
          confidence_level: 75,
          last_updated: '2025-07-15',
          guidance_available: true
        },
        {
          id: 'recover',
          name: 'Recover',
          description: 'Recovery planning and improvements',
          weight: 5,
          current_score: 58,
          max_score: 100,
          confidence_level: 70,
          last_updated: '2025-07-15',
          guidance_available: true
        }
      ];

      setCategories(mockCategories);
      if (mockCategories.length > 0) {
        setSelectedCategory(mockCategories[0].id);
      }
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load scoring data');
    } finally {
      setIsLoading(false);
    }
  };

  const fetchCategoryGuidance = async (categoryId: string) => {
    try {
      // const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      
      // Mock guidance data
      const mockGuidance: ScoringGuidance = {
        category_id: categoryId,
        category_name: categories.find(c => c.id === categoryId)?.name || '',
        description: 'Detailed scoring guidance and recommendations',
        scoring_criteria: [
          {
            criterion: 'Policy Documentation',
            weight: 30,
            description: 'Comprehensive documented policies and procedures',
            examples: ['Written security policies', 'Documented procedures', 'Regular policy updates']
          },
          {
            criterion: 'Implementation Evidence',
            weight: 40,
            description: 'Evidence of actual implementation and enforcement',
            examples: ['Audit logs', 'Training records', 'Compliance reports']
          },
          {
            criterion: 'Monitoring & Review',
            weight: 30,
            description: 'Regular monitoring and review processes',
            examples: ['Regular assessments', 'Metrics tracking', 'Continuous improvement']
          }
        ],
        improvement_recommendations: [
          'Implement automated monitoring tools',
          'Establish regular review cycles',
          'Enhance documentation quality',
          'Improve staff training programs'
        ],
        industry_benchmarks: {
          average_score: 72,
          top_quartile: 88,
          your_percentile: 65
        }
      };

      setGuidance(mockGuidance);
    } catch (err) {
      console.error('Failed to fetch guidance:', err);
    }
  };

  const fetchCategoryEvidence = async (categoryId: string) => {
    try {
      // Mock evidence data
      const mockEvidence: EvidenceItem[] = [
        {
          id: '1',
          category: categoryId,
          description: 'Security policy documentation reviewed',
          evidence_type: 'Document Review',
          confidence_score: 85,
          impact_weight: 25,
          source: 'Internal Audit',
          date_collected: '2025-07-15'
        },
        {
          id: '2',
          category: categoryId,
          description: 'Access control implementation verified',
          evidence_type: 'Technical Assessment',
          confidence_score: 92,
          impact_weight: 35,
          source: 'Security Assessment',
          date_collected: '2025-07-14'
        },
        {
          id: '3',
          category: categoryId,
          description: 'Staff training completion tracked',
          evidence_type: 'Training Records',
          confidence_score: 78,
          impact_weight: 20,
          source: 'HR System',
          date_collected: '2025-07-13'
        }
      ];

      setEvidence(mockEvidence);
    } catch (err) {
      console.error('Failed to fetch evidence:', err);
    }
  };

  const getScoreColor = (score: number): string => {
    if (score >= 90) return 'text-green-400';
    if (score >= 80) return 'text-blue-400';
    if (score >= 70) return 'text-yellow-400';
    if (score >= 60) return 'text-orange-400';
    return 'text-red-400';
  };

  const getScoreBg = (score: number): string => {
    if (score >= 90) return 'bg-green-500/20 border-green-500/30';
    if (score >= 80) return 'bg-blue-500/20 border-blue-500/30';
    if (score >= 70) return 'bg-yellow-500/20 border-yellow-500/30';
    if (score >= 60) return 'bg-orange-500/20 border-orange-500/30';
    return 'bg-red-500/20 border-red-500/30';
  };

  const calculateOverallScore = (): number => {
    const weightedSum = categories.reduce((sum, cat) => sum + (cat.current_score * cat.weight / 100), 0);
    const totalWeight = categories.reduce((sum, cat) => sum + cat.weight, 0);
    return totalWeight > 0 ? weightedSum : 0;
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-950 to-gray-900 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-indigo-400 mx-auto mb-4"></div>
          <p className="text-white text-lg">Loading Scoring System...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-950 to-gray-900 flex items-center justify-center">
        <div className="text-center p-8 bg-red-900/50 rounded-lg max-w-md">
          <h2 className="text-red-400 text-xl font-bold mb-2">Error Loading Scoring Data</h2>
          <p className="text-red-300 mb-4">{error}</p>
          <button
            onClick={fetchScoringData}
            className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition mr-2"
          >
            Retry
          </button>
          <button
            onClick={() => router.push('/')}
            className="px-4 py-2 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition"
          >
            Back to Dashboard
          </button>
        </div>
      </div>
    );
  }

  const overallScore = calculateOverallScore();
  const selectedCategoryData = categories.find(c => c.id === selectedCategory);

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-950 to-gray-900 text-white">
      {/* Header */}
      <header className="p-6 bg-gray-900/80 backdrop-blur-md shadow-lg">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div>
            <h1 className="text-4xl font-bold bg-gradient-to-r from-indigo-400 to-purple-500 bg-clip-text text-transparent mb-2">
              Objective Scoring
            </h1>
            <p className="text-gray-300 text-lg">Evidence-based scoring with detailed justifications</p>
          </div>
          <button
            onClick={() => router.push('/')}
            className="px-4 py-2 bg-gray-700 text-white rounded-lg hover:bg-gray-600 transition"
          >
            ← Back to Dashboard
          </button>
        </div>
      </header>

      <div className="p-6">
        <div className="max-w-7xl mx-auto">
          {/* Overall Score */}
          <div className="bg-gray-800/50 rounded-lg p-6 mb-8">
            <h2 className="text-2xl font-bold mb-6 flex items-center gap-2">
              <span>🎯</span> Overall Security Score
            </h2>
            <div className="flex items-center justify-center mb-6">
              <div className="relative w-48 h-48">
                <svg className="w-48 h-48 transform -rotate-90" viewBox="0 0 100 100">
                  <circle
                    cx="50"
                    cy="50"
                    r="40"
                    stroke="currentColor"
                    strokeWidth="8"
                    fill="transparent"
                    className="text-gray-700"
                  />
                  <circle
                    cx="50"
                    cy="50"
                    r="40"
                    stroke="currentColor"
                    strokeWidth="8"
                    fill="transparent"
                    strokeDasharray={`${2 * Math.PI * 40}`}
                    strokeDashoffset={`${2 * Math.PI * 40 * (1 - overallScore / 100)}`}
                    className={getScoreColor(overallScore).replace('text-', 'stroke-')}
                  />
                </svg>
                <div className="absolute inset-0 flex items-center justify-center">
                  <div className="text-center">
                    <div className={`text-4xl font-bold ${getScoreColor(overallScore)}`}>
                      {overallScore.toFixed(0)}
                    </div>
                    <div className="text-sm text-gray-400">out of 100</div>
                  </div>
                </div>
              </div>
            </div>
            <p className="text-center text-gray-300">
              Your organization&apos;s overall cybersecurity maturity score based on evidence-based assessment
            </p>
          </div>

          {/* Category Scores */}
          <div className="bg-gray-800/50 rounded-lg p-6 mb-8">
            <h2 className="text-2xl font-bold mb-6 flex items-center gap-2">
              <span>📊</span> Category Breakdown
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4">
              {categories.map((category) => (
                <button
                  key={category.id}
                  onClick={() => setSelectedCategory(category.id)}
                  className={`p-4 rounded-lg border-2 transition-all text-left ${
                    selectedCategory === category.id
                      ? 'border-indigo-500 bg-indigo-500/10'
                      : 'border-gray-600 hover:border-gray-500'
                  }`}
                >
                  <div className="flex items-center justify-between mb-2">
                    <h3 className="font-semibold text-gray-300">{category.name}</h3>
                    <span className={`text-xl font-bold ${getScoreColor(category.current_score)}`}>
                      {category.current_score}
                    </span>
                  </div>
                  <p className="text-sm text-gray-400 mb-2">{category.description}</p>
                  <div className="flex items-center justify-between text-xs text-gray-500">
                    <span>Weight: {category.weight}%</span>
                    <span>Confidence: {category.confidence_level}%</span>
                  </div>
                </button>
              ))}
            </div>
          </div>

          {/* Detailed Category View */}
          {selectedCategoryData && (
            <div className="bg-gray-800/50 rounded-lg p-6">
              <div className="flex items-center justify-between mb-6">
                <h2 className="text-2xl font-bold flex items-center gap-2">
                  <span>🔍</span> {selectedCategoryData.name} Details
                </h2>
                <div className="flex border-b border-gray-700">
                  <button
                    onClick={() => setActiveTab('overview')}
                    className={`px-4 py-2 font-medium transition ${
                      activeTab === 'overview'
                        ? 'border-b-2 border-indigo-500 text-indigo-400'
                        : 'text-gray-400 hover:text-gray-300'
                    }`}
                  >
                    Overview
                  </button>
                  <button
                    onClick={() => setActiveTab('guidance')}
                    className={`px-4 py-2 font-medium transition ${
                      activeTab === 'guidance'
                        ? 'border-b-2 border-indigo-500 text-indigo-400'
                        : 'text-gray-400 hover:text-gray-300'
                    }`}
                  >
                    Guidance
                  </button>
                  <button
                    onClick={() => setActiveTab('evidence')}
                    className={`px-4 py-2 font-medium transition ${
                      activeTab === 'evidence'
                        ? 'border-b-2 border-indigo-500 text-indigo-400'
                        : 'text-gray-400 hover:text-gray-300'
                    }`}
                  >
                    Evidence
                  </button>
                </div>
              </div>

              {/* Overview Tab */}
              {activeTab === 'overview' && (
                <div className="space-y-6">
                  <div className={`p-6 rounded-lg border ${getScoreBg(selectedCategoryData.current_score)}`}>
                    <div className="flex items-center justify-between mb-4">
                      <h3 className="text-xl font-semibold text-gray-300">Current Score</h3>
                      <span className={`text-3xl font-bold ${getScoreColor(selectedCategoryData.current_score)}`}>
                        {selectedCategoryData.current_score}/{selectedCategoryData.max_score}
                      </span>
                    </div>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-sm">
                      <div>
                        <span className="text-gray-400">Weight in Overall Score:</span>
                        <span className="ml-2 font-medium text-gray-300">{selectedCategoryData.weight}%</span>
                      </div>
                      <div>
                        <span className="text-gray-400">Confidence Level:</span>
                        <span className="ml-2 font-medium text-gray-300">{selectedCategoryData.confidence_level}%</span>
                      </div>
                      <div>
                        <span className="text-gray-400">Last Updated:</span>
                        <span className="ml-2 font-medium text-gray-300">{selectedCategoryData.last_updated}</span>
                      </div>
                    </div>
                  </div>
                </div>
              )}

              {/* Guidance Tab */}
              {activeTab === 'guidance' && guidance && (
                <div className="space-y-6">
                  <div className="bg-gray-700/50 p-6 rounded-lg">
                    <h3 className="text-lg font-semibold text-gray-300 mb-4">Scoring Criteria</h3>
                    <div className="space-y-4">
                      {guidance.scoring_criteria.map((criterion, index) => (
                        <div key={index} className="border-l-4 border-indigo-500 pl-4">
                          <div className="flex items-center justify-between mb-2">
                            <h4 className="font-medium text-gray-300">{criterion.criterion}</h4>
                            <span className="text-sm text-indigo-400">{criterion.weight}% weight</span>
                          </div>
                          <p className="text-sm text-gray-400 mb-2">{criterion.description}</p>
                          <div className="text-xs text-gray-500">
                            Examples: {criterion.examples.join(', ')}
                          </div>
                        </div>
                      ))}
                    </div>
                  </div>

                  <div className="bg-gray-700/50 p-6 rounded-lg">
                    <h3 className="text-lg font-semibold text-gray-300 mb-4">Industry Benchmarks</h3>
                    <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                      <div className="text-center">
                        <div className="text-2xl font-bold text-blue-400">{guidance.industry_benchmarks.average_score}</div>
                        <div className="text-sm text-gray-400">Industry Average</div>
                      </div>
                      <div className="text-center">
                        <div className="text-2xl font-bold text-green-400">{guidance.industry_benchmarks.top_quartile}</div>
                        <div className="text-sm text-gray-400">Top 25%</div>
                      </div>
                      <div className="text-center">
                        <div className="text-2xl font-bold text-yellow-400">{guidance.industry_benchmarks.your_percentile}</div>
                        <div className="text-sm text-gray-400">Your Percentile</div>
                      </div>
                    </div>
                  </div>

                  <div className="bg-gray-700/50 p-6 rounded-lg">
                    <h3 className="text-lg font-semibold text-gray-300 mb-4">Improvement Recommendations</h3>
                    <ul className="space-y-2">
                      {guidance.improvement_recommendations.map((rec, index) => (
                        <li key={index} className="flex items-start gap-3">
                          <span className="text-green-400 mt-1">✓</span>
                          <span className="text-gray-300">{rec}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>
              )}

              {/* Evidence Tab */}
              {activeTab === 'evidence' && (
                <div className="space-y-4">
                  {evidence.map((item) => (
                    <div key={item.id} className="bg-gray-700/50 p-4 rounded-lg">
                      <div className="flex items-center justify-between mb-2">
                        <h4 className="font-medium text-gray-300">{item.description}</h4>
                        <span className="text-sm text-indigo-400">{item.evidence_type}</span>
                      </div>
                      <div className="grid grid-cols-1 md:grid-cols-4 gap-4 text-sm text-gray-400">
                        <div>
                          <span>Confidence: </span>
                          <span className={`font-medium ${getScoreColor(item.confidence_score)}`}>
                            {item.confidence_score}%
                          </span>
                        </div>
                        <div>
                          <span>Impact Weight: </span>
                          <span className="font-medium text-gray-300">{item.impact_weight}%</span>
                        </div>
                        <div>
                          <span>Source: </span>
                          <span className="font-medium text-gray-300">{item.source}</span>
                        </div>
                        <div>
                          <span>Collected: </span>
                          <span className="font-medium text-gray-300">{item.date_collected}</span>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ScoringPage;