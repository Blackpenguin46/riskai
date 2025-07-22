import React, { useState, useEffect } from 'react';
import { useRouter } from 'next/router';
import {
  getIndustrySectors,
  getIndustryValidations,
  analyzeGeneralizability,
  analyzeDomainPerformance,
  getIndustryBenchmarkComparison
} from '../lib/validation-api';

const ValidationPage: React.FC = () => {
  const router = useRouter();
  const [loading, setLoading] = useState<boolean>(true);
  const [error, setError] = useState<string | null>(null);
  const [industries, setIndustries] = useState<any[]>([]);
  const [selectedIndustry, setSelectedIndustry] = useState<string>('');
  const [selectedCompanySize, setSelectedCompanySize] = useState<string>('');
  const [generalizabilityData, setGeneralizabilityData] = useState<any>(null);
  const [domainPerformanceData, setDomainPerformanceData] = useState<any>(null);
  const [benchmarkComparisonData, setBenchmarkComparisonData] = useState<any>(null);

  // Company size options
  const companySizeOptions = [
    { value: '', label: 'All Company Sizes' },
    { value: 'small', label: 'Small (1-50 employees)' },
    { value: 'medium', label: 'Medium (51-500 employees)' },
    { value: 'large', label: 'Large (501-5000 employees)' },
    { value: 'enterprise', label: 'Enterprise (5000+ employees)' }
  ];

  useEffect(() => {
    loadIndustries();
    loadGeneralizabilityData();
  }, []);

  useEffect(() => {
    if (selectedIndustry) {
      loadDomainPerformanceData();
      loadBenchmarkComparisonData();
    }
  }, [selectedIndustry, selectedCompanySize]);

  const loadIndustries = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const result = await getIndustrySectors();
      setIndustries(result.industries || []);
    } catch (err) {
      console.error('Error loading industries:', err);
      setError('Failed to load industry data');
    } finally {
      setLoading(false);
    }
  };

  const loadGeneralizabilityData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const result = await analyzeGeneralizability();
      setGeneralizabilityData(result);
    } catch (err) {
      console.error('Error loading generalizability data:', err);
      setError('Failed to load generalizability data');
    } finally {
      setLoading(false);
    }
  };

  const loadDomainPerformanceData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const industryId = selectedIndustry ? parseInt(selectedIndustry) : undefined;
      const companySize = selectedCompanySize || undefined;
      
      const result = await analyzeDomainPerformance(industryId, companySize);
      setDomainPerformanceData(result);
    } catch (err) {
      console.error('Error loading domain performance data:', err);
      setError('Failed to load domain performance data');
    } finally {
      setLoading(false);
    }
  };

  const loadBenchmarkComparisonData = async () => {
    try {
      setLoading(true);
      setError(null);
      
      const industryId = parseInt(selectedIndustry);
      const companySize = selectedCompanySize || undefined;
      
      const result = await getIndustryBenchmarkComparison(industryId, undefined, companySize);
      setBenchmarkComparisonData(result);
    } catch (err) {
      console.error('Error loading benchmark comparison data:', err);
      // Don't set error here as this is optional data
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

  if (loading && !generalizabilityData) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-950 to-gray-900 p-6">
        <div className="max-w-7xl mx-auto">
          <h1 className="text-3xl font-bold text-white mb-6">Cross-Industry Validation</h1>
          <div className="flex justify-center items-center h-64">
            <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-indigo-400"></div>
          </div>
        </div>
      </div>
    );
  }

  if (error && !generalizabilityData) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-950 to-gray-900 p-6">
        <div className="max-w-7xl mx-auto">
          <h1 className="text-3xl font-bold text-white mb-6">Cross-Industry Validation</h1>
          <div className="bg-red-900/30 border border-red-500 rounded-lg p-4">
            <p className="text-red-300">{error}</p>
            <button 
              onClick={loadGeneralizabilityData}
              className="mt-4 px-4 py-2 bg-red-700 hover:bg-red-600 text-white rounded-lg"
            >
              Retry
            </button>
          </div>
        </div>
      </div>
    );
  }

  const getIndustryName = (id: number) => {
    const industry = industries.find(i => i.id === id);
    return industry ? industry.name : `Industry ${id}`;
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-950 to-gray-900 p-6">
      <div className="max-w-7xl mx-auto">
        <div className="flex justify-between items-center mb-6">
          <h1 className="text-3xl font-bold text-white">Cross-Industry Validation</h1>
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
                <option value="">All Industries</option>
                {industries.map((industry) => (
                  <option key={industry.id} value={industry.id}>
                    {industry.name}
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

        {/* Generalizability Summary */}
        {generalizabilityData && (
          <div className="bg-gray-800 rounded-lg p-6 mb-6">
            <h2 className="text-2xl font-bold text-white mb-4">Generalizability Analysis</h2>
            
            <div className="grid grid-cols-1 md:grid-cols-3 gap-4 mb-6">
              <div className="bg-gray-700 rounded-lg p-4">
                <h3 className="text-lg font-medium text-white mb-2">Overall Accuracy</h3>
                <p className="text-3xl font-bold text-indigo-400">
                  {(generalizabilityData.overall.accuracy * 100).toFixed(1)}%
                </p>
                <p className="text-gray-400 text-sm mt-1">
                  Based on {generalizabilityData.overall.sample_size} validation responses
                </p>
              </div>
              
              <div className="bg-gray-700 rounded-lg p-4">
                <h3 className="text-lg font-medium text-white mb-2">Generalizability</h3>
                <p className="text-3xl font-bold text-indigo-400">
                  {generalizabilityData.generalizability}
                </p>
                <p className="text-gray-400 text-sm mt-1">
                  Industry Variance: {generalizabilityData.industry_variance.variance.toFixed(3)}
                </p>
              </div>
              
              <div className="bg-gray-700 rounded-lg p-4">
                <h3 className="text-lg font-medium text-white mb-2">Industries Covered</h3>
                <p className="text-3xl font-bold text-indigo-400">
                  {generalizabilityData.industry_metrics.length}
                </p>
                <p className="text-gray-400 text-sm mt-1">
                  Company Sizes: {generalizabilityData.company_size_metrics.length}
                </p>
              </div>
            </div>
            
            <div className="bg-gray-700 rounded-lg p-4">
              <h3 className="text-lg font-medium text-white mb-2">Interpretation</h3>
              <p className="text-gray-300">
                {generalizabilityData.interpretation}
              </p>
            </div>
          </div>
        )}

        {/* Industry Performance */}
        {generalizabilityData && (
          <div className="bg-gray-800 rounded-lg p-6 mb-6">
            <h2 className="text-2xl font-bold text-white mb-4">Industry Performance</h2>
            
            <div className="overflow-x-auto">
              <table className="w-full text-left">
                <thead>
                  <tr className="border-b border-gray-700">
                    <th className="py-2 px-4 text-gray-300">Industry</th>
                    <th className="py-2 px-4 text-gray-300">Accuracy</th>
                    <th className="py-2 px-4 text-gray-300">Sample Size</th>
                    <th className="py-2 px-4 text-gray-300">Confidence Interval</th>
                  </tr>
                </thead>
                <tbody>
                  {generalizabilityData.industry_metrics.map((metric: any, index: number) => (
                    <tr key={index} className="border-b border-gray-700">
                      <td className="py-2 px-4 font-medium text-white">{metric.industry_name}</td>
                      <td className="py-2 px-4 text-white">{(metric.accuracy * 100).toFixed(1)}%</td>
                      <td className="py-2 px-4 text-white">{metric.sample_size}</td>
                      <td className="py-2 px-4 text-white">
                        {(metric.confidence_interval[0] * 100).toFixed(1)}% - {(metric.confidence_interval[1] * 100).toFixed(1)}%
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* Company Size Performance */}
        {generalizabilityData && (
          <div className="bg-gray-800 rounded-lg p-6 mb-6">
            <h2 className="text-2xl font-bold text-white mb-4">Company Size Performance</h2>
            
            <div className="overflow-x-auto">
              <table className="w-full text-left">
                <thead>
                  <tr className="border-b border-gray-700">
                    <th className="py-2 px-4 text-gray-300">Company Size</th>
                    <th className="py-2 px-4 text-gray-300">Accuracy</th>
                    <th className="py-2 px-4 text-gray-300">Sample Size</th>
                    <th className="py-2 px-4 text-gray-300">Confidence Interval</th>
                  </tr>
                </thead>
                <tbody>
                  {generalizabilityData.company_size_metrics.map((metric: any, index: number) => (
                    <tr key={index} className="border-b border-gray-700">
                      <td className="py-2 px-4 font-medium text-white">{metric.company_size}</td>
                      <td className="py-2 px-4 text-white">{(metric.accuracy * 100).toFixed(1)}%</td>
                      <td className="py-2 px-4 text-white">{metric.sample_size}</td>
                      <td className="py-2 px-4 text-white">
                        {(metric.confidence_interval[0] * 100).toFixed(1)}% - {(metric.confidence_interval[1] * 100).toFixed(1)}%
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* Domain Performance */}
        {domainPerformanceData && (
          <div className="bg-gray-800 rounded-lg p-6 mb-6">
            <h2 className="text-2xl font-bold text-white mb-4">
              Domain Performance
              {selectedIndustry && ` for ${getIndustryName(parseInt(selectedIndustry))}`}
              {selectedCompanySize && ` (${selectedCompanySize})`}
            </h2>
            
            <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-6">
              {/* Strengths */}
              <div className="bg-gray-700 rounded-lg p-4">
                <h3 className="text-lg font-medium text-white mb-3">Strengths</h3>
                <ul className="space-y-2">
                  {domainPerformanceData.strengths.map((strength: any, index: number) => (
                    <li key={index} className="flex justify-between items-center">
                      <span className="text-gray-300">{strength.domain_name}</span>
                      <span className="text-green-400 font-medium">{(strength.accuracy * 100).toFixed(1)}%</span>
                    </li>
                  ))}
                </ul>
              </div>
              
              {/* Weaknesses */}
              <div className="bg-gray-700 rounded-lg p-4">
                <h3 className="text-lg font-medium text-white mb-3">Areas for Improvement</h3>
                <ul className="space-y-2">
                  {domainPerformanceData.weaknesses.map((weakness: any, index: number) => (
                    <li key={index} className="flex justify-between items-center">
                      <span className="text-gray-300">{weakness.domain_name}</span>
                      <span className="text-red-400 font-medium">{(weakness.accuracy * 100).toFixed(1)}%</span>
                    </li>
                  ))}
                </ul>
              </div>
            </div>
            
            {/* All Domains */}
            <div className="overflow-x-auto">
              <table className="w-full text-left">
                <thead>
                  <tr className="border-b border-gray-700">
                    <th className="py-2 px-4 text-gray-300">Domain</th>
                    <th className="py-2 px-4 text-gray-300">Framework</th>
                    <th className="py-2 px-4 text-gray-300">Accuracy</th>
                    <th className="py-2 px-4 text-gray-300">Sample Size</th>
                    <th className="py-2 px-4 text-gray-300">Confidence Interval</th>
                  </tr>
                </thead>
                <tbody>
                  {domainPerformanceData.domain_metrics.map((metric: any, index: number) => (
                    <tr key={index} className="border-b border-gray-700">
                      <td className="py-2 px-4 font-medium text-white">{metric.domain_name}</td>
                      <td className="py-2 px-4 text-gray-300">{metric.framework_name}</td>
                      <td className="py-2 px-4 text-white">{(metric.accuracy * 100).toFixed(1)}%</td>
                      <td className="py-2 px-4 text-white">{metric.sample_size}</td>
                      <td className="py-2 px-4 text-white">
                        {(metric.confidence_interval[0] * 100).toFixed(1)}% - {(metric.confidence_interval[1] * 100).toFixed(1)}%
                      </td>
                    </tr>
                  ))}
                </tbody>
              </table>
            </div>
          </div>
        )}

        {/* Benchmark Comparison */}
        {benchmarkComparisonData && selectedIndustry && (
          <div className="bg-gray-800 rounded-lg p-6 mb-6">
            <h2 className="text-2xl font-bold text-white mb-4">
              Benchmark Comparison for {getIndustryName(parseInt(selectedIndustry))}
              {selectedCompanySize && ` (${selectedCompanySize})`}
            </h2>
            
            {benchmarkComparisonData.comparison.length > 0 ? (
              <div className="overflow-x-auto">
                <table className="w-full text-left">
                  <thead>
                    <tr className="border-b border-gray-700">
                      <th className="py-2 px-4 text-gray-300">Domain</th>
                      <th className="py-2 px-4 text-gray-300">Industry Score</th>
                      <th className="py-2 px-4 text-gray-300">Overall Average</th>
                      <th className="py-2 px-4 text-gray-300">Difference</th>
                      <th className="py-2 px-4 text-gray-300">% Difference</th>
                    </tr>
                  </thead>
                  <tbody>
                    {benchmarkComparisonData.comparison.map((comp: any, index: number) => (
                      <tr key={index} className="border-b border-gray-700">
                        <td className="py-2 px-4 font-medium text-white">Domain {comp.domain_id}</td>
                        <td className="py-2 px-4 text-white">{comp.industry_score.toFixed(1)}</td>
                        <td className="py-2 px-4 text-white">{comp.overall_score.toFixed(1)}</td>
                        <td className="py-2 px-4 text-white">
                          <span className={comp.difference > 0 ? 'text-green-400' : 'text-red-400'}>
                            {comp.difference > 0 ? '+' : ''}{comp.difference.toFixed(1)}
                          </span>
                        </td>
                        <td className="py-2 px-4 text-white">
                          <span className={comp.percentage_difference > 0 ? 'text-green-400' : 'text-red-400'}>
                            {comp.percentage_difference > 0 ? '+' : ''}{comp.percentage_difference.toFixed(1)}%
                          </span>
                        </td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            ) : (
              <div className="bg-gray-700 rounded-lg p-4">
                <p className="text-gray-300">No benchmark comparison data available for the selected industry.</p>
              </div>
            )}
          </div>
        )}
      </div>
    </div>
  );
};

export default ValidationPage;