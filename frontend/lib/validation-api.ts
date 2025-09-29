/**
 * Validation API Client
 * Handles communication with the validation API endpoints
 */

// API base URL
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:9000';

/**
 * Get all industry sectors
 * @returns List of industry sectors
 */
export async function getIndustrySectors() {
  const response = await fetch(`${API_URL}/validation/industries`);
  
  if (!response.ok) {
    throw new Error(`Failed to get industry sectors: ${response.statusText}`);
  }
  
  return await response.json();
}

/**
 * Get all security frameworks
 * @returns List of security frameworks
 */
export async function getSecurityFrameworks() {
  const response = await fetch(`${API_URL}/validation/frameworks`);
  
  if (!response.ok) {
    throw new Error(`Failed to get security frameworks: ${response.statusText}`);
  }
  
  return await response.json();
}

/**
 * Get security domains
 * @param frameworkId Optional framework ID filter
 * @returns List of security domains
 */
export async function getSecurityDomains(frameworkId?: number) {
  let url = `${API_URL}/validation/domains`;
  
  if (frameworkId) {
    url += `?framework_id=${frameworkId}`;
  }
  
  const response = await fetch(url);
  
  if (!response.ok) {
    throw new Error(`Failed to get security domains: ${response.statusText}`);
  }
  
  return await response.json();
}

/**
 * Get assessment questions
 * @param domainId Optional domain ID filter
 * @returns List of assessment questions
 */
export async function getAssessmentQuestions(domainId?: number) {
  let url = `${API_URL}/validation/questions`;
  
  if (domainId) {
    url += `?domain_id=${domainId}`;
  }
  
  const response = await fetch(url);
  
  if (!response.ok) {
    throw new Error(`Failed to get assessment questions: ${response.statusText}`);
  }
  
  return await response.json();
}

/**
 * Get industry validations
 * @param industryId Optional industry ID filter
 * @param companySize Optional company size filter
 * @returns List of industry validations
 */
export async function getIndustryValidations(industryId?: number, companySize?: string) {
  let url = `${API_URL}/validation/industry-validations`;
  
  const params = new URLSearchParams();
  if (industryId) {
    params.append('industry_id', industryId.toString());
  }
  
  if (companySize) {
    params.append('company_size', companySize);
  }
  
  if (params.toString()) {
    url += `?${params.toString()}`;
  }
  
  const response = await fetch(url);
  
  if (!response.ok) {
    throw new Error(`Failed to get industry validations: ${response.statusText}`);
  }
  
  return await response.json();
}

/**
 * Get validation metrics for an industry validation
 * @param validationId Validation ID
 * @returns List of validation metrics
 */
export async function getValidationMetrics(validationId: number) {
  const response = await fetch(`${API_URL}/validation/metrics/${validationId}`);
  
  if (!response.ok) {
    throw new Error(`Failed to get validation metrics: ${response.statusText}`);
  }
  
  return await response.json();
}

/**
 * Get validation responses
 * @param questionId Optional question ID filter
 * @param industryId Optional industry ID filter
 * @param companySize Optional company size filter
 * @returns List of validation responses
 */
export async function getValidationResponses(questionId?: number, industryId?: number, companySize?: string) {
  let url = `${API_URL}/validation/responses`;
  
  const params = new URLSearchParams();
  if (questionId) {
    params.append('question_id', questionId.toString());
  }
  
  if (industryId) {
    params.append('industry_id', industryId.toString());
  }
  
  if (companySize) {
    params.append('company_size', companySize);
  }
  
  if (params.toString()) {
    url += `?${params.toString()}`;
  }
  
  const response = await fetch(url);
  
  if (!response.ok) {
    throw new Error(`Failed to get validation responses: ${response.statusText}`);
  }
  
  return await response.json();
}

/**
 * Get scoring rubrics
 * @param domainId Optional domain ID filter
 * @returns List of scoring rubrics
 */
export async function getScoringRubrics(domainId?: number) {
  let url = `${API_URL}/validation/rubrics`;
  
  if (domainId) {
    url += `?domain_id=${domainId}`;
  }
  
  const response = await fetch(url);
  
  if (!response.ok) {
    throw new Error(`Failed to get scoring rubrics: ${response.statusText}`);
  }
  
  return await response.json();
}

/**
 * Get industry benchmarks
 * @param industryId Optional industry ID filter
 * @param domainId Optional domain ID filter
 * @param companySize Optional company size filter
 * @returns List of industry benchmarks
 */
