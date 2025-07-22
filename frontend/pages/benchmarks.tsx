import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import {
  getDashboardData,
  getToolComparisonChart,
  getCategoryComparisonChart,
  getROIChart,
  getStrengthsWeaknessesChart
} from '../lib/benchmark-api';

const BenchmarksPage: React.FC = () => {
  const router = useRouter();
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [dashboardData, setDashboardData] = useState<any>(null);
  const [selectedIndustry, setSelectedIndustry] = useState<string>('');
  const [selectedCompanySize, setSelectedCompanySize] = useState<string>('');

  // Mock industry and company size options
  const industryOptions = [
    { value: '', label: 'All Industries' },
    { value: 'technology', label: 'Technology' },
    { value: 'finance', label: 'Finance' },
    { value: 'healthcare', label: 'Healthcare' },
    { value: 'manufacturing', label: 'Manufacturing' },
    { value: 'retail', label: 'Retail' }
  ];

  const companySizeOptions = [
    { value: '', label: 'All Company Sizes' },
    { value: 'small', label: 'Small (1-50 employees)' },
    { value: 'medium', label: 'Medium (51-500 employees)' },
    { value: 'large', label: 'Large (501-5000 employees)' },
    { value: 'enterprise', label: 'Enterprise (5000+ employees)' }
  ];

  useEffect(() => {
    loadDashboardData();
  }, [selectedIndustry, selectedCompanySize]);

  const loadDashboardData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const data = await getDashboardData(selectedIndustry || undefined, selectedCompanySize || undefined);
      setDashboardData(data);
    } catch (err) {
      console.error('Error loading dashboard data:', err);
      setError('Failed to load benchmark data. Please try again later.');
    } finally {
      setLoading(false);
    }
  };

  const handleIndustryChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    setSelectedIndustry(e.target.value);
  };

  const handleCompanySizeChange = (e: React.ChangeEvent<HTMLSelectElement>) => {
    setSelectedCompanySize(e.target.value);
  };

  const handleExportReport = () => {
    // In a real implementation, this would generate and download a report
    alert('Report export functionality would be implemented here');
  };

  if (loading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-950 to-gray-900 p-6">
        <div className="max-w-7xl mx-auto">
          <h1 className="text-3xl font-bold text-white mb-6">Benchmarks</h1>
          <div className="flex justify-center items-center h-64">
            <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-indigo-400"></div>
          </div>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-950 to-gray-900 p-6">
        <div className="max-w-7xl mx-auto">
          <h1 className="text-3xl font-bold text-white mb-6">Benchmarks</h1>
          <div className="bg-red-900/30 border border-red-500 rounded-lg p-4">
            <p className="text-red-300">{error}</p>
            <button 
              onClick={loadDashboardData}
              className="mt-4 px-4 py-2 bg-red-700 hover:bg-red-600 text-white rounded-lg"
            >
              Retry
            </button>
          </div>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-950 to-gray-900 p-6">
      <div className="max-w-7xl mx-auto">
        <div className="flex justify-between items-center mb-6">
          <h1 className="text-3xl font-bold text-white">Benchmarks</h1>
          <button
            onClick={handleExportReport}
            className="px-4 py-2 bg-indigo-600 hover:bg-indigo-700 text-white rounded-lg"
          >
            Export Report
          </button>
        </div>

        {/* Filters */}
        <div className="bg-gray-800 rounded-lg p-4 mb-6">
          <div className="flex flex-wrap gap-4">
            <div className="flex-1">
              <label className="block text-gray-300 mb-2">Industry</label>
              <select
                className="w-full bg-gray-700 text-white border border-gray-600 rounded-lg p-2"
                value={selectedIndustry}
                onChange={handleIndustryChange}
              >
                {industryOptions.map((option) => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
            </div>
            <div className="flex-1">
              <label className="block text-gray-300 mb-2">Company Size</label>
              <select
                className="w-full bg-gray-700 text-white border border-gray-600 rounded-lg p-2"
                value={selectedCompanySize}
                onChange={handleCompanySizeChange}
              >
                {companySizeOptions.map((option) => (
                  <option key={option.value} value={option.value}>
                    {option.label}
                  </option>
                ))}
              </select>
            </div>
          </div>
        </div>

        {/* Summary Cards */}
        <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4 mb-6">
          <div className="bg-gray-800 rounded-lg p-4">
            <h3 className="text-gray-400 text-sm mb-1">Overall Advantage</h3>
            <p className="text-2xl font-bold text-white">
              {dashboardData?.summary?.overall_advantage?.toFixed(1)}%
            </p>
            <p className="text-gray-400 text-xs mt-1">vs. other GRC tools</p>
          </div>
          <div className="bg-gray-800 rounded-lg p-4">
            <h3 className="text-gray-400 text-sm mb-1">Average ROI</h3>
            <p className="text-2xl font-bold text-white">
              {dashboardData?.summary?.average_roi?.toFixed(1)}%
            </p>
            <p className="text-gray-400 text-xs mt-1">return on investment</p>
          </div>
          <div className="bg-gray-800 rounded-lg p-4">
            <h3 className="text-gray-400 text-sm mb-1">Cost Savings</h3>
            <p className="text-2xl font-bold text-white">
              {dashboardData?.summary?.average_cost_savings?.toFixed(1)}%
            </p>
            <p className="text-gray-400 text-xs mt-1">vs. traditional approaches</p>
          </div>
          <div className="bg-gray-800 rounded-lg p-4">
            <h3 className="text-gray-400 text-sm mb-1">Time Savings</h3>
            <p className="text-2xl font-bold text-white">
              {dashboardData?.summary?.average_time_savings?.toFixed(1)}%
            </p>
            <p className="text-gray-400 text-xs mt-1">vs. traditional approaches</p>
          </div>
        </div>

        {/* Charts */}
        <div className="grid grid-cols-1 lg:grid-cols-2 gap-6 mb-6">
          {/* Category Comparison Chart */}
          <div className="bg-gray-800 rounded-lg p-4">
            <h2 className="text-xl font-bold text-white mb-4">Performance by Category</h2>
            <div className="h-64 flex items-center justify-center">
              {/* In a real implementation, this would be a radar chart */}
              <div className="text-gray-400">
                [Radar Chart: RiskAI Performance by Category]
                <p className="mt-2 text-sm">
                  {dashboardData?.charts?.category_comparison?.title || "Category Comparison Chart"}
                </p>
              </div>
            </div>
          </div>

          {/* ROI Analysis Chart */}
          <div className="bg-gray-800 rounded-lg p-4">
            <h2 className="text-xl font-bold text-white mb-4">ROI Analysis</h2>
            <div className="h-64 flex items-center justify-center">
              {/* In a real implementation, this would be a column chart */}
              <div className="text-gray-400">
                [Column Chart: ROI Analysis by Company Size]
                <p className="mt-2 text-sm">
                  {dashboardData?.charts?.roi_analysis?.title || "ROI Analysis Chart"}
                </p>
              </div>
            </div>
          </div>

          {/* Strengths Chart */}
          <div className="bg-gray-800 rounded-lg p-4">
            <h2 className="text-xl font-bold text-white mb-4">Key Strengths</h2>
            <div className="h-64 flex items-center justify-center">
              {/* In a real implementation, this would be a column chart */}
              <div className="text-gray-400">
                [Column Chart: RiskAI Strengths]
                <p className="mt-2 text-sm">
                  {dashboardData?.charts?.strengths?.title || "Strengths Chart"}
                </p>
              </div>
            </div>
          </div>

          {/* Weaknesses Chart */}
          <div className="bg-gray-800 rounded-lg p-4">
            <h2 className="text-xl font-bold text-white mb-4">Areas for Improvement</h2>
            <div className="h-64 flex items-center justify-center">
              {/* In a real implementation, this would be a column chart */}
              <div className="text-gray-400">
                [Column Chart: Areas for Improvement]
                <p className="mt-2 text-sm">
                  {dashboardData?.charts?.weaknesses?.title || "Weaknesses Chart"}
                </p>
              </div>
            </div>
          </div>
        </div>

        {/* Tool Comparison Table */}
        <div className="bg-gray-800 rounded-lg p-4 mb-6">
          <h2 className="text-xl font-bold text-white mb-4">Tool Comparison</h2>
          <div className="overflow-x-auto">
            <table className="w-full text-left">
              <thead>
                <tr className="border-b border-gray-700">
                  <th className="py-2 px-4 text-gray-300">Tool</th>
                  <th className="py-2 px-4 text-gray-300">Performance</th>
                  <th className="py-2 px-4 text-gray-300">Cost</th>
                  <th className="py-2 px-4 text-gray-300">Coverage</th>
                  <th className="py-2 px-4 text-gray-300">Usability</th>
                  <th className="py-2 px-4 text-gray-300">Overall</th>
                </tr>
              </thead>
              <tbody>
                <tr className="border-b border-gray-700 bg-indigo-900/20">
                  <td className="py-2 px-4 font-medium text-indigo-400">RiskAI</td>
                  <td className="py-2 px-4 text-white">9.2</td>
                  <td className="py-2 px-4 text-white">8.7</td>
                  <td className="py-2 px-4 text-white">9.5</td>
                  <td className="py-2 px-4 text-white">9.0</td>
                  <td className="py-2 px-4 text-white font-medium">9.1</td>
                </tr>
                <tr className="border-b border-gray-700">
                  <td className="py-2 px-4 font-medium text-gray-300">GRC Tool A</td>
                  <td className="py-2 px-4 text-gray-300">8.5</td>
                  <td className="py-2 px-4 text-gray-300">7.2</td>
                  <td className="py-2 px-4 text-gray-300">8.8</td>
                  <td className="py-2 px-4 text-gray-300">7.9</td>
                  <td className="py-2 px-4 text-gray-300 font-medium">8.1</td>
                </tr>
                <tr className="border-b border-gray-700">
                  <td className="py-2 px-4 font-medium text-gray-300">GRC Tool B</td>
                  <td className="py-2 px-4 text-gray-300">7.8</td>
                  <td className="py-2 px-4 text-gray-300">8.5</td>
                  <td className="py-2 px-4 text-gray-300">7.6</td>
                  <td className="py-2 px-4 text-gray-300">8.2</td>
                  <td className="py-2 px-4 text-gray-300 font-medium">8.0</td>
                </tr>
                <tr className="border-b border-gray-700">
                  <td className="py-2 px-4 font-medium text-gray-300">GRC Tool C</td>
                  <td className="py-2 px-4 text-gray-300">8.9</td>
                  <td className="py-2 px-4 text-gray-300">6.5</td>
                  <td className="py-2 px-4 text-gray-300">8.2</td>
                  <td className="py-2 px-4 text-gray-300">7.8</td>
                  <td className="py-2 px-4 text-gray-300 font-medium">7.9</td>
                </tr>
                <tr>
                  <td className="py-2 px-4 font-medium text-gray-300">GRC Tool D</td>
                  <td className="py-2 px-4 text-gray-300">7.5</td>
                  <td className="py-2 px-4 text-gray-300">8.9</td>
                  <td className="py-2 px-4 text-gray-300">7.2</td>
                  <td className="py-2 px-4 text-gray-300">7.5</td>
                  <td className="py-2 px-4 text-gray-300 font-medium">7.8</td>
                </tr>
              </tbody>
            </table>
          </div>
        </div>

        {/* ROI Analysis */}
        <div className="bg-gray-800 rounded-lg p-4">
          <h2 className="text-xl font-bold text-white mb-4">ROI Analysis</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div>
              <h3 className="text-lg font-medium text-white mb-3">Cost Comparison</h3>
              <div className="space-y-4">
                <div>
                  <div className="flex justify-between mb-1">
                    <span className="text-gray-300">RiskAI</span>
                    <span className="text-gray-300">$10,000</span>
                  </div>
                  <div className="w-full bg-gray-700 rounded-full h-2">
                    <div className="bg-indigo-600 h-2 rounded-full" style={{ width: '40%' }}></div>
                  </div>
                </div>
                <div>
                  <div className="flex justify-between mb-1">
                    <span className="text-gray-300">Traditional GRC</span>
                    <span className="text-gray-300">$25,000</span>
                  </div>
                  <div className="w-full bg-gray-700 rounded-full h-2">
                    <div className="bg-red-600 h-2 rounded-full" style={{ width: '100%' }}></div>
                  </div>
                </div>
              </div>
              <p className="mt-4 text-gray-400 text-sm">
                RiskAI provides a 60% cost reduction compared to traditional GRC approaches.
              </p>
            </div>
            <div>
              <h3 className="text-lg font-medium text-white mb-3">Time Savings</h3>
              <div className="space-y-4">
                <div>
                  <div className="flex justify-between mb-1">
                    <span className="text-gray-300">RiskAI</span>
                    <span className="text-gray-300">40 hours</span>
                  </div>
                  <div className="w-full bg-gray-700 rounded-full h-2">
                    <div className="bg-indigo-600 h-2 rounded-full" style={{ width: '30%' }}></div>
                  </div>
                </div>
                <div>
                  <div className="flex justify-between mb-1">
                    <span className="text-gray-300">Traditional GRC</span>
                    <span className="text-gray-300">120 hours</span>
                  </div>
                  <div className="w-full bg-gray-700 rounded-full h-2">
                    <div className="bg-red-600 h-2 rounded-full" style={{ width: '100%' }}></div>
                  </div>
                </div>
              </div>
              <p className="mt-4 text-gray-400 text-sm">
                RiskAI reduces assessment time by 67% compared to traditional approaches.
              </p>
            </div>
          </div>
        </div>
      </div>
    </div>
  );
};

export default BenchmarksPage;