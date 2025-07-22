import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/router';

interface AdvisoryTopic {
  id: string;
  name: string;
  description: string;
  typical_timeline: string;
  complexity: string;
  focus_areas: string[];
}

interface AdvisoryRequest {
  topic: string;
  specific_focus: string;
  organization_context: {
    industry?: string;
    size?: string;
    current_maturity?: string;
  };
  current_challenges: string[];
  desired_outcomes: string[];
  timeline: string;
  budget_constraints?: string;
}

interface Recommendation {
  title: string;
  description: string;
  implementation_steps: string[];
  prerequisites: string[];
  success_metrics: string[];
  risks_and_mitigations: Array<{risk: string; mitigation: string}>;
  frameworks_referenced: string[];
  estimated_timeline: string;
  estimated_cost: string;
  confidence_score: number;
  sources: string[];
}

interface AdvisoryPlan {
  topic: string;
  executive_summary: string;
  situation_analysis: string;
  strategic_approach: string;
  detailed_recommendations: Recommendation[];
  implementation_roadmap: Record<string, string[]>;
  success_factors: string[];
  potential_challenges: string[];
  next_steps: string[];
  knowledge_sources: string[];
  confidence_metrics: Record<string, number>;
  generation_timestamp: string;
}

const ChatPage: React.FC = () => {
  const router = useRouter();
  const [currentStep, setCurrentStep] = useState<'topics' | 'form' | 'results'>('topics');
  const [availableTopics, setAvailableTopics] = useState<AdvisoryTopic[]>([]);
  const [selectedTopic, setSelectedTopic] = useState<AdvisoryTopic | null>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [advisoryPlan, setAdvisoryPlan] = useState<AdvisoryPlan | null>(null);
  
  // Form state
  const [formData, setFormData] = useState<AdvisoryRequest>({
    topic: '',
    specific_focus: '',
    organization_context: {},
    current_challenges: [],
    desired_outcomes: [],
    timeline: '',
    budget_constraints: ''
  });

  // Load available topics on component mount
  useEffect(() => {
    loadAvailableTopics();
  }, []);

  const loadAvailableTopics = async () => {
    try {
      setLoading(true);
      const response = await fetch('/api/advisory/topics');
      if (response.ok) {
        const topics = await response.json();
        setAvailableTopics(topics);
      } else {
        setError('Failed to load advisory topics');
      }
    } catch (err) {
      setError('Error loading topics');
      console.error('Error loading topics:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleTopicSelect = (topic: AdvisoryTopic) => {
    setSelectedTopic(topic);
    setFormData(prev => ({ ...prev, topic: topic.id }));
    setCurrentStep('form');
  };

  const handleFormSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    
    if (!selectedTopic) return;
    
    try {
      setLoading(true);
      setError(null);
      
      const response = await fetch('/api/advisory/generate-plan', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(formData)
      });
      
      if (response.ok) {
        const plan = await response.json();
        setAdvisoryPlan(plan);
        setCurrentStep('results');
      } else {
        const errorData = await response.json();
        setError(errorData.detail || 'Failed to generate advisory plan');
      }
    } catch (err) {
      setError('Error generating advisory plan');
      console.error('Error generating plan:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleInputChange = (field: string, value: any) => {
    if (field.includes('.')) {
      const [parent, child] = field.split('.');
      setFormData(prev => ({
        ...prev,
        [parent]: {
          ...prev[parent as keyof AdvisoryRequest],
          [child]: value
        }
      }));
    } else {
      setFormData(prev => ({ ...prev, [field]: value }));
    }
  };

  const handleArrayInput = (field: string, value: string) => {
    if (value.trim()) {
      const items = value.split(',').map(item => item.trim()).filter(item => item);
      setFormData(prev => ({ ...prev, [field]: items }));
    }
  };

  const renderTopicSelection = () => (
    <div className="max-w-6xl mx-auto px-4 py-8">
      <div className="text-center mb-8">
        <h1 className="text-3xl font-bold text-gray-900 mb-4">
          AI-Powered Risk Advisory
        </h1>
        <p className="text-lg text-gray-600 max-w-3xl mx-auto">
          Get detailed guidance on risk management, emerging technology integration, and cybersecurity strategy. 
          Our AI advisor uses comprehensive knowledge from industry frameworks and best practices.
        </p>
      </div>

      {loading ? (
        <div className="text-center py-12">
          <div className="text-xl text-gray-600">Loading advisory topics...</div>
        </div>
      ) : (
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
          {availableTopics.map((topic) => (
            <div
              key={topic.id}
              onClick={() => handleTopicSelect(topic)}
              className="bg-white rounded-lg shadow-lg p-6 cursor-pointer hover:shadow-xl transition-shadow duration-200 border border-gray-200"
            >
              <div className="flex items-start justify-between mb-4">
                <h3 className="text-xl font-semibold text-gray-900">{topic.name}</h3>
                <span className={`px-2 py-1 text-xs rounded-full ${
                  topic.complexity === 'High' ? 'bg-red-100 text-red-800' :
                  topic.complexity === 'Medium' ? 'bg-yellow-100 text-yellow-800' :
                  'bg-green-100 text-green-800'
                }`}>
                  {topic.complexity}
                </span>
              </div>
              
              <p className="text-gray-600 mb-4 text-sm">{topic.description}</p>
              
              <div className="mb-4">
                <div className="text-sm text-gray-500 mb-2">Timeline: {topic.typical_timeline}</div>
                <div className="text-sm text-gray-500">Focus Areas:</div>
                <ul className="text-xs text-gray-600 mt-1">
                  {topic.focus_areas.slice(0, 3).map((area, index) => (
                    <li key={index} className="flex items-center">
                      <span className="w-1 h-1 bg-gray-400 rounded-full mr-2"></span>
                      {area}
                    </li>
                  ))}
                  {topic.focus_areas.length > 3 && (
                    <li className="text-gray-500">+{topic.focus_areas.length - 3} more</li>
                  )}
                </ul>
              </div>
              
              <button className="w-full bg-blue-600 text-white py-2 px-4 rounded-lg hover:bg-blue-700 transition-colors">
                Get Guidance
              </button>
            </div>
          ))}
        </div>
      )}
    </div>
  );

  const renderForm = () => (
    <div className="max-w-4xl mx-auto px-4 py-8">
      <div className="bg-white rounded-lg shadow-lg p-8">
        <div className="flex items-center mb-6">
          <button
            onClick={() => setCurrentStep('topics')}
            className="text-blue-600 hover:text-blue-800 mr-4"
          >
            ← Back to Topics
          </button>
          <h2 className="text-2xl font-bold text-gray-900">
            {selectedTopic?.name} - Advisory Request
          </h2>
        </div>

        <form onSubmit={handleFormSubmit} className="space-y-6">
          {/* Specific Focus */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Specific Focus Area *
            </label>
            <input
              type="text"
              required
              value={formData.specific_focus}
              onChange={(e) => handleInputChange('specific_focus', e.target.value)}
              placeholder="e.g., AI governance for financial services, IoT security for manufacturing"
              className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
            />
          </div>

          {/* Organization Context */}
          <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Industry</label>
              <select
                value={formData.organization_context.industry || ''}
                onChange={(e) => handleInputChange('organization_context.industry', e.target.value)}
                className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="">Select Industry</option>
                <option value="Technology">Technology</option>
                <option value="Finance">Finance</option>
                <option value="Healthcare">Healthcare</option>
                <option value="Manufacturing">Manufacturing</option>
                <option value="Retail">Retail</option>
                <option value="Government">Government</option>
                <option value="Education">Education</option>
                <option value="Energy">Energy</option>
                <option value="Other">Other</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Company Size</label>
              <select
                value={formData.organization_context.size || ''}
                onChange={(e) => handleInputChange('organization_context.size', e.target.value)}
                className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="">Select Size</option>
                <option value="Small (1-50)">Small (1-50)</option>
                <option value="Medium (51-500)">Medium (51-500)</option>
                <option value="Large (501-5000)">Large (501-5000)</option>
                <option value="Enterprise (5000+)">Enterprise (5000+)</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Current Maturity</label>
              <select
                value={formData.organization_context.current_maturity || ''}
                onChange={(e) => handleInputChange('organization_context.current_maturity', e.target.value)}
                className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="">Select Maturity</option>
                <option value="Initial">Initial</option>
                <option value="Developing">Developing</option>
                <option value="Defined">Defined</option>
                <option value="Managed">Managed</option>
                <option value="Optimized">Optimized</option>
              </select>
            </div>
          </div>

          {/* Current Challenges */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Current Challenges *
            </label>
            <textarea
              required
              placeholder="Enter challenges separated by commas (e.g., Lack of AI governance, Insufficient risk assessment processes, Limited emerging tech expertise)"
              value={formData.current_challenges.join(', ')}
              onChange={(e) => handleArrayInput('current_challenges', e.target.value)}
              className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              rows={3}
            />
          </div>

          {/* Desired Outcomes */}
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">
              Desired Outcomes *
            </label>
            <textarea
              required
              placeholder="Enter desired outcomes separated by commas (e.g., Establish AI governance framework, Reduce technology risks, Improve compliance posture)"
              value={formData.desired_outcomes.join(', ')}
              onChange={(e) => handleArrayInput('desired_outcomes', e.target.value)}
              className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              rows={3}
            />
          </div>

          {/* Timeline and Budget */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-4">
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Timeline *</label>
              <select
                required
                value={formData.timeline}
                onChange={(e) => handleInputChange('timeline', e.target.value)}
                className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="">Select Timeline</option>
                <option value="Immediate (0-3 months)">Immediate (0-3 months)</option>
                <option value="Short-term (3-6 months)">Short-term (3-6 months)</option>
                <option value="Medium-term (6-12 months)">Medium-term (6-12 months)</option>
                <option value="Long-term (12+ months)">Long-term (12+ months)</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Budget Constraints</label>
              <select
                value={formData.budget_constraints || ''}
                onChange={(e) => handleInputChange('budget_constraints', e.target.value)}
                className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
              >
                <option value="">Select Budget Level</option>
                <option value="Low">Low Budget</option>
                <option value="Medium">Medium Budget</option>
                <option value="High">High Budget</option>
                <option value="No constraints">No Budget Constraints</option>
              </select>
            </div>
          </div>

          <div className="flex justify-end space-x-4">
            <button
              type="button"
              onClick={() => setCurrentStep('topics')}
              className="px-6 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
            >
              Cancel
            </button>
            <button
              type="submit"
              disabled={loading}
              className="px-6 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
            >
              {loading ? 'Generating Plan...' : 'Generate Advisory Plan'}
            </button>
          </div>
        </form>
      </div>
    </div>
  );

  const renderResults = () => (
    <div className="max-w-6xl mx-auto px-4 py-8">
      <div className="bg-white rounded-lg shadow-lg p-8">
        <div className="flex items-center justify-between mb-6">
          <h2 className="text-2xl font-bold text-gray-900">
            {advisoryPlan?.topic} - Advisory Plan
          </h2>
          <div className="flex space-x-4">
            <button
              onClick={() => setCurrentStep('form')}
              className="px-4 py-2 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
            >
              Modify Request
            </button>
            <button
              onClick={() => setCurrentStep('topics')}
              className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
            >
              New Topic
            </button>
          </div>
        </div>

        {advisoryPlan && (
          <div className="space-y-8">
            {/* Executive Summary */}
            <div>
              <h3 className="text-xl font-semibold text-gray-900 mb-4">Executive Summary</h3>
              <div className="bg-blue-50 p-4 rounded-lg">
                <p className="text-gray-700 whitespace-pre-line">{advisoryPlan.executive_summary}</p>
              </div>
            </div>

            {/* Confidence Metrics */}
            <div className="bg-gray-50 p-4 rounded-lg">
              <h4 className="font-medium text-gray-900 mb-2">AI Confidence Metrics</h4>
              <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
                {Object.entries(advisoryPlan.confidence_metrics).map(([key, value]) => (
                  <div key={key} className="text-center">
                    <div className="text-2xl font-bold text-blue-600">
                      {typeof value === 'number' ? `${Math.round(value * 100)}%` : value}
                    </div>
                    <div className="text-sm text-gray-600 capitalize">
                      {key.replace('_', ' ')}
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Situation Analysis */}
            <div>
              <h3 className="text-xl font-semibold text-gray-900 mb-4">Situation Analysis</h3>
              <p className="text-gray-700 whitespace-pre-line">{advisoryPlan.situation_analysis}</p>
            </div>

            {/* Strategic Approach */}
            <div>
              <h3 className="text-xl font-semibold text-gray-900 mb-4">Strategic Approach</h3>
              <p className="text-gray-700 whitespace-pre-line">{advisoryPlan.strategic_approach}</p>
            </div>

            {/* Detailed Recommendations */}
            <div>
              <h3 className="text-xl font-semibold text-gray-900 mb-4">Detailed Recommendations</h3>
              <div className="space-y-6">
                {advisoryPlan.detailed_recommendations.map((rec, index) => (
                  <div key={index} className="border border-gray-200 rounded-lg p-6">
                    <div className="flex items-start justify-between mb-4">
                      <h4 className="text-lg font-semibold text-gray-900">{rec.title}</h4>
                      <div className="flex space-x-2">
                        <span className={`px-2 py-1 text-xs rounded-full ${
                          rec.estimated_cost === 'High' ? 'bg-red-100 text-red-800' :
                          rec.estimated_cost === 'Medium' ? 'bg-yellow-100 text-yellow-800' :
                          'bg-green-100 text-green-800'
                        }`}>
                          {rec.estimated_cost} Cost
                        </span>
                        <span className="px-2 py-1 text-xs rounded-full bg-blue-100 text-blue-800">
                          {Math.round(rec.confidence_score * 100)}% Confidence
                        </span>
                      </div>
                    </div>
                    
                    <p className="text-gray-700 mb-4">{rec.description}</p>
                    
                    <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                      <div>
                        <h5 className="font-medium text-gray-900 mb-2">Implementation Steps</h5>
                        <ul className="text-sm text-gray-700 space-y-1">
                          {rec.implementation_steps.map((step, stepIndex) => (
                            <li key={stepIndex} className="flex items-start">
                              <span className="text-blue-600 mr-2">{stepIndex + 1}.</span>
                              {step}
                            </li>
                          ))}
                        </ul>
                      </div>
                      
                      <div>
                        <h5 className="font-medium text-gray-900 mb-2">Success Metrics</h5>
                        <ul className="text-sm text-gray-700 space-y-1">
                          {rec.success_metrics.map((metric, metricIndex) => (
                            <li key={metricIndex} className="flex items-start">
                              <span className="text-green-600 mr-2">•</span>
                              {metric}
                            </li>
                          ))}
                        </ul>
                      </div>
                    </div>
                    
                    <div className="mt-4 pt-4 border-t border-gray-200">
                      <div className="flex flex-wrap gap-4 text-sm text-gray-600">
                        <span>Timeline: {rec.estimated_timeline}</span>
                        {rec.frameworks_referenced.length > 0 && (
                          <span>Frameworks: {rec.frameworks_referenced.join(', ')}</span>
                        )}
                      </div>
                    </div>
                  </div>
                ))}
              </div>
            </div>

            {/* Implementation Roadmap */}
            <div>
              <h3 className="text-xl font-semibold text-gray-900 mb-4">Implementation Roadmap</h3>
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                {Object.entries(advisoryPlan.implementation_roadmap).map(([phase, items]) => (
                  <div key={phase} className="bg-gray-50 p-4 rounded-lg">
                    <h4 className="font-medium text-gray-900 mb-3">{phase}</h4>
                    <ul className="space-y-2">
                      {items.map((item, index) => (
                        <li key={index} className="text-sm text-gray-700 flex items-start">
                          <span className="text-blue-600 mr-2">•</span>
                          {item}
                        </li>
                      ))}
                    </ul>
                  </div>
                ))}
              </div>
            </div>

            {/* Success Factors and Challenges */}
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Success Factors</h3>
                <ul className="space-y-2">
                  {advisoryPlan.success_factors.map((factor, index) => (
                    <li key={index} className="text-sm text-gray-700 flex items-start">
                      <span className="text-green-600 mr-2">✓</span>
                      {factor}
                    </li>
                  ))}
                </ul>
              </div>
              
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Potential Challenges</h3>
                <ul className="space-y-2">
                  {advisoryPlan.potential_challenges.map((challenge, index) => (
                    <li key={index} className="text-sm text-gray-700 flex items-start">
                      <span className="text-yellow-600 mr-2">⚠</span>
                      {challenge}
                    </li>
                  ))}
                </ul>
              </div>
            </div>

            {/* Next Steps */}
            <div>
              <h3 className="text-xl font-semibold text-gray-900 mb-4">Next Steps</h3>
              <div className="bg-green-50 p-4 rounded-lg">
                <ol className="space-y-2">
                  {advisoryPlan.next_steps.map((step, index) => (
                    <li key={index} className="text-gray-700 flex items-start">
                      <span className="text-green-600 font-medium mr-2">{index + 1}.</span>
                      {step}
                    </li>
                  ))}
                </ol>
              </div>
            </div>

            {/* Knowledge Sources */}
            {advisoryPlan.knowledge_sources.length > 0 && (
              <div>
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Knowledge Sources</h3>
                <div className="text-sm text-gray-600">
                  <p className="mb-2">This advisory plan was generated using insights from:</p>
                  <div className="flex flex-wrap gap-2">
                    {advisoryPlan.knowledge_sources.slice(0, 10).map((source, index) => (
                      <span key={index} className="bg-gray-100 px-2 py-1 rounded text-xs">
                        {source.split('/').pop()?.replace('.pdf', '') || source}
                      </span>
                    ))}
                    {advisoryPlan.knowledge_sources.length > 10 && (
                      <span className="text-gray-500">+{advisoryPlan.knowledge_sources.length - 10} more</span>
                    )}
                  </div>
                </div>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );

  return (
    <div className="min-h-screen bg-gray-50">
      {error && (
        <div className="bg-red-50 border border-red-200 rounded-lg p-4 mx-4 mt-4">
          <div className="text-red-800">{error}</div>
          <button
            onClick={() => setError(null)}
            className="text-red-600 hover:text-red-800 text-sm mt-2"
          >
            Dismiss
          </button>
        </div>
      )}

      {currentStep === 'topics' && renderTopicSelection()}
      {currentStep === 'form' && renderForm()}
      {currentStep === 'results' && renderResults()}
    </div>
  );
};

export default ChatPage;