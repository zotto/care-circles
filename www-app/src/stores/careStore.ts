import { defineStore } from 'pinia';
import { ref, computed } from 'vue';
import type { CareRequest, CareCircle, Job } from '@/types';

/**
 * Main store for Care Circles application
 * Manages care requests, circles, and job status
 */
export const useCareStore = defineStore('care', () => {
  // State
  const currentCareCircle = ref<CareCircle | null>(null);
  const careRequests = ref<CareRequest[]>([]);
  const activeJob = ref<Job | null>(null);
  const isLoading = ref(false);
  const error = ref<string | null>(null);

  // Computed
  const hasActiveRequest = computed(() => {
    return careRequests.value.some(
      (request) => request.status === 'processing' || request.status === 'submitted'
    );
  });

  const latestRequest = computed(() => {
    if (careRequests.value.length === 0) return null;
    return careRequests.value.reduce((latest, current) => {
      return new Date(current.created_at) > new Date(latest.created_at) ? current : latest;
    });
  });

  // Actions
  const createCareRequest = async (
    narrative: string,
    constraints?: string,
    boundaries?: string
  ): Promise<CareRequest> => {
    isLoading.value = true;
    error.value = null;

    try {
      // TODO: Replace with actual API call when backend is ready
      // const response = await fetch('/api/care-requests', {
      //   method: 'POST',
      //   headers: { 'Content-Type': 'application/json' },
      //   body: JSON.stringify({ narrative, constraints, boundaries })
      // });
      // const data = await response.json();

      // Mock implementation for now
      const mockRequest: CareRequest = {
        id: `req_${Date.now()}`,
        care_circle_id: currentCareCircle.value?.id || 'default',
        narrative,
        constraints,
        boundaries,
        status: 'submitted',
        created_at: new Date().toISOString(),
      };

      careRequests.value.push(mockRequest);
      return mockRequest;
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to create care request';
      throw err;
    } finally {
      isLoading.value = false;
    }
  };

  const getCareRequest = async (id: string): Promise<CareRequest | null> => {
    isLoading.value = true;
    error.value = null;

    try {
      // TODO: Replace with actual API call
      // const response = await fetch(`/api/care-requests/${id}`);
      // const data = await response.json();

      const request = careRequests.value.find((r) => r.id === id);
      return request || null;
    } catch (err) {
      error.value = err instanceof Error ? err.message : 'Failed to fetch care request';
      return null;
    } finally {
      isLoading.value = false;
    }
  };

  const pollJobStatus = async (jobId: string): Promise<Job> => {
    // TODO: Replace with actual API call
    // const response = await fetch(`/api/jobs/${jobId}`);
    // const data = await response.json();

    // Mock implementation
    const mockJob: Job = {
      id: jobId,
      care_request_id: latestRequest.value?.id || '',
      status: 'queued',
      started_at: new Date().toISOString(),
      completed_at: null,
      error: null,
    };

    activeJob.value = mockJob;
    return mockJob;
  };

  const clearError = () => {
    error.value = null;
  };

  const reset = () => {
    currentCareCircle.value = null;
    careRequests.value = [];
    activeJob.value = null;
    isLoading.value = false;
    error.value = null;
  };

  return {
    // State
    currentCareCircle,
    careRequests,
    activeJob,
    isLoading,
    error,

    // Computed
    hasActiveRequest,
    latestRequest,

    // Actions
    createCareRequest,
    getCareRequest,
    pollJobStatus,
    clearError,
    reset,
  };
});
