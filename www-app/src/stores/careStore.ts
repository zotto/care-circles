import { defineStore } from 'pinia';
import { ref } from 'vue';
import type { CareRequest, CareCircle, CareTask, JobStatusResponse } from '@/types';
import { api } from '@/services/api';
import type { ApiError } from '@/services/api';

/**
 * Main store for Care Circles application
 * Manages care requests, circles, and job status
 */
export const useCareStore = defineStore('care', () => {
  // State
  const currentCareCircle = ref<CareCircle | null>(null);
  const careRequests = ref<CareRequest[]>([]);
  const activeJob = ref<any | null>(null); // Using any to allow extra properties
  const currentJobId = ref<string | null>(null);
  const tasks = ref<CareTask[]>([]);
  const currentPlanId = ref<string | null>(null);
  const shareUrl = ref<string | null>(null);
  const isLoading = ref(false);
  const isPolling = ref(false);
  const error = ref<string | null>(null);

  // Computed
  const hasActiveRequest = () => {
    return careRequests.value.some(
      (request) => request.status === 'processing' || request.status === 'submitted'
    );
  };

  const latestRequest = () => {
    if (careRequests.value.length === 0) return null;
    return careRequests.value.reduce((latest, current) => {
      return new Date(current.created_at) > new Date(latest.created_at) ? current : latest;
    });
  };

  const hasTasks = () => tasks.value.length > 0;

  const isJobComplete = () => {
    return activeJob.value?.status === 'completed';
  };

  // Actions
  const createCareRequest = async (
    narrative: string,
    constraints?: string,
    boundaries?: string
  ): Promise<CareRequest> => {
    isLoading.value = true;
    error.value = null;

    try {
      const response = await api.createCareRequest({
        narrative,
        constraints,
        boundaries,
        care_circle_id: currentCareCircle.value?.id,
      });

      // Store the care request and job ID
      careRequests.value.push(response.care_request);
      currentJobId.value = response.job_id;

      // Create a job object for tracking
      activeJob.value = {
        id: response.job_id,
        care_request_id: response.care_request.id,
        status: 'queued',
        started_at: null,
        completed_at: null,
        error: null,
        current_agent: null,
        agent_progress: {},
      };

      // Start polling for job status
      startPolling(response.job_id);

      return response.care_request;
    } catch (err) {
      const apiError = err as ApiError;
      error.value = apiError.message || 'Failed to create care request';
      throw err;
    } finally {
      isLoading.value = false;
    }
  };

  const getCareRequest = async (id: string): Promise<CareRequest | null> => {
    isLoading.value = true;
    error.value = null;

    try {
      const request = await api.getCareRequest(id);
      return request;
    } catch (err) {
      const apiError = err as ApiError;
      error.value = apiError.message || 'Failed to fetch care request';
      return null;
    } finally {
      isLoading.value = false;
    }
  };

  const fetchJobStatus = async (jobId: string): Promise<JobStatusResponse | null> => {
    try {
      const response = await api.pollJobStatus(jobId, (status) => {
        console.log('📊 Job status update:', {
          status: status.status,
          agent: status.current_agent,
          progress: status.agent_progress,
          hasTasks: !!status.tasks,
          taskCount: status.tasks?.length || 0
        });
        
        // Update active job with progress
        activeJob.value = {
          id: status.job_id,
          care_request_id: status.care_request_id,
          status: status.status,
          started_at: status.started_at,
          completed_at: status.completed_at,
          error: status.error,
          current_agent: status.current_agent,
          agent_progress: status.agent_progress,
        };

        // Update tasks if completed
        if (status.status === 'completed' && status.tasks && status.tasks.length > 0) {
          console.log('✅ Job completed with tasks:', status.tasks.length);
          tasks.value = status.tasks;
          stopPolling();
        }

        // Handle failed status
        if (status.status === 'failed') {
          console.error('❌ Job failed:', status.error);
          error.value = status.error || 'Job failed';
          stopPolling();
        }
      });

      return response;
    } catch (err) {
      const apiError = err as ApiError;
      console.error('❌ Polling error:', apiError);
      error.value = apiError.message || 'Failed to fetch job status';
      stopPolling();
      return null;
    }
  };

  const startPolling = (jobId: string) => {
    // Set polling flag
    isPolling.value = true;

    // Start the long-polling process
    fetchJobStatus(jobId);
  };

  const stopPolling = () => {
    isPolling.value = false;
  };

  const refreshJobStatus = async () => {
    if (currentJobId.value) {
      try {
        const status = await api.getJobStatus(currentJobId.value);
        
        // Update active job
        activeJob.value = {
          id: status.job_id,
          care_request_id: status.care_request_id,
          status: status.status,
          started_at: status.started_at,
          completed_at: status.completed_at,
          error: status.error,
          current_agent: status.current_agent,
          agent_progress: status.agent_progress,
        };

        // Update tasks if completed
        if (status.status === 'completed' && status.tasks) {
          tasks.value = status.tasks;
        }
      } catch (err) {
        const apiError = err as ApiError;
        error.value = apiError.message || 'Failed to refresh job status';
      }
    }
  };

  const updateTask = (taskId: string, updates: Partial<CareTask>) => {
    const taskIndex = tasks.value.findIndex((t) => t.id === taskId);
    if (taskIndex !== -1) {
      tasks.value[taskIndex] = { ...tasks.value[taskIndex], ...updates } as CareTask;
    }
  };

  const deleteTask = (taskId: string) => {
    tasks.value = tasks.value.filter((t) => t.id !== taskId);
  };

  const clearError = () => {
    error.value = null;
  };

  const approvePlan = async (planName?: string): Promise<string | null> => {
    if (!tasks.value || tasks.value.length === 0) {
      error.value = 'No tasks to approve';
      return null;
    }

    const latestReq = latestRequest();
    if (!latestReq) {
      error.value = 'No care request found';
      return null;
    }

    isLoading.value = true;
    error.value = null;

    try {
      // Use provided plan name or default to 'Care Plan'
      const finalPlanName = planName?.trim() || 'Care Plan';
      console.log('Approving plan with name:', finalPlanName, 'provided:', planName);

      // First, create the care plan (if not already created)
      if (!currentPlanId.value) {
        console.log('Creating new plan with name:', finalPlanName);
        const planResponse = await api.createCarePlan(
          latestReq.id,
          finalPlanName,
          tasks.value.map(task => ({
            title: task.title,
            description: task.description,
            category: task.category,
            priority: task.priority,
          }))
        );
        currentPlanId.value = planResponse.plan_id;
      } else {
        // Plan already exists, update the name
        console.log('Updating existing plan', currentPlanId.value, 'with name:', finalPlanName);
        await api.updateCarePlan(currentPlanId.value, finalPlanName);
      }

      // Approve the plan
      await api.approveCarePlan(currentPlanId.value);

      // Generate share link
      const shareResponse = await api.generateShareLink(currentPlanId.value);
      // Construct full URL for sharing
      const baseUrl = window.location.origin;
      shareUrl.value = `${baseUrl}${shareResponse.share_url}`;

      return shareUrl.value;
    } catch (err) {
      const apiError = err as ApiError;
      error.value = apiError.message || 'Failed to approve plan';
      throw err;
    } finally {
      isLoading.value = false;
    }
  };

  const reset = () => {
    stopPolling();
    currentCareCircle.value = null;
    careRequests.value = [];
    activeJob.value = null;
    currentJobId.value = null;
    tasks.value = [];
    currentPlanId.value = null;
    shareUrl.value = null;
    isLoading.value = false;
    isPolling.value = false;
    error.value = null;
  };

  return {
    // State
    currentCareCircle,
    careRequests,
    activeJob,
    currentJobId,
    tasks,
    currentPlanId,
    shareUrl,
    isLoading,
    isPolling,
    error,

    // Computed
    hasActiveRequest,
    latestRequest,
    hasTasks,
    isJobComplete,

    // Actions
    createCareRequest,
    getCareRequest,
    fetchJobStatus,
    startPolling,
    stopPolling,
    refreshJobStatus,
    updateTask,
    deleteTask,
    clearError,
    approvePlan,
    reset,
  };
});
