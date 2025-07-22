import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import Link from 'next/link';

interface AssessmentResults {
  profile: any;
  questions: any;
  responses: Record<string, any>;
  scoring: {
    overall_score: number;
    risk_level: string;
    risk_color: string;
    section_breakdown: Array<{
      section_id: string;
      section_name: string;
      score: number;
      risk_level: string;
      weight: number;
      questions_answered: number;
      total_questions: number;
    }>;
    risk_categorization?: {
      confidence_interval: {
        lower_bound: number;
        upper_bound: number;
      };
      recommendations: string[];
    };
  };
  completedAt: string;
  totalQuestions: number;
  answeredQuestions: number;
}

const EnhancedReportsPage: React.FC = () => {
  const router = useRouter();
  const [results, setResults] = useState<AssessmentResults | null>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    loadResults();
  }, []);

  const loadResults = () => {
    try {
      const storedResults = sessionStorage.getItem('enhancedAssessmentResults');
      if (!storedResults) {
        setError('No assessment results found. Please complete an assessment first.');
        setLoading(false);
        return;
      }

      const parsedResults = JSON.parse(storedResults);
      setResults(parsedResults);
    } catch (err) {
      console.error('Error loading assessment results:', err);
      setError('Failed to load assessment results.');
    } finally {
      setLoading(false);
    }
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-xl text-gray-600">Loading assessment results...</p>
        </div>
      </div>
    );
  }

  if (error || !results) {
    return (
      <div className="min-h-screen bg-gray-50 py-12">
        <div className="max-w-4xl mx-auto px-4">
          <div className="bg-white rounded-lg shadow-lg p-8 text-center">
            <div className="text-red-600 mb-6">{error || 'No results available'}</div>
            <Link href="/enhanced-assessment">
              <a className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700">
                Start New Assessment
              </a>
            </Link>
          </div>
        </div>
      </div>
    );
  }

  const { scoring } = results;
  const completionRate = Math.round((results.answeredQuestions / results.totalQuestions) * 100);
  
  // Get risk color
  const getRiskColor = (riskLevel: string) => {
    const colors: Record<string, string> = {
      'Critical Risk': '#dc2626',
      'High Risk': '#ea580c',
      'Medium Risk': '#ca8a04',
      'Low Risk': '#16a34a'
    };
    return colors[riskLevel] || '#6b7280';
  };

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-6xl mx-auto px-4">
        {/* Header */}
        <div className="bg-white rounded-lg shadow-lg p-8 mb-6">
          <div className="flex flex-col md:flex-row justify-between items-start md:items-center mb-6">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 mb-2">
                Cybersecurity Risk Assessment Results
              </h1>
              <p className="text-gray-600">
                Completed on {new Date(results.completedAt).toLocaleDateString()} • 
                {completionRate}% Completion Rate
              </p>
            </div>
            
            <div className="mt-4 md:mt-0 flex items-center">
              <div className="text-center mr-6">
                <div className="text-4xl font-bold" style={{ color: getRiskColor(scoring.risk_level) }}>
                  {Math.round(scoring.overall_score)}%
                </div>
                <div className="text-sm font-medium" style={{ color: getRiskColor(scoring.risk_level) }}>
                  {scoring.risk_level}
                </div>
              </div>
              
              <button 
                onClick={() => window.print()}
                className="px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50"
              >
                Export Report
              </button>
            </div>
          </div>
          
          {/* Confidence Interval */}
          {scoring.risk_categorization?.confidence_interval && (
            <div className="bg-blue-50 border-l-4 border-blue-400 p-4">
              <div className="flex flex-col md:flex-row md:items-center">
                <div className="font-medium text-blue-800 mr-4">Statistical Confidence:</div>
                <div className="text-blue-700">
                  Your true security score is between 
                  <span className="font-bold mx-1">
                    {Math.round(scoring.risk_categorization.confidence_interval.lower_bound)}%
                  </span> 
                  and 
                  <span className="font-bold mx-1">
                    {Math.round(scoring.risk_categorization.confidence_interval.upper_bound)}%
                  </span> 
                  with 95% confidence
                </div>
              </div>
            </div>
          )}
        </div>
        
        {/* Domain Breakdown */}
        <div className="bg-white rounded-lg shadow-lg p-8">
          <h2 className="text-2xl font-bold text-gray-900 mb-6">Domain Breakdown</h2>
          
          <div className="space-y-6">
            {scoring.section_breakdown.map((section) => (
              <div key={section.section_id} className="border border-gray-200 rounded-lg overflow-hidden">
                <div className="flex items-center justify-between p-4 bg-gray-50">
                  <div>
                    <div className="font-medium text-gray-900">{section.section_name}</div>
                    <div className="text-sm text-gray-500">
                      Weight: {section.weight}% • {section.questions_answered}/{section.total_questions} Questions
                    </div>
                  </div>
                  <div className="text-right">
                    <div 
                      className="text-2xl font-bold" 
                      style={{ color: getRiskColor(section.risk_level) }}
                    >
                      {Math.round(section.score)}%
                    </div>
                    <div 
                      className="text-sm font-medium" 
                      style={{ color: getRiskColor(section.risk_level) }}
                    >
                      {section.risk_level}
                    </div>
                  </div>
                </div>
                
                <div className="h-2 w-full" style={{ backgroundColor: getRiskColor(section.risk_level) }}></div>
              </div>
            ))}
          </div>
        </div>

        {/* Action Buttons */}
        <div className="mt-8 flex justify-between">
          <Link href="/enhanced-assessment">
            <a className="px-6 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700">
              Start New Assessment
            </a>
          </Link>
          
          <button 
            onClick={() => window.print()}
            className="px-6 py-3 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
          >
            Export PDF Report
          </button>
        </div>
      </div>
    </div>
  );
};

export default EnhancedReportsPage;