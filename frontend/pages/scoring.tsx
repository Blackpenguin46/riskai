import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import Link from 'next/link';
import ScoringVisualization from '../components/ScoringVisualization';
import RealTimeScoringDisplay from '../components/RealTimeScoringDisplay';
import { calculateOverallScore, OverallScore, generateStrategicRecommendations } from '../lib/assessment-scoring';
import { ASSESSMENT_SECTIONS } from '../lib/assessment-questions';
import { getScoringMethodology } from '../lib/enhanced-assessment-api';

interface ScoringPageProps {}

const ScoringPage: React.FC<ScoringPageProps> = () => {
  const router = useRouter();
  const [overallScore, setOverallScore] = useState<OverallScore | null>(null);
  const [responses, setResponses] = useState<Record<string, Record<string, any>>>({});
  const [methodology, setMethodology] = useState<any>(null);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeDemo, setActiveDemo] = useState<'sample' | 'live' | 'comparison'>('sample');

  useEffect(() => {
    loadScoringData();
    loadMethodology();
  }, []);

  const loadScoringData = () => {
    try {
      // Try to load from session storage first
      const storedResponses = sessionStorage.getItem('assessmentResponses');
      const storedResults = sessionStorage.getItem('enhancedAssessmentResults');
      
      if (storedResults) {
        const results = JSON.parse(storedResults);
        setOverallScore(results.scoring);
        setResponses(results.responses || {});
      } else if (storedResponses) {
        const parsedResponses = JSON.parse(storedResponses);
        setResponses(parsedResponses);
        
        // Calculate score from responses
        const calculatedScore = calculateOverallScore(ASSESSMENT_SECTIONS, parsedResponses);
        setOverallScore(calculatedScore);
      } else {
        // Generate sample data for demonstration
        generateSampleData();
      }
    } catch (err) {
      console.error('Error loading scoring data:', err);
      generateSampleData();
    } finally {
      setLoading(false);
    }
  };

  const loadMethodology = async () => {
    try {
      const methodologyData = await getScoringMethodology();
      setMethodology(methodologyData);
    } catch (err) {
      console.error('Error loading methodology:', err);
    }
  };

  const generateSampleData = () => {
    // Generate sample responses for demonstration
    const sampleResponses: Record<string, Record<string, any>> = {};
    
    ASSESSMENT_SECTIONS.forEach(section => {
      sampleResponses[section.id] = {};
      section.questions.forEach((question, index) => {
        // Generate realistic sample answers
        switch (question.type) {
          case 'boolean':
            sampleResponses[section.id][question.id] = Math.random() > 0.3;
            break;
          case 'scale':
            const min = question.min || 1;
            const max = question.max || 5;
            sampleResponses[section.id][question.id] = Math.floor(Math.random() * (max - min + 1)) + min;
            break;
          case 'select':
            if (question.options && question.options.length > 0) {
              const randomIndex = Math.floor(Math.random() * question.options.length);
              sampleResponses[section.id][question.id] = question.options[randomIndex];
            }
            break;
          case 'multiselect':
            if (question.options && question.options.length > 0) {
              const numSelections = Math.floor(Math.random() * Math.min(3, question.options.length)) + 1;
              const selections = [];
              for (let i = 0; i < numSelections; i++) {
                const randomIndex = Math.floor(Math.random() * question.options.length);
                if (!selections.includes(question.options[randomIndex])) {
                  selections.push(question.options[randomIndex]);
                }
              }
              sampleResponses[section.id][question.id] = selections;
            }
            break;
          case 'text':
            sampleResponses[section.id][question.id] = `Sample response for ${question.id}`;
            break;
        }
      });
    });

    setResponses(sampleResponses);
    
    // Calculate score from sample responses
    const calculatedScore = calculateOverallScore(ASSESSMENT_SECTIONS, sampleResponses);
    setOverallScore(calculatedScore);
  };

  const handleScoreUpdate = (newScore: OverallScore) => {
    setOverallScore(newScore);
  };

  const exportScoringReport = () => {
    if (!overallScore) return;
    
    const reportData = {
      timestamp: new Date().toISOString(),
      overallScore,
      methodology,
      responses: Object.keys(responses).length > 0 ? responses : 'Sample data used for demonstration'
    };
    
    const blob = new Blob([JSON.stringify(reportData, null, 2)], { type: 'application/json' });
    const url = URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = `scoring-report-${new Date().toISOString().split('T')[0]}.json`;
    document.body.appendChild(a);
    a.click();
    document.body.removeChild(a);
    URL.revokeObjectURL(url);
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gray-50 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-xl text-gray-600">Loading scoring system...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gray-50 py-12">
        <div className="max-w-4xl mx-auto px-4">
          <div className="bg-white rounded-lg shadow-lg p-8 text-center">
            <div className="text-red-600 mb-6">{error}</div>
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

  return (
    <div className="min-h-screen bg-gray-50 py-8">
      <div className="max-w-7xl mx-auto px-4">
        {/* Header */}
        <div className="mb-8">
          <div className="flex flex-col md:flex-row justify-between items-start md:items-center">
            <div>
              <h1 className="text-3xl font-bold text-gray-900 mb-2">
                Mathematical Scoring System
              </h1>
              <p className="text-gray-600">
                Comprehensive risk assessment scoring with real-time calculations and detailed mathematical explanations
              </p>
            </div>
            
            <div className="mt-4 md:mt-0 flex space-x-3">
              <button
                onClick={exportScoringReport}
                className="px-4 py-2 border border-gray-300 rounded-lg text-gray-700 hover:bg-gray-50"
              >
                Export Report
              </button>
              <Link href="/enhanced-assessment">
                <a className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700">
                  New Assessment
                </a>
              </Link>
            </div>
          </div>
        </div>

        {/* Demo mode selector */}
        <div className="mb-6">
          <div className="bg-white rounded-lg shadow p-4">
            <div className="flex items-center space-x-4">
              <span className="text-sm font-medium text-gray-700">Demo Mode:</span>
              <div className="flex space-x-2">
                <button
                  onClick={() => setActiveDemo('sample')}
                  className={`px-3 py-1 rounded text-sm ${
                    activeDemo === 'sample'
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                  }`}
                >
                  Sample Data
                </button>
                <button
                  onClick={() => setActiveDemo('live')}
                  className={`px-3 py-1 rounded text-sm ${
                    activeDemo === 'live'
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                  }`}
                >
                  Live Scoring
                </button>
                <button
                  onClick={() => setActiveDemo('comparison')}
                  className={`px-3 py-1 rounded text-sm ${
                    activeDemo === 'comparison'
                      ? 'bg-blue-600 text-white'
                      : 'bg-gray-200 text-gray-700 hover:bg-gray-300'
                  }`}
                >
                  Comparison View
                </button>
              </div>
            </div>
          </div>
        </div>

        <div className="grid grid-cols-1 lg:grid-cols-3 gap-8">
          {/* Main scoring visualization */}
          <div className="lg:col-span-2">
            {overallScore && (
              <ScoringVisualization
                overallScore={overallScore}
                showMathematicalDetails={true}
                showRealTimeUpdates={activeDemo === 'live'}
                onScoreUpdate={handleScoreUpdate}
              />
            )}
          </div>

          {/* Sidebar with real-time updates and additional info */}
          <div className="space-y-6">
            {/* Real-time scoring display */}
            {activeDemo === 'live' && overallScore && (
              <RealTimeScoringDisplay
                responses={responses}
                onScoreUpdate={handleScoreUpdate}
                showProjectedScore={true}
              />
            )}

            {/* Quick stats */}
            {overallScore && (
              <div className="bg-white rounded-lg shadow p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Quick Stats</h3>
                <div className="space-y-3">
                  <div className="flex justify-between">
                    <span className="text-gray-600">Overall Score</span>
                    <span className="font-semibold">{Math.round(overallScore.percentage)}%</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Risk Level</span>
                    <span className="font-semibold" style={{ color: overallScore.riskColor }}>
                      {overallScore.riskLevel}
                    </span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Domains Assessed</span>
                    <span className="font-semibold">{overallScore.sectionBreakdown.length}</span>
                  </div>
                  <div className="flex justify-between">
                    <span className="text-gray-600">Confidence Range</span>
                    <span className="font-semibold text-sm">
                      {overallScore.confidenceInterval[0].toFixed(1)}% - {overallScore.confidenceInterval[1].toFixed(1)}%
                    </span>
                  </div>
                </div>
              </div>
            )}

            {/* Top recommendations */}
            {overallScore && (
              <div className="bg-white rounded-lg shadow p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Key Recommendations</h3>
                <div className="space-y-3">
                  {(() => {
                    const recommendations = generateStrategicRecommendations(responses, overallScore);
                    const allRecommendations = [
                      ...recommendations.immediate.slice(0, 2),
                      ...recommendations.shortTerm.slice(0, 2),
                      ...recommendations.strategic.slice(0, 1)
                    ];
                    
                    return allRecommendations.map((rec, index) => (
                      <div key={index} className="text-sm text-gray-700 p-2 bg-gray-50 rounded">
                        {rec}
                      </div>
                    ));
                  })()}
                </div>
                <div className="mt-4">
                  <Link href="/enhanced-reports">
                    <a className="text-blue-600 hover:text-blue-800 text-sm font-medium">
                      View Full Report →
                    </a>
                  </Link>
                </div>
              </div>
            )}

            {/* Methodology info */}
            {methodology && (
              <div className="bg-white rounded-lg shadow p-6">
                <h3 className="text-lg font-semibold text-gray-900 mb-4">Scoring Method</h3>
                <div className="space-y-2 text-sm text-gray-600">
                  <div>
                    <span className="font-medium">System:</span> {methodology.methodology?.name || 'RiskAI Mathematical Scoring'}
                  </div>
                  <div>
                    <span className="font-medium">Version:</span> {methodology.methodology?.version || '1.0'}
                  </div>
                  <div className="mt-3">
                    <div className="font-medium text-gray-700 mb-1">Key Formulas:</div>
                    <div className="text-xs bg-gray-50 p-2 rounded font-mono">
                      Section Score = Σ(Q×W) / ΣW × 100
                    </div>
                    <div className="text-xs bg-gray-50 p-2 rounded font-mono mt-1">
                      Overall = Σ(Section × Weight)
                    </div>
                  </div>
                </div>
              </div>
            )}
          </div>
        </div>

        {/* Comparison view */}
        {activeDemo === 'comparison' && overallScore && (
          <div className="mt-8">
            <div className="bg-white rounded-lg shadow p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-6">Score Comparison</h3>
              
              <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                <div className="text-center p-4 border border-gray-200 rounded-lg">
                  <div className="text-2xl font-bold mb-2" style={{ color: overallScore.riskColor }}>
                    {Math.round(overallScore.percentage)}%
                  </div>
                  <div className="text-sm font-medium text-gray-900">Your Score</div>
                  <div className="text-xs text-gray-500 mt-1">{overallScore.riskLevel}</div>
                </div>
                
                <div className="text-center p-4 border border-gray-200 rounded-lg">
                  <div className="text-2xl font-bold text-yellow-600 mb-2">65%</div>
                  <div className="text-sm font-medium text-gray-900">Industry Average</div>
                  <div className="text-xs text-gray-500 mt-1">Medium Risk</div>
                </div>
                
                <div className="text-center p-4 border border-gray-200 rounded-lg">
                  <div className="text-2xl font-bold text-green-600 mb-2">85%</div>
                  <div className="text-sm font-medium text-gray-900">Best Practice</div>
                  <div className="text-xs text-gray-500 mt-1">Low Risk</div>
                </div>
              </div>
              
              <div className="mt-6">
                <div className="text-sm text-gray-600 mb-2">Performance vs Benchmarks</div>
                <div className="w-full bg-gray-200 rounded-full h-4 relative">
                  <div className="absolute inset-0 flex">
                    <div className="bg-red-400 h-full" style={{ width: '40%' }}></div>
                    <div className="bg-yellow-400 h-full" style={{ width: '25%' }}></div>
                    <div className="bg-green-400 h-full" style={{ width: '35%' }}></div>
                  </div>
                  
                  {/* Your score marker */}
                  <div
                    className="absolute top-0 w-1 h-full bg-black"
                    style={{ left: `${overallScore.percentage}%` }}
                  ></div>
                  
                  {/* Industry average marker */}
                  <div
                    className="absolute top-0 w-1 h-full bg-yellow-600"
                    style={{ left: '65%' }}
                  ></div>
                  
                  {/* Best practice marker */}
                  <div
                    className="absolute top-0 w-1 h-full bg-green-600"
                    style={{ left: '85%' }}
                  ></div>
                </div>
                <div className="flex justify-between text-xs text-gray-500 mt-1">
                  <span>Critical</span>
                  <span>High</span>
                  <span>Medium</span>
                  <span>Low</span>
                </div>
              </div>
            </div>
          </div>
        )}
      </div>
    </div>
  );
};

export default ScoringPage;