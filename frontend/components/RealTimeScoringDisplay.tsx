import React, { useState, useEffect } from 'react';
import { calculateOverallScore, calculateSectionScore, OverallScore, SectionScore, getRiskColor } from '../lib/assessment-scoring';
import { ASSESSMENT_SECTIONS, Question } from '../lib/assessment-questions';

interface RealTimeScoringDisplayProps {
  responses: Record<string, Record<string, any>>;
  currentSection?: string;
  currentQuestion?: string;
  onScoreUpdate?: (score: OverallScore) => void;
  showProjectedScore?: boolean;
}

const RealTimeScoringDisplay: React.FC<RealTimeScoringDisplayProps> = ({
  responses,
  currentSection,
  currentQuestion,
  onScoreUpdate,
  showProjectedScore = true
}) => {
  const [currentScore, setCurrentScore] = useState<OverallScore | null>(null);
  const [previousScore, setPreviousScore] = useState<OverallScore | null>(null);
  const [scoreHistory, setScoreHistory] = useState<{ timestamp: Date; score: number }[]>([]);

  // Calculate current score whenever responses change
  useEffect(() => {
    try {
      const newScore = calculateOverallScore(ASSESSMENT_SECTIONS, responses);
      
      // Update score history
      setScoreHistory(prev => [
        ...prev.slice(-19), // Keep last 20 entries
        { timestamp: new Date(), score: newScore.percentage }
      ]);
      
      setPreviousScore(currentScore);
      setCurrentScore(newScore);
      
      if (onScoreUpdate) {
        onScoreUpdate(newScore);
      }
    } catch (error) {
      console.error('Error calculating real-time score:', error);
    }
  }, [responses, onScoreUpdate]);

  // Calculate completion statistics
  const getCompletionStats = () => {
    const totalQuestions = ASSESSMENT_SECTIONS.reduce((sum, section) => sum + section.questions.length, 0);
    const answeredQuestions = Object.values(responses).reduce((sum, sectionResponses) => {
      return sum + Object.values(sectionResponses).filter(response => 
        response !== null && response !== undefined && response !== ''
      ).length;
    }, 0);
    
    return {
      totalQuestions,
      answeredQuestions,
      completionRate: (answeredQuestions / totalQuestions) * 100
    };
  };

  // Calculate projected final score based on current performance
  const getProjectedScore = () => {
    if (!currentScore) return null;
    
    const stats = getCompletionStats();
    if (stats.answeredQuestions === 0) return null;
    
    // Simple projection: assume remaining questions will be answered at current average performance
    const currentAverage = currentScore.percentage;
    const projectedScore = currentAverage; // Could be more sophisticated
    
    return {
      projected: projectedScore,
      confidence: Math.min(stats.completionRate / 100, 0.95) // Max 95% confidence
    };
  };

  // Mini score gauge component
  const MiniScoreGauge: React.FC<{ score: number; size?: number }> = ({ score, size = 60 }) => {
    const radius = size / 2 - 4;
    const circumference = radius * 2 * Math.PI;
    const strokeDasharray = `${(score / 100) * circumference} ${circumference}`;
    
    return (
      <div className="relative" style={{ width: size, height: size }}>
        <svg width={size} height={size} className="transform -rotate-90">
          <circle
            stroke="#e5e7eb"
            fill="transparent"
            strokeWidth="3"
            r={radius}
            cx={size / 2}
            cy={size / 2}
          />
          <circle
            stroke={getRiskColor(currentScore?.riskLevel || 'Critical Risk')}
            fill="transparent"
            strokeWidth="3"
            strokeDasharray={strokeDasharray}
            strokeLinecap="round"
            r={radius}
            cx={size / 2}
            cy={size / 2}
            style={{ transition: 'stroke-dasharray 0.5s ease-in-out' }}
          />
        </svg>
        <div className="absolute inset-0 flex items-center justify-center">
          <span className="text-xs font-bold" style={{ color: getRiskColor(currentScore?.riskLevel || 'Critical Risk') }}>
            {Math.round(score)}%
          </span>
        </div>
      </div>
    );
  };

  // Score trend indicator
  const ScoreTrendIndicator: React.FC = () => {
    if (!currentScore || !previousScore) return null;
    
    const change = currentScore.percentage - previousScore.percentage;
    const isPositive = change > 0;
    const isNeutral = Math.abs(change) < 0.1;
    
    if (isNeutral) return null;
    
    return (
      <div className={`flex items-center text-xs ${isPositive ? 'text-green-600' : 'text-red-600'}`}>
        <svg className="w-3 h-3 mr-1" fill="currentColor" viewBox="0 0 20 20">
          {isPositive ? (
            <path fillRule="evenodd" d="M3.293 9.707a1 1 0 010-1.414l6-6a1 1 0 011.414 0l6 6a1 1 0 01-1.414 1.414L11 5.414V17a1 1 0 11-2 0V5.414L4.707 9.707a1 1 0 01-1.414 0z" clipRule="evenodd" />
          ) : (
            <path fillRule="evenodd" d="M16.707 10.293a1 1 0 010 1.414l-6 6a1 1 0 01-1.414 0l-6-6a1 1 0 111.414-1.414L9 14.586V3a1 1 0 012 0v11.586l4.293-4.293a1 1 0 011.414 0z" clipRule="evenodd" />
          )}
        </svg>
        {isPositive ? '+' : ''}{change.toFixed(1)}%
      </div>
    );
  };

  // Section progress bars
  const SectionProgressBars: React.FC = () => {
    if (!currentScore) return null;
    
    return (
      <div className="space-y-2">
        {currentScore.sectionBreakdown.map((section) => (
          <div key={section.sectionId} className="flex items-center space-x-2">
            <div className="w-20 text-xs text-gray-600 truncate" title={section.sectionName}>
              {section.sectionName.split(' ')[0]}
            </div>
            <div className="flex-1 bg-gray-200 rounded-full h-2">
              <div
                className="h-2 rounded-full transition-all duration-500"
                style={{
                  width: `${section.percentage}%`,
                  backgroundColor: getRiskColor(section.riskLevel)
                }}
              ></div>
            </div>
            <div className="w-12 text-xs text-right font-medium">
              {Math.round(section.percentage)}%
            </div>
          </div>
        ))}
      </div>
    );
  };

  const stats = getCompletionStats();
  const projectedScore = getProjectedScore();

  if (!currentScore) {
    return (
      <div className="bg-white rounded-lg shadow p-4">
        <div className="text-center text-gray-500">
          <div className="animate-pulse">Calculating score...</div>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-lg p-4 space-y-4">
      {/* Header with current score */}
      <div className="flex items-center justify-between">
        <div>
          <h3 className="text-lg font-semibold text-gray-900">Current Score</h3>
          <p className="text-sm text-gray-600">
            {stats.answeredQuestions} of {stats.totalQuestions} questions answered
          </p>
        </div>
        <div className="flex items-center space-x-3">
          <MiniScoreGauge score={currentScore.percentage} />
          <div className="text-right">
            <div className="text-2xl font-bold" style={{ color: getRiskColor(currentScore.riskLevel) }}>
              {Math.round(currentScore.percentage)}%
            </div>
            <div className="text-sm font-medium" style={{ color: getRiskColor(currentScore.riskLevel) }}>
              {currentScore.riskLevel}
            </div>
            <ScoreTrendIndicator />
          </div>
        </div>
      </div>

      {/* Progress bar */}
      <div className="space-y-2">
        <div className="flex justify-between text-sm text-gray-600">
          <span>Assessment Progress</span>
          <span>{Math.round(stats.completionRate)}% Complete</span>
        </div>
        <div className="w-full bg-gray-200 rounded-full h-2">
          <div
            className="bg-blue-600 h-2 rounded-full transition-all duration-500"
            style={{ width: `${stats.completionRate}%` }}
          ></div>
        </div>
      </div>

      {/* Projected score */}
      {showProjectedScore && projectedScore && stats.completionRate > 10 && (
        <div className="bg-blue-50 border border-blue-200 rounded-lg p-3">
          <div className="flex items-center justify-between">
            <div>
              <div className="text-sm font-medium text-blue-900">Projected Final Score</div>
              <div className="text-xs text-blue-700">
                Based on current performance ({Math.round(projectedScore.confidence * 100)}% confidence)
              </div>
            </div>
            <div className="text-right">
              <div className="text-xl font-bold text-blue-900">
                {Math.round(projectedScore.projected)}%
              </div>
              <div className="text-xs text-blue-700">
                ±{Math.round((1 - projectedScore.confidence) * 10)}%
              </div>
            </div>
          </div>
        </div>
      )}

      {/* Section breakdown */}
      <div>
        <h4 className="text-sm font-medium text-gray-900 mb-2">Domain Scores</h4>
        <SectionProgressBars />
      </div>

      {/* Current section highlight */}
      {currentSection && (
        <div className="bg-yellow-50 border border-yellow-200 rounded-lg p-3">
          <div className="text-sm font-medium text-yellow-900">
            Currently Working On
          </div>
          <div className="text-sm text-yellow-800">
            {ASSESSMENT_SECTIONS.find(s => s.id === currentSection)?.name || currentSection}
          </div>
          {currentQuestion && (
            <div className="text-xs text-yellow-700 mt-1">
              Question: {currentQuestion}
            </div>
          )}
        </div>
      )}

      {/* Mathematical impact preview */}
      <div className="text-xs text-gray-500 border-t pt-2">
        <div>Confidence Interval: [{currentScore.confidenceInterval[0].toFixed(1)}%, {currentScore.confidenceInterval[1].toFixed(1)}%]</div>
        <div>Score updates in real-time as you answer questions</div>
      </div>
    </div>
  );
};

export default RealTimeScoringDisplay;