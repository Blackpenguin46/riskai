import React, { useState, useEffect } from 'react';
import type { NextPage } from 'next';
import { useRouter } from 'next/router';

interface CompanyProfile {
  id?: number;
  name: string;
  size: string;
  industry: string;
  location: string;
  annual_revenue: string;
  employee_count: number;
  it_budget: string;
  compliance_requirements: string[];
  current_security_tools: string[];
  description?: string;
}

interface UploadedDocument {
  id: string;
  filename: string;
  upload_date: string;
  file_size: number;
  document_type: string;
  analysis_status: string;
  key_insights: string[];
}

interface CompanyWorkspace {
  company_id: string;
  company_name: string;
  created_date: string;
  document_count: number;
  last_activity: string;
  analysis_complete: boolean;
}

const CompanyPage: NextPage = () => {
  const router = useRouter();
  const [companyProfile, setCompanyProfile] = useState<CompanyProfile>({
    name: '',
    size: 'medium',
    industry: '',
    location: '',
    annual_revenue: '',
    employee_count: 0,
    it_budget: '',
    compliance_requirements: [],
    current_security_tools: []
  });
  const [workspaces, setWorkspaces] = useState<CompanyWorkspace[]>([]);
  const [uploadedDocuments, setUploadedDocuments] = useState<UploadedDocument[]>([]);
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [activeTab, setActiveTab] = useState<'profile' | 'documents' | 'workspaces'>('profile');
  const [selectedFiles, setSelectedFiles] = useState<FileList | null>(null);

  const companySizes = ['startup', 'small', 'medium', 'large', 'enterprise'];
  const industries = [
    'Technology', 'Healthcare', 'Financial Services', 'Manufacturing', 
    'Retail', 'Government', 'Education', 'Energy', 'Transportation', 'Other'
  ];
  const complianceOptions = [
    'SOX', 'HIPAA', 'PCI DSS', 'GDPR', 'ISO 27001', 'NIST', 'SOC 2', 'FedRAMP'
  ];

  useEffect(() => {
    loadCompanyData();
  }, []);

  const loadCompanyData = async () => {
    try {
      setIsLoading(true);
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      
      // Load company profile if exists
      try {
        const profileResponse = await fetch(`${apiUrl}/company/1`);
        if (profileResponse.ok) {
          const profile = await profileResponse.json();
          setCompanyProfile(profile);
        }
      } catch {
        // Company profile doesn't exist yet, that's okay
      }

      // Load workspaces
      // Note: This would be implemented when the backend supports multiple companies
      setWorkspaces([]);
      setUploadedDocuments([]);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load company data');
    } finally {
      setIsLoading(false);
    }
  };

  const handleProfileSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      setIsLoading(true);
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      
      const response = await fetch(`${apiUrl}/company/workspace`, {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json',
        },
        body: JSON.stringify(companyProfile),
      });

      if (!response.ok) {
        throw new Error('Failed to save company profile');
      }

      const result = await response.json();
      setCompanyProfile(prev => ({ ...prev, id: result.company_id }));
      
      // Show success message or redirect
      alert('Company profile saved successfully!');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to save company profile');
    } finally {
      setIsLoading(false);
    }
  };

  const handleFileUpload = async () => {
    if (!selectedFiles || !companyProfile.id) return;

    try {
      setIsLoading(true);
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

      for (let i = 0; i < selectedFiles.length; i++) {
        const formData = new FormData();
        formData.append('file', selectedFiles[i]);
        formData.append('company_id', companyProfile.id.toString());

        const response = await fetch(`${apiUrl}/company/upload-ai`, {
          method: 'POST',
          body: formData,
        });

        if (!response.ok) {
          throw new Error(`Failed to upload ${selectedFiles[i].name}`);
        }
      }

      // Refresh documents list
      await loadCompanyData();
      setSelectedFiles(null);
      alert('Documents uploaded successfully!');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to upload documents');
    } finally {
      setIsLoading(false);
    }
  };

  const handleComplianceChange = (requirement: string, checked: boolean) => {
    setCompanyProfile(prev => ({
      ...prev,
      compliance_requirements: checked
        ? [...prev.compliance_requirements, requirement]
        : prev.compliance_requirements.filter(r => r !== requirement)
    }));
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-950 to-gray-900 text-white">
      {/* Header */}
      <header className="p-6 bg-gray-900/80 backdrop-blur-md shadow-lg">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div>
            <h1 className="text-4xl font-bold bg-gradient-to-r from-indigo-400 to-purple-500 bg-clip-text text-transparent mb-2">
              Company Data Management
            </h1>
            <p className="text-gray-300 text-lg">Manage company profile and upload documents for personalized assessments</p>
          </div>
          <button
            onClick={() => router.push('/')}
            className="px-4 py-2 bg-gray-700 text-white rounded-lg hover:bg-gray-600 transition"
          >
            ← Back to Dashboard
          </button>
        </div>
      </header>

      {/* Tab Navigation */}
      <div className="p-6">
        <div className="max-w-7xl mx-auto">
          <div className="flex border-b border-gray-700 mb-6">
            <button
              onClick={() => setActiveTab('profile')}
              className={`px-6 py-3 font-medium transition ${
                activeTab === 'profile'
                  ? 'border-b-2 border-indigo-500 text-indigo-400'
                  : 'text-gray-400 hover:text-gray-300'
              }`}
            >
              Company Profile
            </button>
            <button
              onClick={() => setActiveTab('documents')}
              className={`px-6 py-3 font-medium transition ${
                activeTab === 'documents'
                  ? 'border-b-2 border-indigo-500 text-indigo-400'
                  : 'text-gray-400 hover:text-gray-300'
              }`}
            >
              Documents
            </button>
            <button
              onClick={() => setActiveTab('workspaces')}
              className={`px-6 py-3 font-medium transition ${
                activeTab === 'workspaces'
                  ? 'border-b-2 border-indigo-500 text-indigo-400'
                  : 'text-gray-400 hover:text-gray-300'
              }`}
            >
              Workspaces
            </button>
          </div>

          {error && (
            <div className="bg-red-900/50 border border-red-500/50 p-4 rounded-lg mb-6">
              <p className="text-red-300">{error}</p>
              <button
                onClick={() => setError(null)}
                className="mt-2 px-3 py-1 bg-red-600 text-white rounded text-sm hover:bg-red-700 transition"
              >
                Dismiss
              </button>
            </div>
          )}

          {/* Company Profile Tab */}
          {activeTab === 'profile' && (
            <div className="bg-gray-800/50 rounded-lg p-6">
              <h2 className="text-2xl font-bold mb-6 flex items-center gap-2">
                <span>🏢</span> Company Profile
              </h2>
              <form onSubmit={handleProfileSubmit} className="space-y-6">
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-2">
                      Company Name *
                    </label>
                    <input
                      type="text"
                      required
                      value={companyProfile.name}
                      onChange={(e) => setCompanyProfile(prev => ({ ...prev, name: e.target.value }))}
                      className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:border-indigo-500"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-2">
                      Company Size *
                    </label>
                    <select
                      required
                      value={companyProfile.size}
                      onChange={(e) => setCompanyProfile(prev => ({ ...prev, size: e.target.value }))}
                      className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:border-indigo-500"
                    >
                      {companySizes.map(size => (
                        <option key={size} value={size}>
                          {size.charAt(0).toUpperCase() + size.slice(1)}
                        </option>
                      ))}
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-2">
                      Industry *
                    </label>
                    <select
                      required
                      value={companyProfile.industry}
                      onChange={(e) => setCompanyProfile(prev => ({ ...prev, industry: e.target.value }))}
                      className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:border-indigo-500"
                    >
                      <option value="">Select Industry</option>
                      {industries.map(industry => (
                        <option key={industry} value={industry}>
                          {industry}
                        </option>
                      ))}
                    </select>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-2">
                      Location
                    </label>
                    <input
                      type="text"
                      value={companyProfile.location}
                      onChange={(e) => setCompanyProfile(prev => ({ ...prev, location: e.target.value }))}
                      className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:border-indigo-500"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-2">
                      Employee Count
                    </label>
                    <input
                      type="number"
                      value={companyProfile.employee_count}
                      onChange={(e) => setCompanyProfile(prev => ({ ...prev, employee_count: parseInt(e.target.value) || 0 }))}
                      className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:border-indigo-500"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-2">
                      Annual Revenue
                    </label>
                    <input
                      type="text"
                      value={companyProfile.annual_revenue}
                      onChange={(e) => setCompanyProfile(prev => ({ ...prev, annual_revenue: e.target.value }))}
                      placeholder="e.g., $1M-$10M"
                      className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:border-indigo-500"
                    />
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Compliance Requirements
                  </label>
                  <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                    {complianceOptions.map(requirement => (
                      <label key={requirement} className="flex items-center space-x-2 cursor-pointer">
                        <input
                          type="checkbox"
                          checked={companyProfile.compliance_requirements.includes(requirement)}
                          onChange={(e) => handleComplianceChange(requirement, e.target.checked)}
                          className="rounded border-gray-600 text-indigo-600 focus:ring-indigo-500"
                        />
                        <span className="text-sm text-gray-300">{requirement}</span>
                      </label>
                    ))}
                  </div>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-300 mb-2">
                    Description
                  </label>
                  <textarea
                    value={companyProfile.description || ''}
                    onChange={(e) => setCompanyProfile(prev => ({ ...prev, description: e.target.value }))}
                    rows={4}
                    className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:border-indigo-500"
                    placeholder="Brief description of your company and security posture..."
                  />
                </div>

                <button
                  type="submit"
                  disabled={isLoading}
                  className="px-6 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition disabled:opacity-50"
                >
                  {isLoading ? 'Saving...' : 'Save Company Profile'}
                </button>
              </form>
            </div>
          )}

          {/* Documents Tab */}
          {activeTab === 'documents' && (
            <div className="space-y-6">
              {/* Upload Section */}
              <div className="bg-gray-800/50 rounded-lg p-6">
                <h2 className="text-2xl font-bold mb-6 flex items-center gap-2">
                  <span>📁</span> Document Upload
                </h2>
                
                {!companyProfile.id && (
                  <div className="bg-yellow-900/50 border border-yellow-500/50 p-4 rounded-lg mb-4">
                    <p className="text-yellow-300">Please save your company profile first before uploading documents.</p>
                  </div>
                )}

                <div className="border-2 border-dashed border-gray-600 rounded-lg p-8 text-center">
                  <input
                    type="file"
                    multiple
                    accept=".pdf,.doc,.docx,.txt"
                    onChange={(e) => setSelectedFiles(e.target.files)}
                    className="hidden"
                    id="file-upload"
                    disabled={!companyProfile.id}
                  />
                  <label
                    htmlFor="file-upload"
                    className={`cursor-pointer ${companyProfile.id ? 'text-indigo-400 hover:text-indigo-300' : 'text-gray-500'}`}
                  >
                    <div className="text-4xl mb-4">📄</div>
                    <p className="text-lg font-medium mb-2">
                      {selectedFiles ? `${selectedFiles.length} file(s) selected` : 'Click to upload documents'}
                    </p>
                    <p className="text-sm text-gray-400">
                      Supported formats: PDF, DOC, DOCX, TXT
                    </p>
                  </label>
                </div>

                {selectedFiles && selectedFiles.length > 0 && (
                  <div className="mt-4">
                    <h4 className="font-medium text-gray-300 mb-2">Selected Files:</h4>
                    <ul className="space-y-1">
                      {Array.from(selectedFiles).map((file, index) => (
                        <li key={index} className="text-sm text-gray-400">
                          {file.name} ({(file.size / 1024 / 1024).toFixed(2)} MB)
                        </li>
                      ))}
                    </ul>
                    <button
                      onClick={handleFileUpload}
                      disabled={isLoading || !companyProfile.id}
                      className="mt-4 px-6 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition disabled:opacity-50"
                    >
                      {isLoading ? 'Uploading...' : 'Upload Documents'}
                    </button>
                  </div>
                )}
              </div>

              {/* Uploaded Documents List */}
              <div className="bg-gray-800/50 rounded-lg p-6">
                <h3 className="text-xl font-bold mb-4">Uploaded Documents</h3>
                {uploadedDocuments.length === 0 ? (
                  <p className="text-gray-400">No documents uploaded yet.</p>
                ) : (
                  <div className="space-y-3">
                    {uploadedDocuments.map((doc) => (
                      <div key={doc.id} className="bg-gray-700/50 p-4 rounded-lg">
                        <div className="flex items-center justify-between">
                          <div>
                            <h4 className="font-medium text-gray-300">{doc.filename}</h4>
                            <p className="text-sm text-gray-400">
                              {doc.document_type} • {(doc.file_size / 1024 / 1024).toFixed(2)} MB • {doc.upload_date}
                            </p>
                          </div>
                          <span className={`px-2 py-1 rounded text-xs ${
                            doc.analysis_status === 'completed' ? 'bg-green-500/20 text-green-400' :
                            doc.analysis_status === 'processing' ? 'bg-yellow-500/20 text-yellow-400' :
                            'bg-gray-500/20 text-gray-400'
                          }`}>
                            {doc.analysis_status}
                          </span>
                        </div>
                        {doc.key_insights.length > 0 && (
                          <div className="mt-3">
                            <h5 className="text-sm font-medium text-gray-300 mb-1">Key Insights:</h5>
                            <ul className="text-sm text-gray-400 space-y-1">
                              {doc.key_insights.map((insight, index) => (
                                <li key={index}>• {insight}</li>
                              ))}
                            </ul>
                          </div>
                        )}
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Workspaces Tab */}
          {activeTab === 'workspaces' && (
            <div className="bg-gray-800/50 rounded-lg p-6">
              <h2 className="text-2xl font-bold mb-6 flex items-center gap-2">
                <span>🏗️</span> Company Workspaces
              </h2>
              {workspaces.length === 0 ? (
                <p className="text-gray-400">No additional workspaces created yet.</p>
              ) : (
                <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
                  {workspaces.map((workspace) => (
                    <div key={workspace.company_id} className="bg-gray-700/50 p-6 rounded-lg">
                      <h3 className="text-lg font-semibold text-gray-300 mb-2">{workspace.company_name}</h3>
                      <div className="space-y-2 text-sm text-gray-400">
                        <p>Created: {workspace.created_date}</p>
                        <p>Documents: {workspace.document_count}</p>
                        <p>Last Activity: {workspace.last_activity}</p>
                      </div>
                      <div className="mt-4">
                        <span className={`px-2 py-1 rounded text-xs ${
                          workspace.analysis_complete ? 'bg-green-500/20 text-green-400' : 'bg-yellow-500/20 text-yellow-400'
                        }`}>
                          {workspace.analysis_complete ? 'Analysis Complete' : 'In Progress'}
                        </span>
                      </div>
                    </div>
                  ))}
                </div>
              )}
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default CompanyPage;