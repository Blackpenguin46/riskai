import React, { useState } from 'react';
import type { NextPage } from 'next';
import { useRouter } from 'next/router';

interface CompanyData {
  id?: number;
  name: string;
  industry: string;
  size: string;
  country: string;
  settings: {
    compliance_frameworks: string[];
    risk_tolerance: string;
    assessment_frequency: string;
  };
  contact_info: {
    primary_contact: string;
    email: string;
    phone: string;
  };
  compliance_requirements: {
    required_frameworks: string[];
    audit_schedule: string;
    reporting_requirements: string[];
  };
}

const CompanySetupPage: NextPage = () => {
  const [companyData, setCompanyData] = useState<CompanyData>({
    name: '',
    industry: '',
    size: '',
    country: '',
    settings: {
      compliance_frameworks: [],
      risk_tolerance: 'medium',
      assessment_frequency: 'annual'
    },
    contact_info: {
      primary_contact: '',
      email: '',
      phone: ''
    },
    compliance_requirements: {
      required_frameworks: [],
      audit_schedule: 'annual',
      reporting_requirements: []
    }
  });

  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [saveSuccess, setSaveSuccess] = useState(false);
  const router = useRouter();

  const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

  const industries = [
    'Technology', 'Healthcare', 'Financial Services', 'Manufacturing', 
    'Retail', 'Government', 'Education', 'Energy', 'Transportation', 'Other'
  ];

  const companySizes = [
    '1-50 employees', '51-200 employees', '201-500 employees', 
    '501-1000 employees', '1001-5000 employees', '5000+ employees'
  ];

  const frameworks = [
    'NIST CSF 2.0', 'ISO 27001', 'SOC 2', 'CIS Controls', 
    'GDPR', 'HIPAA', 'PCI DSS', 'FedRAMP'
  ];

  const handleInputChange = (field: string, value: string) => {
    setCompanyData(prev => ({
      ...prev,
      [field]: value
    }));
  };

  const handleNestedInputChange = (section: string, field: string, value: string) => {
    setCompanyData(prev => {
      const sectionData = prev[section as keyof CompanyData] as Record<string, string | string[]>;
      return {
        ...prev,
        [section]: {
          ...sectionData,
          [field]: value
        }
      };
    });
  };

  const handleFrameworkToggle = (framework: string, section: 'settings' | 'compliance_requirements', field: string) => {
    setCompanyData(prev => {
      const sectionData = prev[section] as Record<string, string | string[]>;
      const currentFrameworks = sectionData[field] as string[] || [];
      const newFrameworks = currentFrameworks.includes(framework)
        ? currentFrameworks.filter(f => f !== framework)
        : [...currentFrameworks, framework];
      
      return {
        ...prev,
        [section]: {
          ...sectionData,
          [field]: newFrameworks
        }
      };
    });
  };

  const handleSave = async () => {
    setIsLoading(true);
    setError(null);
    
    try {
      const response = await fetch(`${apiUrl}/company/save`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify(companyData)
      });
      
      if (!response.ok) throw new Error('Failed to save company data');
      
      await response.json();
      setSaveSuccess(true);
      
      // Auto-hide success message after 3 seconds
      setTimeout(() => setSaveSuccess(false), 3000);
      
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to save company data');
    }
    
    setIsLoading(false);
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-950 to-gray-900 text-white">
      <header className="p-4 bg-gray-900/80 backdrop-blur-md shadow-lg">
        <div className="flex items-center justify-between max-w-6xl mx-auto">
          <button
            onClick={() => router.push('/')}
            className="text-indigo-400 hover:text-indigo-300 transition flex items-center gap-2"
          >
            ← Back to Dashboard
          </button>
          <h1 className="text-2xl font-bold bg-gradient-to-r from-indigo-400 to-purple-500 bg-clip-text text-transparent">
            Company Setup
          </h1>
          <div className="w-32"></div>
        </div>
      </header>

      <main className="max-w-4xl mx-auto p-6">
        {error && (
          <div className="bg-red-900/50 border border-red-600 text-red-200 p-4 rounded-lg mb-6">
            {error}
          </div>
        )}

        {saveSuccess && (
          <div className="bg-green-900/50 border border-green-600 text-green-200 p-4 rounded-lg mb-6">
            Company data saved successfully!
          </div>
        )}

        <div className="bg-gray-800 rounded-lg p-8">
          <h2 className="text-2xl font-bold mb-6">Company Information</h2>
          
          {/* Basic Information */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
            <div>
              <label className="block text-sm font-medium mb-2">Company Name *</label>
              <input
                type="text"
                value={companyData.name}
                onChange={(e) => handleInputChange('name', e.target.value)}
                className="w-full p-3 bg-gray-700 border border-gray-600 rounded-lg text-white focus:ring-2 focus:ring-indigo-500"
                placeholder="Enter company name"
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">Industry *</label>
              <select
                value={companyData.industry}
                onChange={(e) => handleInputChange('industry', e.target.value)}
                className="w-full p-3 bg-gray-700 border border-gray-600 rounded-lg text-white focus:ring-2 focus:ring-indigo-500"
              >
                <option value="">Select industry</option>
                {industries.map(industry => (
                  <option key={industry} value={industry}>{industry}</option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">Company Size *</label>
              <select
                value={companyData.size}
                onChange={(e) => handleInputChange('size', e.target.value)}
                className="w-full p-3 bg-gray-700 border border-gray-600 rounded-lg text-white focus:ring-2 focus:ring-indigo-500"
              >
                <option value="">Select size</option>
                {companySizes.map(size => (
                  <option key={size} value={size}>{size}</option>
                ))}
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">Country *</label>
              <input
                type="text"
                value={companyData.country}
                onChange={(e) => handleInputChange('country', e.target.value)}
                className="w-full p-3 bg-gray-700 border border-gray-600 rounded-lg text-white focus:ring-2 focus:ring-indigo-500"
                placeholder="Enter country"
              />
            </div>
          </div>

          {/* Contact Information */}
          <h3 className="text-xl font-semibold mb-4">Contact Information</h3>
          <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-8">
            <div>
              <label className="block text-sm font-medium mb-2">Primary Contact</label>
              <input
                type="text"
                value={companyData.contact_info.primary_contact}
                onChange={(e) => handleNestedInputChange('contact_info', 'primary_contact', e.target.value)}
                className="w-full p-3 bg-gray-700 border border-gray-600 rounded-lg text-white focus:ring-2 focus:ring-indigo-500"
                placeholder="Contact name"
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">Email</label>
              <input
                type="email"
                value={companyData.contact_info.email}
                onChange={(e) => handleNestedInputChange('contact_info', 'email', e.target.value)}
                className="w-full p-3 bg-gray-700 border border-gray-600 rounded-lg text-white focus:ring-2 focus:ring-indigo-500"
                placeholder="contact@company.com"
              />
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">Phone</label>
              <input
                type="tel"
                value={companyData.contact_info.phone}
                onChange={(e) => handleNestedInputChange('contact_info', 'phone', e.target.value)}
                className="w-full p-3 bg-gray-700 border border-gray-600 rounded-lg text-white focus:ring-2 focus:ring-indigo-500"
                placeholder="+1 (555) 123-4567"
              />
            </div>
          </div>

          {/* Compliance Frameworks */}
          <h3 className="text-xl font-semibold mb-4">Compliance Frameworks</h3>
          <div className="mb-8">
            <label className="block text-sm font-medium mb-3">Required Frameworks</label>
            <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
              {frameworks.map(framework => (
                <label key={framework} className="flex items-center gap-2 p-3 bg-gray-700 rounded-lg hover:bg-gray-600 cursor-pointer transition">
                  <input
                    type="checkbox"
                    checked={companyData.compliance_requirements.required_frameworks.includes(framework)}
                    onChange={() => handleFrameworkToggle(framework, 'compliance_requirements', 'required_frameworks')}
                    className="text-indigo-500"
                  />
                  <span className="text-sm">{framework}</span>
                </label>
              ))}
            </div>
          </div>

          {/* Settings */}
          <h3 className="text-xl font-semibold mb-4">Assessment Settings</h3>
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6 mb-8">
            <div>
              <label className="block text-sm font-medium mb-2">Risk Tolerance</label>
              <select
                value={companyData.settings.risk_tolerance}
                onChange={(e) => handleNestedInputChange('settings', 'risk_tolerance', e.target.value)}
                className="w-full p-3 bg-gray-700 border border-gray-600 rounded-lg text-white focus:ring-2 focus:ring-indigo-500"
              >
                <option value="low">Low - Conservative approach</option>
                <option value="medium">Medium - Balanced approach</option>
                <option value="high">High - Aggressive approach</option>
              </select>
            </div>

            <div>
              <label className="block text-sm font-medium mb-2">Assessment Frequency</label>
              <select
                value={companyData.settings.assessment_frequency}
                onChange={(e) => handleNestedInputChange('settings', 'assessment_frequency', e.target.value)}
                className="w-full p-3 bg-gray-700 border border-gray-600 rounded-lg text-white focus:ring-2 focus:ring-indigo-500"
              >
                <option value="monthly">Monthly</option>
                <option value="quarterly">Quarterly</option>
                <option value="biannual">Bi-annual</option>
                <option value="annual">Annual</option>
              </select>
            </div>
          </div>

          {/* Action Buttons */}
          <div className="flex gap-4 justify-end">
            <button
              onClick={() => router.push('/')}
              className="px-6 py-3 rounded-lg bg-gray-600 text-white hover:bg-gray-500 transition"
              disabled={isLoading}
            >
              Cancel
            </button>
            <button
              onClick={handleSave}
              disabled={isLoading || !companyData.name || !companyData.industry}
              className="px-6 py-3 rounded-lg bg-gradient-to-r from-indigo-500 to-purple-600 text-white font-semibold hover:from-indigo-600 hover:to-purple-700 transition disabled:opacity-50"
            >
              {isLoading ? 'Saving...' : 'Save Company Data'}
            </button>
          </div>
        </div>
      </main>
    </div>
  );
};

export default CompanySetupPage;