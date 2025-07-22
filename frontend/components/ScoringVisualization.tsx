import React, { useState, useEffect } from 'react';
import { OverallScore, SectionScore, getRiskColor } from '../lib/assessment-scoring';

interface ScoringVisualizationProps {
  overallScore: OverallScore;
  showMathematicalDetails?: boolean;
  showRealTimeUpdates?: boolean;
  onScoreUpdate?: (score: OverallScore) => void;
}

const ScoringVisualization: React.FC<ScoringVisualizationProps> = ({
  overallScore,
  showMathematicalDetails = false,
  showRealTimeUpdates = false,
  onScoreUpdate
}) => {
  const [activeTab, setActiveTab] = useState<'overview' | 'breakdown' | 'methodology'>('overview');
  const [animatedScore, setAnimatedScore] = useState(0);

  // Animate score on mount
  useEffect(() => {
    const timer = setTimeout(() => {
      setAnimatedScore(overallScore.percentage);
    }, 100);
    return () => clearTimeout(timer);
  }, [overallScore.percentage]);

  // Score gauge component
  const ScoreGauge: React.FC<{ score: number; size?: 'small' | 'large' }> = ({ score, size = 'large' }) => {
    const radius = size === 'large' ? 80 : 40;
    const strokeWidth = size === 'large' ? 8 : 4;
    const normalizedRadius = radius - strokeWidth * 2;
    const circumference = normalizedRadius * 2 * Math.PI;
    const strokeDasharray = `${(score / 100) * circumference} ${circumference}`;
    
    return (
      <div className={`relative ${size === 'large' ? 'w-48 h-48' : 'w-24 h-24'}`}>
        <svg
          className="transform -rotate-90 w-full h-full"
          width={radius * 2}
          height={radius * 2}
        >
          {/* Background circle */}
          <circle
            stroke="#e5e7eb"
            fill="transparent"
            strokeWidth={strokeWidth}
            r={normalizedRadius}
            cx={radius}
            cy={radius}
          />
          {/* Progress circle */}
          <circle
            stroke={getRiskColor(overallScore.riskLevel)}
            fill="transparent"
            strokeWidth={strokeWidth}
            strokeDasharray={strokeDasharray}
            strokeLinecap="round"
            r={normalizedRadius}
            cx={radius}
            cy={radius}
            style={{
              transition: 'stroke-dasharray 1s ease-in-out',
            }}
          />
        </svg>
        <div className="absolute inset-0 flex items-center justify-center">
          <div className="text-center">
            <div className={`font-bold ${size === 'large' ? 'text-3xl' : 'text-lg'}`} style={{ color: getRiskColor(overallScore.riskLevel) }}>
              {Math.round(animatedScore)}%
            </div>
            <div className={`text-gray-600 ${size === 'large' ? 'text-sm' : 'text-xs'}`}>
              {overallScore.riskLevel}
            </div>
          </div>
        </div>
      </div>
    );
  };

  // Section breakdown chart
  const SectionBreakdownChart: React.FC = () => {
    return (
      <div className="space-y-4">
        {overallScore.sectionBreakdown.map((section) => (
          <div key={section.sectionId} className="bg-white border border-gray-200 rounded-lg p-4">
            <div className="flex items-center justify-between mb-3">
              <div>
                <h4 className="font-medium text-gray-900">{section.sectionName}</h4>
                <p className="text-sm text-gray-500">
                  Weight: {section.weight}% • {section.questionsAnswered}/{section.totalQuestions} Questions
                </p>
              </div>
              <div className="text-right">
                <div className="text-2xl font-bold" style={{ color: getRiskColor(section.riskLevel) }}>
                  {Math.round(section.percentage)}%
                </div>
                <div className="text-sm font-medium" style={{ color: getRiskColor(section.riskLevel) }}>
                  {section.riskLevel}
                </div>
              </div>
            </div>
            
            {/* Progress bar */}
            <div className="w-full bg-gray-200 rounded-full h-3 mb-2">
              <div
                className="h-3 rounded-full transition-all duration-1000 ease-out"
                style={{
                  width: `${section.percentage}%`,
                  backgroundColor: getRiskColor(section.riskLevel)
                }}
              ></div>
            </div>
            
            {/* Mathematical breakdown */}
            {showMathematicalDetails && (
              <div className="mt-3 p-3 bg-gray-50 rounded text-sm">
                <div className="font-medium text-gray-700 mb-1">Mathematical Calculation:</div>
                <div className="text-gray-600">
                  Section Score = ({section.score.toFixed(1)} / {section.maxScore}) × 100 = {section.percentage.toFixed(2)}%
                </div>
                <div className="text-gray-600">
                  Weighted Contribution = {section.percentage.toFixed(2)}% × {section.weight}% = {((section.percentage * section.weight) / 100).toFixed(2)}%
                </div>
              </div>
            )}
          </div>
        ))}
      </div>
    );
  };

  // Mathematical methodology display
  const MethodologyDisplay: React.FC = () => {
    const totalWeightedScore = overallScore.sectionBreakdown.reduce(
      (sum, section) => sum + (section.percentage * section.weight) / 100,
      0
    );

    return (
      <div className="space-y-6">
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-blue-900 mb-4">Scoring Methodology</h3>
          
          <div className="space-y-4">
            <div>
              <h4 className="font-medium text-blue-800 mb-2">Section Score Formula</h4>
              <div className="bg-white p-3 rounded border font-mono text-sm">
                Section Score = Σ(Question Score × Question Weight) / Σ(Question Weights) × 100
              </div>
            </div>
            
            <div>
              <h4 className="font-medium text-blue-800 mb-2">Overall Score Formula</h4>
              <div className="bg-white p-3 rounded border font-mono text-sm">
                Overall Score = Σ(Section Score × Section Weight)
              </div>
            </div>
            
            <div>
              <h4 className="font-medium text-blue-800 mb-2">Confidence Interval</h4>
              <div className="bg-white p-3 rounded border font-mono text-sm">
                CI = Score ± (1 - Completion Rate) × 10%
              </div>
              <div className="text-sm text-blue-700 mt-1">
                Current CI: [{overallScore.confidenceInterval[0].toFixed(1)}%, {overallScore.confidenceInterval[1].toFixed(1)}%]
              </div>
            </div>
          </div>
        </div>

        <div className="bg-gray-50 border border-gray-200 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-gray-900 mb-4">Calculation Breakdown</h3>
          
          <div className="space-y-3">
            {overallScore.sectionBreakdown.map((section) => (
              <div key={section.sectionId} className="flex justify-between items-center py-2 border-b border-gray-200 last:border-b-0">
                <div className="text-gray-700">{section.sectionName}</div>
                <div className="text-right text-sm">
                  <div>{section.percentage.toFixed(2)}% × {section.weight}% = {((section.percentage * section.weight) / 100).toFixed(2)}%</div>
                </div>
              </div>
            ))}
            <div className="flex justify-between items-center py-2 font-semibold border-t-2 border-gray-300">
              <div className="text-gray-900">Total Weighted Score</div>
              <div className="text-gray-900">{totalWeightedScore.toFixed(2)}%</div>
            </div>
          </div>
        </div>

        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-6">
          <h3 className="text-lg font-semibold text-yellow-900 mb-4">Risk Level Thresholds</h3>
          
          <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
            <div className="text-center p-3 bg-red-100 rounded">
              <div className="font-semibold text-red-800">Critical Risk</div>
              <div className="text-red-600">0-40%</div>
            </div>
            <div className="text-center p-3 bg-orange-100 rounded">
              <div className="font-semibold text-orange-800">High Risk</div>
              <div className="text-orange-600">41-60%</div>
            </div>
            <div className="text-center p-3 bg-yellow-100 rounded">
              <div className="font-semibold text-yellow-800">Medium Risk</div>
              <div className="text-yellow-600">61-80%</div>
            </div>
            <div className="text-center p-3 bg-green-100 rounded">
              <div className="font-semibold text-green-800">Low Risk</div>
              <div className="text-green-600">81-100%</div>
            </div>
          </div>
        </div>
      </div>
    );
  };

  return (
    <div className="bg-white rounded-lg shadow-lg">
      {/* Header with score gauge */}
      <div className="p-6 border-b border-gray-200">
        <div className="flex flex-col lg:flex-row items-center justify-between">
          <div className="mb-6 lg:mb-0">
            <h2 className="text-2xl font-bold text-gray-900 mb-2">Assessment Score</h2>
            <p className="text-gray-600">
              Mathematical scoring with {overallScore.sectionBreakdown.length} security domains
            </p>
          </div>
          
          <div className="flex items-center space-x-8">
            <ScoreGauge score={animatedScore} />
            
            <div className="text-center">
              <div className="text-sm text-gray-500 mb-1">Confidence Interval</div>
              <div className="text-lg font-semibold text-gray-900">
                {overallScore.confidenceInterval[0].toFixed(1)}% - {overallScore.confidenceInterval[1].toFixed(1)}%
              </div>
              <div className="text-sm text-gray-500 mt-1">95% Confidence</div>
            </div>
          </div>
        </div>
      </div>

      {/* Navigation tabs */}
      <div className="border-b border-gray-200">
        <nav className="-mb-px flex">
          <button
            onClick={() => setActiveTab('overview')}
            className={`py-4 px-6 font-medium text-sm ${
              activeTab === 'overview'
                ? 'border-b-2 border-blue-500 text-blue-600'
                : 'text-gray-500 hover:text-gray-700'
            }`}
          >
            Overview
          </button>
          <button
            onClick={() => setActiveTab('breakdown')}
            className={`py-4 px-6 font-medium text-sm ${
              activeTab === 'breakdown'
                ? 'border-b-2 border-blue-500 text-blue-600'
                : 'text-gray-500 hover:text-gray-700'
            }`}
          >
            Domain Breakdown
          </button>
          <button
            onClick={() => setActiveTab('methodology')}
            className={`py-4 px-6 font-medium text-sm ${
              activeTab === 'methodology'
                ? 'border-b-2 border-blue-500 text-blue-600'
                : 'text-gray-500 hover:text-gray-700'
            }`}
          >
            Mathematical Details
          </button>
        </nav>
      </div>

      {/* Tab content */}
      <div className="p-6">
        {activeTab === 'overview' && (
          <div className="space-y-6">
            {/* Key metrics */}
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="bg-gray-50 rounded-lg p-6 text-center">
                <div className="text-3xl font-bold mb-2" style={{ color: getRiskColor(overallScore.riskLevel) }}>
                  {Math.round(overallScore.percentage)}%
                </div>
                <div className="text-gray-600">Overall Score</div>
                <div className="text-sm font-medium mt-1" style={{ color: getRiskColor(overallScore.riskLevel) }}>
                  {overallScore.riskLevel}
                </div>
              </div>
              
              <div className="bg-gray-50 rounded-lg p-6 text-center">
                <div className="text-3xl font-bold text-green-600 mb-2">
                  {Math.round(Math.max(...overallScore.sectionBreakdown.map(s => s.percentage)))}%
                </div>
                <div className="text-gray-600">Strongest Domain</div>
                <div className="text-sm font-medium text-gray-800 mt-1">
                  {overallScore.sectionBreakdown.find(s => s.percentage === Math.max(...overallScore.sectionBreakdown.map(s => s.percentage)))?.sectionName}
                </div>
              </div>
              
              <div className="bg-gray-50 rounded-lg p-6 text-center">
                <div className="text-3xl font-bold text-red-600 mb-2">
                  {Math.round(Math.min(...overallScore.sectionBreakdown.map(s => s.percentage)))}%
                </div>
                <div className="text-gray-600">Weakest Domain</div>
                <div className="text-sm font-medium text-gray-800 mt-1">
                  {overallScore.sectionBreakdown.find(s => s.percentage === Math.min(...overallScore.sectionBreakdown.map(s => s.percentage)))?.sectionName}
                </div>
              </div>
            </div>

            {/* Risk level visualization */}
            <div className="bg-gray-50 rounded-lg p-6">
              <h3 className="text-lg font-semibold text-gray-900 mb-4">Risk Level Distribution</h3>
              <div className="w-full h-4 bg-gray-200 rounded-full mb-4 relative overflow-hidden">
                <div className="absolute inset-0 flex">
                  <div className="bg-red-500 h-full" style={{ width: '40%' }}></div>
                  <div className="bg-orange-500 h-full" style={{ width: '20%' }}></div>
                  <div className="bg-yellow-500 h-full" style={{ width: '20%' }}></div>
                  <div className="bg-green-500 h-full" style={{ width: '20%' }}></div>
                </div>
                <div
                  className="absolute top-0 w-1 h-full bg-black"
                  style={{ left: `${overallScore.percentage}%` }}
                ></div>
              </div>
              <div className="flex justify-between text-sm text-gray-600">
                <span>Critical (0-40%)</span>
                <span>High (41-60%)</span>
                <span>Medium (61-80%)</span>
                <span>Low (81-100%)</span>
              </div>
            </div>
          </div>
        )}

        {activeTab === 'breakdown' && <SectionBreakdownChart />}
        {activeTab === 'methodology' && <MethodologyDisplay />}
      </div>
    </div>
  );
};

export default ScoringVisualization;