/**
 * Risk Categorization API Client
 * Handles communication with the risk categorization API endpoints
 */

// API base URL
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

// Types
export interface ConfidenceInterval {
  lower_bound: number;
  upper_bound: number;
  confidence_level: number;
  margin_of_error: number;
  sample_size: number;
}

export interface RiskAssessment {
  score: number;
  risk_level: string;
  risk_label: string;
  risk_color: string;
  risk_description: string;
  action_required: string;
  confidence_interval: ConfidenceInterval;
  statistical_significance: number;
  benchmark_comparison: Record<string, any>;
  trend_analysis: Record<string, any>;
  recommendations: string[];
}

export interface RiskCategorizationRequest {
  score: number;
  completion_rate?: number;
  industry?: string;
  company_size?: string;
  historical_scores?: number[];
}

/**
 * Get risk level information based on score
 * @param score Numerical score (0-100)
 * @returns Risk level information
 */
export function getRiskLevelInfo(score: number): {
  level: string;
  label: string;
  color: string;
  description: string;
} {
  if (score >= 0 && score <= 40) {
    return {
      level: 'CRITICAL',
      label: 'Critical Risk',
      color: '#dc2626',
      description: 'Immediate action required. Significant security gaps pose severe risk.',
    };
  } else if (score > 40 && score <= 60) {
    return {
      level: 'HIGH',
      label: 'High Risk',
      color: '#ea580c',
      description: 'Priority improvements needed. Notable security weaknesses require prompt attention.',
    };
  } else if (score > 60 && score <= 80) {
    return {
      level: 'MEDIUM',
      label: 'Medium Risk',
      color: '#ca8a04',
      description: 'Moderate improvements recommended. Security posture is adequate but can be enhanced.',
    };
  } else {
    return {
      level: 'LOW',
      label: 'Low Risk',
      color: '#16a34a',
      description: 'Maintain current practices. Strong security posture with minor optimization opportunities.',
    };
  }
}

/**
 * Format score as a percentage
 * @param score Numerical score
 * @returns Formatted percentage string
 */
export function formatScore(score: number): string {
  return `${Math.round(score)}%`;
}

/**
 * Get available industries for benchmarking
 * @returns List of available industries
 */
export function getAvailableIndustries(): string[] {
  return [
    'financial_services',
    'healthcare',
    'technology',
    'manufacturing',
    'government'
  ];
}

/**
 * Get available company sizes
 * @returns List of available company sizes
 */
export function getAvailableCompanySizes(): string[] {
  return ['small', 'medium', 'large', 'enterprise'];
}