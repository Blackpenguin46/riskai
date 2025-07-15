import React, { useState } from 'react';
import type { NextPage } from 'next';
import { useRouter } from 'next/router';

interface SystemSettings {
  notifications: {
    email_alerts: boolean;
    assessment_reminders: boolean;
    security_updates: boolean;
    weekly_reports: boolean;
  };
  assessment: {
    default_framework: string;
    auto_save_interval: number;
    scoring_methodology: string;
    compliance_standards: string[];
  };
  security: {
    session_timeout: number;
    password_requirements: {
      min_length: number;
      require_uppercase: boolean;
      require_lowercase: boolean;
      require_numbers: boolean;
      require_symbols: boolean;
    };
    two_factor_auth: boolean;
    login_attempts: number;
  };
  integration: {
    api_enabled: boolean;
    webhook_url: string;
    export_formats: string[];
    data_retention_days: number;
  };
  appearance: {
    theme: 'dark' | 'light' | 'auto';
    language: string;
    timezone: string;
    dashboard_layout: 'grid' | 'list';
  };
}

interface UserProfile {
  name: string;
  email: string;
  role: string;
  organization: string;
  last_login: string;
  assessments_completed: number;
}

const SettingsPage: NextPage = () => {
  const router = useRouter();
  const [settings, setSettings] = useState<SystemSettings>({
    notifications: {
      email_alerts: true,
      assessment_reminders: true,
      security_updates: true,
      weekly_reports: false
    },
    assessment: {
      default_framework: 'NIST CSF 2.0',
      auto_save_interval: 300,
      scoring_methodology: 'evidence_based',
      compliance_standards: ['ISO 27001', 'SOC 2']
    },
    security: {
      session_timeout: 3600,
      password_requirements: {
        min_length: 8,
        require_uppercase: true,
        require_lowercase: true,
        require_numbers: true,
        require_symbols: false
      },
      two_factor_auth: false,
      login_attempts: 5
    },
    integration: {
      api_enabled: false,
      webhook_url: '',
      export_formats: ['PDF', 'Excel'],
      data_retention_days: 365
    },
    appearance: {
      theme: 'dark',
      language: 'en',
      timezone: 'UTC',
      dashboard_layout: 'grid'
    }
  });

  const [userProfile, setUserProfile] = useState<UserProfile>({
    name: 'System Administrator',
    email: 'admin@company.com',
    role: 'Administrator',
    organization: 'TechCorp Solutions',
    last_login: '2025-07-15 10:30 AM',
    assessments_completed: 12
  });

  const [activeTab, setActiveTab] = useState<'general' | 'security' | 'assessment' | 'integration' | 'profile'>('general');
  const [isLoading, setIsLoading] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [successMessage, setSuccessMessage] = useState<string | null>(null);

  const frameworks = ['NIST CSF 2.0', 'ISO 27001', 'CIS Controls', 'NIST AI RMF'];
  const languages = ['English', 'Spanish', 'French', 'German', 'Japanese'];
  const timezones = ['UTC', 'EST', 'PST', 'GMT', 'CET'];
  const complianceStandards = ['ISO 27001', 'SOC 2', 'PCI DSS', 'HIPAA', 'GDPR', 'FedRAMP'];

  const handleSaveSettings = async () => {
    try {
      setIsLoading(true);
      setError(null);
      
      // Mock save operation
      await new Promise(resolve => setTimeout(resolve, 1000));
      
      setSuccessMessage('Settings saved successfully!');
      setTimeout(() => setSuccessMessage(null), 3000);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to save settings');
    } finally {
      setIsLoading(false);
    }
  };

  const handleResetSettings = () => {
    if (confirm('Are you sure you want to reset all settings to default values?')) {
      // Reset to default settings
      setSettings({
        notifications: {
          email_alerts: true,
          assessment_reminders: true,
          security_updates: true,
          weekly_reports: false
        },
        assessment: {
          default_framework: 'NIST CSF 2.0',
          auto_save_interval: 300,
          scoring_methodology: 'evidence_based',
          compliance_standards: ['ISO 27001']
        },
        security: {
          session_timeout: 3600,
          password_requirements: {
            min_length: 8,
            require_uppercase: true,
            require_lowercase: true,
            require_numbers: true,
            require_symbols: false
          },
          two_factor_auth: false,
          login_attempts: 5
        },
        integration: {
          api_enabled: false,
          webhook_url: '',
          export_formats: ['PDF'],
          data_retention_days: 365
        },
        appearance: {
          theme: 'dark',
          language: 'en',
          timezone: 'UTC',
          dashboard_layout: 'grid'
        }
      });
      setSuccessMessage('Settings reset to defaults');
      setTimeout(() => setSuccessMessage(null), 3000);
    }
  };

  const updateNestedSetting = <T extends keyof SystemSettings>(
    category: T,
    key: keyof SystemSettings[T],
    value: unknown
  ) => {
    setSettings(prev => ({
      ...prev,
      [category]: {
        ...prev[category],
        [key]: value as SystemSettings[T][keyof SystemSettings[T]]
      }
    }));
  };

  const updateComplianceStandards = (standard: string, checked: boolean) => {
    setSettings(prev => ({
      ...prev,
      assessment: {
        ...prev.assessment,
        compliance_standards: checked
          ? [...prev.assessment.compliance_standards, standard]
          : prev.assessment.compliance_standards.filter(s => s !== standard)
      }
    }));
  };

  const updateExportFormats = (format: string, checked: boolean) => {
    setSettings(prev => ({
      ...prev,
      integration: {
        ...prev.integration,
        export_formats: checked
          ? [...prev.integration.export_formats, format]
          : prev.integration.export_formats.filter(f => f !== format)
      }
    }));
  };

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-950 to-gray-900 text-white">
      {/* Header */}
      <header className="p-6 bg-gray-900/80 backdrop-blur-md shadow-lg">
        <div className="max-w-7xl mx-auto flex items-center justify-between">
          <div>
            <h1 className="text-4xl font-bold bg-gradient-to-r from-indigo-400 to-purple-500 bg-clip-text text-transparent mb-2">
              System Settings
            </h1>
            <p className="text-gray-300 text-lg">Configure system preferences and security options</p>
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
          {/* Success/Error Messages */}
          {successMessage && (
            <div className="bg-green-900/50 border border-green-500/50 p-4 rounded-lg mb-6">
              <p className="text-green-300">{successMessage}</p>
            </div>
          )}
          
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

          {/* Tab Navigation */}
          <div className="flex border-b border-gray-700 mb-6 overflow-x-auto">
            {[
              { id: 'general', label: 'General', icon: '⚙️' },
              { id: 'security', label: 'Security', icon: '🔒' },
              { id: 'assessment', label: 'Assessment', icon: '📊' },
              { id: 'integration', label: 'Integration', icon: '🔗' },
              { id: 'profile', label: 'Profile', icon: '👤' }
            ].map((tab) => (
              <button
                key={tab.id}
                onClick={() => setActiveTab(tab.id as typeof activeTab)}
                className={`px-6 py-3 font-medium transition whitespace-nowrap ${
                  activeTab === tab.id
                    ? 'border-b-2 border-indigo-500 text-indigo-400'
                    : 'text-gray-400 hover:text-gray-300'
                }`}
              >
                <span className="mr-2">{tab.icon}</span>
                {tab.label}
              </button>
            ))}
          </div>

          {/* General Settings */}
          {activeTab === 'general' && (
            <div className="space-y-6">
              <div className="bg-gray-800/50 rounded-lg p-6">
                <h3 className="text-xl font-bold mb-4">Appearance</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-2">Theme</label>
                    <select
                      value={settings.appearance.theme}
                      onChange={(e) => updateNestedSetting('appearance', 'theme', e.target.value)}
                      className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white"
                    >
                      <option value="dark">Dark</option>
                      <option value="light">Light</option>
                      <option value="auto">Auto</option>
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-2">Language</label>
                    <select
                      value={settings.appearance.language}
                      onChange={(e) => updateNestedSetting('appearance', 'language', e.target.value)}
                      className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white"
                    >
                      {languages.map(lang => (
                        <option key={lang} value={lang.toLowerCase()}>{lang}</option>
                      ))}
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-2">Timezone</label>
                    <select
                      value={settings.appearance.timezone}
                      onChange={(e) => updateNestedSetting('appearance', 'timezone', e.target.value)}
                      className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white"
                    >
                      {timezones.map(tz => (
                        <option key={tz} value={tz}>{tz}</option>
                      ))}
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-2">Dashboard Layout</label>
                    <select
                      value={settings.appearance.dashboard_layout}
                      onChange={(e) => updateNestedSetting('appearance', 'dashboard_layout', e.target.value)}
                      className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white"
                    >
                      <option value="grid">Grid</option>
                      <option value="list">List</option>
                    </select>
                  </div>
                </div>
              </div>

              <div className="bg-gray-800/50 rounded-lg p-6">
                <h3 className="text-xl font-bold mb-4">Notifications</h3>
                <div className="space-y-4">
                  {Object.entries(settings.notifications).map(([key, value]) => (
                    <label key={key} className="flex items-center space-x-3 cursor-pointer">
                      <input
                        type="checkbox"
                        checked={value}
                        onChange={(e) => updateNestedSetting('notifications', key as keyof SystemSettings['notifications'], e.target.checked)}
                        className="rounded border-gray-600 text-indigo-600 focus:ring-indigo-500"
                      />
                      <span className="text-gray-300">
                        {key.replace(/_/g, ' ').replace(/\b\w/g, l => l.toUpperCase())}
                      </span>
                    </label>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* Security Settings */}
          {activeTab === 'security' && (
            <div className="space-y-6">
              <div className="bg-gray-800/50 rounded-lg p-6">
                <h3 className="text-xl font-bold mb-4">Authentication</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-2">
                      Session Timeout (seconds)
                    </label>
                    <input
                      type="number"
                      value={settings.security.session_timeout}
                      onChange={(e) => updateNestedSetting('security', 'session_timeout', parseInt(e.target.value))}
                      className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-2">
                      Max Login Attempts
                    </label>
                    <input
                      type="number"
                      value={settings.security.login_attempts}
                      onChange={(e) => updateNestedSetting('security', 'login_attempts', parseInt(e.target.value))}
                      className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white"
                    />
                  </div>
                </div>
                
                <div className="mt-4">
                  <label className="flex items-center space-x-3 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={settings.security.two_factor_auth}
                      onChange={(e) => updateNestedSetting('security', 'two_factor_auth', e.target.checked)}
                      className="rounded border-gray-600 text-indigo-600 focus:ring-indigo-500"
                    />
                    <span className="text-gray-300">Enable Two-Factor Authentication</span>
                  </label>
                </div>
              </div>

              <div className="bg-gray-800/50 rounded-lg p-6">
                <h3 className="text-xl font-bold mb-4">Password Requirements</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-2">
                      Minimum Length
                    </label>
                    <input
                      type="number"
                      value={settings.security.password_requirements.min_length}
                      onChange={(e) => setSettings(prev => ({
                        ...prev,
                        security: {
                          ...prev.security,
                          password_requirements: {
                            ...prev.security.password_requirements,
                            min_length: parseInt(e.target.value)
                          }
                        }
                      }))}
                      className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white"
                    />
                  </div>
                  <div className="space-y-3">
                    {Object.entries(settings.security.password_requirements).map(([key, value]) => {
                      if (key === 'min_length') return null;
                      return (
                        <label key={key} className="flex items-center space-x-3 cursor-pointer">
                          <input
                            type="checkbox"
                            checked={value as boolean}
                            onChange={(e) => setSettings(prev => ({
                              ...prev,
                              security: {
                                ...prev.security,
                                password_requirements: {
                                  ...prev.security.password_requirements,
                                  [key]: e.target.checked
                                }
                              }
                            }))}
                            className="rounded border-gray-600 text-indigo-600 focus:ring-indigo-500"
                          />
                          <span className="text-gray-300">
                            {key.replace(/require_|_/g, ' ').replace(/\b\w/g, l => l.toUpperCase()).trim()}
                          </span>
                        </label>
                      );
                    })}
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Assessment Settings */}
          {activeTab === 'assessment' && (
            <div className="space-y-6">
              <div className="bg-gray-800/50 rounded-lg p-6">
                <h3 className="text-xl font-bold mb-4">Assessment Configuration</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-2">
                      Default Framework
                    </label>
                    <select
                      value={settings.assessment.default_framework}
                      onChange={(e) => updateNestedSetting('assessment', 'default_framework', e.target.value)}
                      className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white"
                    >
                      {frameworks.map(framework => (
                        <option key={framework} value={framework}>{framework}</option>
                      ))}
                    </select>
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-2">
                      Auto-save Interval (seconds)
                    </label>
                    <input
                      type="number"
                      value={settings.assessment.auto_save_interval}
                      onChange={(e) => updateNestedSetting('assessment', 'auto_save_interval', parseInt(e.target.value))}
                      className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white"
                    />
                  </div>
                </div>

                <div className="mt-6">
                  <label className="block text-sm font-medium text-gray-300 mb-3">
                    Compliance Standards
                  </label>
                  <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
                    {complianceStandards.map(standard => (
                      <label key={standard} className="flex items-center space-x-2 cursor-pointer">
                        <input
                          type="checkbox"
                          checked={settings.assessment.compliance_standards.includes(standard)}
                          onChange={(e) => updateComplianceStandards(standard, e.target.checked)}
                          className="rounded border-gray-600 text-indigo-600 focus:ring-indigo-500"
                        />
                        <span className="text-sm text-gray-300">{standard}</span>
                      </label>
                    ))}
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Integration Settings */}
          {activeTab === 'integration' && (
            <div className="space-y-6">
              <div className="bg-gray-800/50 rounded-lg p-6">
                <h3 className="text-xl font-bold mb-4">API Configuration</h3>
                <div className="space-y-4">
                  <label className="flex items-center space-x-3 cursor-pointer">
                    <input
                      type="checkbox"
                      checked={settings.integration.api_enabled}
                      onChange={(e) => updateNestedSetting('integration', 'api_enabled', e.target.checked)}
                      className="rounded border-gray-600 text-indigo-600 focus:ring-indigo-500"
                    />
                    <span className="text-gray-300">Enable API Access</span>
                  </label>

                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-2">
                      Webhook URL
                    </label>
                    <input
                      type="url"
                      value={settings.integration.webhook_url}
                      onChange={(e) => updateNestedSetting('integration', 'webhook_url', e.target.value)}
                      placeholder="https://example.com/webhook"
                      className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white"
                    />
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-2">
                      Data Retention (days)
                    </label>
                    <input
                      type="number"
                      value={settings.integration.data_retention_days}
                      onChange={(e) => updateNestedSetting('integration', 'data_retention_days', parseInt(e.target.value))}
                      className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white"
                    />
                  </div>
                </div>
              </div>

              <div className="bg-gray-800/50 rounded-lg p-6">
                <h3 className="text-xl font-bold mb-4">Export Formats</h3>
                <div className="grid grid-cols-2 md:grid-cols-4 gap-3">
                  {['PDF', 'Excel', 'Word', 'JSON'].map(format => (
                    <label key={format} className="flex items-center space-x-2 cursor-pointer">
                      <input
                        type="checkbox"
                        checked={settings.integration.export_formats.includes(format)}
                        onChange={(e) => updateExportFormats(format, e.target.checked)}
                        className="rounded border-gray-600 text-indigo-600 focus:ring-indigo-500"
                      />
                      <span className="text-sm text-gray-300">{format}</span>
                    </label>
                  ))}
                </div>
              </div>
            </div>
          )}

          {/* Profile Settings */}
          {activeTab === 'profile' && (
            <div className="space-y-6">
              <div className="bg-gray-800/50 rounded-lg p-6">
                <h3 className="text-xl font-bold mb-4">User Profile</h3>
                <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-2">Name</label>
                    <input
                      type="text"
                      value={userProfile.name}
                      onChange={(e) => setUserProfile(prev => ({ ...prev, name: e.target.value }))}
                      className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-2">Email</label>
                    <input
                      type="email"
                      value={userProfile.email}
                      onChange={(e) => setUserProfile(prev => ({ ...prev, email: e.target.value }))}
                      className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-2">Role</label>
                    <input
                      type="text"
                      value={userProfile.role}
                      onChange={(e) => setUserProfile(prev => ({ ...prev, role: e.target.value }))}
                      className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white"
                    />
                  </div>
                  <div>
                    <label className="block text-sm font-medium text-gray-300 mb-2">Organization</label>
                    <input
                      type="text"
                      value={userProfile.organization}
                      onChange={(e) => setUserProfile(prev => ({ ...prev, organization: e.target.value }))}
                      className="w-full px-3 py-2 bg-gray-700 border border-gray-600 rounded-lg text-white"
                    />
                  </div>
                </div>

                <div className="mt-6 grid grid-cols-1 md:grid-cols-2 gap-6">
                  <div className="bg-gray-700/50 p-4 rounded-lg">
                    <h4 className="font-medium text-gray-300 mb-2">Account Statistics</h4>
                    <div className="space-y-2 text-sm">
                      <div><span className="text-gray-400">Last Login:</span> <span className="text-gray-300">{userProfile.last_login}</span></div>
                      <div><span className="text-gray-400">Assessments Completed:</span> <span className="text-gray-300">{userProfile.assessments_completed}</span></div>
                    </div>
                  </div>
                  <div className="bg-gray-700/50 p-4 rounded-lg">
                    <h4 className="font-medium text-gray-300 mb-2">Actions</h4>
                    <div className="space-y-2">
                      <button className="w-full px-3 py-2 bg-blue-600 text-white rounded text-sm hover:bg-blue-700 transition">
                        Change Password
                      </button>
                      <button className="w-full px-3 py-2 bg-red-600 text-white rounded text-sm hover:bg-red-700 transition">
                        Export Account Data
                      </button>
                    </div>
                  </div>
                </div>
              </div>
            </div>
          )}

          {/* Action Buttons */}
          <div className="flex justify-between items-center pt-6 border-t border-gray-700">
            <button
              onClick={handleResetSettings}
              className="px-6 py-3 bg-gray-600 text-white rounded-lg hover:bg-gray-700 transition"
            >
              Reset to Defaults
            </button>
            <button
              onClick={handleSaveSettings}
              disabled={isLoading}
              className="px-6 py-3 bg-indigo-600 text-white rounded-lg hover:bg-indigo-700 transition disabled:opacity-50"
            >
              {isLoading ? 'Saving...' : 'Save Settings'}
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

export default SettingsPage;