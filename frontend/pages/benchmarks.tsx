import React, { useState, useEffect } from 'react';
import type { NextPage } from 'next';
import { useRouter } from 'next/router';

interface BenchmarkTool {
  name: string;
  score: number;
  price_per_month: number;
  assessment_time: string;
  pros: string[];
  cons: string[];
  market_share: number;
  customer_rating: number;
}

interface ROIData {
  company_size: string;
  annual_savings: number;
  implementation_cost: number;
  payback_period_months: number;
  five_year_roi: number;
  efficiency_gain: number;
}

interface BenchmarkData {
  tools_comparison: BenchmarkTool[];
  competitive_analysis: {
    riskai_advantages: string[];
    market_position: string;
    unique_features: string[];
  };
  roi_analysis: ROIData[];
  market_trends: {
    growth_rate: number;
    market_size: string;
    adoption_rate: number;
  };
}

const BenchmarksPage: NextPage = () => {
  const router = useRouter();
  const [benchmarkData, setBenchmarkData] = useState<BenchmarkData | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedCompanySize, setSelectedCompanySize] = useState<string>('medium');

  useEffect(() => {
    fetchBenchmarkData();
  }, []);

  const fetchBenchmarkData = async () => {
    try {
      setIsLoading(true);
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const response = await fetch(`${apiUrl}/benchmarks/realtime`);
      if (!response.ok) {
        throw new Error(`Failed to fetch benchmarks: ${response.status}`);
      }
      const data = await response.json();
      setBenchmarkData(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load benchmarks');
    } finally {
      setIsLoading(false);
    }
  };

  const getScoreColor = (score: number): string => {
    if (score >= 90) return 'text-green-400';
    if (score >= 80) return 'text-blue-400';
    if (score >= 70) return 'text-yellow-400';
    return 'text-red-400';
  };

  // Removed unused function getScoreBg

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-950 to-gray-900 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-indigo-400 mx-auto mb-4"></div>
          <p className="text-white text-lg">Loading GRC Benchmarks...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-950 to-gray-900 flex items-center justify-center">
        <div className="text-center p-8 bg-red-900/50 rounded-lg max-w-md">
          <h2 className="text-red-400 text-xl font-bold mb-2">Error Loading Benchmarks</h2>
          <p className="text-red-300 mb-4">{error}</p>
          <button
            onClick={fetchBenchmarkData}
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

  if (!benchmarkData) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-950 to-gray-900 flex items-center justify-center">
        <p className="text-white text-lg">No benchmark data available</p>
      </div>
    );
  }

  const selectedROI = benchmarkData.roi_analysis.find(roi => roi.company_size === selectedCompanySize);

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-950 to-gray-900 text-white">
      {/* Header */}
      <header className="p-6 bg-gray-900/80 backdrop-blur-md shadow-lg">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div>
            <h1 className="text-4xl font-bold bg-gradient-to-r from-indigo-400 to-purple-500 bg-clip-text text-transparent mb-2">
              GRC Benchmarking
            </h1>
            <p className="text-gray-300 text-lg">Compare against major GRC tools and industry benchmarks</p>
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
          {/* Market Overview */}
          <div className="bg-gray-800/50 rounded-lg p-6 mb-8">
            <h2 className="text-2xl font-bold mb-6 flex items-center gap-2">
              <span>📊</span> Market Overview
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
              <div className="bg-gradient-to-r from-blue-600/20 to-purple-600/20 p-6 rounded-lg border border-blue-500/30">
                <h3 className="text-lg font-semibold text-blue-300 mb-2">Market Growth</h3>
                <div className="text-3xl font-bold text-blue-400">{benchmarkData.market_trends.growth_rate}%</div>
                <p className="text-sm text-gray-400">Annual growth rate</p>
              </div>
              <div className="bg-gradient-to-r from-green-600/20 to-emerald-600/20 p-6 rounded-lg border border-green-500/30">
                <h3 className="text-lg font-semibold text-green-300 mb-2">Market Size</h3>
                <div className="text-3xl font-bold text-green-400">{benchmarkData.market_trends.market_size}</div>
                <p className="text-sm text-gray-400">Total addressable market</p>
              </div>
              <div className="bg-gradient-to-r from-yellow-600/20 to-orange-600/20 p-6 rounded-lg border border-yellow-500/30">
                <h3 className="text-lg font-semibold text-yellow-300 mb-2">Adoption Rate</h3>
                <div className="text-3xl font-bold text-yellow-400">{benchmarkData.market_trends.adoption_rate}%</div>
                <p className="text-sm text-gray-400">Enterprise adoption</p>
              </div>
            </div>
          </div>

          {/* Tools Comparison */}
          <div className="bg-gray-800/50 rounded-lg p-6 mb-8">
            <h2 className="text-2xl font-bold mb-6 flex items-center gap-2">
              <span>⚖️</span> Competitive Analysis
            </h2>
            <div className="overflow-x-auto">
              <table className="w-full min-w-full">
                <thead>
                  <tr className="border-b border-gray-600">
                    <th className="text-left py-4 px-4 font-semibold text-gray-300">Tool</th>
                    <th className="text-center py-4 px-4 font-semibold text-gray-300">Score</th>
                    <th className="text-center py-4 px-4 font-semibold text-gray-300">Price/Month</th>
                    <th className="text-center py-4 px-4 font-semibold text-gray-300">Assessment Time</th>
                    <th className="text-center py-4 px-4 font-semibold text-gray-300">Market Share</th>
                    <th className="text-center py-4 px-4 font-semibold text-gray-300">Rating</th>
                  </tr>
                </thead>
                <tbody>
                  {benchmarkData.tools_comparison.map((tool, index) => (
                    <tr key={index} className="border-b border-gray-700 hover:bg-gray-700/30">
                      <td className="py-4 px-4">
                        <div className="flex items-center gap-3">
                          <div className={`w-3 h-3 rounded-full ${tool.name === 'RiskAI' ? 'bg-indigo-500' : 'bg-gray-500'}`}></div>
                          <span className={`font-medium ${tool.name === 'RiskAI' ? 'text-indigo-300' : 'text-gray-300'}`}>
                            {tool.name}
                          </span>
                        </div>
                      </td>
                      <td className="py-4 px-4 text-center">
                        <span className={`font-bold text-lg ${getScoreColor(tool.score)}`}>
                          {tool.score}
                        </span>
                      </td>
                      <td className="py-4 px-4 text-center text-gray-300">
                        ${tool.price_per_month}
                      </td>
                      <td className="py-4 px-4 text-center text-gray-300">
                        {tool.assessment_time}
                      </td>
                      <td className="py-4 px-4 text-center text-gray-300">
                        {tool.market_share}%
                      </td>
                      <td className="py-4 px-4 text-center">
                        <div className="flex items-center justify-center gap-1">
                          <span className="text-yellow-400">★</span>
                          <span className="text-gray-300">{tool.customer_rating}</span>
                        </div>
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>

          {/* RiskAI Advantages */}
          <div className="bg-gray-800/50 rounded-lg p-6 mb-8">
            <h2 className="text-2xl font-bold mb-6 flex items-center gap-2">
              <span>🚀</span> RiskAI Competitive Advantages
            </h2>
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
              <div>
                <h3 className="text-lg font-semibold text-indigo-300 mb-4">Key Advantages</h3>
                <ul className="space-y-3">
                  {benchmarkData.competitive_analysis.riskai_advantages.map((advantage, index) => (
                    <li key={index} className="flex items-start gap-3">
                      <span className="text-green-400 mt-1">✓</span>
                      <span className="text-gray-300">{advantage}</span>
                    </li>
                  ))}
                </ul>
              </div>
              <div>
                <h3 className="text-lg font-semibold text-purple-300 mb-4">Unique Features</h3>
                <ul className="space-y-3">
                  {benchmarkData.competitive_analysis.unique_features.map((feature, index) => (
                    <li key={index} className="flex items-start gap-3">
                      <span className="text-purple-400 mt-1">⭐</span>
                      <span className="text-gray-300">{feature}</span>
                    </li>
                  ))}
                </ul>
              </div>
            </div>
            <div className="mt-6 p-4 bg-indigo-900/30 rounded-lg border border-indigo-500/30">
              <h4 className="font-semibold text-indigo-300 mb-2">Market Position</h4>
              <p className="text-gray-300">{benchmarkData.competitive_analysis.market_position}</p>
            </div>
          </div>

          {/* ROI Analysis */}
          <div className="bg-gray-800/50 rounded-lg p-6">
            <h2 className="text-2xl font-bold mb-6 flex items-center gap-2">
              <span>💰</span> ROI Analysis
            </h2>
            
            {/* Company Size Selector */}
            <div className="mb-6">
              <label className="block text-sm font-medium text-gray-300 mb-2">
                Select Company Size:
              </label>
              <div className="flex flex-wrap gap-2">
                {benchmarkData.roi_analysis.map((roi) => (
                  <button
                    key={roi.company_size}
                    onClick={() => setSelectedCompanySize(roi.company_size)}
                    className={`px-4 py-2 rounded-lg transition ${
                      selectedCompanySize === roi.company_size
                        ? 'bg-indigo-600 text-white'
                        : 'bg-gray-700 text-gray-300 hover:bg-gray-600'
                    }`}
                  >
                    {roi.company_size.charAt(0).toUpperCase() + roi.company_size.slice(1)}
                  </button>
                ))}
              </div>
            </div>

            {/* ROI Metrics */}
            {selectedROI && (
              <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
                <div className="bg-green-500/20 border border-green-500/30 p-6 rounded-lg">
                  <h3 className="text-lg font-semibold text-green-300 mb-2">Annual Savings</h3>
                  <div className="text-3xl font-bold text-green-400">
                    ${selectedROI.annual_savings.toLocaleString()}
                  </div>
                  <p className="text-sm text-gray-400 mt-1">Cost reduction per year</p>
                </div>

                <div className="bg-blue-500/20 border border-blue-500/30 p-6 rounded-lg">
                  <h3 className="text-lg font-semibold text-blue-300 mb-2">Implementation Cost</h3>
                  <div className="text-3xl font-bold text-blue-400">
                    ${selectedROI.implementation_cost.toLocaleString()}
                  </div>
                  <p className="text-sm text-gray-400 mt-1">One-time setup cost</p>
                </div>

                <div className="bg-yellow-500/20 border border-yellow-500/30 p-6 rounded-lg">
                  <h3 className="text-lg font-semibold text-yellow-300 mb-2">Payback Period</h3>
                  <div className="text-3xl font-bold text-yellow-400">
                    {selectedROI.payback_period_months} mo
                  </div>
                  <p className="text-sm text-gray-400 mt-1">Time to break even</p>
                </div>

                <div className="bg-purple-500/20 border border-purple-500/30 p-6 rounded-lg">
                  <h3 className="text-lg font-semibold text-purple-300 mb-2">5-Year ROI</h3>
                  <div className="text-3xl font-bold text-purple-400">
                    {selectedROI.five_year_roi}%
                  </div>
                  <p className="text-sm text-gray-400 mt-1">Return on investment</p>
                </div>
              </div>
            )}
          </div>
        </div>
      </div>
    </div>
  );
};

export default BenchmarksPage;