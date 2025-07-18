import React, { useState, useEffect } from 'react';
import type { NextPage } from 'next';
import { useRouter } from 'next/router';

// --- Type Definitions ---
interface DashboardCard {
  id: string;
  title: string;
  description: string;
  icon: string;
  category: string;
  route: string;
  enabled: boolean;
  badge?: string;
  priority: string;
  estimated_time?: string;
  features: string[];
}

interface DashboardProgress {
  in_progress: boolean;
  completed: boolean;
  completion_percentage: number;
  sections_completed: number;
  total_sections: number;
  estimated_time_remaining: string;
}

interface QuickAction {
  id: string;
  title: string;
  description: string;
  icon: string;
  route: string;
  primary: boolean;
  enabled?: boolean;
}

interface DashboardData {
  dashboard_info: {
    title: string;
    subtitle: string;
    version: string;
    description: string;
  };
  navigation_cards: DashboardCard[];
  cards_by_category: { [key: string]: DashboardCard[] };
  assessment_progress: DashboardProgress;
  quick_actions: QuickAction[];
  featured_frameworks: Array<{
    name: string;
    description: string;
    coverage: string;
    icon: string;
  }>;
}

const MainDashboard: NextPage = () => {
  const [dashboardData, setDashboardData] = useState<DashboardData | null>(null);
  const [isLoading, setIsLoading] = useState(true);
  const [error, setError] = useState<string | null>(null);
  const [selectedCategory, setSelectedCategory] = useState<string>('all');
  const router = useRouter();

  useEffect(() => {
    fetchDashboardData();
    fetchAssessmentProgress();
  }, []);

  const fetchAssessmentProgress = async () => {
    try {
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const response = await fetch(`${apiUrl}/assessment/latest`);
      if (response.ok) {
        const data = await response.json();
        if (data && data.status === 'in_progress') {
          // Update dashboard data with real assessment progress
          setDashboardData(prev => {
            if (!prev) return prev;
            return {
              ...prev,
              assessment_progress: {
                in_progress: true,
                completed: false,
                completion_percentage: data.completion_percentage || 0,
                sections_completed: data.sections_completed || 0,
                total_sections: 10, // Standard number of sections
                estimated_time_remaining: calculateTimeRemaining(data.completion_percentage || 0)
              },
              quick_actions: prev.quick_actions.map(action => {
                if (action.id === 'continue_assessment') {
                  return { ...action, enabled: true };
                }
                return action;
              })
            };
          });
        }
      }
    } catch (err) {
      console.error('Failed to fetch assessment progress:', err);
    }
  };

  const calculateTimeRemaining = (completionPercentage: number): string => {
    const totalMinutes = 45; // Estimated total time for assessment
    const remainingMinutes = Math.round((totalMinutes * (100 - completionPercentage)) / 100);
    if (remainingMinutes <= 0) return "Almost done!";
    if (remainingMinutes < 60) return `${remainingMinutes} min`;
    const hours = Math.floor(remainingMinutes / 60);
    const minutes = remainingMinutes % 60;
    return `${hours}h ${minutes}m`;
  };

  const fetchDashboardData = async () => {
    try {
      setIsLoading(true);
      const apiUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
      const response = await fetch(`${apiUrl}/`);
      if (!response.ok) {
        throw new Error(`Failed to fetch dashboard data: ${response.status}`);
      }
      const data: DashboardData = await response.json();
      setDashboardData(data);
    } catch (err) {
      setError(err instanceof Error ? err.message : 'Failed to load dashboard');
    } finally {
      setIsLoading(false);
    }
  };

  const handleCardClick = (route: string) => {
    if (route === '/assessment/dashboard') {
      router.push('/assessment');
    } else if (route === '/chat') {
      router.push('/chat');
    } else if (route === '/metrics') {
      router.push('/metrics');
    } else if (route === '/benchmarks') {
      router.push('/benchmarks');
    } else if (route === '/company') {
      router.push('/company');
    } else if (route === '/scoring') {
      router.push('/scoring');
    } else if (route === '/reports') {
      router.push('/reports');
    } else if (route === '/settings') {
      router.push('/settings');
    } else {
      // Fallback for unknown routes
      router.push(route);
    }
  };

  const handleQuickAction = (action: QuickAction) => {
    if (!action.enabled && action.enabled !== undefined) {
      return;
    }
    handleCardClick(action.route);
  };

  const getCardsByCategory = (category: string): DashboardCard[] => {
    if (!dashboardData) return [];
    if (category === 'all') return dashboardData.navigation_cards;
    return dashboardData.cards_by_category[category] || [];
  };

  const getPriorityColor = (priority: string): string => {
    switch (priority) {
      case 'high': return 'border-red-500 bg-red-50';
      case 'medium': return 'border-yellow-500 bg-yellow-50';
      case 'low': return 'border-green-500 bg-green-50';
      default: return 'border-gray-500 bg-gray-50';
    }
  };

  const getCompletionColor = (percentage: number): string => {
    if (percentage >= 100) return 'text-green-600';
    if (percentage >= 50) return 'text-yellow-600';
    return 'text-red-600';
  };

  if (isLoading) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-950 to-gray-900 flex items-center justify-center">
        <div className="text-center">
          <div className="animate-spin rounded-full h-16 w-16 border-b-2 border-indigo-400 mx-auto mb-4"></div>
          <p className="text-white text-lg">Loading RiskAI Dashboard...</p>
        </div>
      </div>
    );
  }

  if (error) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-950 to-gray-900 flex items-center justify-center">
        <div className="text-center p-8 bg-red-900/50 rounded-lg max-w-md">
          <h2 className="text-red-400 text-xl font-bold mb-2">Error Loading Dashboard</h2>
          <p className="text-red-300 mb-4">{error}</p>
          <button
            onClick={fetchDashboardData}
            className="px-4 py-2 bg-red-600 text-white rounded-lg hover:bg-red-700 transition"
          >
            Retry
          </button>
        </div>
      </div>
    );
  }

  if (!dashboardData) {
    return (
      <div className="min-h-screen bg-gradient-to-br from-gray-950 to-gray-900 flex items-center justify-center">
        <p className="text-white text-lg">No dashboard data available</p>
      </div>
    );
  }

  const categories = ['all', ...Object.keys(dashboardData.cards_by_category)];

  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-950 to-gray-900 text-white">
      {/* Header */}
      <header className="p-6 bg-gray-900/80 backdrop-blur-md shadow-lg">
        <div className="max-w-7xl mx-auto">
          <h1 className="text-4xl font-bold bg-gradient-to-r from-indigo-400 to-purple-500 bg-clip-text text-transparent mb-2">
            {dashboardData.dashboard_info.title}
          </h1>
          <p className="text-gray-300 text-lg mb-4">{dashboardData.dashboard_info.subtitle}</p>
          <p className="text-gray-400">{dashboardData.dashboard_info.description}</p>
        </div>
      </header>

      {/* Assessment Progress Banner */}
      {dashboardData.assessment_progress && dashboardData.assessment_progress.in_progress && (
        <div className="bg-indigo-900/50 border-l-4 border-indigo-400 p-4 mx-6 mt-6 rounded-r-lg">
          <div className="flex items-center justify-between">
            <div>
              <h3 className="text-indigo-300 font-semibold">Assessment In Progress</h3>
              <p className="text-gray-300">
                {dashboardData.assessment_progress.sections_completed} of {dashboardData.assessment_progress.total_sections} sections completed
              </p>
            </div>
            <div className="flex items-center gap-4">
              <div className="text-right">
                <div className={`text-2xl font-bold ${getCompletionColor(dashboardData.assessment_progress.completion_percentage)}`}>
                  {dashboardData.assessment_progress.completion_percentage.toFixed(0)}%
                </div>
                <div className="text-sm text-gray-400">
                  {dashboardData.assessment_progress.estimated_time_remaining} remaining
                </div>
              </div>
              <button
                onClick={() => router.push('/assessment')}
                className="bg-indigo-600 hover:bg-indigo-700 text-white px-4 py-2 rounded-lg font-semibold transition"
              >
                Continue Assessment
              </button>
            </div>
          </div>
        </div>
      )}

      {/* Quick Actions */}
      <div className="p-6">
        <div className="max-w-7xl mx-auto">
          <h2 className="text-2xl font-bold mb-4">Quick Actions</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-4 mb-8">
            {dashboardData.quick_actions.filter(action => action.id !== 'start_assessment').map((action) => (
              <button
                key={action.id}
                onClick={() => handleQuickAction(action)}
                disabled={action.enabled === false}
                className={`p-4 rounded-lg border-2 transition-all duration-200 ${
                  action.primary
                    ? 'bg-indigo-600 border-indigo-500 hover:bg-indigo-700 text-white'
                    : 'bg-gray-800 border-gray-700 hover:bg-gray-700 text-gray-300'
                } ${
                  action.enabled === false ? 'opacity-50 cursor-not-allowed' : 'cursor-pointer'
                }`}
              >
                <div className="text-2xl mb-2">{action.icon}</div>
                <h3 className="font-semibold mb-1">{action.title}</h3>
                <p className="text-sm opacity-90">{action.description}</p>
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Category Filter */}
      <div className="px-6">
        <div className="max-w-7xl mx-auto">
          <div className="flex flex-wrap gap-2 mb-6">
            {categories.map((category) => (
              <button
                key={category}
                onClick={() => setSelectedCategory(category)}
                className={`px-4 py-2 rounded-lg transition ${
                  selectedCategory === category
                    ? 'bg-indigo-600 text-white'
                    : 'bg-gray-800 text-gray-300 hover:bg-gray-700'
                }`}
              >
                {category === 'all' ? 'All Features' : category}
              </button>
            ))}
          </div>
        </div>
      </div>

      {/* Main Dashboard Cards */}
      <div className="p-6">
        <div className="max-w-7xl mx-auto">
          <div className="grid grid-cols-1 md:grid-cols-2 gap-8">
            {getCardsByCategory(selectedCategory).map((card) => (
              <div
                key={card.id}
                onClick={() => card.enabled && handleCardClick(card.route)}
                className={`bg-gray-800/60 backdrop-blur-md rounded-xl p-8 border-2 transition-all duration-300 cursor-pointer hover:bg-gray-700/70 hover:scale-105 hover:shadow-2xl ${getPriorityColor(card.priority)} ${
                  !card.enabled ? 'opacity-50 cursor-not-allowed' : ''
                }`}
              >
                <div className="flex items-start justify-between mb-6">
                  <div className="text-5xl">{card.icon}</div>
                  <div className="flex flex-col items-end gap-2">
                    {card.badge && (
                      <span className="px-3 py-1 bg-indigo-600 text-white text-sm rounded-full font-medium">
                        {card.badge}
                      </span>
                    )}
                    <span className={`px-3 py-1 text-sm rounded-full font-medium ${
                      card.priority === 'high' ? 'bg-red-500/20 text-red-300 border border-red-500/30' : 
                      card.priority === 'medium' ? 'bg-yellow-500/20 text-yellow-300 border border-yellow-500/30' : 
                      'bg-green-500/20 text-green-300 border border-green-500/30'
                    }`}>
                      {card.priority} priority
                    </span>
                  </div>
                </div>
                
                <h3 className="text-2xl font-bold mb-3 text-white">{card.title}</h3>
                <p className="text-gray-300 mb-6 text-lg leading-relaxed">{card.description}</p>
                
                <div className="grid grid-cols-1 gap-4 mb-6">
                  {card.estimated_time && (
                    <div className="flex items-center text-gray-400 bg-gray-700/50 rounded-lg px-4 py-2">
                      <span className="text-lg mr-3">⏱️</span>
                      <span className="font-medium">{card.estimated_time}</span>
                    </div>
                  )}
                  
                  <div className="flex items-center text-gray-400 bg-gray-700/50 rounded-lg px-4 py-2">
                    <span className="text-lg mr-3">📁</span>
                    <span className="font-medium">{card.category}</span>
                  </div>
                </div>
                
                {card.features && card.features.length > 0 && (
                  <div className="border-t border-gray-700 pt-6">
                    <h4 className="text-lg font-semibold text-gray-300 mb-4 flex items-center">
                      <span className="text-xl mr-2">✨</span>
                      Key Features
                    </h4>
                    <ul className="text-gray-300 space-y-3">
                      {card.features.slice(0, 4).map((feature, index) => (
                        <li key={index} className="flex items-start">
                          <span className="w-2 h-2 bg-indigo-400 rounded-full mr-3 mt-2 flex-shrink-0"></span>
                          <span className="leading-relaxed">{feature}</span>
                        </li>
                      ))}
                      {card.features.length > 4 && (
                        <li className="text-gray-500 italic">
                          +{card.features.length - 4} additional features available
                        </li>
                      )}
                    </ul>
                  </div>
                )}
                
                <div className="mt-6 pt-4 border-t border-gray-700">
                  <div className="flex items-center justify-between">
                    <span className="text-sm text-gray-400">Click to access</span>
                    <span className="text-2xl">→</span>
                  </div>
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Featured Frameworks */}
      <div className="p-6">
        <div className="max-w-7xl mx-auto">
          <h2 className="text-2xl font-bold mb-4">Supported Frameworks</h2>
          <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-4">
            {dashboardData.featured_frameworks.map((framework, index) => (
              <div key={index} className="bg-gray-800 rounded-lg p-4 text-center">
                <div className="text-3xl mb-2">{framework.icon}</div>
                <h3 className="font-semibold text-white mb-1">{framework.name}</h3>
                <p className="text-sm text-gray-400 mb-2">{framework.description}</p>
                <span className="px-2 py-1 bg-indigo-600 text-white text-xs rounded">
                  {framework.coverage}
                </span>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* Footer */}
      <footer className="bg-gray-900/80 backdrop-blur-md mt-12 p-6">
        <div className="max-w-7xl mx-auto text-center text-gray-400">
          <p>RiskAI v{dashboardData.dashboard_info.version} - Professional Cybersecurity Risk Assessment Platform</p>
        </div>
      </footer>
    </div>
  );
};

export default MainDashboard;