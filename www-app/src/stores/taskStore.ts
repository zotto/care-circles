/**
 * Task Store
 * 
 * Manages user's claimed tasks.
 */

import { defineStore } from 'pinia';
import { ref } from 'vue';
import type { CareTask } from '@/types';
import { api } from '@/services/api';
import type { ApiError } from '@/services/api';

export const useTaskStore = defineStore('task', () => {
  // State
  const myTasks = ref<CareTask[]>([]);
  const isLoading = ref(false);
  const error = ref<string | null>(null);

  // Actions
  async function fetchMyTasks() {
    isLoading.value = true;
    error.value = null;

    try {
      const response = await api.get('/users/me/tasks');
      myTasks.value = response.data;
    } catch (err) {
      const apiError = err as ApiError;
      error.value = apiError.message || 'Failed to fetch your tasks';
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  async function claimTask(taskId: string): Promise<CareTask> {
    isLoading.value = true;
    error.value = null;

    try {
      const response = await api.post(`/tasks/${taskId}/claim`);
      const claimedTask = response.data;

      // Add to my tasks if not already there
      const exists = myTasks.value.some((t) => t.id === taskId);
      if (!exists) {
        myTasks.value.push(claimedTask);
      }

      return claimedTask;
    } catch (err) {
      const apiError = err as ApiError;
      error.value = apiError.message || 'Failed to claim task';
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  async function releaseTask(taskId: string): Promise<CareTask> {
    isLoading.value = true;
    error.value = null;

    try {
      const response = await api.post(`/tasks/${taskId}/release`);
      const releasedTask = response.data;

      // Remove from my tasks
      myTasks.value = myTasks.value.filter((t) => t.id !== taskId);

      return releasedTask;
    } catch (err) {
      const apiError = err as ApiError;
      error.value = apiError.message || 'Failed to release task';
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  async function completeTask(taskId: string): Promise<CareTask> {
    isLoading.value = true;
    error.value = null;

    try {
      const response = await api.post(`/tasks/${taskId}/complete`);
      const completedTask = response.data;

      // Update in my tasks
      const index = myTasks.value.findIndex((t) => t.id === taskId);
      if (index !== -1) {
        myTasks.value[index] = completedTask;
      }

      return completedTask;
    } catch (err) {
      const apiError = err as ApiError;
      error.value = apiError.message || 'Failed to complete task';
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  async function updateTask(taskId: string, updates: Partial<CareTask>): Promise<CareTask> {
    isLoading.value = true;
    error.value = null;

    try {
      const response = await api.patch(`/tasks/${taskId}`, updates);
      const updatedTask = response.data;

      // Update in my tasks
      const index = myTasks.value.findIndex((t) => t.id === taskId);
      if (index !== -1) {
        myTasks.value[index] = updatedTask;
      }

      return updatedTask;
    } catch (err) {
      const apiError = err as ApiError;
      error.value = apiError.message || 'Failed to update task';
      throw err;
    } finally {
      isLoading.value = false;
    }
  }

  function clearError() {
    error.value = null;
  }

  function reset() {
    myTasks.value = [];
    isLoading.value = false;
    error.value = null;
  }

  return {
    // State
    myTasks,
    isLoading,
    error,

    // Actions
    fetchMyTasks,
    claimTask,
    releaseTask,
    completeTask,
    updateTask,
    clearError,
    reset,
  };
});
