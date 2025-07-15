import React, { useState, useEffect } from 'react';
import type { NextPage } from 'next';
import { useRouter } from 'next/router';

interface AssessmentSummary {
  id: number;
  company_name: string;
  assessment_date: string;
  overall_score: number;
  completion_percentage: number;
  risk_level: string;
  recommendations_count: number;
  framework_used: string;
}

interface ReportSection {
  section_name: string;
  score: number;
  max_score: number;
  risk_level: string;
  findings: string[];
  recommendations: string[];
  compliance_notes: string[];
}

interface DetailedReport {
  assessment_id: number;
  company_info: {
    name: string;
    size: string;
    industry: string;
    location: string;
  };
  assessment_metadata: {
    date: string;
    assessor: string;
    framework: string;
    version: string;
  };
  executive_summary: {
    overall_score: number;
    risk_level: string;
    key_findings: string[];
    critical_recommendations: string[];
    compliance_status: string;
  };
  sections: ReportSection[];
  appendices: {
    methodology: string;
    risk_matrix: string;
    compliance_mapping: string;
  };
}

const ReportsPage: NextPage = () => {
  const router = useRouter();
  const [assessments, setAssessments] = useState<AssessmentSummary[]>([]);
  const [selectedReport, setSelectedReport] = useState<DetailedReport | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [activeView, setActiveView] = useState<'list' | 'detail'>('list');
  const [exportFormat, setExportFormat] = useState<'pdf' | 'excel' | 'word'>('pdf');

  useEffect(() => {
    fetchAssessments();
  }, []);

  const fetchAssessments = async () => {
    try {
      setIsLoading(true);
      // const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      
      // Mock data for demonstration
      const mockAssessments: AssessmentSummary[] = [
        {
          id: 1,
          company_name: 'TechCorp Solutions',
          assessment_date: '2025-07-15',
          overall_score: 76,
          completion_percentage: 100,
          risk_level: 'Medium',
          recommendations_count: 12,
          framework_used: 'NIST CSF 2.0'
        },
        {
          id: 2,
          company_name: 'DataSecure Inc.',
          assessment_date: '2025-07-10',
          overall_score: 82,
          completion_percentage: 95,
          risk_level: 'Low',
          recommendations_count: 8,
          framework_used: 'ISO 27001'
        },
        {
          id: 3,
          company_name: 'CloudFirst Ltd.',
          assessment_date: '2025-07-05',
          overall_score: 68,
          completion_percentage: 100,
          risk_level: 'Medium-High',
          recommendations_count: 15,
          framework_used: 'NIST CSF 2.0'
        }
      ];

      setAssessments(mockAssessments);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load assessments');
    } finally {
      setIsLoading(false);
    }
  };

  const fetchDetailedReport = async (assessmentId: number) => {
    try {
      setIsLoading(true);
      
      // Mock detailed report
      const mockReport: DetailedReport = {
        assessment_id: assessmentId,
        company_info: {
          name: 'TechCorp Solutions',
          size: 'Medium (100-500 employees)',
          industry: 'Technology',
          location: 'San Francisco, CA'
        },
        assessment_metadata: {
          date: '2025-07-15',
          assessor: 'RiskAI Platform',
          framework: 'NIST Cybersecurity Framework 2.0',
          version: '2.0.1'
        },
        executive_summary: {
          overall_score: 76,
          risk_level: 'Medium',
          key_findings: [
            'Strong governance framework in place',
            'Access controls need improvement',
            'Incident response procedures are comprehensive',
            'Monitoring capabilities require enhancement'
          ],
          critical_recommendations: [
            'Implement multi-factor authentication across all systems',
            'Establish automated security monitoring',
            'Develop data classification scheme',
            'Conduct regular vulnerability assessments'
          ],
          compliance_status: 'Partially Compliant'
        },
        sections: [
          {
            section_name: 'Governance',
            score: 85,
            max_score: 100,
            risk_level: 'Low',
            findings: [
              'Comprehensive cybersecurity policy in place',
              'Regular board reporting on security matters',
              'Clear roles and responsibilities defined'
            ],
            recommendations: [
              'Establish cybersecurity metrics dashboard',
              'Implement third-party risk assessment process'
            ],
            compliance_notes: [
              'Meets ISO 27001 governance requirements',
              'Aligns with NIST CSF governance objectives'
            ]
          },
          {
            section_name: 'Identify',
            score: 72,
            max_score: 100,
            risk_level: 'Medium',
            findings: [
              'Asset inventory partially maintained',
              'Risk assessment conducted annually',
              'Business environment understood'
            ],
            recommendations: [
              'Implement automated asset discovery',
              'Increase risk assessment frequency to quarterly',
              'Develop data flow mapping'
            ],
            compliance_notes: [
              'Partial compliance with asset management standards'
            ]
          },
          {
            section_name: 'Protect',
            score: 78,
            max_score: 100,
            risk_level: 'Medium',
            findings: [
              'Access controls implemented but inconsistent',
              'Data protection measures in place',
              'Security awareness training provided'
            ],
            recommendations: [
              'Standardize access control implementation',
              'Implement data loss prevention tools',
              'Enhance security training program'
            ],
            compliance_notes: [
              'Meets basic protection requirements',
              'Additional controls needed for sensitive data'
            ]
          }
        ],
        appendices: {
          methodology: 'Assessment conducted using NIST CSF 2.0 framework with evidence-based scoring',
          risk_matrix: 'Risk levels determined using probability and impact matrix',
          compliance_mapping: 'Detailed mapping to ISO 27001, SOC 2, and regulatory requirements'
        }
      };

      setSelectedReport(mockReport);
      setActiveView('detail');
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load detailed report');
    } finally {
      setIsLoading(false);
    }
  };

  const handleExport = async (format: 'pdf' | 'excel' | 'word') => {
    try {
      if (!selectedReport) return;
      
      // Mock export functionality
      alert(`Exporting report as ${format.toUpperCase()}...`);
      
      // In real implementation, this would trigger a download
      const filename = `assessment-report-${selectedReport.assessment_id}.${format}`;
      console.log(`Would download: ${filename}`);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to export report');
    }
  };

  const getRiskLevelColor = (riskLevel: string): string => {
    switch (riskLevel.toLowerCase()) {
      case 'low': return 'text-green-400 bg-green-500/20';
      case 'medium': return 'text-yellow-400 bg-yellow-500/20';
      case 'medium-high': return 'text-orange-400 bg-orange-500/20';
      case 'high': return 'text-red-400 bg-red-500/20';
      case 'critical': return 'text-red-300 bg-red-600/20';
      default: return 'text-gray-400 bg-gray-500/20';
    }
  };

  const getScoreColor = (score: number): string => {
    if (score >= 90) return 'text-green-400';
    if (score >= 80) return 'text-blue-400';
    if (score >= 70) return 'text-yellow-400';
    if (score >= 60) return 'text-orange-400';
    return 'text-red-400';
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-950 to-gray-900 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-indigo-400 mx-auto mb-4"></div>
          <p className="text-white text-lg">Loading Assessment Reports...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-950 to-gray-900 flex items-center justify-center">
        <div className="text-center p-8 bg-red-900/50 rounded-lg max-w-md">
          <h2 className="text-red-400 text-xl font-bold mb-2">Error Loading Reports</h2>
          <p className="text-red-300 mb-4">{error}</p>
          <button
            onClick={fetchAssessments}
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

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-950 to-gray-900 text-white">
      {/* Header */}
      <header className="p-6 bg-gray-900/80 backdrop-blur-md shadow-lg">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div>
            <h1 className="text-4xl font-bold bg-gradient-to-r from-indigo-400 to-purple-500 bg-clip-text text-transparent mb-2">
              Assessment Reports
            </h1>
            <p className="text-gray-300 text-lg">Generate and manage comprehensive cybersecurity assessment reports</p>
          </div>
          <div className="flex gap-3">
            {activeView === 'detail' && (
              <button
                onClick={() => setActiveView('list')}
                className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition"
              >
                ← Back to List
              </button>
            )}
            <button
              onClick={() => router.push('/')}
              className="px-4 py-2 bg-gray-700 text-white rounded-lg hover:bg-gray-600 transition"
            >
              ← Back to Dashboard
            </button>
          </div>
        </div>
      </header>

      <div className="p-6">
        <div className="max-w-7xl mx-auto">
          {/* Assessment List View */}
          {activeView === 'list' && (
            <div className="space-y-6">
              <div className="bg-gray-800/50 rounded-lg p-6">
                <h2 className="text-2xl font-bold mb-6 flex items-center gap-2">
                  <span>📄</span> Recent Assessments
                </h2>
                
                {assessments.length === 0 ? (
                  <div className="text-center py-12">
                    <div className="text-6xl mb-4">📄</div>
                    <h3 className="text-xl font-semibold text-gray-300 mb-2">No Reports Available</h3>
                    <p className="text-gray-400 mb-6">Complete an assessment to generate your first report</p>
                    <button
                      onClick={() => router.push('/assessment')}
                      className="px-6 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition"
                    >
                      Start Assessment
                    </button>
                  </div>
                ) : (
                  <div className="space-y-4">
                    {assessments.map((assessment) => (
                      <div
                        key={assessment.id}
                        className="bg-gray-700/50 p-6 rounded-lg border border-gray-600 hover:border-gray-500 transition"
                      >
                        <div className="flex items-center justify-between mb-4">
                          <div>
                            <h3 className="text-xl font-semibold text-gray-300 mb-1">
                              {assessment.company_name}
                            </h3>
                            <p className="text-sm text-gray-400">
                              Assessment Date: {assessment.assessment_date} • Framework: {assessment.framework_used}
                            </p>
                          </div>
                          <div className="text-right">
                            <div className={`text-2xl font-bold ${getScoreColor(assessment.overall_score)}`}>
                              {assessment.overall_score}
                            </div>
                            <div className="text-sm text-gray-400">Overall Score</div>
                          </div>
                        </div>

                        <div className="grid grid-cols-1 md:grid-cols-4 gap-4 mb-4">
                          <div className="text-center">
                            <div className="text-lg font-semibold text-gray-300">
                              {assessment.completion_percentage}%
                            </div>
                            <div className="text-sm text-gray-400">Complete</div>
                          </div>
                          <div className="text-center">
                            <span className={`px-3 py-1 rounded-full text-sm font-medium ${getRiskLevelColor(assessment.risk_level)}`}>
                              {assessment.risk_level}
                            </span>
                            <div className="text-sm text-gray-400 mt-1">Risk Level</div>
                          </div>
                          <div className="text-center">
                            <div className="text-lg font-semibold text-gray-300">
                              {assessment.recommendations_count}
                            </div>
                            <div className="text-sm text-gray-400">Recommendations</div>
                          </div>
                          <div className="text-center">
                            <button
                              onClick={() => fetchDetailedReport(assessment.id)}
                              className="px-4 py-2 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition"
                            >
                              View Report
                            </button>
                          </div>
                        </div>
                      </div>
                    ))}
                  </div>
                )}
              </div>
            </div>
          )}

          {/* Detailed Report View */}
          {activeView === 'detail' && selectedReport && (
            <div className="space-y-6">
              {/* Report Header */}
              <div className="bg-gray-800/50 rounded-lg p-6">
                <div className="flex items-center justify-between mb-6">
                  <h2 className="text-2xl font-bold">Assessment Report</h2>
                  <div className="flex gap-3">
                    <select
                      value={exportFormat}
                      onChange={(e) => setExportFormat(e.target.value as 'pdf' | 'excel' | 'word')}
                      className="px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white focus:outline-none focus:border-indigo-500"
                    >
                      <option value="pdf">PDF Report</option>
                      <option value="excel">Excel Export</option>
                      <option value="word">Word Document</option>
                    </select>
                    <button
                      onClick={() => handleExport(exportFormat)}
                      className="px-4 py-2 bg-green-600 text-white rounded-lg hover:bg-green-700 transition"
                    >
                      Export {exportFormat.toUpperCase()}
                    </button>
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <h3 className="text-lg font-semibold text-gray-300 mb-3">Company Information</h3>
                    <div className="space-y-2 text-sm">
                      <div><span className="text-gray-400">Name:</span> <span className="text-gray-300">{selectedReport.company_info.name}</span></div>
                      <div><span className="text-gray-400">Size:</span> <span className="text-gray-300">{selectedReport.company_info.size}</span></div>
                      <div><span className="text-gray-400">Industry:</span> <span className="text-gray-300">{selectedReport.company_info.industry}</span></div>
                      <div><span className="text-gray-400">Location:</span> <span className="text-gray-300">{selectedReport.company_info.location}</span></div>
                    </div>
                  </div>
                  <div>
                    <h3 className="text-lg font-semibold text-gray-300 mb-3">Assessment Details</h3>
                    <div className="space-y-2 text-sm">
                      <div><span className="text-gray-400">Date:</span> <span className="text-gray-300">{selectedReport.assessment_metadata.date}</span></div>
                      <div><span className="text-gray-400">Framework:</span> <span className="text-gray-300">{selectedReport.assessment_metadata.framework}</span></div>
                      <div><span className="text-gray-400">Version:</span> <span className="text-gray-300">{selectedReport.assessment_metadata.version}</span></div>
                      <div><span className="text-gray-400">Assessor:</span> <span className="text-gray-300">{selectedReport.assessment_metadata.assessor}</span></div>
                    </div>
                  </div>
                </div>
              </div>

              {/* Executive Summary */}
              <div className="bg-gray-800/50 rounded-lg p-6">
                <h3 className="text-xl font-bold mb-4 flex items-center gap-2">
                  <span>📋</span> Executive Summary
                </h3>
                
                <div className="grid grid-cols-1 md:grid-cols-3 gap-6 mb-6">
                  <div className="text-center">
                    <div className={`text-3xl font-bold ${getScoreColor(selectedReport.executive_summary.overall_score)}`}>
                      {selectedReport.executive_summary.overall_score}
                    </div>
                    <div className="text-sm text-gray-400">Overall Score</div>
                  </div>
                  <div className="text-center">
                    <span className={`px-4 py-2 rounded-full font-medium ${getRiskLevelColor(selectedReport.executive_summary.risk_level)}`}>
                      {selectedReport.executive_summary.risk_level}
                    </span>
                    <div className="text-sm text-gray-400 mt-2">Risk Level</div>
                  </div>
                  <div className="text-center">
                    <div className="text-lg font-semibold text-gray-300">
                      {selectedReport.executive_summary.compliance_status}
                    </div>
                    <div className="text-sm text-gray-400">Compliance Status</div>
                  </div>
                </div>

                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <h4 className="font-semibold text-gray-300 mb-3">Key Findings</h4>
                    <ul className="space-y-2">
                      {selectedReport.executive_summary.key_findings.map((finding, index) => (
                        <li key={index} className="flex items-start gap-2">
                          <span className="text-blue-400 mt-1">•</span>
                          <span className="text-gray-300 text-sm">{finding}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                  <div>
                    <h4 className="font-semibold text-gray-300 mb-3">Critical Recommendations</h4>
                    <ul className="space-y-2">
                      {selectedReport.executive_summary.critical_recommendations.map((rec, index) => (
                        <li key={index} className="flex items-start gap-2">
                          <span className="text-red-400 mt-1">!</span>
                          <span className="text-gray-300 text-sm">{rec}</span>
                        </li>
                      ))}
                    </ul>
                  </div>
                </div>
              </div>

              {/* Section Details */}
              <div className="bg-gray-800/50 rounded-lg p-6">
                <h3 className="text-xl font-bold mb-6 flex items-center gap-2">
                  <span>📊</span> Detailed Section Analysis
                </h3>
                
                <div className="space-y-6">
                  {selectedReport.sections.map((section, index) => (
                    <div key={index} className="bg-gray-700/50 p-6 rounded-lg">
                      <div className="flex items-center justify-between mb-4">
                        <h4 className="text-lg font-semibold text-gray-300">{section.section_name}</h4>
                        <div className="flex items-center gap-4">
                          <span className={`px-3 py-1 rounded-full text-sm font-medium ${getRiskLevelColor(section.risk_level)}`}>
                            {section.risk_level}
                          </span>
                          <span className={`text-xl font-bold ${getScoreColor(section.score)}`}>
                            {section.score}/{section.max_score}
                          </span>
                        </div>
                      </div>

                      <div className="grid grid-cols-1 md:grid-cols-3 gap-6">
                        <div>
                          <h5 className="font-medium text-gray-300 mb-2">Findings</h5>
                          <ul className="space-y-1">
                            {section.findings.map((finding, idx) => (
                              <li key={idx} className="text-sm text-gray-400 flex items-start gap-2">
                                <span className="text-green-400 mt-1">✓</span>
                                {finding}
                              </li>
                            ))}
                          </ul>
                        </div>
                        <div>
                          <h5 className="font-medium text-gray-300 mb-2">Recommendations</h5>
                          <ul className="space-y-1">
                            {section.recommendations.map((rec, idx) => (
                              <li key={idx} className="text-sm text-gray-400 flex items-start gap-2">
                                <span className="text-yellow-400 mt-1">→</span>
                                {rec}
                              </li>
                            ))}
                          </ul>
                        </div>
                        <div>
                          <h5 className="font-medium text-gray-300 mb-2">Compliance Notes</h5>
                          <ul className="space-y-1">
                            {section.compliance_notes.map((note, idx) => (
                              <li key={idx} className="text-sm text-gray-400 flex items-start gap-2">
                                <span className="text-blue-400 mt-1">ℹ</span>
                                {note}
                              </li>
                            ))}
                          </ul>
                        </div>
                      </div>
                    </div>
                  ))}
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
};

export default ReportsPage;