import React, { useState, useEffect } from 'react';

interface Recommendation {
  recommendation_id: string;
  category: string;
  text: string;
  confidence_score: number;
  implementation_difficulty: string;
  expected_impact: string;
  timeframe: string;
  primary_sources?: Array<{
    framework: string;
    control_id: string;
    control_title: string;
    relevance_score: number;
  }>;
  bias_score?: number;
  fairness_metrics?: {
    demographic_parity: number;
    individual_fairness: number;
    group_fairness: number;
    overall_fairness: number;
  };
  bias_warnings?: string[];
  review_required?: boolean;
}

interface FeedbackVisualizationProps {
  assessmentId: number;
  recommendations: Recommendation[];
  qualityMetrics: {
    total_recommendations: number;
    high_confidence_count: number;
    average_confidence: number;
    review_required_count: number;
  };
}

const FeedbackVisualization: React.FC<FeedbackVisualizationProps> = ({
  assessmentId,
  recommendations,
  qualityMetrics
}) => {
  const [activeTab, setActiveTab] = useState<'immediate' | 'short_term' | 'strategic'>('immediate');
  const [selectedRecommendation, setSelectedRecommendation] = useState<Recommendation | null>(null);

  const getConfidenceColor = (confidence: number) => {
    if (confidence >= 0.8) return '#16a34a'; // green
    if (confidence >= 0.6) return '#ca8a04'; // yellow
    return '#dc2626'; // red
  };

  const getDifficultyColor = (difficulty: string) => {
    switch (difficulty.toLowerCase()) {
      case 'easy': return '#16a34a';
      case 'medium': return '#ca8a04';
      case 'hard': return '#dc2626';
      default: return '#6b7280';
    }
  };

  const getImpactColor = (impact: string) => {
    switch (impact.toLowerCase()) {
      case 'high': return '#dc2626';
      case 'medium': return '#ca8a04';
      case 'low': return '#16a34a';
      default: return '#6b7280';
    }
  };

  const filteredRecommendations = recommendations.filter(rec => rec.category === activeTab);

  const RecommendationCard: React.FC<{ recommendation: Recommendation }> = ({ recommendation }) => (
    <div className="bg-white border border-gray-200 rounded-lg p-6 hover:shadow-md transition-shadow">
      <div className="flex items-start justify-between mb-4">
        <div className="flex-1">
          <p className="text-gray-900 mb-3">{recommendation.text}</p>
          
          <div className="flex items-center space-x-4 text-sm">
            <div className="flex items-center">
              <span className="text-gray-500 mr-1">Confidence:</span>
              <span 
                className="font-medium"
                style={{ color: getConfidenceColor(recommendation.confidence_score) }}
              >
                {Math.round(recommendation.confidence_score * 100)}%
              </span>
            </div>
            
            <div className="flex items-center">
              <span className="text-gray-500 mr-1">Difficulty:</span>
              <span 
                className="font-medium"
                style={{ color: getDifficultyColor(recommendation.implementation_difficulty) }}
              >
                {recommendation.implementation_difficulty}
              </span>
            </div>
            
            <div className="flex items-center">
              <span className="text-gray-500 mr-1">Impact:</span>
              <span 
                className="font-medium"
                style={{ color: getImpactColor(recommendation.expected_impact) }}
              >
                {recommendation.expected_impact}
              </span>
            </div>
            
            <div className="flex items-center">
              <span className="text-gray-500 mr-1">Timeframe:</span>
              <span className="font-medium text-gray-700">{recommendation.timeframe}</span>
            </div>
          </div>
        </div>
        
        <button
          onClick={() => setSelectedRecommendation(recommendation)}
          className="ml-4 px-3 py-1 text-sm bg-blue-100 text-blue-700 rounded hover:bg-blue-200"
        >
          Details
        </button>
      </div>

      {/* Source Attribution Preview */}
      {recommendation.primary_sources && recommendation.primary_sources.length > 0 && (
        <div className="mb-3">
          <div className="text-sm text-gray-600 mb-1">Framework References:</div>
          <div className="flex flex-wrap gap-2">
            {recommendation.primary_sources.slice(0, 3).map((source, index) => (
              <span 
                key={index}
                className="px-2 py-1 bg-blue-50 text-blue-700 text-xs rounded"
              >
                {source.framework}: {source.control_id}
              </span>
            ))}
            {recommendation.primary_sources.length > 3 && (
              <span className="px-2 py-1 bg-gray-50 text-gray-600 text-xs rounded">
                +{recommendation.primary_sources.length - 3} more
              </span>
            )}
          </div>
        </div>
      )}

      {/* Bias Warnings */}
      {recommendation.bias_warnings && recommendation.bias_warnings.length > 0 && (
        <div className="mb-3">
          <div className="flex items-center text-sm text-amber-600 mb-1">
            <svg className="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
            </svg>
            Bias Detected
          </div>
          <div className="text-xs text-amber-700">
            {recommendation.bias_warnings[0]}
          </div>
        </div>
      )}

      {/* Review Required */}
      {recommendation.review_required && (
        <div className="bg-red-50 border border-red-200 rounded p-2">
          <div className="flex items-center text-sm text-red-700">
            <svg className="w-4 h-4 mr-1" fill="currentColor" viewBox="0 0 20 20">
              <path fillRule="evenodd" d="M10 18a8 8 0 100-16 8 8 0 000 16zM8.707 7.293a1 1 0 00-1.414 1.414L8.586 10l-1.293 1.293a1 1 0 101.414 1.414L10 11.414l1.293 1.293a1 1 0 001.414-1.414L11.414 10l1.293-1.293a1 1 0 00-1.414-1.414L10 8.586 8.707 7.293z" clipRule="evenodd" />
            </svg>
            Human review required
          </div>
        </div>
      )}
    </div>
  );

  return (
    <div className="bg-white rounded-lg shadow-lg">
      {/* Header */}
      <div className="p-6 border-b border-gray-200">
        <h2 className="text-2xl font-bold text-gray-900 mb-2">AI-Powered Recommendations</h2>
        <div className="grid grid-cols-4 gap-4 text-sm">
          <div className="text-center">
            <div className="text-2xl font-bold text-blue-600">{qualityMetrics.total_recommendations}</div>
            <div className="text-gray-600">Total Recommendations</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-green-600">{qualityMetrics.high_confidence_count}</div>
            <div className="text-gray-600">High Confidence</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-gray-900">{Math.round(qualityMetrics.average_confidence * 100)}%</div>
            <div className="text-gray-600">Avg Confidence</div>
          </div>
          <div className="text-center">
            <div className="text-2xl font-bold text-red-600">{qualityMetrics.review_required_count}</div>
            <div className="text-gray-600">Need Review</div>
          </div>
        </div>
      </div>

      {/* Navigation Tabs */}
      <div className="border-b border-gray-200">
        <nav className="-mb-px flex">
          {[
            { key: 'immediate', label: 'Immediate Actions (0-30 days)', color: 'red' },
            { key: 'short_term', label: 'Short-term (1-6 months)', color: 'yellow' },
            { key: 'strategic', label: 'Strategic (6+ months)', color: 'green' }
          ].map(tab => (
            <button
              key={tab.key}
              onClick={() => setActiveTab(tab.key as any)}
              className={`py-4 px-6 font-medium text-sm border-b-2 ${
                activeTab === tab.key
                  ? `border-${tab.color}-500 text-${tab.color}-600`
                  : 'border-transparent text-gray-500 hover:text-gray-700'
              }`}
            >
              {tab.label}
              <span className="ml-2 px-2 py-1 bg-gray-100 text-gray-600 text-xs rounded">
                {recommendations.filter(r => r.category === tab.key).length}
              </span>
            </button>
          ))}
        </nav>
      </div>

      {/* Recommendations List */}
      <div className="p-6">
        {filteredRecommendations.length > 0 ? (
          <div className="space-y-4">
            {filteredRecommendations.map((recommendation) => (
              <RecommendationCard 
                key={recommendation.recommendation_id} 
                recommendation={recommendation} 
              />
            ))}
          </div>
        ) : (
          <div className="text-center py-8 text-gray-500">
            No recommendations in this category
          </div>
        )}
      </div>

      {/* Detailed Modal */}
      {selectedRecommendation && (
        <div className="fixed inset-0 bg-black bg-opacity-50 flex items-center justify-center z-50">
          <div className="bg-white rounded-lg max-w-4xl max-h-[90vh] overflow-y-auto m-4">
            <div className="p-6 border-b border-gray-200">
              <div className="flex justify-between items-start">
                <h3 className="text-xl font-bold text-gray-900">Recommendation Details</h3>
                <button
                  onClick={() => setSelectedRecommendation(null)}
                  className="text-gray-400 hover:text-gray-600"
                >
                  <svg className="w-6 h-6" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                    <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M6 18L18 6M6 6l12 12" />
                  </svg>
                </button>
              </div>
            </div>
            
            <div className="p-6 space-y-6">
              {/* Recommendation Text */}
              <div>
                <h4 className="font-semibold text-gray-900 mb-2">Recommendation</h4>
                <p className="text-gray-700">{selectedRecommendation.text}</p>
              </div>

              {/* Metrics */}
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                <div className="text-center p-3 bg-gray-50 rounded">
                  <div className="text-lg font-bold" style={{ color: getConfidenceColor(selectedRecommendation.confidence_score) }}>
                    {Math.round(selectedRecommendation.confidence_score * 100)}%
                  </div>
                  <div className="text-sm text-gray-600">Confidence</div>
                </div>
                <div className="text-center p-3 bg-gray-50 rounded">
                  <div className="text-lg font-bold" style={{ color: getDifficultyColor(selectedRecommendation.implementation_difficulty) }}>
                    {selectedRecommendation.implementation_difficulty}
                  </div>
                  <div className="text-sm text-gray-600">Difficulty</div>
                </div>
                <div className="text-center p-3 bg-gray-50 rounded">
                  <div className="text-lg font-bold" style={{ color: getImpactColor(selectedRecommendation.expected_impact) }}>
                    {selectedRecommendation.expected_impact}
                  </div>
                  <div className="text-sm text-gray-600">Impact</div>
                </div>
                <div className="text-center p-3 bg-gray-50 rounded">
                  <div className="text-lg font-bold text-gray-900">{selectedRecommendation.timeframe}</div>
                  <div className="text-sm text-gray-600">Timeframe</div>
                </div>
              </div>

              {/* Framework Sources */}
              {selectedRecommendation.primary_sources && (
                <div>
                  <h4 className="font-semibold text-gray-900 mb-3">Framework References</h4>
                  <div className="space-y-2">
                    {selectedRecommendation.primary_sources.map((source, index) => (
                      <div key={index} className="border border-gray-200 rounded p-3">
                        <div className="flex justify-between items-start">
                          <div>
                            <div className="font-medium text-gray-900">{source.framework}</div>
                            <div className="text-sm text-gray-600">{source.control_id}: {source.control_title}</div>
                          </div>
                          <div className="text-sm text-gray-500">
                            {Math.round(source.relevance_score * 100)}% relevance
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Fairness Metrics */}
              {selectedRecommendation.fairness_metrics && (
                <div>
                  <h4 className="font-semibold text-gray-900 mb-3">Fairness Analysis</h4>
                  <div className="grid grid-cols-2 gap-4">
                    {Object.entries(selectedRecommendation.fairness_metrics).map(([metric, value]) => (
                      <div key={metric} className="flex justify-between items-center p-2 bg-gray-50 rounded">
                        <span className="text-sm text-gray-600 capitalize">{metric.replace('_', ' ')}</span>
                        <span className="font-medium">{Math.round(value * 100)}%</span>
                      </div>
                    ))}
                  </div>
                </div>
              )}

              {/* Bias Warnings */}
              {selectedRecommendation.bias_warnings && selectedRecommendation.bias_warnings.length > 0 && (
                <div>
                  <h4 className="font-semibold text-gray-900 mb-3">Bias Analysis</h4>
                  <div className="space-y-2">
                    {selectedRecommendation.bias_warnings.map((warning, index) => (
                      <div key={index} className="bg-amber-50 border border-amber-200 rounded p-3">
                        <div className="flex items-center text-amber-700">
                          <svg className="w-4 h-4 mr-2" fill="currentColor" viewBox="0 0 20 20">
                            <path fillRule="evenodd" d="M8.257 3.099c.765-1.36 2.722-1.36 3.486 0l5.58 9.92c.75 1.334-.213 2.98-1.742 2.98H4.42c-1.53 0-2.493-1.646-1.743-2.98l5.58-9.92zM11 13a1 1 0 11-2 0 1 1 0 012 0zm-1-8a1 1 0 00-1 1v3a1 1 0 002 0V6a1 1 0 00-1-1z" clipRule="evenodd" />
                          </svg>
                          {warning}
                        </div>
                      </div>
                    ))}
                  </div>
                </div>
              )}
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

export default FeedbackVisualization;