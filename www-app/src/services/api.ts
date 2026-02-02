/**
 * API Service Layer
 * Handles all HTTP requests to the backend API
 */

import axios, { type AxiosInstance, AxiosError } from 'axios';
import { API } from '@/constants';
import type {
  CareRequest,
  Job,
  CareRequestCreatePayload,
  CareRequestResponse,
  JobStatusResponse,
} from '@/types';
import * as storage from '@/services/storage';
import * as authService from '@/services/auth';

/**
 * API Client Configuration
 */
class ApiClient {
  private client: AxiosInstance;

  constructor() {
    this.client = axios.create({
      baseURL: API.BASE_URL,
      timeout: API.TIMEOUT,
      headers: {
        'Content-Type': 'application/json',
      },
    });

    // Request interceptor
    this.client.interceptors.request.use(
      async (config) => {
        // Get fresh token from Supabase session (handles token refresh automatically)
        // Fallback to localStorage if session is not available
        let token: string | null = null;
        try {
          const session = await authService.getCurrentSession();
          token = session?.access_token ?? null;
          
          // If we got a fresh token, update localStorage
          if (token) {
            storage.saveAccessToken(token);
          }
        } catch (error) {
          // If getting session fails, try localStorage as fallback
          console.warn('Failed to get session, using localStorage token:', error);
          token = storage.getAccessToken();
        }
        
        // If still no token, try localStorage
        if (!token) {
          token = storage.getAccessToken();
        }
        
        if (token) {
          config.headers.Authorization = `Bearer ${token}`;
        }
        return config;
      },
      (error) => Promise.reject(error)
    );

    // Response interceptor
    this.client.interceptors.response.use(
      (response) => response,
      (error: AxiosError) => {
        // Handle 401 - redirect to login
        if (error.response?.status === 401) {
          // Clear auth data
          storage.clearAuthStorage();
          
          // Redirect to login if not already there
          if (window.location.pathname !== '/login') {
            window.location.href = '/login';
          }
        }
        
        return Promise.reject(this.handleError(error));
      }
    );
  }

  private handleError(error: AxiosError): ApiError {
    if (error.response) {
      // Server responded with error status
      return {
        message: (error.response.data as any)?.detail || error.message,
        status: error.response.status,
        data: error.response.data,
      };
    } else if (error.request) {
      // Request made but no response
      return {
        message: 'No response from server. Please check your connection.',
        status: 0,
      };
    } else {
      // Something else happened
      return {
        message: error.message || 'An unexpected error occurred',
        status: 0,
      };
    }
  }

  /**
   * Create a new care request
   */
  async createCareRequest(data: CareRequestCreatePayload): Promise<CareRequestResponse> {
    const response = await this.client.post<CareRequestResponse>('/care-requests', data);
    return response.data;
  }

  /**
   * Get a care request by ID
   */
  async getCareRequest(requestId: string): Promise<CareRequest> {
    const response = await this.client.get<CareRequest>(`/care-requests/${requestId}`);
    return response.data;
  }

  /**
   * Get job status by ID with long-polling support
   * 
   * @param jobId - The job ID to query
   * @param timeout - Maximum wait time in seconds (default: 30)
   * @returns JobStatusResponse when status changes or timeout occurs
   */
  async getJobStatus(jobId: string, timeout: number = 30): Promise<JobStatusResponse> {
    const response = await this.client.get<JobStatusResponse>(`/jobs/${jobId}`, {
      timeout: timeout * 1000, // Convert to milliseconds
    });
    return response.data;
  }

  /**
   * Poll job status with smart polling (non-blocking)
   * Continues polling until job completes or fails
   * 
   * @param jobId - The job ID to monitor
   * @param onProgress - Callback for progress updates
   * @returns Final JobStatusResponse when completed
   */
  async pollJobStatus(
    jobId: string,
    onProgress?: (status: JobStatusResponse) => void
  ): Promise<JobStatusResponse> {
    let lastStatus: string | null = null;
    let lastAgent: string | null = null;
    
    while (true) {
      try {
        const status = await this.getJobStatus(jobId, 5); // 5 second timeout
        
        // Call progress callback if status or agent changed
        if (onProgress) {
          const statusChanged = status.status !== lastStatus;
          const agentChanged = status.current_agent !== lastAgent;
          
          if (statusChanged || agentChanged) {
            onProgress(status);
            lastStatus = status.status;
            lastAgent = status.current_agent;
          }
        }
        
        // Check if job is in terminal state
        if (status.status === 'completed' || status.status === 'failed') {
          // Always call progress one final time to ensure UI updates
          if (onProgress) {
            onProgress(status);
          }
          return status;
        }
        
        // Wait before next poll (2 seconds)
        await new Promise((resolve) => setTimeout(resolve, API.POLL_INTERVAL));
      } catch (error) {
        // On error, wait and retry
        console.warn('Polling error, retrying...', error);
        await new Promise((resolve) => setTimeout(resolve, API.POLL_INTERVAL));
      }
    }
  }

