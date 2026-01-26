<template>
  <div class="my-tasks-view">
    <div class="container">
      <div class="page-header">
        <h1 class="page-title">My Tasks</h1>
        <p class="page-description">Tasks you've claimed from care plans</p>
      </div>

      <div v-if="isLoading" class="loading-state">
        <div class="spinner"></div>
        <p>Loading your tasks...</p>
      </div>

      <div v-else-if="error" class="error-state">
        <p class="error-message">{{ error }}</p>
        <button @click="loadTasks" class="retry-button">Try Again</button>
      </div>

      <div v-else-if="myTasks.length === 0" class="empty-state">
        <p>You haven't claimed any tasks yet.</p>
        <p class="empty-hint">Browse shared plans to find tasks you can help with!</p>
      </div>

      <div v-else class="tasks-list">
        <div v-for="task in myTasks" :key="task.id" class="task-card">
          <div class="task-header">
            <span class="task-priority" :class="`priority-${task.priority}`">
              {{ task.priority.toUpperCase() }}
            </span>
            <span class="task-status" :class="`status-${task.status}`">
              {{ task.status }}
            </span>
          </div>

          <h3 class="task-title">{{ task.title }}</h3>
          <p class="task-description">{{ task.description }}</p>

          <div class="task-meta">
            <span class="task-category">{{ task.category }}</span>
          </div>

          <div class="task-actions">
            <button
              v-if="task.status === 'claimed'"
              @click="openCompleteDialog(task)"
              class="action-button primary"
            >
              Mark Complete
            </button>
            <button
              v-if="task.status === 'claimed'"
              @click="openReleaseDialog(task)"
              class="action-button secondary"
            >
              Release Task
            </button>
          </div>
        </div>
      </div>
    </div>

    <!-- Release Confirmation Dialog -->
    <ConfirmDialog
      ref="releaseDialog"
      title="Release Task?"
      message="Are you sure you want to release this task? It will become available for others to claim."
      confirm-text="Release Task"
      cancel-text="Keep Task"
      variant="warning"
      :icon="mdiAlertCircleOutline"
      @confirm="confirmRelease"
      @cancel="cancelRelease"
    />

    <!-- Complete Confirmation Dialog -->
    <ConfirmDialog
      ref="completeDialog"
      title="Mark as Complete?"
      message="Are you sure you want to mark this task as complete?"
      confirm-text="Mark Complete"
      cancel-text="Cancel"
      variant="primary"
      :icon="mdiCheckCircleOutline"
      @confirm="confirmComplete"
      @cancel="cancelComplete"
    />

    <!-- Error Dialog -->
    <ConfirmDialog
      ref="errorDialog"
      :title="errorDialogTitle"
      :message="errorDialogMessage"
      confirm-text="OK"
      :cancel-text="''"
      variant="danger"
      :icon="mdiAlertCircleOutline"
      @confirm="closeErrorDialog"
    />
  </div>
</template>

<script setup lang="ts">
import { ref, onMounted, computed } from 'vue';
import { useTaskStore } from '@/stores/taskStore';
import ConfirmDialog from '@/components/organisms/ConfirmDialog.vue';
import { mdiAlertCircleOutline, mdiCheckCircleOutline } from '@mdi/js';

const taskStore = useTaskStore();

const isLoading = ref(false);
const error = ref<string | null>(null);
const releaseDialog = ref<InstanceType<typeof ConfirmDialog> | null>(null);
const completeDialog = ref<InstanceType<typeof ConfirmDialog> | null>(null);
const errorDialog = ref<InstanceType<typeof ConfirmDialog> | null>(null);
const pendingTaskId = ref<string | null>(null);
const errorDialogTitle = ref('Error');
const errorDialogMessage = ref('An error occurred');

const myTasks = computed(() => taskStore.myTasks);

onMounted(async () => {
  await loadTasks();
});

async function loadTasks() {
  isLoading.value = true;
  error.value = null;

  try {
    await taskStore.fetchMyTasks();
  } catch (err: any) {
    error.value = err.message || 'Failed to load tasks';
  } finally {
    isLoading.value = false;
  }
}

function openCompleteDialog(task: any) {
  pendingTaskId.value = task.id;
  completeDialog.value?.open();
}

function openReleaseDialog(task: any) {
  pendingTaskId.value = task.id;
  releaseDialog.value?.open();
}

async function confirmComplete() {
  if (!pendingTaskId.value || !completeDialog.value) return;

  completeDialog.value.setLoading(true);
  
  try {
    await taskStore.completeTask(pendingTaskId.value);
    completeDialog.value.setLoading(false);
    completeDialog.value.close();
    pendingTaskId.value = null;
  } catch (err: any) {
    completeDialog.value.setLoading(false);
    completeDialog.value.close();
    showError('Failed to Complete Task', err.message || 'Failed to complete task. Please try again.');
  }
}

function cancelComplete() {
  pendingTaskId.value = null;
}

