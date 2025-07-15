import React, { useState, useEffect } from 'react';
import type { NextPage } from 'next';
import { useRouter } from 'next/router';

interface MetricsData {
  performance_score: number;
  assessments_completed: number;
  average_confidence: number;
  system_reliability: number;
  uptime_percentage: number;
  last_system_check: string;
  realtime_metrics: {
    cpu_usage: number;
    memory_usage: number;
    response_time: number;
    active_users: number;
    error_rate: number;
  };
  validation_results: {
    data_quality: number;
    model_accuracy: number;
    framework_compliance: number;
    security_coverage: number;
  };
}

const MetricsPage: NextPage = () => {
  const router = useRouter();
  const [metricsData, setMetricsData] = useState<MetricsData | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  useEffect(() => {
    fetchMetricsData();
  }, []);

  const fetchMetricsData = async () => {
    try {
      setIsLoading(true);
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const response = await fetch(`${apiUrl}/metrics/dashboard/realtime`);
      if (!response.ok) {
        throw new Error(`Failed to fetch metrics: ${response.status}`);
      }
      const data = await response.json();
      setMetricsData(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load metrics');
    } finally {
      setIsLoading(false);
    }
  };

  const getScoreColor = (score: number): string => {
    if (score >= 90) return 'text-green-400';
    if (score >= 70) return 'text-yellow-400';
    return 'text-red-400';
  };

  const getScoreBg = (score: number): string => {
    if (score >= 90) return 'bg-green-500/20 border-green-500/30';
    if (score >= 70) return 'bg-yellow-500/20 border-yellow-500/30';
    return 'bg-red-500/20 border-red-500/30';
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-950 to-gray-900 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-indigo-400 mx-auto mb-4"></div>
          <p className="text-white text-lg">Loading Performance Metrics...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-950 to-gray-900 flex items-center justify-center">
        <div className="text-center p-8 bg-red-900/50 rounded-lg max-w-md">
          <h2 className="text-red-400 text-xl font-bold mb-2">Error Loading Metrics</h2>
          <p className="text-red-300 mb-4">{error}</p>
          <button
            onClick={fetchMetricsData}
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

  if (!metricsData) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-950 to-gray-900 flex items-center justify-center">
        <p className="text-white text-lg">No metrics data available</p>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-950 to-gray-900 text-white">
      {/* Header */}
      <header className="p-6 bg-gray-900/80 backdrop-blur-md shadow-lg">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div>
            <h1 className="text-4xl font-bold bg-gradient-to-r from-indigo-400 to-purple-500 bg-clip-text text-transparent mb-2">
              Performance Metrics
            </h1>
            <p className="text-gray-300 text-lg">System performance tracking and analytics</p>
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
          {/* Key Performance Indicators */}
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6 mb-8">
            <div className={`p-6 rounded-lg border ${getScoreBg(metricsData.performance_score)}`}>
              <div className="flex items-center justify-between mb-2">
                <h3 className="text-lg font-semibold text-gray-300">Performance Score</h3>
                <span className="text-2xl">📊</span>
              </div>
              <div className={`text-3xl font-bold ${getScoreColor(metricsData.performance_score)}`}>
                {metricsData.performance_score}%
              </div>
              <p className="text-sm text-gray-400 mt-1">Overall system performance</p>
            </div>

            <div className={`p-6 rounded-lg border ${getScoreBg(metricsData.uptime_percentage)}`}>
              <div className="flex items-center justify-between mb-2">
                <h3 className="text-lg font-semibold text-gray-300">Uptime</h3>
                <span className="text-2xl">⏱️</span>
              </div>
              <div className={`text-3xl font-bold ${getScoreColor(metricsData.uptime_percentage)}`}>
                {metricsData.uptime_percentage}%
              </div>
              <p className="text-sm text-gray-400 mt-1">System availability</p>
            </div>

            <div className="p-6 rounded-lg border bg-blue-500/20 border-blue-500/30">
              <div className="flex items-center justify-between mb-2">
                <h3 className="text-lg font-semibold text-gray-300">Assessments</h3>
                <span className="text-2xl">📋</span>
              </div>
              <div className="text-3xl font-bold text-blue-400">
                {metricsData.assessments_completed}
              </div>
              <p className="text-sm text-gray-400 mt-1">Total completed</p>
            </div>

            <div className={`p-6 rounded-lg border ${getScoreBg(metricsData.system_reliability)}`}>
              <div className="flex items-center justify-between mb-2">
                <h3 className="text-lg font-semibold text-gray-300">Reliability</h3>
                <span className="text-2xl">🔧</span>
              </div>
              <div className={`text-3xl font-bold ${getScoreColor(metricsData.system_reliability)}`}>
                {metricsData.system_reliability}%
              </div>
              <p className="text-sm text-gray-400 mt-1">System reliability score</p>
            </div>
          </div>

          {/* Real-time Metrics */}
          {metricsData.realtime_metrics && (
            <div className="bg-gray-800/50 rounded-lg p-6 mb-8">
              <h2 className="text-2xl font-bold mb-6 flex items-center gap-2">
                <span>📈</span> Real-time System Metrics
              </h2>
              <div className="grid grid-cols-1 md:grid-cols-3 lg:grid-cols-5 gap-4">
                <div className="bg-gray-700/50 p-4 rounded-lg">
                  <h4 className="text-sm font-medium text-gray-300 mb-1">CPU Usage</h4>
                  <div className="text-2xl font-bold text-cyan-400">
                    {metricsData.realtime_metrics.cpu_usage}%
                  </div>
                </div>
                <div className="bg-gray-700/50 p-4 rounded-lg">
                  <h4 className="text-sm font-medium text-gray-300 mb-1">Memory Usage</h4>
                  <div className="text-2xl font-bold text-purple-400">
                    {metricsData.realtime_metrics.memory_usage}%
                  </div>
                </div>
                <div className="bg-gray-700/50 p-4 rounded-lg">
                  <h4 className="text-sm font-medium text-gray-300 mb-1">Response Time</h4>
                  <div className="text-2xl font-bold text-green-400">
                    {metricsData.realtime_metrics.response_time}ms
                  </div>
                </div>
                <div className="bg-gray-700/50 p-4 rounded-lg">
                  <h4 className="text-sm font-medium text-gray-300 mb-1">Active Users</h4>
                  <div className="text-2xl font-bold text-blue-400">
                    {metricsData.realtime_metrics.active_users}
                  </div>
                </div>
                <div className="bg-gray-700/50 p-4 rounded-lg">
                  <h4 className="text-sm font-medium text-gray-300 mb-1">Error Rate</h4>
                  <div className="text-2xl font-bold text-red-400">
                    {metricsData.realtime_metrics.error_rate}%
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Validation Results */}
          {metricsData.validation_results && (
            <div className="bg-gray-800/50 rounded-lg p-6">
              <h2 className="text-2xl font-bold mb-6 flex items-center gap-2">
                <span>✅</span> Validation Results
              </h2>
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                <div className="text-center">
                  <div className="w-24 h-24 mx-auto mb-4 relative">
                    <svg className="w-24 h-24 transform -rotate-90" viewBox="0 0 100 100">
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
                        strokeDashoffset={`${2 * Math.PI * 40 * (1 - metricsData.validation_results.data_quality / 100)}`}
                        className="text-green-500"
                      />
                    </svg>
                    <div className="absolute inset-0 flex items-center justify-center">
                      <span className="text-lg font-bold text-green-400">
                        {metricsData.validation_results.data_quality}%
                      </span>
                    </div>
                  </div>
                  <h4 className="font-semibold text-gray-300">Data Quality</h4>
                </div>

                <div className="text-center">
                  <div className="w-24 h-24 mx-auto mb-4 relative">
                    <svg className="w-24 h-24 transform -rotate-90" viewBox="0 0 100 100">
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
                        strokeDashoffset={`${2 * Math.PI * 40 * (1 - metricsData.validation_results.model_accuracy / 100)}`}
                        className="text-blue-500"
                      />
                    </svg>
                    <div className="absolute inset-0 flex items-center justify-center">
                      <span className="text-lg font-bold text-blue-400">
                        {metricsData.validation_results.model_accuracy}%
                      </span>
                    </div>
                  </div>
                  <h4 className="font-semibold text-gray-300">Model Accuracy</h4>
                </div>

                <div className="text-center">
                  <div className="w-24 h-24 mx-auto mb-4 relative">
                    <svg className="w-24 h-24 transform -rotate-90" viewBox="0 0 100 100">
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
                        strokeDashoffset={`${2 * Math.PI * 40 * (1 - metricsData.validation_results.framework_compliance / 100)}`}
                        className="text-purple-500"
                      />
                    </svg>
                    <div className="absolute inset-0 flex items-center justify-center">
                      <span className="text-lg font-bold text-purple-400">
                        {metricsData.validation_results.framework_compliance}%
                      </span>
                    </div>
                  </div>
                  <h4 className="font-semibold text-gray-300">Framework Compliance</h4>
                </div>

                <div className="text-center">
                  <div className="w-24 h-24 mx-auto mb-4 relative">
                    <svg className="w-24 h-24 transform -rotate-90" viewBox="0 0 100 100">
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
                        strokeDashoffset={`${2 * Math.PI * 40 * (1 - metricsData.validation_results.security_coverage / 100)}`}
                        className="text-yellow-500"
                      />
                    </svg>
                    <div className="absolute inset-0 flex items-center justify-center">
                      <span className="text-lg font-bold text-yellow-400">
                        {metricsData.validation_results.security_coverage}%
                      </span>
                    </div>
                  </div>
                  <h4 className="font-semibold text-gray-300">Security Coverage</h4>
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default MetricsPage;