import React, { useState, useEffect } from 'react';
import { getSupportedIndustries, getComplianceFrameworks } from '../lib/enhanced-assessment-api';

interface IndustryProfileSetupProps {
  onProfileComplete: (profile: {
    industry?: string;
    compliance_requirements?: string[];
    company_size?: string;
    data_types?: string[];
  }) => void;
  onCancel?: () => void;
}

const IndustryProfileSetup: React.FC<IndustryProfileSetupProps> = ({
  onProfileComplete,
  onCancel
}) => {
  const [industries, setIndustries] = useState<{ industries: string[]; descriptions: Record<string, string> }>({ industries: [], descriptions: {} });
  const [frameworks, setFrameworks] = useState<{ frameworks: string[]; descriptions: Record<string, string> }>({ frameworks: [], descriptions: {} });
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);

  // Form state
  const [selectedIndustry, setSelectedIndustry] = useState<string>('');
  const [selectedFrameworks, setSelectedFrameworks] = useState<string[]>([]);
  const [companySize, setCompanySize] = useState<string>('');
  const [dataTypes, setDataTypes] = useState<string[]>([]);

  useEffect(() => {
    loadOptions();
  }, []);

  const loadOptions = async () => {
    try {
      setLoading(true);
      const [industriesData, frameworksData] = await Promise.all([
        getSupportedIndustries(),
        getComplianceFrameworks()
      ]);
      
      setIndustries(industriesData);
      setFrameworks(frameworksData);
    } catch (err) {
      setError('Failed to load industry and compliance options');
      console.error('Error loading options:', err);
    } finally {
      setLoading(false);
    }
  };

  const handleFrameworkToggle = (framework: string) => {
    setSelectedFrameworks(prev => 
      prev.includes(framework)
        ? prev.filter(f => f !== framework)
        : [...prev, framework]
    );
  };

  const handleDataTypeToggle = (dataType: string) => {
    setDataTypes(prev => 
      prev.includes(dataType)
        ? prev.filter(dt => dt !== dataType)
        : [...prev, dataType]
    );
  };

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    
    const profile = {
      industry: selectedIndustry || undefined,
      compliance_requirements: selectedFrameworks.length > 0 ? selectedFrameworks : undefined,
      company_size: companySize || undefined,
      data_types: dataTypes.length > 0 ? dataTypes : undefined,
    };

    onProfileComplete(profile);
  };

  if (loading) {
    return (
      <div className="bg-white rounded-lg shadow-lg p-8">
        <div className="text-center">
          <div className="animate-spin rounded-full h-12 w-12 border-b-2 border-blue-600 mx-auto"></div>
          <p className="mt-4 text-gray-600">Loading assessment options...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="bg-white rounded-lg shadow-lg p-8">
        <div className="text-center">
          <div className="text-red-600 mb-4">{error}</div>
          <button
            onClick={loadOptions}
            className="px-4 py-2 bg-blue-600 text-white rounded-lg hover:bg-blue-700"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  return (
    <div className="bg-white rounded-lg shadow-lg p-8">
      <h2 className="text-2xl font-bold text-gray-900 mb-6">
        Customize Your Assessment
      </h2>
      <p className="text-gray-600 mb-8">
        Help us tailor the 120-question assessment to your organization's specific needs and compliance requirements.
      </p>

      <form onSubmit={handleSubmit} className="space-y-8">
        {/* Industry Selection */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-3">
            Industry Sector
          </label>
          <select
            value={selectedIndustry}
            onChange={(e) => setSelectedIndustry(e.target.value)}
            className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="">Select your industry (optional)</option>
            {industries.industries.map(industry => (
              <option key={industry} value={industry}>
                {industry.replace('_', ' ').replace(/\b\w/g, l => l.toUpperCase())} - {industries.descriptions[industry]}
              </option>
            ))}
          </select>
        </div>

        {/* Company Size */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-3">
            Company Size
          </label>
          <select
            value={companySize}
            onChange={(e) => setCompanySize(e.target.value)}
            className="w-full p-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
          >
            <option value="">Select company size (optional)</option>
            <option value="small">Small (1-50 employees)</option>
            <option value="medium">Medium (51-500 employees)</option>
            <option value="large">Large (501-5000 employees)</option>
            <option value="enterprise">Enterprise (5000+ employees)</option>
          </select>
        </div>

        {/* Compliance Requirements */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-3">
            Compliance Requirements
          </label>
          <p className="text-sm text-gray-500 mb-4">
            Select all compliance frameworks that apply to your organization:
          </p>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-3">
            {frameworks.frameworks.map(framework => (
              <label key={framework} className="flex items-start space-x-3 p-3 border border-gray-200 rounded-lg hover:bg-gray-50">
                <input
                  type="checkbox"
                  checked={selectedFrameworks.includes(framework)}
                  onChange={() => handleFrameworkToggle(framework)}
                  className="mt-1 h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                />
                <div>
                  <div className="font-medium text-gray-900">
                    {framework.toUpperCase()}
                  </div>
                  <div className="text-sm text-gray-500">
                    {frameworks.descriptions[framework]}
                  </div>
                </div>
              </label>
            ))}
          </div>
        </div>

        {/* Data Types */}
        <div>
          <label className="block text-sm font-medium text-gray-700 mb-3">
            Types of Data You Handle
          </label>
          <p className="text-sm text-gray-500 mb-4">
            Select the types of sensitive data your organization processes:
          </p>
          <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
            {[
              { id: 'pii', label: 'Personal Information (PII)' },
              { id: 'phi', label: 'Health Information (PHI)' },
              { id: 'payment_data', label: 'Payment Card Data' },
              { id: 'financial_data', label: 'Financial Records' },
              { id: 'intellectual_property', label: 'Intellectual Property' },
              { id: 'government_data', label: 'Government/Classified Data' }
            ].map(dataType => (
              <label key={dataType.id} className="flex items-center space-x-2 p-2 border border-gray-200 rounded-lg hover:bg-gray-50">
                <input
                  type="checkbox"
                  checked={dataTypes.includes(dataType.id)}
                  onChange={() => handleDataTypeToggle(dataType.id)}
                  className="h-4 w-4 text-blue-600 focus:ring-blue-500 border-gray-300 rounded"
                />
                <span className="text-sm text-gray-700">{dataType.label}</span>
              </label>
            ))}
          </div>
        </div>

        {/* Action Buttons */}
        <div className="flex justify-between pt-6">
          {onCancel && (
            <button
              type="button"
              onClick={onCancel}
              className="px-6 py-3 border border-gray-300 text-gray-700 rounded-lg hover:bg-gray-50"
            >
              Skip Customization
            </button>
          )}
          
          <button
            type="submit"
            className="px-8 py-3 bg-blue-600 text-white rounded-lg hover:bg-blue-700 font-medium"
          >
            Start Tailored Assessment
          </button>
        </div>
      </form>

      {/* Preview */}
      {(selectedIndustry || selectedFrameworks.length > 0 || companySize) && (
        <div className="mt-8 p-4 bg-blue-50 rounded-lg">
          <h3 className="font-medium text-blue-900 mb-2">Assessment Preview:</h3>
          <ul className="text-sm text-blue-800 space-y-1">
            {selectedIndustry && (
              <li>• Industry-specific questions for {selectedIndustry.replace('_', ' ')}</li>
            )}
            {selectedFrameworks.length > 0 && (
              <li>• Compliance questions for {selectedFrameworks.map(f => f.toUpperCase()).join(', ')}</li>
            )}
            {companySize && (
              <li>• Questions tailored for {companySize} organizations</li>
            )}
            <li>• Total: 120 questions across 12 security domains</li>
          </ul>
        </div>
      )}
    </div>
  );
};

export default IndustryProfileSetup;