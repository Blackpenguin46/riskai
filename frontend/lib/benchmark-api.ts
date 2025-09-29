/**
 * Benchmark API Client
 * Handles communication with the benchmark API endpoints
 */

// API base URL
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:9000';

/**
 * Get tool comparison data for a specific category
 * @param category Category to compare
 * @param metricName Optional specific metric to compare
 * @param industry Optional industry filter
 * @param companySize Optional company size filter
 * @returns Tool comparison data
 */
export async function getToolComparisonChart(
  category: string,
  metricName?: string,
  industry?: string,
  companySize?: string
) {
  let url = `${API_URL}/benchmarks/visualization/tool-comparison?category=${encodeURIComponent(category)}`;
  
  if (metricName) {
    url += `&metric_name=${encodeURIComponent(metricName)}`;
  }
  
  if (industry) {
    url += `&industry=${encodeURIComponent(industry)}`;
  }
  
  if (companySize) {
    url += `&company_size=${encodeURIComponent(companySize)}`;
  }
  
  const response = await fetch(url);
  
  if (!response.ok) {
    throw new Error(`Failed to get tool comparison chart: ${response.statusText}`);
  }
  
  return await response.json();
}

/**
 * Get category comparison data
 * @param industry Optional industry filter
 * @param companySize Optional company size filter
 * @returns Category comparison data
 */
export async function getCategoryComparisonChart(industry?: string, companySize?: string) {
  let url = `${API_URL}/benchmarks/visualization/category-comparison`;
  
  const params = new URLSearchParams();
  if (industry) {
    params.append('industry', industry);
  }
  
  if (companySize) {
    params.append('company_size', companySize);
  }
  
  if (params.toString()) {
    url += `?${params.toString()}`;
  }
  
  const response = await fetch(url);
  
  if (!response.ok) {
    throw new Error(`Failed to get category comparison chart: ${response.statusText}`);
  }
  
  return await response.json();
}

/**
 * Get ROI chart data
 * @param companySize Optional company size filter
 * @returns ROI chart data
 */
export async function getROIChart(companySize?: string) {
  let url = `${API_URL}/benchmarks/visualization/roi`;
  
  if (companySize) {
    url += `?company_size=${encodeURIComponent(companySize)}`;
  }
  
  const response = await fetch(url);
  
  if (!response.ok) {
    throw new Error(`Failed to get ROI chart: ${response.statusText}`);
  }
  
  return await response.json();
}

/**
 * Get strengths and weaknesses chart data
 * @returns Strengths and weaknesses chart data
 */
export async function getStrengthsWeaknessesChart() {
  const response = await fetch(`${API_URL}/benchmarks/visualization/strengths-weaknesses`);
  
  if (!response.ok) {
    throw new Error(`Failed to get strengths and weaknesses chart: ${response.statusText}`);
  }
  
  return await response.json();
}

/**
 * Get comprehensive dashboard data
 * @param industry Optional industry filter
 * @param companySize Optional company size filter
 * @returns Dashboard data
 */
export async function getDashboardData(industry?: string, companySize?: string) {
  let url = `${API_URL}/benchmarks/visualization/dashboard`;
  
  const params = new URLSearchParams();
  if (industry) {
    params.append('industry', industry);
  }
  
  if (companySize) {
    params.append('company_size', companySize);
  }
  
  if (params.toString()) {
    url += `?${params.toString()}`;
  }
  
  const response = await fetch(url);
  
  if (!response.ok) {
    throw new Error(`Failed to get dashboard data: ${response.statusText}`);
  }
  
  return await response.json();
}

/**
 * Get comprehensive report data
 * @param industry Optional industry filter
 * @param companySize Optional company size filter
 * @param format Output format ('json' or 'html')
 * @returns Report data
 */
export async function getReportData(industry?: string, companySize?: string, format: string = 'json') {
  let url = `${API_URL}/benchmarks/visualization/report`;
  
  const params = new URLSearchParams();
  if (industry) {
    params.append('industry', industry);
  }
  
  if (companySize) {
    params.append('company_size', companySize);
  }
  
  params.append('format', format);
  
  url += `?${params.toString()}`;
  
  const response = await fetch(url);
  
  if (!response.ok) {
    throw new Error(`Failed to get report data: ${response.statusText}`);
  }
  
  return await response.json();
}

/**
 * Compare tools by category
 * @param category Category to compare
 * @param industry Optional industry filter
 * @param companySize Optional company size filter
 * @returns Comparison data
 */
export async function compareToolsByCategory(category: string, industry?: string, companySize?: string) {
  let url = `${API_URL}/benchmarks/compare/category/${encodeURIComponent(category)}`;
  
  const params = new URLSearchParams();
  if (industry) {
    params.append('industry', industry);
  }
  
  if (companySize) {
    params.append('company_size', companySize);
  }
  
  if (params.toString()) {
    url += `?${params.toString()}`;
  }
  
  const response = await fetch(url);
  
  if (!response.ok) {
    throw new Error(`Failed to compare tools by category: ${response.statusText}`);
  }
  
  return await response.json();
}

/**
 * Compare all categories
 * @param industry Optional industry filter
 * @param companySize Optional company size filter
 * @returns Comparison data for all categories
 */
export async function compareAllCategories(industry?: string, companySize?: string) {
  let url = `${API_URL}/benchmarks/compare/all`;
  
  const params = new URLSearchParams();
  if (industry) {
    params.append('industry', industry);
  }
  
  if (companySize) {
    params.append('company_size', companySize);
  }
  
  if (params.toString()) {
    url += `?${params.toString()}`;
  }
  
  const response = await fetch(url);
  
  if (!response.ok) {
    throw new Error(`Failed to compare all categories: ${response.statusText}`);
  }
  
  return await response.json();
}

/**
 * Calculate ROI metrics
 * @param companySize Optional company size filter
 * @returns ROI metrics
 */
export async function calculateROIMetrics(companySize?: string) {
  let url = `${API_URL}/benchmarks/roi/metrics`;
  
  if (companySize) {
    url += `?company_size=${encodeURIComponent(companySize)}`;
  }
  
  const response = await fetch(url);
  
  if (!response.ok) {
    throw new Error(`Failed to calculate ROI metrics: ${response.statusText}`);
  }
  
  return await response.json();
}

/**
 * Analyze strengths and weaknesses
 * @returns Strengths and weaknesses analysis
 */
export async function analyzeStrengthsAndWeaknesses() {
  const response = await fetch(`${API_URL}/benchmarks/strengths-weaknesses`);
  
  if (!response.ok) {
    throw new Error(`Failed to analyze strengths and weaknesses: ${response.statusText}`);
  }
  
  return await response.json();
}

/**
 * Generate comparative report
 * @param industry Optional industry filter
 * @param companySize Optional company size filter
 * @returns Comparative report
 */
export async function generateComparativeReport(industry?: string, companySize?: string) {
  let url = `${API_URL}/benchmarks/report`;
  
  const params = new URLSearchParams();
  if (industry) {
    params.append('industry', industry);
  }
  
  if (companySize) {
    params.append('company_size', companySize);
  }
  
  if (params.toString()) {
    url += `?${params.toString()}`;
  }
  
  const response = await fetch(url);
  
  if (!response.ok) {
    throw new Error(`Failed to generate comparative report: ${response.statusText}`);
  }
  
  return await response.json();
}