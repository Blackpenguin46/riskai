/**
 * Dashboard API Client
 * Handles communication with the dashboard API endpoints
 */

// API base URL
const API_URL = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';

/**
 * Get dashboard data
 * @returns Dashboard data including scores, sections, and recommendations
 */
export async function getDashboardData() {
  try {
    const response = await fetch(`${API_URL}/api/dashboard/data`);
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error fetching dashboard data:', error);
    throw error;
  }
}

/**
 * Get dashboard statistics
 * @returns Dashboard statistics including trends and completion rates
 */
export async function getDashboardStats() {
  try {
    const response = await fetch(`${API_URL}/api/dashboard/stats`);
    
    if (!response.ok) {
      throw new Error(`HTTP error! status: ${response.status}`);
    }
    
    const data = await response.json();
    return data;
  } catch (error) {
    console.error('Error fetching dashboard stats:', error);
    throw error;
  }
}