export async function getIndustryBenchmarks(industryId?: number, domainId?: number, companySize?: string) {
  let url = `${API_URL}/validation/benchmarks`;
  
  const params = new URLSearchParams();
  if (industryId) {
    params.append('industry_id', industryId.toString());
  }
  
  if (domainId) {
    params.append('domain_id', domainId.toString());
  }
  
  if (companySize) {
    params.append('company_size', companySize);
  }
  
  if (params.toString()) {
    url += `?${params.toString()}`;
  }
  
  const response = await fetch(url);
  
  if (!response.ok) {
    throw new Error(`Failed to get industry benchmarks: ${response.statusText}`);
  }
  
  return await response.json();
}

/**
 * Get a complete profile for an industry
 * @param industryId Industry ID
 * @returns Industry profile
 */
export async function getIndustryProfile(industryId: number) {
  const response = await fetch(`${API_URL}/validation/industry-profile/${industryId}`);
  
  if (!response.ok) {
    throw new Error(`Failed to get industry profile: ${response.statusText}`);
  }
  
  return await response.json();
}

/**
 * Get a complete profile for a company size
 * @param companySize Company size category
 * @returns Company size profile
 */
export async function getCompanySizeProfile(companySize: string) {
  const response = await fetch(`${API_URL}/validation/company-size-profile/${companySize}`);
  
  if (!response.ok) {
    throw new Error(`Failed to get company size profile: ${response.statusText}`);
  }
  
  return await response.json();
}

/**
 * Get an assessment template for a specific industry and company size
 * @param industryId Optional industry ID filter
 * @param companySize Optional company size filter
 * @param frameworkId Optional framework ID filter
 * @returns Assessment template
 */
export async function getAssessmentTemplate(industryId?: number, companySize?: string, frameworkId?: number) {
  let url = `${API_URL}/validation/assessment-template`;
  
  const params = new URLSearchParams();
  if (industryId) {
    params.append('industry_id', industryId.toString());
  }
  
  if (companySize) {
    params.append('company_size', companySize);
  }
  
  if (frameworkId) {
    params.append('framework_id', frameworkId.toString());
  }
  
  if (params.toString()) {
    url += `?${params.toString()}`;
  }
  
  const response = await fetch(url);
  
  if (!response.ok) {
    throw new Error(`Failed to get assessment template: ${response.statusText}`);
  }
  
  return await response.json();
}

/**
 * Get industry-specific assessment questions
 * @param industryId Industry ID
 * @returns List of industry-specific questions
 */
export async function getIndustrySpecificQuestions(industryId: number) {
  const response = await fetch(`${API_URL}/validation/industry-specific-questions/${industryId}`);
  
  if (!response.ok) {
    throw new Error(`Failed to get industry-specific questions: ${response.statusText}`);
  }
  
  return await response.json();
}

/**
 * Get benchmark comparison for an industry
 * @param industryId Industry ID
 * @param domainId Optional domain ID filter
 * @param companySize Optional company size filter
 * @returns Benchmark comparison
 */
export async function getIndustryBenchmarkComparison(industryId: number, domainId?: number, companySize?: string) {
  let url = `${API_URL}/validation/industry-benchmark-comparison/${industryId}`;
  
  const params = new URLSearchParams();
  if (domainId) {
    params.append('domain_id', domainId.toString());
  }
  
  if (companySize) {
    params.append('company_size', companySize);
  }
  
  if (params.toString()) {
    url += `?${params.toString()}`;
  }
  
  const response = await fetch(url);
  
  if (!response.ok) {
    throw new Error(`Failed to get industry benchmark comparison: ${response.statusText}`);
  }
  
  return await response.json();
}

/**
 * Calculate confidence intervals for validation metrics
 * @param industryId Optional industry ID filter
 * @param companySize Optional company size filter
 * @returns Confidence intervals
 */
export async function calculateConfidenceIntervals(industryId?: number, companySize?: string) {
  let url = `${API_URL}/validation/confidence-intervals`;
  
  const params = new URLSearchParams();
  if (industryId) {
    params.append('industry_id', industryId.toString());
  }
  
  if (companySize) {
    params.append('company_size', companySize);
  }
  
  if (params.toString()) {
    url += `?${params.toString()}`;
  }
  
  const response = await fetch(url);
  
  if (!response.ok) {
    throw new Error(`Failed to calculate confidence intervals: ${response.statusText}`);
  }
  
  return await response.json();
}

/**
 * Perform hypothesis test to compare two industries
 * @param industryId1 First industry ID
 * @param industryId2 Second industry ID
 * @param companySize Optional company size filter
 * @returns Hypothesis test results
 */
