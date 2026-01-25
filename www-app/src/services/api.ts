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
      (config) => {
        // Add auth headers when available
        // const token = localStorage.getItem('auth_token');
        // if (token) {
        //   config.headers.Authorization = `Bearer ${token}`;
        // }
        return config;
      },
      (error) => Promise.reject(error)
    );

    // Response interceptor
    this.client.interceptors.response.use(
      (response) => response,
      (error: AxiosError) => {
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