async function confirmRelease() {
  if (!pendingTaskId.value || !releaseDialog.value) return;

  releaseDialog.value.setLoading(true);
  
  try {
    await taskStore.releaseTask(pendingTaskId.value);
    releaseDialog.value.setLoading(false);
    releaseDialog.value.close();
    pendingTaskId.value = null;
  } catch (err: any) {
    releaseDialog.value.setLoading(false);
    releaseDialog.value.close();
    showError('Failed to Release Task', err.message || 'Failed to release task. Please try again.');
  }
}

function cancelRelease() {
  pendingTaskId.value = null;
}

function showError(title: string, message: string) {
  errorDialogTitle.value = title;
  errorDialogMessage.value = message;
  errorDialog.value?.open();
}

function closeErrorDialog() {
  errorDialog.value?.close();
}
</script>

<style scoped>
.my-tasks-view {
  min-height: 100vh;
  padding: var(--spacing-2xl) 0;
  background: var(--color-bg-primary);
}

.container {
  max-width: 1000px;
  margin: 0 auto;
  padding: 0 var(--spacing-lg);
}

.page-header {
  margin-bottom: var(--spacing-2xl);
}

.page-title {
  font-size: var(--font-size-3xl);
  font-weight: var(--font-weight-bold);
  color: var(--color-text-primary);
  margin: 0 0 var(--spacing-xs);
}

.page-description {
  font-size: var(--font-size-base);
  color: var(--color-text-secondary);
  margin: 0;
}

.loading-state,
.error-state,
.empty-state {
  text-align: center;
  padding: var(--spacing-2xl);
}

.spinner {
  width: 48px;
  height: 48px;
  border: 4px solid var(--color-border);
  border-top-color: var(--color-primary);
  border-radius: 50%;
  animation: spin 1s linear infinite;
  margin: 0 auto var(--spacing-lg);
}

@keyframes spin {
  to {
    transform: rotate(360deg);
  }
}

.error-message {
  color: var(--color-danger);
  margin-bottom: var(--spacing-lg);
}

.retry-button {
  padding: var(--spacing-md) var(--spacing-xl);
  background: var(--color-primary);
  color: white;
  border: none;
  border-radius: var(--radius-md);
  cursor: pointer;
}

.empty-hint {
  color: var(--color-text-tertiary);
  margin-top: var(--spacing-sm);
}

.tasks-list {
  display: grid;
  gap: var(--spacing-lg);
}

.task-card {
  background: white;
  border: 1px solid var(--color-border);
  border-radius: var(--radius-lg);
  padding: var(--spacing-lg);
  box-shadow: var(--shadow-sm);
  transition: all var(--transition-base);
}

.task-card:hover {
  box-shadow: var(--shadow-md);
}

.task-header {
  display: flex;
  gap: var(--spacing-sm);
  margin-bottom: var(--spacing-md);
}

.task-priority,
.task-status {
  padding: 4px 12px;
  border-radius: var(--radius-full);
  font-size: var(--font-size-xs);
  font-weight: var(--font-weight-semibold);
  text-transform: uppercase;
}

.priority-high {
  background: var(--color-danger-light);
  color: var(--color-danger);
}

.priority-medium {
  background: var(--color-warning-light);
  color: var(--color-warning);
}

.priority-low {
  background: var(--color-success-light);
  color: var(--color-success);
}

.status-claimed {
  background: var(--color-info-light);
  color: var(--color-info);
}

.status-completed {
  background: var(--color-success-light);
  color: var(--color-success);
}

.task-title {
  font-size: var(--font-size-lg);
  font-weight: var(--font-weight-semibold);
  color: var(--color-text-primary);
  margin: 0 0 var(--spacing-sm);
}

.task-description {
  font-size: var(--font-size-base);
  color: var(--color-text-secondary);
  line-height: 1.6;
  margin: 0 0 var(--spacing-md);
}

.task-meta {
  margin-bottom: var(--spacing-md);
}

.task-category {
  display: inline-block;
  padding: 4px 12px;
  background: var(--color-bg-secondary);
  border-radius: var(--radius-sm);
  font-size: var(--font-size-sm);
  color: var(--color-text-secondary);
}

.task-actions {
  display: flex;
  gap: var(--spacing-sm);
  margin-top: var(--spacing-lg);
}

.action-button {
  padding: var(--spacing-sm) var(--spacing-lg);
  border-radius: var(--radius-md);
  font-size: var(--font-size-sm);
  font-weight: var(--font-weight-semibold);
  cursor: pointer;
  transition: all var(--transition-base);
  border: none;
}

.action-button.primary {
  background: var(--color-primary);
  color: white;
}

.action-button.primary:hover {
  background: var(--color-primary-dark);
}

.action-button.secondary {
  background: white;
  color: var(--color-text-secondary);
  border: 1px solid var(--color-border);
}

.action-button.secondary:hover {
  background: var(--color-bg-secondary);
}
</style>