export async function performHypothesisTest(industryId1: number, industryId2: number, companySize?: string) {
  let url = `${API_URL}/validation/hypothesis-test?industry_id1=${industryId1}&industry_id2=${industryId2}`;
  
  if (companySize) {
    url += `&company_size=${companySize}`;
  }
  
  const response = await fetch(url);
  
  if (!response.ok) {
    throw new Error(`Failed to perform hypothesis test: ${response.statusText}`);
  }
  
  return await response.json();
}

/**
 * Analyze generalizability of RiskAI across industries and company sizes
 * @returns Generalizability analysis
 */
export async function analyzeGeneralizability() {
  const response = await fetch(`${API_URL}/validation/generalizability`);
  
  if (!response.ok) {
    throw new Error(`Failed to analyze generalizability: ${response.statusText}`);
  }
  
  return await response.json();
}

/**
 * Analyze RiskAI's performance across security domains
 * @param industryId Optional industry ID filter
 * @param companySize Optional company size filter
 * @returns Domain performance analysis
 */
export async function analyzeDomainPerformance(industryId?: number, companySize?: string) {
  let url = `${API_URL}/validation/domain-performance`;
  
  const params = new URLSearchParams();
  if (industryId) {
    params.append('industry_id', industryId.toString());
  }
  
  if (companySize) {
    params.append('company_size', companySize);
  }
  
  if (params.toString()) {
    url += `?${params.toString()}`;
  }
  
  const response = await fetch(url);
  
  if (!response.ok) {
    throw new Error(`Failed to analyze domain performance: ${response.statusText}`);
  }
  
  return await response.json();
}

/**
 * Calculate validation metrics for an industry
 * @param industryId Industry ID
 * @param companySize Optional company size filter
 * @returns Validation metrics
 */
export async function calculateValidationMetrics(industryId: number, companySize?: string) {
  let url = `${API_URL}/validation/calculate-metrics/${industryId}`;
  
  if (companySize) {
    url += `?company_size=${companySize}`;
  }
  
  const response = await fetch(url, {
    method: 'POST'
  });
  
  if (!response.ok) {
    throw new Error(`Failed to calculate validation metrics: ${response.statusText}`);
  }
  
  return await response.json();
}

/**
 * Categorize a company by size based on employee count
 * @param employeeCount Number of employees
 * @returns Company size category
 */
export async function categorizeCompanyBySize(employeeCount: number) {
  const response = await fetch(`${API_URL}/validation/categorize-company?employee_count=${employeeCount}`);
  
  if (!response.ok) {
    throw new Error(`Failed to categorize company by size: ${response.statusText}`);
  }
  
  return await response.json();
}/**

 * Calculate a score for a security domain based on responses
 * @param domainId Security domain ID
 * @param responses Dictionary of question_id -> response_value
 * @param industryId Optional industry ID
 * @param companySize Optional company size
 * @returns Domain score data
 */
export async function calculateDomainScore(
  domainId: number,
  responses: Record<string, any>,
  industryId?: number,
  companySize?: string
) {
  const response = await fetch(`${API_URL}/validation/score/domain`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      domain_id: domainId,
      responses: responses,
      industry_id: industryId,
      company_size: companySize
    }),
  });
  
  if (!response.ok) {
    throw new Error(`Failed to calculate domain score: ${response.statusText}`);
  }
  
  return await response.json();
}

/**
 * Calculate an overall assessment score based on responses
 * @param responses Dictionary of section_id -> {question_id -> response_value}
 * @param frameworkId Optional framework ID
 * @param industryId Optional industry ID
 * @param companySize Optional company size
 * @returns Assessment score data
 */
export async function calculateAssessmentScore(
  responses: Record<string, Record<string, any>>,
  frameworkId?: number,
  industryId?: number,
  companySize?: string
) {
  const response = await fetch(`${API_URL}/validation/score/assessment`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      responses: responses,
      framework_id: frameworkId,
      industry_id: industryId,
      company_size: companySize
    }),
  });
  
  if (!response.ok) {
    throw new Error(`Failed to calculate assessment score: ${response.statusText}`);
  }
  
  return await response.json();
}

/**
 * Generate recommendations based on assessment responses
 * @param responses Dictionary of section_id -> {question_id -> response_value}
 * @param frameworkId Optional framework ID
 * @param industryId Optional industry ID
 * @param companySize Optional company size
 * @returns Assessment score and recommendations
 */
export async function generateRecommendations(
  responses: Record<string, Record<string, any>>,
  frameworkId?: number,
  industryId?: number,
  companySize?: string
) {
  const response = await fetch(`${API_URL}/validation/recommendations`, {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({
      responses: responses,
      framework_id: frameworkId,
      industry_id: industryId,
      company_size: companySize
    }),
  });
  
  if (!response.ok) {
    throw new Error(`Failed to generate recommendations: ${response.statusText}`);
  }
  
  return await response.json();
}