  /**
   * List all jobs (for debugging)
   */
  async listJobs(): Promise<{ total: number; jobs: Job[] }> {
    const response = await this.client.get('/jobs');
    return response.data;
  }

  /**
   * Generic GET request
   */
  async get<T = any>(url: string, config?: any): Promise<{ data: T }> {
    const response = await this.client.get<T>(url, config);
    return { data: response.data };
  }

  /**
   * Generic POST request
   */
  async post<T = any>(url: string, data?: any, config?: any): Promise<{ data: T }> {
    const response = await this.client.post<T>(url, data, config);
    return { data: response.data };
  }

  /**
   * Generic PATCH request
   */
  async patch<T = any>(url: string, data?: any, config?: any): Promise<{ data: T }> {
    const response = await this.client.patch<T>(url, data, config);
    return { data: response.data };
  }

  /**
   * Generic DELETE request
   */
  async delete<T = any>(url: string, config?: any): Promise<{ data: T }> {
    const response = await this.client.delete<T>(url, config);
    return { data: response.data };
  }

  /**
   * Create a care plan from care request (for approval flow)
   */
  async createCarePlan(careRequestId: string, summary: string, tasks: any[]): Promise<{ plan_id: string; care_plan: any }> {
    const response = await this.client.post('/care-plans', {
      care_request_id: careRequestId,
      summary,
      tasks,
    });
    return response.data;
  }

  /**
   * Approve a care plan
   */
  async approveCarePlan(planId: string): Promise<any> {
    const response = await this.client.post(`/care-plans/${planId}/approve`);
    return response.data;
  }

  /**
   * Generate a share link for a care plan
   */
  async generateShareLink(planId: string): Promise<{ share_token: string; share_url: string }> {
    const response = await this.client.post(`/care-plans/${planId}/share`);
    return response.data;
  }

  /**
   * List all care plans for the current user
   */
  async listCarePlans(): Promise<any[]> {
    const response = await this.client.get('/care-plans');
    return response.data;
  }

  /**
   * Get a specific care plan with tasks
   */
  async getCarePlan(planId: string): Promise<any> {
    const response = await this.client.get(`/care-plans/${planId}`);
    return response.data;
  }

  /**
   * Get tasks for a specific care plan
   */
  async getCarePlanTasks(planId: string): Promise<any[]> {
    const response = await this.client.get(`/care-plans/${planId}/tasks`);
    return response.data;
  }

  /**
   * Update care plan summary/name
   */
  async updateCarePlan(planId: string, summary: string): Promise<any> {
    const response = await this.client.patch(`/care-plans/${planId}`, {
      summary,
    });
    return response.data;
  }

  /**
   * Delete a care plan (creator only). Tasks are cascade-deleted.
   */
  async deleteCarePlan(planId: string): Promise<void> {
    await this.client.delete(`/care-plans/${planId}`);
  }

  /**
   * Add a task to an existing plan (creator only).
   */
  async addTaskToPlan(
    planId: string,
    task: { title: string; description?: string; category?: string; priority?: string }
  ): Promise<any> {
    const response = await this.client.post(`/care-plans/${planId}/tasks`, task);
    return response.data;
  }

  /**
   * Delete a task (plan creator only).
   */
  async deleteCareTask(taskId: string): Promise<void> {
    await this.client.delete(`/tasks/${taskId}`);
  }

  /**
   * Add a status update to a claimed task (task diary).
   */
  async addTaskStatus(taskId: string, content: string): Promise<any> {
    const response = await this.client.post(`/tasks/${taskId}/events`, { content });
    return response.data;
  }

  /**
   * Get task diary (events) for a task. Plan owner or task owner.
   */
  async getTaskEvents(taskId: string): Promise<any[]> {
    const response = await this.client.get(`/tasks/${taskId}/events`);
    return response.data;
  }

  /**
   * Complete a task with final outcome (recorded in task diary).
   */
  async completeTaskWithOutcome(taskId: string, outcome: string): Promise<any> {
    const response = await this.client.post(`/tasks/${taskId}/complete`, { outcome });
    return response.data;
  }

  /**
   * Release a task with reason (recorded in task diary).
   */
  async releaseTaskWithReason(taskId: string, reason: string): Promise<any> {
    const response = await this.client.post(`/tasks/${taskId}/release`, { reason });
    return response.data;
  }
}

/**
 * API Error type
 */
export interface ApiError {
  message: string;
  status: number;
  data?: any;
}

// Export singleton instance
export const api = new ApiClient();
